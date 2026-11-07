"""Regression tests for the 2 November 2026 senior-engineer review findings H1 and M1-M5."""
import json,shutil,threading
import pytest
from fastapi.testclient import TestClient
from backend import store,supply_reference
from backend.app import app
from backend.engine import digest
from backend.work_packages import defaults
from tests.test_engineering import AOI,wind_csv

FINANCE={'aoi':AOI,'capacity_mw':150,'wake_loss':.05,'electrical_loss':.03,'availability_loss':.04,'curtailment_loss':.02,'uncertainty_fraction':.1,'capex_gbp_per_kw':2500,'opex_gbp_per_kw_year':70,'decommission_gbp':1e7,'discount_rate':.06,'power_price_gbp_mwh':80}

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB',tmp_path/'test.sqlite')
    import backend.app as module
    monkeypatch.setattr(module,'DATA_ROOT',tmp_path/'data')
    with TestClient(app) as c:yield c
@pytest.fixture
def bare_store(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB',tmp_path/'concurrency.sqlite');store.init()
    with store.connect() as c:c.execute("INSERT INTO projects VALUES('p1','Concurrency test','2026-01-01T00:00:00+00:00')")
def create(client):
    p=client.post('/api/projects',json={'name':'Review regressions'}).json()
    return p,client.post(f'/api/projects/{p["id"]}/scenarios',json={}).json()
def with_wind(client,p,s,height=150):
    s=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'inputs':FINANCE}).json()
    r=client.post(f'/api/scenarios/{s["id"]}/wind',json={'csv_text':wind_csv(height=height),'source_name':'Synthetic regression fixture','license':'Test only','method':'Constant hourly fixture','measurement_type':'synthetic_demo_only'})
    assert r.status_code==200,r.text
    return r.json()
def concurrently(target,n=12,rounds=3):
    errors=[]
    for r in range(rounds):
        barrier=threading.Barrier(n)
        def run(k):
            try:barrier.wait();target(r*n+k)
            except Exception as e:errors.append(repr(e))
        threads=[threading.Thread(target=run,args=(k,)) for k in range(n)];[t.start() for t in threads];[t.join() for t in threads]
    return errors

# H1: revision numbers and the event hash chain must stay sequential under concurrent writers.
def test_concurrent_scenario_creation_gets_unique_sequential_revisions(bare_store):
    errors=concurrently(lambda k:store.create_scenario('p1','SITE_01','LAYOUT_01',{},None,'concurrency test'))
    with store.connect() as c:revisions=sorted(r[0] for r in c.execute('SELECT revision FROM scenarios'))
    assert errors==[] and revisions==list(range(1,37))
def test_concurrent_events_form_one_linear_hash_chain(bare_store):
    def write(k):
        with store.connect() as c:store.event(c,'p1',None,'concurrency_test',{'k':k})
    errors=concurrently(write)
    with store.connect() as c:rows=c.execute('SELECT previous_hash,event_hash FROM events ORDER BY id').fetchall()
    assert errors==[] and len(rows)==36 and rows[0][0] is None
    assert all(b[0]==a[1] for a,b in zip(rows,rows[1:]))
def test_duplicate_revision_number_is_rejected_by_schema(bare_store):
    s=store.create_scenario('p1','SITE_01','LAYOUT_01',{},None,'first')
    with pytest.raises(Exception,match='UNIQUE'):
        with store.connect() as c:c.execute('INSERT INTO scenarios(id,project_id,site_id,layout_id,revision,parent_id,created,hash,payload) VALUES(?,?,?,?,?,?,?,?,?)',('duplicate','p1','SITE_01','LAYOUT_01',s['revision'],None,s['created'],s['hash'],'{}'))

# M1: a cleared required design field must be rejected, not saved as a broken revision.
@pytest.mark.parametrize('field',['capacity_mw','turbine_mw','rotor_diameter_m','hub_height_m','lifetime_years','price_year'])
def test_required_design_inputs_cannot_be_saved_blank(client,field):
    p,s=create(client)
    r=client.post(f'/api/projects/{p["id"]}/scenarios',json={'site_id':s['site_id'],'layout_id':s['layout_id'],'parent_id':s['id'],'inputs':{field:None}})
    assert r.status_code==422 and field in r.json()['detail']
    assert len(client.get(f'/api/projects/{p["id"]}/scenarios').json())==1
