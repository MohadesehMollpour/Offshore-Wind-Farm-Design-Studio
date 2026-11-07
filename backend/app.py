import csv,importlib.util,io,json,uuid
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request,BackgroundTasks
from fastapi.responses import FileResponse,Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field,ConfigDict
from .catalog import ROOT,CATEGORIES,BY_ID,load
from . import store
from .engine import now,digest
from .engineering import parse_wind
DATA_ROOT=ROOT/'data'

@asynccontextmanager
async def lifespan(app):
    store.init()
    from .ingestion import recover_interrupted_jobs
    recover_interrupted_jobs()
    yield
app=FastAPI(title='Offshore Wind Farm Design Studio',version='0.2.0',lifespan=lifespan)

@app.middleware('http')
async def local_only(request:Request,call_next):
    if request.headers.get('host','').split(':')[0] not in ['127.0.0.1','localhost','testserver']:
        return Response('Local use only',status_code=403)
    # Prevent cross-origin writes from unrelated pages to the local service.
    origin=request.headers.get('origin')
    if origin and origin not in ['http://127.0.0.1:8000','http://localhost:8000','http://127.0.0.1:5173','http://localhost:5173']:
        return Response('Origin is not allowed',status_code=403)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    return response

@app.exception_handler(ValueError)
async def value_error(request,exc):return Response(json.dumps({'detail':str(exc)}),status_code=422,media_type='application/json')
@app.exception_handler(KeyError)
async def key_error(request,exc):return Response(json.dumps({'detail':str(exc)}),status_code=404,media_type='application/json')

class StrictModel(BaseModel):model_config=ConfigDict(extra='forbid')
class ProjectInput(StrictModel):name:str=Field(min_length=1,max_length=150)
class ScenarioInput(StrictModel):
    site_id:str='SITE_01'
    layout_id:str='LAYOUT_01'
    inputs:dict=Field(default_factory=dict)
    parent_id:str|None=None
    reason:str=Field(default='Selected design alternative',max_length=1000)
class WindInput(StrictModel):
    csv_text:str=Field(max_length=15_000_000)
    source_name:str=Field(min_length=1,max_length=500)
    source_url:str=Field(default='',max_length=2000)
    license:str=Field(min_length=1,max_length=500)
    method:str=Field(min_length=1,max_length=1000)
    measurement_type:str=Field(pattern='^(observed|reanalysis|modelled|synthetic_demo_only)$')

