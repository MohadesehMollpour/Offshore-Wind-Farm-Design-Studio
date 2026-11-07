import copy,json
import pytest
from fastapi.testclient import TestClient
from backend import store,ingestion
from backend.app import app
from backend.engineering import parse_wind,wind_summary
from tests.test_engineering import wind_csv,AOI

@pytest.fixture
def client(tmp_path,monkeypatch):
    import backend.app as application
    monkeypatch.setattr(store,'DB',tmp_path/'test.sqlite')
    monkeypatch.setattr(ingestion,'DATA_ROOT',tmp_path/'data')
    monkeypatch.setattr(application,'DATA_ROOT',tmp_path/'data')
    with TestClient(app) as c:yield c

def create(client):
    p=client.post('/api/projects',json={'name':'Source integration test'}).json()
    s=client.post(f'/api/projects/{p["id"]}/scenarios',json={'inputs':{'screening_point':{'lat':53.88,'lon':1.89,'label':'Test regional reference'}}}).json()
    return p,s

def wind_data():
    heights={}
    for h in [10,100]:
        rows=parse_wind(wind_csv(height=h));heights[str(h)]={'rows':rows,'summary':wind_summary(rows)}
    return {'heights':heights,'grid_point':{'lat':54,'lon':2},'sample_hours':48,'limitations':['Regional reanalysis; not proposed site evidence.']}

def collect(client,s,monkeypatch):
    monkeypatch.setattr(ingestion,'collect',lambda *a,**k:wind_data())
    r=client.post(f'/api/scenarios/{s["id"]}/collect',json={'providers':['era5_wind'],'start_date':'2025-01-01','end_date':'2025-01-02'})
    assert r.status_code==202,r.text
    job=client.get('/api/data-jobs/'+r.json()['id']).json()
    assert job['status']=='completed',job
    return client.get('/api/scenarios/'+job['result_scenario_id']).json(),job

def test_api_collection_snapshot_and_no_implicit_energy(client,monkeypatch):
    p,s=create(client);result,job=collect(client,s,monkeypatch);new=result['scenario']
    assert new['id']!=s['id'] and new['inputs']['aoi'] is None and new['inputs']['wind_dataset_id'] is None
    assert len(client.get('/api/projects/'+p['id']+'/datasets').json())==1
    assert len(client.get('/api/scenarios/'+new['id']+'/datasets').json())==1
    assert client.get('/api/scenarios/'+s['id']+'/datasets').json()==[]
    wind=result['results']['C07'];assert wind['data']['hub_height_m']==100 and len(wind['data']['height_profile'])==2
    assert wind['data']['data_scope']=='regional_reference_only' and wind['evidence_maturity']=='publisher_api_screening'
    energy=client.post(f'/api/scenarios/{new["id"]}/categories/C26/run',json={}).json()
    assert energy['data']=={} and energy['status']=='needs-review'
    assert client.get('/api/scenarios/'+s['id']).json()['results']=={}

@pytest.mark.parametrize('edit',[{'screening_point':{'lat':54,'lon':2}},{'aoi':AOI}])
def test_point_or_geometry_edit_clears_data_bindings(client,monkeypatch,edit):
    p,s=create(client);result,_=collect(client,s,monkeypatch);new=result['scenario']
    changed=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':new['id'],'inputs':{**new['inputs'],**edit}}).json()
    assert changed['inputs']['data_bindings']=={}

def test_layout_or_cost_change_preserves_independent_evidence(client,monkeypatch):
    p,s=create(client);result,_=collect(client,s,monkeypatch);new=result['scenario']
    changed=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':new['id'],'layout_id':'LAYOUT_02','inputs':{'capex_gbp_per_kw':3000}}).json()
    assert changed['inputs']['data_bindings']==new['inputs']['data_bindings']
    assert client.post(f'/api/scenarios/{changed["id"]}/categories/C07/run',json={}).json()['data']['sample_count']==48

def test_foreign_external_binding_rejected(client,monkeypatch):
    p,s=create(client);result,_=collect(client,s,monkeypatch);p2,s2=create(client)
    forged=client.post(f'/api/projects/{p2["id"]}/scenarios',json={'parent_id':s2['id'],'inputs':{'data_bindings':result['scenario']['inputs']['data_bindings']}}).json()
    r=client.post(f'/api/scenarios/{forged["id"]}/categories/C07/run',json={})
    assert r.status_code==422 and 'scope' in r.json()['detail']

def test_provider_binding_cannot_be_swapped(client,monkeypatch):
    p,s=create(client);result,_=collect(client,s,monkeypatch);new=result['scenario']
    bad=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':new['id'],'inputs':{'data_bindings':{'nsta_fields':new['inputs']['data_bindings']['era5_wind']}}}).json()
    r=client.post(f'/api/scenarios/{bad["id"]}/categories/C39/run',json={})
    assert r.status_code==422 and 'provider' in r.json()['detail']

def test_failed_provider_not_promoted(client,monkeypatch):
    p,s=create(client)
    def failure(*a,**k):raise ValueError('Provider unavailable')
    monkeypatch.setattr(ingestion,'collect',failure)
    r=client.post(f'/api/scenarios/{s["id"]}/collect',json={'providers':['era5_wind']}).json();job=client.get('/api/data-jobs/'+r['id']).json()
    assert job['status']=='failed' and job['result_scenario_id'] is None
    assert job['steps'][0]['status']=='failed' and 'unavailable' in job['steps'][0]['error']
    assert client.get('/api/projects/'+p['id']+'/datasets').json()==[]

def test_refresh_failure_retains_prior_values_as_stale(client,monkeypatch):
    p,s=create(client);result,_=collect(client,s,monkeypatch);new=result['scenario']
    def failure(*a,**k):raise ValueError('Source schema changed')
    monkeypatch.setattr(ingestion,'collect',failure)
    r=client.post(f'/api/scenarios/{new["id"]}/collect',json={'providers':['era5_wind'],'force':True}).json()
    job=client.get('/api/data-jobs/'+r['id']).json();assert job['status']=='partial'
    refreshed=client.get('/api/scenarios/'+job['result_scenario_id']).json()
    assert refreshed['results']['C07']['data']['mean_speed_ms']==result['results']['C07']['data']['mean_speed_ms']
    assert refreshed['results']['C07']['evidence_maturity']=='stale_publisher_data'
    assert refreshed['results']['C07']['gaps'][0].startswith('STALE')

def test_collection_request_guards(client):
    p,s=create(client)
    for body in [{'providers':['unknown']},{'providers':[]},{'start_date':'2025-02-30'},{'start_date':'2025-12-31','end_date':'2025-01-01'},{'start_date':'1900-01-01'}]:
        assert client.post(f'/api/scenarios/{s["id"]}/collect',json=body).status_code==422
    providers=client.get('/api/providers').json()
    assert len(providers)==14 and any(p['id']=='site_screening' for p in providers)

def test_duplicate_collection_and_restart_recovery(client):
    p,s=create(client);job=ingestion.new_job(s,['era5_wind'],'2025-01-01','2025-12-31')
    with pytest.raises(ValueError,match='already running'):ingestion.new_job(s,['era5_wind'],'2025-01-01','2025-12-31')
    ingestion.recover_interrupted_jobs();assert ingestion.get_job(job['id'])['status']=='failed'

def test_new_region_clears_reference_and_all_bindings(client,monkeypatch):
    p,s=create(client);result,_=collect(client,s,monkeypatch);new=result['scenario']
    changed=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':new['id'],'site_id':'SITE_02','inputs':new['inputs']}).json()
    assert changed['inputs']['screening_point'] is None and changed['inputs']['data_bindings']=={}
