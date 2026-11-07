import json,os,sqlite3,uuid
from contextlib import contextmanager
from pathlib import Path
from .catalog import ROOT,CATEGORIES
from .engine import now,digest,DEFAULT_INPUTS,VERSION
from .engineering import validate_inputs

DB=Path(os.environ.get('WIND_STUDIO_DB',ROOT/'data/studio.sqlite'))
@contextmanager
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DB,timeout=20);conn.row_factory=sqlite3.Row
    try:
        conn.execute('PRAGMA foreign_keys=ON');yield conn;conn.commit()
    finally:conn.close()
def init():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT NOT NULL,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS scenarios(id TEXT PRIMARY KEY,project_id TEXT NOT NULL REFERENCES projects(id),site_id TEXT NOT NULL,layout_id TEXT NOT NULL,revision INTEGER NOT NULL,parent_id TEXT,created TEXT NOT NULL,hash TEXT NOT NULL,payload TEXT NOT NULL,baseline INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS results(scenario_id TEXT NOT NULL REFERENCES scenarios(id),category_id TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(scenario_id,category_id));
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id TEXT,scenario_id TEXT,category_id TEXT,action TEXT NOT NULL,created TEXT NOT NULL,payload TEXT NOT NULL,previous_hash TEXT,event_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS datasets(id TEXT PRIMARY KEY,project_id TEXT NOT NULL,site_id TEXT NOT NULL,aoi_hash TEXT NOT NULL,created TEXT NOT NULL,meta TEXT NOT NULL,rows_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS external_datasets(id TEXT PRIMARY KEY,project_id TEXT NOT NULL,site_id TEXT NOT NULL,provider_id TEXT NOT NULL,scope_hash TEXT NOT NULL,created TEXT NOT NULL,meta TEXT NOT NULL,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS ingestion_jobs(id TEXT PRIMARY KEY,project_id TEXT NOT NULL,scenario_id TEXT NOT NULL,status TEXT NOT NULL,created TEXT NOT NULL,updated TEXT NOT NULL,payload TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS external_project_site ON external_datasets(project_id,site_id,created);
        CREATE UNIQUE INDEX IF NOT EXISTS scenario_project_revision ON scenarios(project_id,revision);
        ''')
def event(c,project_id,scenario_id,action,payload,category_id=None):
    # Take the write lock before reading the chain tip so concurrent writers cannot fork the hash chain.
    if not c.in_transaction:c.execute('BEGIN IMMEDIATE')
    prior=c.execute('SELECT event_hash FROM events ORDER BY id DESC LIMIT 1').fetchone();prev=prior[0] if prior else None;t=now()
    h=digest({'previous_hash':prev,'project_id':project_id,'scenario_id':scenario_id,'category_id':category_id,'action':action,'created':t,'payload':payload})
    c.execute('INSERT INTO events(project_id,scenario_id,category_id,action,created,payload,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)',(project_id,scenario_id,category_id,action,t,json.dumps(payload),prev,h))
def get_scenario(sid):
    with connect() as c:row=c.execute('SELECT payload,baseline FROM scenarios WHERE id=?',(sid,)).fetchone()
    if not row:raise KeyError('Scenario not found')
    s=json.loads(row['payload']);s['baseline']=bool(row['baseline']);return s
def as_float(v):
    if isinstance(v,int) and not isinstance(v,bool):return float(v)
    if isinstance(v,list):return [as_float(x) for x in v]
    if isinstance(v,dict):return {k:as_float(x) for k,x in v.items()}
    return v
def create_scenario(project_id,site_id,layout_id,inputs=None,parent_id=None,reason='Selected design alternative',trusted_data_refresh=False):
    parent=get_scenario(parent_id) if parent_id else None
    if parent and parent['project_id']!=project_id:raise ValueError('Parent scenario belongs to a different project')
    i={**DEFAULT_INPUTS,**(parent['inputs'] if parent else {}),**(inputs or {})}
    # A browser JSON round trip turns 54.0 into 54; numerically identical locations keep the parent's exact object and bindings.
    for key in ['aoi','screening_point']:
        if parent and digest(as_float(i.get(key)))==digest(as_float(parent['inputs'].get(key))):i[key]=parent['inputs'].get(key)
    location_changed=parent and (site_id!=parent['site_id'] or digest(i.get('aoi'))!=digest(parent['inputs'].get('aoi')) or digest(i.get('screening_point'))!=digest(parent['inputs'].get('screening_point')))
    if location_changed and not trusted_data_refresh:i['data_bindings']={}
    if parent and (site_id!=parent['site_id'] or digest(i.get('aoi'))!=digest(parent['inputs'].get('aoi'))):
        i['wind_dataset_id']=None
        if site_id!=parent['site_id']:
            i['aoi']=None;i['exclusions']=[];i['geometry_source']='';i['geometry_reviewed']=False;i['site_name']='';i['jurisdiction']=''
            i['screening_point']=None
        elif not trusted_data_refresh:i['screening_point']=None
    validate_inputs(i)
    sid=str(uuid.uuid4());t=now()
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')  # Serialise revision numbering with the insert that claims it.
        if not c.execute('SELECT id FROM projects WHERE id=?',(project_id,)).fetchone():raise KeyError('Project not found')
        rev=c.execute('SELECT COALESCE(MAX(revision),0)+1 FROM scenarios WHERE project_id=?',(project_id,)).fetchone()[0]
        s={'id':sid,'project_id':project_id,'site_id':site_id,'layout_id':layout_id,'revision':rev,'parent_id':parent_id,'created':t,'inputs':i,'hash':digest({'project_id':project_id,'site_id':site_id,'layout_id':layout_id,'inputs':i,'method_version':VERSION}),'baseline':False}
        c.execute('INSERT INTO scenarios(id,project_id,site_id,layout_id,revision,parent_id,created,hash,payload) VALUES(?,?,?,?,?,?,?,?,?)',(sid,project_id,site_id,layout_id,rev,parent_id,t,s['hash'],json.dumps(s)))
        changes={k:{'before':parent['inputs'].get(k) if parent else None,'after':v} for k,v in i.items() if not parent or parent['inputs'].get(k)!=v}
        event(c,project_id,sid,'scenario_created',{'reason':reason,'parent_id':parent_id,'before_hash':parent['hash'] if parent else None,'after_hash':s['hash'],'changes':changes,'invalidated_categories':[x['id'] for x in CATEGORIES] if parent else [],'invalidation_policy':'Conservative full-snapshot recomputation; raw reference files remain immutable.'})
    return s
def get_results(sid):
    with connect() as c:rows=c.execute('SELECT category_id,payload FROM results WHERE scenario_id=?',(sid,)).fetchall()
    return {r['category_id']:json.loads(r['payload']) for r in rows}
def context(s):
    ctx={'results':get_results(s['id'])}
    from .ingestion import attached_data
    ctx['external']=attached_data(s)
    if s['inputs'].get('wind_dataset_id'):
        with connect() as c:row=c.execute('SELECT * FROM datasets WHERE id=?',(s['inputs']['wind_dataset_id'],)).fetchone()
        if not row or row['project_id']!=s['project_id'] or row['site_id']!=s['site_id'] or row['aoi_hash']!=digest(s['inputs'].get('aoi')):raise ValueError('Wind dataset scope does not match this project, site and AOI')
        ctx.update(wind=json.loads(row['rows_json']),wind_meta=json.loads(row['meta']))
    return ctx