def test_optional_financial_inputs_can_still_be_blank(client):
    p,s=create(client)
    r=client.post(f'/api/projects/{p["id"]}/scenarios',json={'site_id':s['site_id'],'layout_id':s['layout_id'],'parent_id':s['id'],'inputs':{'wake_loss':None,'power_price_gbp_mwh':None}})
    assert r.status_code==200,r.text

# M2: later labelling rules must never upgrade results that rest on synthetic demo wind.
def test_synthetic_wind_label_is_not_upgraded_by_later_rules(client):
    p,s=create(client);s=with_wind(client,p,s)
    for cid in ['C10','C12','C27','C60','C61']:
        r=client.post(f'/api/scenarios/{s["id"]}/categories/{cid}/run',json={}).json()
        assert r['evidence_maturity']=='synthetic_demo_only',(cid,r['evidence_maturity'])

# M3: a browser JSON round trip (54.0 -> 54) must not look like a moved AOI and drop the evidence bindings.
def as_browser_json(v):
    if isinstance(v,float) and v.is_integer():return int(v)
    if isinstance(v,list):return [as_browser_json(x) for x in v]
    if isinstance(v,dict):return {k:as_browser_json(x) for k,x in v.items()}
    return v
def test_browser_number_round_trip_keeps_location_bindings(client):
    p,s=create(client);s=with_wind(client,p,s);assert s['inputs']['wind_dataset_id']
    edited={**as_browser_json(s['inputs']),'discount_rate':.07}
    child=client.post(f'/api/projects/{p["id"]}/scenarios',json={'site_id':s['site_id'],'layout_id':s['layout_id'],'parent_id':s['id'],'inputs':edited}).json()
    assert child['inputs']['wind_dataset_id']==s['inputs']['wind_dataset_id']
    assert digest(child['inputs']['aoi'])==digest(s['inputs']['aoi'])
    r=client.post(f'/api/scenarios/{child["id"]}/categories/C10/run',json={})
    assert r.status_code==200 and r.json()['data'],r.text
def test_really_moved_aoi_still_drops_wind_binding(client):
    p,s=create(client);s=with_wind(client,p,s)
    moved={'type':'Polygon','coordinates':[[[1.0,54.0],[1.6,54.0],[1.6,54.3],[1.0,54.3],[1.0,54.0]]]}
    child=client.post(f'/api/projects/{p["id"]}/scenarios',json={'site_id':s['site_id'],'layout_id':s['layout_id'],'parent_id':s['id'],'inputs':{'aoi':moved}}).json()
    assert child['inputs']['wind_dataset_id'] is None

# M4: a C54 reference file changed while the server runs must be re-verified, not served from a stale cache.
def test_changed_supply_reference_is_rejected_without_restart(client,tmp_path,monkeypatch):
    copy_dir=tmp_path/'lattice_supply';shutil.copytree(supply_reference.REFERENCE_DIR,copy_dir)
    monkeypatch.setattr(supply_reference,'REFERENCE_DIR',copy_dir)
    assert client.get('/api/references/lattice-supply/data.json').status_code==200
    path=copy_dir/'reference.json';record=json.loads(path.read_text(encoding='utf-8'))
    record['data']['kg']['meta']['dataNotes']=['Changed after the server started']
    path.write_text(json.dumps(record),encoding='utf-8')
    assert client.get('/api/references/lattice-supply/data.json').status_code==422
    assert client.get('/api/references/lattice-supply').status_code==422

# M5: an ordinary energy/layout gap must keep the editable C61 workspace and report the gap.
def test_c61_energy_gap_keeps_editable_workspace(client):
    p,s=create(client);s=with_wind(client,p,s,height=100)
    r=client.post(f'/api/scenarios/{s["id"]}/categories/C61/run',json={}).json()
    assert r['data'].get('work_package') and any('hub height' in g for g in r['gaps'])
    preview=client.post(f'/api/scenarios/{s["id"]}/categories/C61/preview',json={'draft':defaults('C61')}).json()
    assert 'work_package' in preview['data']
