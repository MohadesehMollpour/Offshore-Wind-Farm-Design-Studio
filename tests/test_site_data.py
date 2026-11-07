import copy
import pytest
from shapely.geometry import LineString
from backend.site_data import coast_distance,point_distance,density_point,preference_scores
from backend.providers import ProviderError
from backend.engineering import validate_inputs
from backend.engine import DEFAULT_INPUTS
from tests.test_ingestion import client,create
from backend import ingestion

PREFS={'weights':{'port_km':40,'coast_km':30,'shipping':30},'year':2023,'density_threshold':1,'vessel_speed_knots':20}

def benchmarks():
    return [{'id':'a','port_km':10,'coast_km':30,'density':{'2023':0,'2024':3}},
            {'id':'b','port_km':30,'coast_km':10,'density':{'2023':2,'2024':1}}]

def test_geodesic_and_coast_nearest_point():
    p={'lat':0,'lon':0}
    assert point_distance(p,{'lat':0,'lon':1})==pytest.approx(111.31949,abs=.001)
    coast=coast_distance(p,LineString([(1,-1),(1,1)]))
    assert coast['lon']==pytest.approx(1,abs=.001)
    assert coast['lat']==pytest.approx(0,abs=.001)
    assert coast['distance_km']==pytest.approx(111.32,abs=.02)

def test_weights_change_preference_but_never_eligibility():
    port=preference_scores(benchmarks(),{'port_km':1},2023)
    coast=preference_scores(benchmarks(),{'coast_km':1},2023)
    assert port[0]['id']=='a' and coast[0]['id']=='b'
    assert port[0]['score']==100 and port[1]['score']==0
    assert all(r['eligible'] is False for r in port+coast)
    assert preference_scores(benchmarks(),{'shipping':1},2024)[0]['id']=='b'

def test_missing_positive_weight_blocks_score_but_zero_weight_does_not():
    rows=benchmarks();rows[0]['density']['2023']=None
    missing=preference_scores(rows,{'shipping':1},2023)
    assert next(r for r in missing if r['id']=='a')['score'] is None
    assert preference_scores(rows,{'port_km':1,'shipping':0},2023)[0]['score']==100
    with pytest.raises(ValueError):preference_scores(rows,{'shipping':0},2023)

def test_constant_criterion_uses_midpoint():
    rows=benchmarks();rows[1]['port_km']=rows[0]['port_km']
    assert [r['score'] for r in preference_scores(rows,{'port_km':1},2023)]==[50,50]

@pytest.mark.parametrize('raw,expected',[(0,0),(None,None),(-9999,None),(2.3,2.3)])
def test_density_time_axis_and_nodata(raw,expected):
    class Fake:
        def json(self,url,params,ttl):
            assert params['time']=='2023-01-01T00:00:00Z'
            assert params['srs']=='EPSG:4326' and params['version']=='1.1.1'
            assert params['bbox'].startswith('1.997,53.997')
            return {'features':[{'properties':{'GRAY_INDEX':raw}}]}
    assert density_point(Fake(),{'lat':54,'lon':2},2023)==expected

def test_density_rejects_invalid_published_value():
    class Fake:
        def json(self,*args):return {'features':[{'properties':{'GRAY_INDEX':'NaN'}}]}
    with pytest.raises(ProviderError):density_point(Fake(),{'lat':54,'lon':2},2023)

@pytest.mark.parametrize('edit',[
    {'weights':{'port_km':0,'coast_km':0,'shipping':0}},
    {'weights':{'port_km':True,'coast_km':1,'shipping':1}},
    {'weights':{'port_km':float('nan'),'coast_km':1,'shipping':1}},
    {'year':2025},{'density_threshold':-1},{'vessel_speed_knots':0},{'vessel_speed_knots':True}])
def test_preference_validation(edit):
    with pytest.raises(ValueError):validate_inputs({**copy.deepcopy(DEFAULT_INPUTS),'site_preferences':{**copy.deepcopy(PREFS),**edit}})

def test_reference_data_and_preferences_stay_in_immutable_revisions(client,monkeypatch):
    p,s=create(client)
    fixture={'benchmarks':benchmarks(),'samples':[],'default_year':2023,'limitations':['Reference only.']}
    monkeypatch.setattr(ingestion,'collect',lambda *a,**k:fixture)
    job=client.post(f'/api/scenarios/{s["id"]}/collect',json={'providers':['site_screening']}).json()
    done=client.get('/api/data-jobs/'+job['id']).json()
    assert done['status']=='completed',done
    old=client.get('/api/scenarios/'+done['result_scenario_id']).json()
    assert set(old['results'])>={'C03','C04','C05'}
    pref=copy.deepcopy(PREFS);pref['weights']={'port_km':0,'coast_km':100,'shipping':0}
    new=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':old['scenario']['id'],'inputs':{'site_preferences':pref}}).json()
    assert new['inputs']['data_bindings']==old['scenario']['inputs']['data_bindings']
    result=client.post(f'/api/scenarios/{new["id"]}/categories/C03/run',json={}).json()
    assert result['data']['baseline_scores'][0]['id']=='b'
    assert result['data']['data_scope']=='regional_reference_only'
    unchanged=client.get('/api/scenarios/'+old['scenario']['id']).json()
    assert unchanged['results']['C03']==old['results']['C03']
    assert unchanged['scenario']['inputs'].get('site_preferences') is None
