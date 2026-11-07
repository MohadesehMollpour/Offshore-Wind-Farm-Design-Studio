import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend import store
from backend.catalog import CATEGORIES,ROOT
from backend.engine import digest
from tests.test_engineering import AOI,wind_csv

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB',tmp_path/'test.sqlite')
    # Keep test result files and synthetic wind evidence out of real data folders.
    import backend.app as module
    monkeypatch.setattr(module,'DATA_ROOT',tmp_path/'data')
    with TestClient(app) as c:yield c
def create(client):
    p=client.post('/api/projects',json={'name':'Test study'}).json()
    s=client.post(f'/api/projects/{p["id"]}/scenarios',json={}).json()
    return p,s
def test_all_70_packages_run_with_honest_gaps(client):
    p,s=create(client)
    r=client.post(f'/api/scenarios/{s["id"]}/screen',json={})
    assert r.status_code==200,r.text
    results=r.json()['results'];assert len(results)==70
    assert all(x['scenario_hash']==s['hash'] for x in results.values())
    assert results['C60']['data']=={} and results['C60']['status']=='needs-review'
    assert len(client.get('/api/catalog').json()['categories'])==70
def test_snapshot_isolation_baseline_and_old_run(client):
    p,s=create(client);client.post(f'/api/scenarios/{s["id"]}/categories/C20/run',json={})
    client.post(f'/api/scenarios/{s["id"]}/baseline',json={})
    n=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'inputs':{'capacity_mw':150}}).json()
    assert n['id']!=s['id'] and n['hash']!=s['hash']
    assert client.get(f'/api/scenarios/{n["id"]}').json()['results']=={}
    assert client.get(f'/api/scenarios/{s["id"]}').json()['scenario']['baseline']
    client.post(f'/api/scenarios/{s["id"]}/categories/C21/run',json={})
    assert client.get(f'/api/scenarios/{n["id"]}').json()['results']=={}
def test_dataset_scope_clear_on_site_or_geometry_change(client):
    p,s=create(client)
    s=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'inputs':{'aoi':AOI}}).json()
    w=client.post(f'/api/scenarios/{s["id"]}/wind',json={'csv_text':wind_csv(),'source_name':'Test synthetic fixture','license':'Test only','method':'Constant hourly fixture','measurement_type':'synthetic_demo_only'})
    assert w.status_code==200,w.text
    s=w.json();assert s['inputs']['wind_dataset_id']
    r=client.post(f'/api/scenarios/{s["id"]}/categories/C08/run',json={}).json()
    assert r['data']['sample_count']==48 and r['evidence_maturity']=='synthetic_demo_only'
    n=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'site_id':'SITE_02','inputs':s['inputs']}).json()
    assert n['inputs']['aoi'] is None and n['inputs']['wind_dataset_id'] is None
    g={**AOI,'coordinates':[[[2,54],[2.5,54],[2.5,54.3],[2,54.3],[2,54]]]}
    n=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'inputs':{'aoi':g}}).json()
    assert n['inputs']['wind_dataset_id'] is None
def test_cross_project_parent_and_foreign_dataset_rejected(client):
    p,s=create(client);p2,s2=create(client)
    r=client.post(f'/api/projects/{p2["id"]}/scenarios',json={'parent_id':s['id']})
    assert r.status_code==422
    s2=client.post(f'/api/projects/{p2["id"]}/scenarios',json={'parent_id':s2['id'],'inputs':{'wind_dataset_id':'foreign-id'}}).json()
    assert client.post(f'/api/scenarios/{s2["id"]}/categories/C08/run',json={}).status_code==422
def test_invalid_design_and_exports(client):
    p,s=create(client)
    assert client.post(f'/api/projects/{p["id"]}/scenarios',json={'inputs':{'capacity_mw':1000}}).status_code==422
    assert client.post(f'/api/projects/{p["id"]}/scenarios',json={'site_id':'invented'}).status_code==422
    assert client.get(f'/api/scenarios/{s["id"]}/export.json').json()['status']=='draft_not_approved'
    assert 'DRAFT' in client.get(f'/api/scenarios/{s["id"]}/report.md').text
    assert client.post(f'/api/scenarios/{s["id"]}/categories/C99/run',json={}).status_code==404
def test_origin_and_host_guard(client):
    assert client.post('/api/projects',json={'name':'bad'},headers={'Origin':'https://unrelated.example'}).status_code==403
    assert client.get('/api/health',headers={'Host':'unrelated.example'}).status_code==403
def test_event_chain(client):
    p,s=create(client);events=list(reversed(client.get(f'/api/projects/{p["id"]}/history').json()))
    for k,e in enumerate(events):
        if k:assert e['previous_hash']==events[k-1]['event_hash']
        expected=digest({key:e[key] for key in ['previous_hash','project_id','scenario_id','category_id','action','created','payload']})
        assert e['event_hash']==expected
def test_dependency_graph_acyclic():
    graph={c['id']:c['dependencies'] for c in CATEGORIES};done=set()
    def visit(n,active):
        assert n not in active,'Dependency cycle'
        if n in done:return
        for parent in graph[n]:visit(parent,active|{n})
        done.add(n)
    for n in graph:visit(n,set())
    assert len(done)==70

def test_full_preliminary_energy_finance_chain(client):
    p,s=create(client)
    assumptions={'aoi':AOI,'capacity_mw':150,'wake_loss':.05,'electrical_loss':.03,'availability_loss':.04,'curtailment_loss':.02,'uncertainty_fraction':.1,'capex_gbp_per_kw':2500,'opex_gbp_per_kw_year':70,'decommission_gbp':1e7,'discount_rate':.06,'power_price_gbp_mwh':80}
    s=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'inputs':assumptions}).json()
    s=client.post(f'/api/scenarios/{s["id"]}/wind',json={'csv_text':wind_csv(),'source_name':'Synthetic integration test','license':'Test only','method':'Hourly constant fixture','measurement_type':'synthetic_demo_only'}).json()
    for cid in ['C01','C08','C21','C23','C26','C27','C28','C58','C59','C60','C61']:
        r=client.post(f'/api/scenarios/{s["id"]}/categories/{cid}/run',json={})
        assert r.status_code==200,r.text
        assert r.json()['data'],(cid,r.json()['gaps'])
    results=client.get(f'/api/scenarios/{s["id"]}').json()['results']
    assert results['C28']['data']['p90_mwh']<results['C28']['data']['p50_mwh']
    assert results['C60']['data']['lcoe_gbp_mwh']>0
    assert results['C60']['data']['energy']['net_aep_mwh']==results['C27']['data']['net_aep_mwh']
    assert results['C08']['data']['directional_proxy_energy'][12]['energy_share_pct']==100
    assert results['C60']['evidence_maturity']=='synthetic_demo_only'
