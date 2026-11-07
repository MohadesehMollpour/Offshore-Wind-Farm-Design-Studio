"""Explicit regional energy/cost case; never a promotion to site evidence."""
import bisect,calendar,csv,hashlib,io,math,posixpath,re,zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from .engineering import finite

COST_PAGE='https://www.gov.uk/government/publications/electricity-generation-costs-2025'
ARUP_URL='https://assets.publishing.service.gov.uk/media/6966a5c7e8c04eb2919f773d/lcoe-2024-offshore-wind.pdf'
ARUP_SHA='e9e999f01dbeb9a284af1015400d7d490230080f57699cb399243325338c31a7'
TURBINE_ROOT='https://raw.githubusercontent.com/NatLabRockies/turbine-models/main/'
CASE_DEFAULTS={'enabled':True,'electrical_loss':.03,'curtailment_loss':.02}
CATEGORIES=['C21','C26','C27','C29','C58','C59','C60','C61']

def workbook_cells(raw):
    """Read published cached values, never execute macros, formulas or external links."""
    n={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        def read(path):
            if z.getinfo(path).file_size>30_000_000:raise ValueError('Workbook XML exceeds the parsing limit')
            return ET.fromstring(z.read(path))
        strings=[''.join(t.text or '' for t in s.findall('.//m:t',n)) for s in read('xl/sharedStrings.xml')]
        relationships={r.get('Id'):r.get('Target') for r in read('xl/_rels/workbook.xml.rels')}
        sheets={}
        for sheet in read('xl/workbook.xml').findall('m:sheets/m:sheet',n):
            target=relationships[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            path=posixpath.normpath(posixpath.join('xl',target)) if not target.startswith('/') else target.lstrip('/')
            if not path.startswith('xl/worksheets/'):raise ValueError('Unexpected workbook relationship')
            cells={}
            for cell in read(path).findall('.//m:sheetData/m:row/m:c',n):
                v=cell.find('m:v',n);value=v.text if v is not None else None
                if cell.get('t')=='e':value=None
                elif cell.get('t')=='s' and value is not None:value=strings[int(value)]
                elif cell.get('t')=='inlineStr':value=''.join(t.text or '' for t in cell.findall('.//m:t',n))
                cells[cell.get('r')]=value
            sheets[sheet.get('name')]=cells
    return sheets

def parse_costs(raw):
    sheets=workbook_cells(raw);home=sheets['Home'];cells=sheets['Technical and Cost Assumptions']
    if home.get('C25')!='All costs are in real 2024 GBP':raise ValueError('DESNZ cost price basis changed; review before use')
    expected={'A1':'Technology','A3':'Reference plant size','A6':'Operating lifetime','A7':'Pre-development Cost','A19':'Construction Cost','A34':'Fixed O&M','A36':'Insurance','A37':'Connection and use of system charges','A38':'Hurdle Rate','A42':'Decommissioning Cost','N1':'Fixed Offshore Wind','B8':'Medium','B20':'Medium','B39':'Medium','B43':'Medium'}
    if any(cells.get(k)!=v for k,v in expected.items()):raise ValueError('DESNZ fixed-offshore table layout changed')
    units={'C3':'MW','C6':'years','C7':'£/kW','C19':'£/kW','C34':'£/MW/year','C35':'£/MWh','C36':'£/MW/year','C37':'£/MW/year','C38':'%','C42':'£/MW'}
    if any(cells.get(k)!=v for k,v in units.items()):raise ValueError('DESNZ table units changed')
    result=[]
    for col,year in zip('NOPQR',[2030,2035,2040,2045,2050]):
        if int(cells[col+'2'])!=year:raise ValueError('Unexpected DESNZ commissioning year')
        def num(row):
            v=cells.get(col+str(row))
            if v is None:raise ValueError('Missing published cost value: '+col+str(row))
            return finite(v,'DESNZ '+col+str(row),0)
        text=cells[col+'4'];match=re.fullmatch(r'(\d+(?:\.\d+)?)%11',text or '')
        if not match:raise ValueError('Review the DESNZ load-factor value and footnote')
        estimates=sheets[f'Additional Estimates {year}']
        if not estimates.get('E4','').startswith('Fixed Offshore Wind') or estimates.get('B15')!='£/MWh':raise ValueError('DESNZ LCOE column changed')
        result.append({'commissioning_year':year,'price_year':2024,'currency':'GBP','reference_plant_mw':num(3),'net_load_factor':float(match[1])/100,'lifetime_years':int(num(6)),
            'predevelopment_gbp_kw':num(8),'construction_gbp_kw':num(20),'capex_low_gbp_kw':num(7)+num(19),'capex_high_gbp_kw':num(9)+num(21),
            'fixed_om_gbp_mw_year':num(34),'variable_om_gbp_mwh':num(35),'insurance_gbp_mw_year':num(36),'connection_gbp_mw_year':num(37),
            'discount_rate':num(39),'discount_low':num(38),'discount_high':num(40),'decommission_gbp_mw':num(43),'published_lcoe_gbp_mwh':finite(estimates['E15'],'published LCOE',0),
            'source_sheet':'Technical and Cost Assumptions','source_column':col,'source_cells':{col+str(r):cells.get(col+str(r)) for r in [2,3,4,6,7,8,9,19,20,21,34,35,36,37,38,39,40,43]},'published_lcoe_cell':f'Additional Estimates {year}!E15'})
    return result

def parse_curve(raw):
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if not {'Wind Speed [m/s]','Power [kW]'}.issubset(reader.fieldnames or []):raise ValueError('Reference power-curve headers changed')
    rows=[{'speed_ms':finite(r['Wind Speed [m/s]'],'curve speed',0,40),'power_mw':finite(r['Power [kW]'],'curve kW',0,15001)/1000} for r in reader]
    if len(rows)<10 or any(b['speed_ms']<=a['speed_ms'] for a,b in zip(rows,rows[1:])):raise ValueError('Power-curve wind speeds must be strictly increasing')
    if abs(rows[0]['speed_ms']-3)>.001 or abs(rows[-1]['speed_ms']-25)>.001 or max(r['power_mw'] for r in rows)<14.9:raise ValueError('Unexpected IEA 15 MW power curve coverage')
    return rows

def collect_overview(fetch):
    html=fetch.get(COST_PAGE,ttl_hours=720).decode();urls=re.findall(r'href=["\']([^"\']+)["\']',html)
    workbook=next((u for u in urls if u.startswith('https://assets.publishing.service.gov.uk/') and 'annex-a-' in u and u.endswith('.xlsx')),None)
    pdf=next((u for u in urls if u.startswith('https://assets.publishing.service.gov.uk/') and 'electricity-generation-costs-report-2025.pdf' in u),None)
    if not workbook or not pdf:raise ValueError('DESNZ source attachments changed; inspect the publication')
    costs=parse_costs(fetch.get(workbook,ttl_hours=720));fetch.get(pdf,ttl_hours=720)
    arup=fetch.get(ARUP_URL,ttl_hours=8760)
    if hashlib.sha256(arup).hexdigest()!=ARUP_SHA:raise ValueError('The manually checked Arup loss reference changed; review its values')
    curve=parse_curve(fetch.get(TURBINE_ROOT+'turbine_models/data/Offshore/IEA_Reference_15MW_240.csv',ttl_hours=720))
    spec=fetch.get(TURBINE_ROOT+'turbine_models/specs/Offshore/IEA_Reference_15MW_240.yaml',ttl_hours=720).decode()
    for k,v in {'rated_power':15000,'rotor_diameter':240,'hub_height':150,'cut_in_wind_speed':3,'cut_out_wind_speed':25}.items():
        m=re.search(r'^'+k+r':\s*([\d.]+)',spec,re.M)
        if not m or float(m[1])!=v:raise ValueError('IEA turbine specification changed: '+k)
    licence=fetch.get(TURBINE_ROOT+'LICENSE.txt',ttl_hours=720).decode()
    return {'source_url':COST_PAGE,'costs':costs,'curve':curve,'curve_type':'published_theoretical_reference','turbine':{'name':'IEA 15 MW / 240 m reference turbine','turbine_mw':15,'rotor_diameter_m':240,'hub_height_m':150,'cut_in_ms':3,'cut_out_ms':25},
        'loss_benchmarks':{'wake_loss':.08,'availability_loss':.041,'source_url':ARUP_URL,'pdf_page':53,'printed_page':48,'wake_sample_projects':5,'wake_range':[.06,.10],'availability_range':[.958,.960],'extraction':'Manually checked section 5.8.7 and 5.8.9; PDF checksum pinned.'},
        'license_text':licence,'files':{'DESNZ-Annex-A-2025.xlsx':workbook,'DESNZ-Generation-Costs-2025.pdf':pdf,'DESNZ-Arup-Offshore-Costs.pdf':ARUP_URL,'IEA-15MW-power-curve.csv':TURBINE_ROOT+'turbine_models/data/Offshore/IEA_Reference_15MW_240.csv','IEA-15MW-specification.yaml':TURBINE_ROOT+'turbine_models/specs/Offshore/IEA_Reference_15MW_240.yaml','Turbine-archive-LICENSE.txt':TURBINE_ROOT+'LICENSE.txt'},
        'limitations':['Generic fixed-bottom UK cost benchmark; not supplier quotes or a Hornsea project budget.','All source costs are real 2024 GBP. Costs from a different price year cannot be mixed without conversion.','Theoretical IEA reference curve is not a certified commercial turbine curve.','Arup wake/availability benchmarks are based on a small survey; they are not a layout wake or reliability model.','Electrical loss and curtailment assumptions are explicit modelling choices, not downloaded observations.']}

def curve_power(speed,curve):
    if speed<3 or speed>=25:return 0.0
    axis=[p['speed_ms'] for p in curve];j=bisect.bisect_right(axis,speed)
    if j==0:return curve[0]['power_mw']
    if j>=len(curve):return curve[-1]['power_mw']
    a,b=curve[j-1],curve[j]
    return a['power_mw']+(b['power_mw']-a['power_mw'])*(speed-a['speed_ms'])/(b['speed_ms']-a['speed_ms'])

def lcoe_components(capex,opex,variable,decommission,rate,life,net):
    if net<=0:raise ValueError('Positive net energy is required for LCOE')
    annuity=sum((1+rate)**-t for t in range(1,life+1));pv_energy=net*annuity
    components=[{'name':'Pre-development + construction','value':capex/pv_energy},
                {'name':'Fixed O&M + insurance + connection','value':opex*annuity/pv_energy},
                {'name':'Variable O&M','value':variable},
                {'name':'Terminal decommissioning','value':decommission/(1+rate)**life/pv_energy}]
    return sum(x['value'] for x in components),components

def regional_case(s,external):
    i=s['inputs'];cfg=i.get('regional_screening_case')
    if not cfg or not cfg.get('enabled') or i.get('wind_dataset_id'):return None
    if 'overview_inputs' not in external:return None
    entry=external['overview_inputs'];source=entry['data'];wind=external.get('era5_wind')
    if not wind:raise ValueError('Collect ERA5 wind before calculating regional overview estimates')
    for key in ['turbine_mw','rotor_diameter_m','hub_height_m']:
        if i[key]!=source['turbine'][key]:raise ValueError('The regional model requires the published IEA 15 MW, 240 m rotor, 150 m hub configuration; configure a matching curve for other turbines')
    cost=next((r for r in source['costs'] if r['commissioning_year']==i['design_year']),None)
    if not cost:raise ValueError('Choose a published DESNZ commissioning year: 2030, 2035, 2040, 2045 or 2050')
    h=wind['data']['heights'];rows=h['100']['rows'];low=h['10']['rows']
    if len(rows)<8760 or len(rows)!=len(low) or any(a['timestamp_utc']!=b['timestamp_utc'] for a,b in zip(rows,low)):raise ValueError('Regional estimates require at least one year of aligned 10 m/100 m hourly wind')
    mean10=sum(r['speed'] for r in low)/len(low);mean100=sum(r['speed'] for r in rows)/len(rows)
    if mean10<=0 or mean100<=0:raise ValueError('Non-positive mean wind prevents height extrapolation')
    alpha=math.log(mean100/mean10)/math.log(10)
    if not -.2<=alpha<=.6:raise ValueError('Derived shear exponent is outside the screening range; investigate the wind source')
    wake=i.get('wake_loss') if i.get('wake_loss') is not None else source['loss_benchmarks']['wake_loss']
    availability=i.get('availability_loss') if i.get('availability_loss') is not None else source['loss_benchmarks']['availability_loss']
    electrical=i.get('electrical_loss') if i.get('electrical_loss') is not None else cfg['electrical_loss']
    curtailment=i.get('curtailment_loss') if i.get('curtailment_loss') is not None else cfg['curtailment_loss']
    factors=[('wake_loss',wake),('electrical_loss',electrical),('availability_loss',availability),('curtailment_loss',curtailment)]
    n=round(i['capacity_mw']/15);hours=8784 if calendar.isleap(i['design_year']) else 8760
    hourly=[curve_power(r['speed']*(1.5**alpha),source['curve'])*n for r in rows]
    gross=sum(hourly)/len(rows)*hours;net=gross;losses=[]
    for name,fraction in factors:
        lost=net*fraction;net-=lost;losses.append({'name':name,'fraction':fraction,'mwh':lost})
    factor=math.prod(1-v for _,v in factors);annual=defaultdict(list);monthly=defaultdict(float)
    for r,power in zip(rows,hourly):annual[r['timestamp_utc'][:4]].append(power);monthly[int(r['timestamp_utc'][5:7])]+=power*factor/len(rows)*hours
    variants=[]
    for label,delta in [('Lower wind speed (-10%)',.9),('Central',1),('Higher wind speed (+10%)',1.1)]:
        estimate=sum(curve_power(r['speed']*(1.5**alpha)*delta,source['curve'])*n for r in rows)/len(rows)*hours*factor
        variants.append({'name':label,'net_aep_mwh':estimate})
    overrides=['capex_gbp_per_kw','opex_gbp_per_kw_year','decommission_gbp']
    if any(i.get(k) is not None for k in overrides) and i['price_year']!=2024:raise ValueError('Regional cost overrides must be real 2024 GBP to match DESNZ, or clear them')
    capex_kw=i.get('capex_gbp_per_kw') if i.get('capex_gbp_per_kw') is not None else cost['predevelopment_gbp_kw']+cost['construction_gbp_kw']
    opex_kw=i.get('opex_gbp_per_kw_year') if i.get('opex_gbp_per_kw_year') is not None else (cost['fixed_om_gbp_mw_year']+cost['insurance_gbp_mw_year']+cost['connection_gbp_mw_year'])/1000
    capex=capex_kw*i['capacity_mw']*1000;opex=opex_kw*i['capacity_mw']*1000
    decomm=i.get('decommission_gbp') if i.get('decommission_gbp') is not None else cost['decommission_gbp_mw']*i['capacity_mw']
    rate=i.get('discount_rate') if i.get('discount_rate') is not None else cost['discount_rate'];life=i['lifetime_years']
    lcoe,components=lcoe_components(capex,opex,cost['variable_om_gbp_mwh'],decomm,rate,life,net)
    assumptions=[{'name':'Wake loss','value':wake,'unit':'fraction','basis':'Scenario override' if i.get('wake_loss') is not None else 'Arup survey mean, PDF page 53 (printed 48); five projects'},
      {'name':'Availability loss','value':availability,'unit':'fraction','basis':'Scenario override' if i.get('availability_loss') is not None else '1 - Arup 95.9% energy availability, PDF page 53'},
      {'name':'Electrical loss','value':electrical,'unit':'fraction','basis':'Scenario override' if i.get('electrical_loss') is not None else 'Explicit modelling assumption'},
      {'name':'Curtailment loss','value':curtailment,'unit':'fraction','basis':'Scenario override' if i.get('curtailment_loss') is not None else 'Explicit modelling assumption; no site grid forecast'},
      {'name':'100 m to 150 m shear exponent','value':alpha,'unit':'dimensionless','basis':'ln(mean 100 m speed / mean 10 m speed) / ln(10); constant power-law extrapolation'},
      {'name':'CAPEX','value':capex_kw,'unit':'2024 GBP/kW','basis':'Scenario override' if i.get('capex_gbp_per_kw') is not None else f'DESNZ {cost["source_column"]}8 + {cost["source_column"]}20'},
      {'name':'Annual fixed expenditure','value':opex_kw,'unit':'2024 GBP/kW/year','basis':'Scenario override' if i.get('opex_gbp_per_kw_year') is not None else f'DESNZ ({cost["source_column"]}34 + {cost["source_column"]}36 + {cost["source_column"]}37) / 1000'},
      {'name':'Real discount rate','value':rate,'unit':'fraction','basis':'Scenario override' if i.get('discount_rate') is not None else f'DESNZ {cost["source_column"]}39'},
      {'name':'Lifetime','value':life,'unit':'years','basis':'Scenario planning assumption'},
      {'name':'Terminal decommissioning','value':decomm,'unit':'2024 GBP','basis':'Scenario override' if i.get('decommission_gbp') is not None else f'DESNZ {cost["source_column"]}43 × capacity MW'}]
    data={'estimate_type':'regional_reference_estimate','data_scope':'regional_model_only','reference_point':i.get('screening_point'),'turbine_name':source['turbine']['name'],'curve_type':source['curve_type'],'curve':source['curve'],
      'gross_aep_mwh':gross,'net_aep_mwh':net,'capacity_factor':net/(i['capacity_mw']*hours),'per_turbine_mwh':gross/n,'reporting_hours':hours,'sample_hours':len(rows),'wind_start':rows[0]['timestamp_utc'],'wind_end':rows[-1]['timestamp_utc'],'wind_dataset_id':wind['meta']['dataset_id'],'mean_100m_speed_ms':mean100,'mean_extrapolated_150m_speed_ms':mean100*1.5**alpha,'shear_exponent':alpha,
      'losses':losses,'annual_estimates':[{'year':year,'net_aep_mwh':sum(v)/len(v)*hours*factor,'sample_hours':len(v)} for year,v in sorted(annual.items())],
      'monthly_estimates':[{'month':m,'net_mwh':v} for m,v in sorted(monthly.items())],'energy_sensitivity':variants,'assumptions':assumptions,
      'lcoe_gbp_mwh':lcoe,'cost_components_lcoe':components,'capex_gbp':capex,'capex_gbp_per_kw':capex_kw,'annual_opex_gbp':opex,'opex_gbp_per_kw_year':opex_kw,'decommission_gbp':decomm,'discount_rate':rate,'lifetime_years':life,'price_year':2024,'currency':'GBP','benchmark':cost,
      'cost_sensitivity':[{'name':x['name'],'lcoe_gbp_mwh':lcoe_components(capex,opex,cost['variable_om_gbp_mwh'],decomm,rate,life,x['net_aep_mwh'])[0]} for x in variants],
      'regional_model_version':'1.0.0','source_files':[{'name':name,'url':f'/api/datasets/{entry["meta"]["dataset_id"]}/files/{name}'} for name in source.get('files',{})],
      'method':'Hourly linear interpolation of the published IEA reference curve at explicitly extrapolated 150 m wind; sample-mean annualization and multiplicative losses. LCOE discounts constant annual net energy and costs over the selected life; CAPEX at year 0 and terminal decommissioning. Not the DESNZ phased-construction LCOE model.'}
    gaps=source['limitations']+['Regional reference estimate only: no proposed AOI, feasible layout or site measurements are established.','Constant shear from two period-mean speeds is an extrapolation, not 150 m measurements; density and stability corrections are absent.','The ±10% wind sensitivity and historical weather-year spread are scenarios, not P50/P90 or confidence intervals.','LCOE excludes construction financing/phasing, tax, debt, degradation, seabed rent and site-specific cost premiums. Published DESNZ LCOE is shown separately for context.','No captured electricity price has been assumed; project NPV, IRR and payback remain unavailable.']
    return data,[entry['meta'],wind['meta']],gaps

def analyze_overview(cid,s,external):
    if cid not in CATEGORIES:return None
    return regional_case(s,external)
