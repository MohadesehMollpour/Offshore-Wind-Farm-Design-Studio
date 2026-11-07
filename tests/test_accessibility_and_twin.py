import copy,math
from datetime import datetime,timedelta
import pytest
from backend import accessibility as access
from backend.farm_preview import arrangement,wake_factors,preview
from backend.engine import DEFAULT_INPUTS
from tests.test_ingestion import client,create

def sample(n=24):
    return {'rows':[{'time':(datetime(2025,1,1)+timedelta(hours=i)).isoformat()+'+00:00','wind_ms':10,'hs_m':1.5,'current_ms':1,'rain_mm_h':0,'is_day':1,'visibility_m':None} for i in range(n)],'start_date':'2025-01-01','end_date':'2025-01-01'}

def test_joint_limits_inclusive_and_unknown_is_not_pass():
    data=sample();cfg=copy.deepcopy(access.DEFAULT_ACCESS)
    result=access.evaluate_access(data,cfg)
    assert result['eligible_hours']==24 and result['window_starts']==13 and result['longest_run_h']==24
    cfg['active']=['W','SH','L','V'];result=access.evaluate_access(data,cfg)
    assert result['eligible_hours']==0 and result['unknown_hours']==24 and result['window_starts']==0
    data['rows'][0]['hs_m']=1.6
    result=access.evaluate_access(data,cfg)
    assert result['ineligible_hours']==1 and result['unknown_hours']==23

def test_consecutive_windows_and_night_and_zero_values():
    data=sample(30);cfg=copy.deepcopy(access.DEFAULT_ACCESS);cfg['duration_h']=12
    data['rows'][12]['is_day']=0
    result=access.evaluate_access(data,cfg)
    assert result['eligible_hours']==29 and result['window_lengths_h']==[12,17] and result['window_starts']==7
    cfg['active']=['C','R','L'];cfg['rain_max_mm_h']=0;cfg['current_max_ms']=0
    for row in data['rows']:row['current_ms']=0
    assert access.evaluate_access(data,cfg)['eligible_hours']==29
    cfg['daylight_required']=False;data['rows'][0]['is_day']=None
    assert access.evaluate_access(data,cfg)['eligible_hours']==30

@pytest.mark.parametrize('edit',[{'active':[]},{'active':[['W']]},{'active':['W','W']},{'active':['bad']},{'wind_max_ms':float('nan')},{'duration_h':1.5},{'wave_max_m':True},{'daylight_required':'yes'}])
def test_access_guards(edit):
    with pytest.raises(ValueError):access.validate_access({**copy.deepcopy(access.DEFAULT_ACCESS),**edit})

class Source:
    def __init__(self,bad=None):self.bad=bad
    def json(self,url,params,*args):
        times=[(datetime(2025,1,1)+timedelta(hours=i)).isoformat(timespec='minutes') for i in range(24)]
        if params['models']=='era5':
            units={'wind_speed_10m':'m/s','wind_speed_100m':'m/s','precipitation':'mm','visibility':'undefined'}
            values={'wind_speed_10m':[0]*24,'wind_direction_10m':[270]*24,'wind_speed_100m':[10]*24,'wind_direction_100m':[270]*24,'precipitation':[0]*24,'is_day':[0]*12+[1]*12,'visibility':[None]*24}
        elif params['models']=='era5_ocean':
            units={'wave_height':'m','wave_period':'s'};values={'wave_height':[0]*24,'wave_period':[8]*24,'wave_direction':[270]*24}
            if self.bad=='timeline':times[0]=times[1]
            if self.bad=='unit':units['wave_height']='feet'
        else:
            if self.bad=='current':raise ValueError('Not available')
            units={'ocean_current_velocity':'km/h'};values={'ocean_current_velocity':[3.6]*24,'ocean_current_direction':[90]*24}
        return {'latitude':54,'longitude':2,'utc_offset_seconds':0,'hourly_units':units,'hourly':{'time':times,**values}}

def test_provider_joint_units_daylight_and_missing(monkeypatch):
    monkeypatch.setattr(access,'recent_complete_year',lambda:('2025-01-01','2025-01-01'))
    d=access.collect_access(Source(),{'lat':54,'lon':2})
    assert d['coverage']['V']==0 and d['coverage']['C']==24
    assert d['rows'][0]['wind_ms']==0 and d['rows'][0]['hs_m']==0 and d['rows'][0]['rain_mm_h']==0
    assert d['rows'][0]['is_day']==0 and d['rows'][0]['current_ms']==pytest.approx(1)
    assert d['rows'][0]['time'].endswith('+00:00')
    assert d['rows'][0]['visibility_m'] is None
    d=access.collect_access(Source('current'),{'lat':54,'lon':2});assert d['coverage']['C']==0

