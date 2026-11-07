"""Summarize an existing collection without making provider requests."""
import argparse,json
from pathlib import Path
from backend import store
from backend.providers import PROVIDERS
from backend.ingestion import attached_data

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--scenario-id',required=True);parser.add_argument('--output',default='reports/data_collection.md');args=parser.parse_args()
    s=store.get_scenario(args.scenario_id);sources=attached_data(s);point=s['inputs'].get('screening_point');results=store.get_results(s['id'])
    lines=['# Hornsea public-data collection','','Collection scope: Hornsea / East Yorkshire regional screening. No proposed AOI has been selected.',f'Scenario revision: {s["revision"]}; ID: {s["id"]}; hash: {s["hash"]}.','',f'Reference: {point["label"]}, {point["lat"]:.7f}° N, {point["lon"]:.7f}° E.',f'Method: {point["method"]}. Feature OBJECTID {point.get("source_feature_id","user AOI")}.',"This is an existing-project reference, not a proposed development area or evidence of vacant seabed.",'','| Source | Retrieved data | Dataset ID |','|---|---|---|']
    for pid,source in sources.items():
        d=source['data'];m=source['meta'];count=d.get('feature_count',d.get('record_count',d.get('sample_hours',1)))
        desc=f'{count:,} published features/records'
        if pid=='era5_wind':desc=f'{d["sample_hours"]:,} hourly records at each of 10 m and 100 m, {d["start_date"]} to {d["end_date"]}'
        elif pid=='marine':desc=f'{d["record_count"]:,} hourly forecast records; {d["missing_count"]} missing'
        elif pid=='bathymetry':desc='One numeric DTM raster-cell sample and preserved WMS capabilities'
        lines.append(f'| [{PROVIDERS[pid]["name"]}]({m["url"]}) | {desc} | {m["dataset_id"]} |')
    w=sources.get('era5_wind',{}).get('data',{});depth=sources.get('bathymetry',{}).get('data',{})
    lines+=['','## Screening observations','']
    if w:
        for height,entry in w['heights'].items():lines.append(f'- Mean ERA5 wind at {height} m: {entry["summary"]["mean_speed_ms"]:.3f} m/s for the retrieved period.')
        lines.append(f'- Provider grid point: {w["grid_point"]["lat"]}° N, {w["grid_point"]["lon"]}° E. This differs from a proposed site or a sensor location.')
    if depth:lines.append(f'- EMODnet reference-cell water-depth magnitude: {depth["water_depth_m"]:.2f} m below the product datum. One cell does not establish a surveyed seabed profile.')
    lines+=['','## Interpretation limits','','These data are regional screening inputs. The 10 m and 100 m winds are reanalysis; the current 150 m turbine hub has not been measured or extrapolated. No automatic site-specific AEP or bankable P90 is produced. Marine values are short-horizon forecasts. Register/lease statuses are retained by source and vintage. TEC cumulative stages are not summed into available headroom. NSTA carbon licences do not establish storage capacity or project rights.','',f'Prepared category views: {", ".join(sorted(results))}.','Source attribution and exact raw-response SHA-256 lineage are available through Data sources & APIs and the preserved metadata files.','', '## Use in the application','','Start the local app with `D:\\Wind_Farm_Design\\Start-Studio.ps1`, open Data sources & APIs, and select the collected revision. C07/C08 show wind, C13 waves, C16 bathymetry, C37 wind agreements/REPD, C34/C35 register context, and C39/C41/C44 NSTA records. Select providers and Collect selected sources to refresh. Fresh caches are reused unless bypassed.','','## Provenance records','']
    for pid,source in sources.items():
        m=source['meta'];lines+=[f'### {m["source_name"]}',f'- Retrieved: {m["retrieved_at"]}; checked: {m["checked_at"]}.',f'- Publisher modified: {m.get("publisher_modified") or "See original publication / source metadata"}.',f'- Licence: {m["license"]}.',f'- Attribution: {m["attribution"]}',f'- Validated payload SHA-256: `{m["sha256"]}`.',f'- Raw response count: {len(m["raw_assets"])}; cached requests: {m["cached_requests"]}.','']
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'revision':s['revision'],'scenario_id':s['id'],'providers':len(sources),'output':str(out),'categories':len(results)}))

if __name__=='__main__':main()
