"""Run a persisted public-data collection without a web server."""
import argparse,json
from backend import store
from backend.ingestion import new_job,execute_job,get_job
from backend.providers import PROVIDERS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--scenario-id',required=True);parser.add_argument('--start-date',default='2025-01-01');parser.add_argument('--end-date',default='2025-12-31');parser.add_argument('--force',action='store_true');parser.add_argument('--prepare-overview',action='store_true');parser.add_argument('--providers',nargs='+',choices=list(PROVIDERS),default=list(PROVIDERS));args=parser.parse_args()
    from backend.overview_data import CASE_DEFAULTS
    store.init();s=store.get_scenario(args.scenario_id);job=new_job(s,args.providers,args.start_date,args.end_date,args.force,overview_case=CASE_DEFAULTS.copy() if args.prepare_overview else None)
    print('Collection job:',job['id'],flush=True)
    print('Read-only providers:',', '.join(job['providers']),flush=True)
    execute_job(job['id']);result=get_job(job['id']);print(json.dumps(result,indent=2),flush=True)
    if result['status']=='failed':raise SystemExit(1)

if __name__=='__main__':main()