@pytest.mark.parametrize('bad',['timeline','unit'])
def test_provider_rejects_misaligned_or_wrong_units(monkeypatch,bad):
    monkeypatch.setattr(access,'recent_complete_year',lambda:('2025-01-01','2025-01-01'))
    with pytest.raises(ValueError):access.collect_access(Source(bad),{'lat':54,'lon':2})

def scenario(layout='LAYOUT_01'):
    return {'id':'test','hash':'abc','site_id':'SITE_01','revision':1,'layout_id':layout,'inputs':copy.deepcopy(DEFAULT_INPUTS)}

def test_configurations_are_deterministic_and_dimensions_follow_inputs():
    grid=arrangement(scenario());assert grid['conceptual'] and grid['count']==66
    assert all(t['lat'] is None for t in grid['turbines'])
    assert arrangement(scenario('LAYOUT_04'))==arrangement(scenario('LAYOUT_04'))
    assert arrangement(scenario('LAYOUT_02'))['turbines']!=grid['turbines']
    rotated=scenario();rotated['inputs']['rotation_deg']=90
    for a,b in zip(grid['turbines'],arrangement(rotated)['turbines']):
        assert b['x_m']==pytest.approx(-a['y_m'],abs=1e-8)
        assert b['y_m']==pytest.approx(a['x_m'],abs=1e-8)
    s=scenario();s['inputs']['capacity_mw']=150
    assert arrangement(s)['count']==10

def test_computed_c23_geometry_is_preferred():
    out=arrangement(scenario(),{'data':{'turbines':[{'id':'T1','lon':1.8,'lat':53.8},{'id':'T2','lon':1.81,'lat':53.81}]}})
    assert not out['conceptual'] and out['count']==2
    assert out['turbines'][0]['lat']==53.8
    assert out['turbines'][1]['x_m']>out['turbines'][0]['x_m']

def test_meteorological_wake_direction_and_expansion():
    turbines=[{'id':'west','x_m':0,'y_m':0},{'id':'east','x_m':1680,'y_m':0}]
    west,east=wake_factors(turbines,240,270)
    assert west['wind_ratio']==1 and east['wind_ratio']<1
    reverse=wake_factors(turbines,240,90)
    assert reverse[0]['wind_ratio']<1 and reverse[1]['wind_ratio']==1
    assert wake_factors(turbines,240,0)[1]['wind_ratio']==1
    assert wake_factors(turbines,240,270,k=.1)[1]['wind_ratio']>east['wind_ratio']
    assert wake_factors(turbines,240,270,ct=0)[1]['wind_ratio']==1

def test_wave_shelter_and_access_are_never_inferred_from_hub_wake():
    out=preview(scenario(),{},wind_ms=12,hs_m=2.3)
    assert any(t['wind_ratio']<1 for t in out['turbines'])
    assert {t['ambient_hs_m'] for t in out['turbines']}=={2.3}
    assert out['access_credit_from_wakes'] is False

def test_preview_endpoints_and_access_prefs_are_revision_scoped(client):
    p,s=create(client)
    assert client.post(f'/api/scenarios/{s["id"]}/farm-preview',json={'wind_from_deg':361}).status_code==422
    out=client.post(f'/api/scenarios/{s["id"]}/farm-preview',json={'wind_from_deg':90}).json()
    assert out['scenario_id']==s['id'] and out['conceptual']
    assert client.post(f'/api/scenarios/{s["id"]}/accessibility/evaluate',json={'preferences':access.DEFAULT_ACCESS}).status_code==422
    cfg={**access.DEFAULT_ACCESS,'wave_max_m':2}
    revised=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'inputs':{'access_preferences':cfg}}).json()
    assert revised['inputs']['access_preferences']['wave_max_m']==2
    assert 'access_preferences' not in client.get('/api/scenarios/'+s['id']).json()['scenario']['inputs']

def test_refresh_reuses_context_and_observes_results_in_order(client,monkeypatch):
    from backend import store
    p,s=create(client);original=store.context;calls=[]
    def context(sc):calls.append(sc['id']);return original(sc)
    monkeypatch.setattr(store,'context',context)
    r=client.post(f'/api/scenarios/{s["id"]}/refresh-evidence',json={})
    assert r.status_code==200 and calls==[s['id']]
    assert set(r.json()['results'])=={'C67','C69'}
