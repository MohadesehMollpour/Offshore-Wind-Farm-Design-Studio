"""Export a reproducible source library and ZIP for a prepared regional overview."""
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path
from backend import store
from backend.ingestion import attached_data,DATA_ROOT
from backend.overview_data import curve_power

def export(sid,output):
    s=store.get_scenario(sid);external=attached_data(s);results=store.get_results(sid)
    source=external['overview_inputs'];wind=external['era5_wind'];data=results['C27']['data']
    if data.get('estimate_type')!='regional_reference_estimate':raise ValueError('Run the explicit regional energy case first')
    output=Path(output);output.mkdir(parents=True,exist_ok=True);library=DATA_ROOT/'library'/f'overview-r{s["revision"]}'
    library.mkdir(parents=True,exist_ok=True);files={};manifest=[]
    def add(name,content):
        raw=content.encode('utf-8') if isinstance(content,str) else content
        (library/name).write_bytes(raw);files[name]=raw
        manifest.append({'filename':name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    for name,url in source['data']['files'].items():
        asset=next(a for a in source['meta']['raw_assets'] if a['url']==url)
        path=(DATA_ROOT/asset['path']).resolve()
        if not path.is_relative_to(DATA_ROOT.resolve()):raise ValueError('Raw asset path escaped data directory')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=asset['sha256']:raise ValueError('Source checksum mismatch: '+name)
        add(name,raw)
    asset=wind['meta']['raw_assets'][0];raw=(DATA_ROOT/asset['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=asset['sha256']:raise ValueError('Wind source checksum mismatch')
    add('Open-Meteo-ERA5-original.json',raw)
    def csv_text(header,rows):
        stream=io.StringIO(newline='');writer=csv.writer(stream);writer.writerow(header);writer.writerows(rows);return stream.getvalue()
    low=wind['data']['heights']['10']['rows'];high=wind['data']['heights']['100']['rows'];n=s['inputs']['capacity_mw']/15
    factor=1
    for loss in data['losses']:factor*=1-loss['fraction']
    rows=[]
    for a,b in zip(low,high):
        v=b['speed']*1.5**data['shear_exponent'];power=curve_power(v,source['data']['curve'])*n
        rows.append([b['timestamp_utc'],a['speed'],a['direction'],b['speed'],b['direction'],v,power,power*factor])
    add('Hourly-wind-and-derived-regional-generation.csv',csv_text(['timestamp_utc','source_10m_speed_ms','source_10m_from_direction_deg','source_100m_speed_ms','source_100m_from_direction_deg','model_extrapolated_150m_speed_ms','model_gross_plant_mw','model_net_plant_mw'],rows))
    add('Monthly-regional-energy.csv',csv_text(['month','normalized_net_mwh'],[[r['month'],r['net_mwh']] for r in data['monthly_estimates']]))
    add('Weather-year-regional-energy.csv',csv_text(['weather_year','annualized_net_mwh','sample_hours'],[[r['year'],r['net_aep_mwh'],r['sample_hours']] for r in data['annual_estimates']]))
    add('Overview-results-and-assumptions.json',json.dumps({'scenario':s,'energy':results['C27'],'cost':results['C60']},indent=2))
    add('Source-provenance.json',json.dumps({k:external[k]['meta'] for k in ['overview_inputs','era5_wind']},indent=2))
    readme=f'''# Downloaded overview evidence — revision {s['revision']}

Scenario: {sid}. Reference point: {s['inputs']['screening_point']}.

The original DESNZ workbook and PDFs, published turbine curve/specification/licence and original Open-Meteo ERA5 JSON are preserved unchanged. The hourly CSV joins the source 10 m/100 m wind with explicitly labelled model outputs. Modelled 150 m wind is not a measurement. The JSON records parameters, source cells, methods and limitations.

Net annual energy: {data['net_aep_mwh']/1000:,.1f} GWh/year. Regional LCOE: {data['lcoe_gbp_mwh']:.2f} real 2024 GBP/MWh. These are planning estimates for {s['inputs']['capacity_mw']:g} MW, not site-specific or investment-ready results.

ERA5: {len(high):,} hourly records at each of 10 m and 100 m, {high[0]['timestamp_utc'][:10]} through {high[-1]['timestamp_utc'][:10]}. IEA reference turbine: 15 MW, 240 m rotor, 150 m hub. Applied losses: {', '.join(r['name']+' '+str(round(100*r['fraction'],3))+'%' for r in data['losses'])}. Electrical loss and curtailment are modelling assumptions. Wake and availability use the manually checked Arup benchmark on PDF page 53 (printed page 48), unless overridden in the scenario. A constant shear exponent is derived from the ratio of the period-mean 100 m and 10 m speeds.

Cost components: predevelopment and construction CAPEX, fixed O&M, insurance, connection/use-of-system charges and terminal decommissioning. Real discounting; CAPEX at year zero. Construction financing/phasing, tax, debt, degradation, seabed rent and site premiums are excluded. The source DESNZ published generic LCOE is a separate benchmark, not this calculation. Revenue, NPV, IRR and payback remain unavailable.

Source portal: https://www.gov.uk/government/publications/electricity-generation-costs-2025
Wind API documentation: https://open-meteo.com/en/docs/historical-weather-api
Turbine archive: https://github.com/NatLabRockies/turbine-models

Licences and attribution: DESNZ Open Government Licence v3.0; Arup report Crown copyright as noted in the source; NREL/IEA archive BSD-3-Clause (included); ERA5/Copernicus via Open-Meteo CC BY 4.0, educational access. File SHA-256 checksums are listed in manifest.json; the manifest excludes its own checksum.
'''
    add('README.md',readme)
    files['manifest.json']=json.dumps({'scenario_id':sid,'revision':s['revision'],'files':manifest},indent=2).encode()
    (library/'manifest.json').write_bytes(files['manifest.json'])
    archive=output/'Wind_Overview_Data.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,raw in files.items():z.writestr(name,raw)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for row in manifest:assert hashlib.sha256(z.read(row['filename'])).hexdigest()==row['sha256']
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'library':str(library),'files':len(files),'scenario_id':sid,'revision':s['revision']},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--scenario-id',required=True);parser.add_argument('--output-dir',required=True);args=parser.parse_args();export(args.scenario_id,args.output_dir)
