"""Persistent source acquisition jobs and scope-checked immutable datasets."""
from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .catalog import ROOT
from .engine import digest, now
from .engineering import geometry
from .providers import Fetcher, PROVIDERS, ProviderError, collect, reference_from_wind
from . import store

DATA_ROOT=ROOT/'data'
_job_lock=threading.Lock()

def scope(s,provider_id,point=None):
    return digest({'project_id':s['project_id'],'site_id':s['site_id'],'aoi_hash':digest(s['inputs'].get('aoi')),'point':{'lat':point['lat'],'lon':point['lon']} if point and PROVIDERS[provider_id]['point_required'] else None})

def save_dataset(s,pid,data,fetch,point):
    did=str(uuid.uuid4());cfg=PROVIDERS[pid];t=now()
    meta={'dataset_id':did,'provider_id':pid,'source_name':cfg['name'],'url':data.get('source_url') or cfg['docs'],'docs_url':cfg['docs'],'license':cfg['license'],'license_text':data.get('license_text'),'attribution':data.get('attribution') or cfg['attribution'],'measurement_type':cfg['kind'],'method':'Provider adapter v0.2.0; validated read-only public API response','retrieved_at':max((a['retrieved_at'] for a in fetch.assets),default=t),'checked_at':t,'publisher_modified':data.get('publisher_modified'),'point':point if cfg['point_required'] else None,'spatial_scope':'regional_reference_only' if not s['inputs'].get('aoi') else 'aoi_screening_only','site_id':s['site_id'],'aoi_hash':digest(s['inputs'].get('aoi')),'scope_hash':scope(s,pid,point),'sha256':digest(data),'raw_assets':fetch.assets,'cached_requests':fetch.cache_hits,'warnings':fetch.warnings,'stale':bool(fetch.warnings),'limitations':data.get('limitations',[]),'refresh_hours':cfg['refresh_hours'],'verification':'retrieved_from_configured_publisher_api_not_independently_field_verified'}
    with store.connect() as c:
        c.execute('INSERT INTO external_datasets VALUES(?,?,?,?,?,?,?,?)',(did,s['project_id'],s['site_id'],pid,meta['scope_hash'],t,json.dumps(meta),json.dumps(data)))
        store.event(c,s['project_id'],s['id'],'provider_dataset_retrieved',{'dataset_id':did,'provider_id':pid,'sha256':meta['sha256'],'raw_checksums':[a['sha256'] for a in fetch.assets],'stale':meta['stale']})
    path=DATA_ROOT/'external'/did;path.mkdir(parents=True,exist_ok=True)
    (path/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');(path/'data.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    return did,meta

def get_dataset(did):
    with store.connect() as c:row=c.execute('SELECT * FROM external_datasets WHERE id=?',(did,)).fetchone()
    if not row:raise KeyError('External dataset not found')
    return {'meta':json.loads(row['meta']),'data':json.loads(row['payload']),'project_id':row['project_id'],'site_id':row['site_id'],'provider_id':row['provider_id']}

def attached_data(s):
    result={};point=s['inputs'].get('screening_point')
    for pid,did in s['inputs'].get('data_bindings',{}).items():
        if pid not in PROVIDERS:raise ProviderError('Unknown bound data provider')
        dataset=get_dataset(did);meta=dataset['meta']
        if dataset['provider_id']!=pid or dataset['project_id']!=s['project_id'] or dataset['site_id']!=s['site_id'] or meta['scope_hash']!=scope(s,pid,point):raise ProviderError('External dataset scope does not match the current provider, project, site, AOI and reference point')
        result[pid]=dataset
    return result

def list_datasets(project_id,site_id=None):
    with store.connect() as c:
        if site_id:rows=c.execute('SELECT meta FROM external_datasets WHERE project_id=? AND site_id=? ORDER BY created DESC LIMIT 100',(project_id,site_id)).fetchall()
        else:rows=c.execute('SELECT meta FROM external_datasets WHERE project_id=? ORDER BY created DESC LIMIT 100',(project_id,)).fetchall()
    return [json.loads(r['meta']) for r in rows]

def get_job(jid):
    with store.connect() as c:r=c.execute('SELECT payload FROM ingestion_jobs WHERE id=?',(jid,)).fetchone()
    if not r:raise KeyError('Data collection job not found')
    return json.loads(r['payload'])
def update_job(job):
    job['updated']=now()
    with store.connect() as c:c.execute('UPDATE ingestion_jobs SET status=?,updated=?,payload=? WHERE id=?',(job['status'],job['updated'],json.dumps(job),job['id']))

def new_job(s,providers,start,end,force=False,overview_case=None):
    if not providers:raise ProviderError('Choose at least one provider')
    if any(p not in PROVIDERS for p in providers):raise ProviderError('Unknown provider')
    # Automatic Hornsea reference is sourced from the wind-agreement dataset.
    providers=list(dict.fromkeys(providers))
    if not s['inputs'].get('aoi') and not s['inputs'].get('screening_point') and any(PROVIDERS[p]['point_required'] for p in providers):
        if s['site_id']!='SITE_01':raise ProviderError('Provide a reference point or AOI for this region; only Hornsea reference discovery is configured')
        if 'tce_wind' not in providers:providers.insert(0,'tce_wind')
    if 'tce_wind' in providers:providers=['tce_wind']+[p for p in providers if p!='tce_wind']
    t=now();job={'id':str(uuid.uuid4()),'project_id':s['project_id'],'scenario_id':s['id'],'status':'queued','created':t,'updated':t,'providers':providers,'start_date':start,'end_date':end,'force':force,'progress':0,'total':len(providers),'steps':[],'result_scenario_id':None}
    if overview_case is not None:
        from .engineering import validate_inputs
        validate_inputs({'regional_screening_case':overview_case})
        if not overview_case['enabled'] or 'overview_inputs' not in providers or 'era5_wind' not in providers:raise ValueError('Overview preparation requires explicit activation plus wind and reference-input providers')
        job['overview_case']=overview_case
    with _job_lock:
        with store.connect() as c:
            if c.execute("SELECT id FROM ingestion_jobs WHERE project_id=? AND status IN ('queued','running')",(s['project_id'],)).fetchone():raise ProviderError('A collection is already running for this project; inspect that job before refreshing')
            c.execute('INSERT INTO ingestion_jobs VALUES(?,?,?,?,?,?,?)',(job['id'],s['project_id'],s['id'],'queued',t,t,json.dumps(job)))
            store.event(c,s['project_id'],s['id'],'data_collection_queued',{'job_id':job['id'],'providers':providers})
    return job

def execute_job(jid):
    job=get_job(jid);s=store.get_scenario(job['scenario_id']);job['status']='running';update_job(job)
    bindings={**s['inputs'].get('data_bindings',{})};point=s['inputs'].get('screening_point');new_count=0
    if s['inputs'].get('aoi'):
        polygon,*_=geometry(s['inputs']['aoi']);p=polygon.representative_point()
        point={'lat':p.y,'lon':p.x,'label':'User AOI interior screening reference','method':'Interior representative point of the user-supplied AOI','scope':'aoi_screening_only','is_proposed_site':True}
    try:
        for pid in job['providers']:
            step={'provider_id':pid,'status':'running','started':now()};job['steps'].append(step);update_job(job)
            fetch=Fetcher(DATA_ROOT,force=job['force'])
            try:
                data=collect(pid,fetch,point,job['start_date'],job['end_date'])
                if pid=='environment_screening':
                    from .environment import build_relief
                    try:build_relief(data)
                    except Exception as render_error:
                        # Derivative rendering does not determine scientific source validity/staleness.
                        from .environment import relief_directory
                        directory=relief_directory(data);directory.mkdir(parents=True,exist_ok=True)
                        (directory/'render-error.json').write_text(json.dumps({'error':str(render_error)[:1000]}),encoding='utf-8')
                did,meta=save_dataset(s,pid,data,fetch,point);bindings[pid]=did;new_count+=1
                if pid=='tce_wind' and point is None:point=reference_from_wind(data,did)
                step.update(status='stale' if meta['stale'] else 'succeeded',dataset_id=did,records=data.get('sample_hours',data.get('record_count',data.get('feature_count',1))),warnings=meta['warnings'])
            except Exception as exc:
                step.update(status='failed',error=str(exc)[:1000])
                # Preserve a valid prior dataset explicitly as stale after a schema/provider failure.
                prior_id=bindings.get(pid)
                if prior_id:
                    prior=get_dataset(prior_id)
                    if prior['meta']['scope_hash']==scope(s,pid,point):
                        fetch.assets=prior['meta']['raw_assets'];fetch.warnings=['STALE: latest provider refresh failed: '+str(exc)[:500]]
                        stale_id,_=save_dataset(s,pid,prior['data'],fetch,point);bindings[pid]=stale_id;new_count+=1;step['stale_dataset_id']=stale_id
                with store.connect() as c:store.event(c,s['project_id'],s['id'],'provider_refresh_failed',{'provider_id':pid,'error':str(exc)[:1000],'job_id':jid})
            finally:fetch.close()
            step['finished']=now();job['progress']+=1;update_job(job)
        if new_count:
            inputs={'screening_point':point,'data_bindings':bindings}
            if job.get('overview_case') and 'overview_inputs' in bindings and 'era5_wind' in bindings:
                inputs['regional_screening_case']=job['overview_case']
            result=store.create_scenario(s['project_id'],s['site_id'],s['layout_id'],inputs,s['id'],'Attached public API data collection '+jid,trusted_data_refresh=True)
            job['result_scenario_id']=result['id']
            job['phase']='analyzing';update_job(job)
            from .app import run_category
            categories=sorted({cat for pid in bindings for cat in PROVIDERS[pid]['categories']}|{'C67','C69'})
            job['analysis_errors']=[]
            ctx=store.context(result)
            for cid in categories:
                try:run_category(result,cid,ctx)
                except Exception as exc:job['analysis_errors'].append({'category':cid,'error':str(exc)[:500]})
            job['analyzed_categories']=categories
        job['status']='completed' if all(x['status']=='succeeded' for x in job['steps']) else 'partial' if new_count else 'failed'
        if job.get('analysis_errors'):job['status']='partial'
        job['phase']='finished'
    except Exception as exc:job['status']='failed';job['error']=str(exc)[:1000]
    update_job(job)
    with store.connect() as c:store.event(c,s['project_id'],s['id'],'data_collection_finished',{'job_id':jid,'status':job['status'],'result_scenario_id':job['result_scenario_id']})

def recover_interrupted_jobs():
    with store.connect() as c:rows=c.execute("SELECT payload FROM ingestion_jobs WHERE status IN ('queued','running')").fetchall()
    for row in rows:
        job=json.loads(row['payload']);job['status']='failed';job['error']='Collection interrupted by application restart. Preserved datasets remain available; refresh to retry.';update_job(job)

def dataset_status(meta):
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(meta['checked_at'])).total_seconds()/3600
    return 'stale' if meta.get('stale') or age>meta['refresh_hours'] else 'available'