def scenario(sid):return store.get_scenario(sid)
def run_category(s,cid,ctx=None):
    if cid not in BY_ID:raise KeyError('Unknown category')
    if ctx is None:ctx=store.context(s)
    path=ROOT/'categories'/cid/'src/controller.py'
    spec=importlib.util.spec_from_file_location('category_'+cid,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with store.connect() as c:store.event(c,s['project_id'],s['id'],'run_started',{'status':'running'},cid)
    try:r=module.run(s,ctx)
    except Exception as exc:
        with store.connect() as c:store.event(c,s['project_id'],s['id'],'run_failed',{'status':'failed','error':str(exc)},cid)
        raise
    # Writes are pinned to the requested immutable ID, so older requests cannot overwrite another revision.
    with store.connect() as c:
        c.execute('INSERT OR REPLACE INTO results VALUES(?,?,?)',(s['id'],cid,json.dumps(r)))
        store.event(c,s['project_id'],s['id'],'run_completed',{'run_id':r['run_id'],'status':r['status'],'scenario_hash':s['hash']},cid)
    out=DATA_ROOT/'processed'/s['project_id']/s['id'];out.mkdir(parents=True,exist_ok=True)
    (out/(cid+'.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
    ctx['results'][cid]=r
    return r

@app.get('/api/health')
def health():
    from .providers import PROVIDERS
    return {'status':'ok','version':'0.2.0','execution':'local_deterministic_with_public_data_adapters','configured_providers':len(PROVIDERS),'autonomous_llm_agents':0}
@app.get('/api/catalog')
def catalog():return {'categories':CATEGORIES,'agents':load('agents'),'sites':load('sites'),'layouts':load('layouts'),'assessment':load('assessment'),'work_packages':load('work_packages'),'sources':json.loads((ROOT/'sources/manifest.json').read_text()),'version':'0.2.0'}
@app.get('/api/projects')
def projects():
    with store.connect() as c:return [dict(r) for r in c.execute('SELECT * FROM projects ORDER BY created DESC')]
@app.post('/api/projects')
def create_project(body:ProjectInput):
    name=body.name.strip()
    if not name:raise ValueError('Project name cannot be blank')
    p={'id':str(uuid.uuid4()),'name':name,'created':now()}
    with store.connect() as c:
        c.execute('INSERT INTO projects VALUES(?,?,?)',tuple(p.values()));store.event(c,p['id'],None,'project_created',p)
    return p
@app.get('/api/projects/{pid}/scenarios')
def scenarios(pid:str):
    with store.connect() as c:rows=c.execute('SELECT payload,baseline FROM scenarios WHERE project_id=? ORDER BY revision DESC',(pid,)).fetchall()
    return [{**json.loads(r['payload']),'baseline':bool(r['baseline'])} for r in rows]
@app.post('/api/projects/{pid}/scenarios')
def create_scenario(pid:str,body:ScenarioInput):
    if body.site_id not in [x['id'] for x in load('sites')]+['CUSTOM']:raise ValueError('Unknown site preset')
    if body.layout_id not in [x['id'] for x in load('layouts')]:raise ValueError('Unknown layout strategy')
    return store.create_scenario(pid,**body.model_dump())
@app.get('/api/scenarios/{sid}')
def get_scenario(sid:str):return {'scenario':scenario(sid),'results':store.get_results(sid)}
@app.post('/api/scenarios/{sid}/baseline')
def baseline(sid:str):
    s=scenario(sid)
    with store.connect() as c:
        c.execute('UPDATE scenarios SET baseline=1 WHERE id=?',(sid,));store.event(c,s['project_id'],sid,'baseline_saved',{'hash':s['hash']})
    return {'baseline':True,'scenario_id':sid}
@app.post('/api/scenarios/{sid}/categories/{cid}/run')
def run(sid:str,cid:str):return run_category(scenario(sid),cid)
@app.post('/api/scenarios/{sid}/screen')
def screen(sid:str):
    s=scenario(sid)
    ctx=store.context(s)
    for cat in CATEGORIES:run_category(s,cat['id'],ctx)
    for cid in ['C67','C69','C70']:run_category(s,cid,ctx)
    return {'results':store.get_results(sid),'mode':'sequential_local_screening','status':'needs-review'}
@app.post('/api/scenarios/{sid}/wind')
def import_wind(sid:str,body:WindInput):
    s=scenario(sid)
    if not s['inputs'].get('aoi'):raise ValueError('Define an AOI first so the dataset can be explicitly scoped to its geometry')
    if body.source_url and not body.source_url.startswith(('https://','http://')):raise ValueError('Source URL must be HTTP(S)')
    rows=parse_wind(body.csv_text);data_id=str(uuid.uuid4());checksum=digest(body.csv_text)
    meta={'dataset_id':data_id,'source_name':body.source_name,'url':body.source_url,'license':body.license,'method':body.method,'measurement_type':body.measurement_type,'retrieved_at':now(),'sha256':checksum,'site_id':s['site_id'],'aoi_hash':digest(s['inputs']['aoi']),'start':rows[0]['timestamp_utc'],'end':rows[-1]['timestamp_utc'],'record_count':len(rows),'verification':'user_asserted_not_independently_verified'}
    raw=DATA_ROOT/'raw'/f'{data_id}.csv';raw.parent.mkdir(parents=True,exist_ok=True);raw.write_text(body.csv_text,encoding='utf-8');(raw.with_suffix('.json')).write_text(json.dumps(meta,indent=2),encoding='utf-8')
    with store.connect() as c:
        c.execute('INSERT INTO datasets VALUES(?,?,?,?,?,?,?)',(data_id,s['project_id'],s['site_id'],meta['aoi_hash'],now(),json.dumps(meta),json.dumps(rows)))
        store.event(c,s['project_id'],sid,'source_imported',meta)
    return store.create_scenario(s['project_id'],s['site_id'],s['layout_id'],{'wind_dataset_id':data_id},sid,'Imported new wind evidence')
@app.get('/api/projects/{pid}/history')
def history(pid:str):
    with store.connect() as c:rows=c.execute('SELECT * FROM events WHERE project_id=? ORDER BY id DESC LIMIT 300',(pid,)).fetchall()
    return [{**dict(r),'payload':json.loads(r['payload'])} for r in rows]
@app.get('/api/sources/{source_id}')
def source_file(source_id:str):
    manifest=json.loads((ROOT/'sources/manifest.json').read_text())
    item=next((s for s in manifest if s['id']==source_id),None)
    if not item:raise KeyError('Unknown source')
    if not (ROOT/item['relative_path']).is_file():raise HTTPException(404,'This course material is kept private and is not included in this checkout')
    return FileResponse(ROOT/item['relative_path'],filename=item['filename'])
@app.get('/api/scenarios/{sid}/export.json')
def export_json(sid:str):
    s=scenario(sid);payload={'scenario':s,'results':store.get_results(sid),'assessment':load('assessment'),'exported_at':now(),'status':'draft_not_approved'}
    return Response(json.dumps(payload,indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="scenario-{sid}.json"'})
@app.get('/api/scenarios/{sid}/categories/{cid}/export.csv')
def category_csv(sid:str,cid:str):
    scenario(sid);r=store.get_results(sid).get(cid)
    if not r:raise KeyError('Run this category before exporting')
    buf=io.StringIO();writer=csv.writer(buf);writer.writerow(['category_id','scenario_id','status','key','value_json'])
    for k,v in r['data'].items():writer.writerow([cid,sid,r['status'],k,json.dumps(v)])
    return Response(buf.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="{cid}-{sid}.csv"'})
@app.get('/api/scenarios/{sid}/report.md')
def report(sid:str):
    s=scenario(sid);results=store.get_results(sid);lines=['# Offshore wind proposal: working draft','','Status: DRAFT — evidence and human approvals incomplete.',f'Snapshot: {sid}; hash: {s["hash"]}',f'Site: {s["site_id"]}; layout: {s["layout_id"]}; revision: {s["revision"]}','','## Assessment requirements','Deadline: 17 December 2026, 14:00 Europe/London. Official rubric: 40/20/20/20.','']
    for topic in load('assessment')['topics']:
        lines.extend(['## '+topic['name'],''])
        for cid in topic['categories']:
            r=results.get(cid);lines.extend([f'### {cid}: {BY_ID[cid]["title"]}',r['interpretation'] if r else 'Not yet evaluated.',''])
            if r:
                lines.extend(['```json',json.dumps({'data':r['data'],'provenance':r['provenance'],'method_version':r['method_version'],'gaps':r['gaps']},indent=2),'```',''])
    lines+=['## Human contributions and AI disclosure',json.dumps(s['inputs'].get('contributions',[]),indent=2),'','## Assumptions',json.dumps(s['inputs'],indent=2),'','## Source hierarchy','Official brief and rubric govern the coursework. The 2023 Viking report is a historical example. The master prompt describes platform extensions. Imports are user-asserted unless independently verified.']
    return Response('\n'.join(lines),media_type='text/markdown',headers={'Content-Disposition':f'attachment; filename="proposal-draft-{sid}.md"'})

class CollectionInput(StrictModel):
    providers:list[str]=Field(default_factory=lambda:['tce_wind','repd','era5_wind','marine','bathymetry','neso_tec','nsta_fields','nsta_platforms','nsta_carbon','site_screening'],min_length=1,max_length=16)
    start_date:str=Field(default='2025-01-01',pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date:str=Field(default='2025-12-31',pattern=r'^\d{4}-\d{2}-\d{2}$')
    force:bool=False

class OverviewInput(StrictModel):
    start_date:str=Field(default='2021-01-01',pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date:str=Field(default='2025-12-31',pattern=r'^\d{4}-\d{2}-\d{2}$')
    electrical_loss:float=Field(default=.03,ge=0,le=.8)
    curtailment_loss:float=Field(default=.02,ge=0,le=.8)
    force:bool=False

class AccessEvaluationInput(StrictModel):
    preferences:dict

class WorkPackageInput(StrictModel):
    draft:dict

@app.post('/api/scenarios/{sid}/categories/{cid}/preview')
def work_package_preview(sid:str,cid:str,body:WorkPackageInput):
    from .work_packages import validate_work_inputs,DEFINITIONS
    from .engine import analyze
    if cid not in DEFINITIONS:raise ValueError('No editable work package is declared for this category')
    validate_work_inputs({cid:body.draft});s=scenario(sid);inputs={**s['inputs'],'category_inputs':{**s['inputs'].get('category_inputs',{}),cid:body.draft}}
    draft={**s,'inputs':inputs,'hash':digest({'base':s['hash'],'draft_inputs':inputs})};r=analyze(cid,draft,store.context(s))
    return {**r,'draft':True,'base_scenario_id':sid,'draft_input_hash':draft['hash']}

@app.get('/api/scenarios/{sid}/readiness')
def readiness(sid:str):
    s=scenario(sid);results=store.get_results(sid);items=[]
    for c in CATEGORIES:
        r=results.get(c['id']);d=(r or {}).get('data',{});wp=d.get('work_package');kind='not_evaluated' if not r else wp['kind'] if wp and wp['kind'] in ['risk_register','stakeholder_register'] else 'evidence_register' if wp and not wp['quantitative_ready'] else 'planning_calculation' if wp else 'source_screening' if d and any(p.get('provider_id') for p in r['provenance']) else 'calculation' if d else 'missing_inputs'
        items.append({'id':c['id'],'title':c['title'],'kind':kind,'status':r['status'] if r else 'not_run','evidence_maturity':r['evidence_maturity'] if r else 'unavailable','open_issues':len(r['gaps']) if r else None,'gaps':r['gaps'] if r else ['Evaluate this category for the selected design.'],'workspace_available':c['id'] in load('work_packages')})
    return {'scenario_id':sid,'scenario_hash':s['hash'],'items':items,'total':70,'evaluated':len(results),'decision_approved':False}

class FarmPreviewInput(StrictModel):
    wind_ms:float=Field(default=10,ge=0,le=60)
    wind_from_deg:float=Field(default=270,ge=0,le=360)
    hs_m:float=Field(default=1.5,ge=0,le=20)
    tp_s:float=Field(default=8,ge=1,le=30)
    wave_from_deg:float=Field(default=270,ge=0,le=360)
    ct:float=Field(default=.8,ge=0,le=.95)
    k:float=Field(default=.04,ge=.01,le=.2)

@app.post('/api/scenarios/{sid}/farm-preview')
def farm_preview(sid:str,body:FarmPreviewInput):
    from .farm_preview import preview
    s=scenario(sid)
    with store.connect() as c:rows=c.execute("SELECT category_id,payload FROM results WHERE scenario_id=? AND category_id IN ('C23','C08')",(sid,)).fetchall()
    return preview(s,{r['category_id']:json.loads(r['payload']) for r in rows},**body.model_dump())

@app.post('/api/scenarios/{sid}/accessibility/evaluate')
def access_evaluate(sid:str,body:AccessEvaluationInput):
    from .ingestion import attached_data
    from .accessibility import evaluate_access
    entries=attached_data(scenario(sid))
    if 'access_metocean' not in entries:raise ValueError('Collect historical accessibility metocean data first')
    return evaluate_access(entries['access_metocean']['data'],body.preferences)

@app.get('/api/scenarios/{sid}/accessibility/history.csv')
def access_history_csv(sid:str):
    from .ingestion import attached_data
    entry=attached_data(scenario(sid)).get('access_metocean')
    if not entry:raise ValueError('No accessibility history is attached to this snapshot')
    rows=entry['data']['rows'];buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return Response(buf.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="accessibility-hourly-{sid}.csv"'})

@app.post('/api/scenarios/{sid}/overview/prepare',status_code=202)
def prepare_overview(sid:str,body:OverviewInput,background_tasks:BackgroundTasks):
    from datetime import date,datetime,timezone,timedelta
    from .ingestion import new_job,execute_job
    s=scenario(sid);start=date.fromisoformat(body.start_date);end=date.fromisoformat(body.end_date)
    if start>end or not 364<=(end-start).days<=1826 or start<date(1940,1,1) or end>datetime.now(timezone.utc).date()-timedelta(days=7):raise ValueError('Overview wind requires 1–5 historical years since 1940, ending at least seven days ago')
    if any(s['inputs'][k]!=v for k,v in {'turbine_mw':15,'rotor_diameter_m':240,'hub_height_m':150}.items()):raise ValueError('Configure 15 MW, 240 m rotor and 150 m hub to use the published IEA reference case')
    case={'enabled':True,'electrical_loss':body.electrical_loss,'curtailment_loss':body.curtailment_loss}
    job=new_job(s,['era5_wind','overview_inputs'],body.start_date,body.end_date,body.force,overview_case=case)
    background_tasks.add_task(execute_job,job['id'])
    return job

@app.get('/api/datasets/{did}/files/{filename}')
def source_file(did:str,filename:str):
    import hashlib
    from .ingestion import get_dataset
    ds=get_dataset(did);url=ds['data'].get('files',{}).get(filename)
    if not url:raise HTTPException(404,'Source file not present in this dataset')
    asset=next((a for a in ds['meta']['raw_assets'] if a['url']==url),None)
    if not asset:raise HTTPException(404,'Preserved source response not found')
    path=(DATA_ROOT/asset['path']).resolve()
    if not path.is_relative_to(DATA_ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=asset['sha256']:raise ValueError('Source file integrity check failed')
    return FileResponse(path,filename=filename,media_type=asset.get('content_type') or 'application/octet-stream')

@app.get('/api/providers')
def providers():
    from .providers import PROVIDERS
    return [{'id':pid,**cfg,'authentication':'none','access_mode':'read_only_public_api'} for pid,cfg in PROVIDERS.items()]

@app.get('/api/references/lattice-supply')
def lattice_supply_reference():
    from .supply_reference import load_supply_reference
    return load_supply_reference()

@app.get('/api/references/lattice-supply/original')
def lattice_supply_original():
    from .supply_reference import original_supply_reference
    return FileResponse(original_supply_reference(), filename='Lattice_Offshore_Wind.original.html', media_type='application/octet-stream')

@app.get('/api/references/lattice-supply/data.json')
def lattice_supply_data():
    from .supply_reference import supply_reference_bytes
    return Response(supply_reference_bytes(),media_type='application/json',headers={'Content-Disposition':'attachment; filename="C54-lattice-directory-reference.json"'})

@app.get('/api/references/hornsea-farms')
def hornsea_reference():
    from .references import load_hornsea_reference
    result=load_hornsea_reference()
    if not result:raise HTTPException(404,'Hornsea reference has not been imported')
    return result

@app.get('/api/references/hornsea-farms/original')
def hornsea_original():
    from .references import original_reference
    return FileResponse(original_reference(),filename='Wind_Farms_Around_Hornsea.original.html',media_type='application/octet-stream')

@app.post('/api/scenarios/{sid}/refresh-evidence')
def refresh_bound_evidence(sid:str):
    from .providers import PROVIDERS
    s=scenario(sid)
    categories=sorted({cid for pid in s['inputs'].get('data_bindings',{}) for cid in PROVIDERS[pid]['categories']}|{'C67','C69'})
    ctx=store.context(s)
    for cid in categories:run_category(s,cid,ctx)
    return {'scenario_id':sid,'results':store.get_results(sid),'categories':categories}

@app.post('/api/scenarios/{sid}/collect',status_code=202)
def collect_data(sid:str,body:CollectionInput,background_tasks:BackgroundTasks):
    from datetime import date,datetime,timezone,timedelta
    from .ingestion import new_job,execute_job
    start=date.fromisoformat(body.start_date);end=date.fromisoformat(body.end_date)
    if start>end or (end-start).days>1826 or start<date(1940,1,1) or end>datetime.now(timezone.utc).date()-timedelta(days=7):raise ValueError('Historical wind period must span 1–5 years and end at least seven days ago')
    job=new_job(scenario(sid),body.providers,body.start_date,body.end_date,body.force)
    background_tasks.add_task(execute_job,job['id'])
    return job

@app.get('/api/data-jobs/{jid}')
def get_data_job(jid:str):
    from .ingestion import get_job
    return get_job(jid)

@app.get('/api/projects/{pid}/data-jobs')
def recent_data_jobs(pid:str):
    with store.connect() as c:rows=c.execute('SELECT payload FROM ingestion_jobs WHERE project_id=? ORDER BY created DESC LIMIT 20',(pid,)).fetchall()
    return [json.loads(r['payload']) for r in rows]

@app.get('/api/projects/{pid}/datasets')
def datasets(pid:str,site_id:str|None=None):
    from .ingestion import list_datasets,dataset_status
    return [{**meta,'availability':dataset_status(meta)} for meta in list_datasets(pid,site_id)]

@app.get('/api/scenarios/{sid}/datasets')
def bound_datasets(sid:str):
    from .ingestion import attached_data,dataset_status
    return [{**entry['meta'],'availability':dataset_status(entry['meta'])} for entry in attached_data(scenario(sid)).values()]

@app.get('/api/datasets/{did}')
def dataset(did:str):
    from .ingestion import get_dataset
    return get_dataset(did)

@app.get('/api/datasets/{did}/environment-relief/{asset}')
def environment_relief(did:str,asset:str):
    from .ingestion import get_dataset
    from .environment import relief_status,relief_directory
    if asset not in ['terrain-relief.png','terrain-relief-preview.png','terrain-relief.metadata.json']:raise HTTPException(404,'Unknown relief asset')
    dataset=get_dataset(did)
    if dataset['provider_id']!='environment_screening':raise HTTPException(404,'Dataset has no environmental relief')
    if not relief_status(dataset['data']).get('available'):raise HTTPException(404,'Rayshader product is not generated for this terrain')
    return FileResponse(relief_directory(dataset['data'])/asset,media_type='image/png' if asset.endswith('.png') else 'application/json')

@app.get('/api/datasets/{did}/download.json')
def download_dataset(did:str):
    from .ingestion import get_dataset
    return Response(json.dumps(get_dataset(did),indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="source-{did}.json"'})

dist=ROOT/'dashboard/dist'
# Root files copied from dashboard/public by the Vite build. Exact allowlist with fixed media types; registered before the SPA catch-all so these names never fall through to index.html.
ROOT_FILES={'robots.txt':'text/plain; charset=utf-8','favicon.svg':'image/svg+xml','site.webmanifest':'application/manifest+json'}
def root_file_route(name:str):
    def root_file():
        path=dist/name
        if not path.is_file():raise HTTPException(404,'Root file is not built')
        return FileResponse(path,media_type=ROOT_FILES[name])
    return root_file
for _root_name in ROOT_FILES:app.get('/'+_root_name,include_in_schema=False)(root_file_route(_root_name))
if dist.exists():
    app.mount('/assets',StaticFiles(directory=dist/'assets'),name='assets')
    @app.get('/{path:path}')
    def frontend(path:str):
        if path.startswith('api/'):raise HTTPException(404,'Unknown API route')
        return FileResponse(dist/'index.html')
