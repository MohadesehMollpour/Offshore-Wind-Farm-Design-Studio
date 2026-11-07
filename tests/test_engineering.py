import calendar,copy,math
from datetime import datetime,timedelta,timezone
import pytest
from shapely.geometry import Point
from backend.engine import DEFAULT_INPUTS,disclosure_complete
from backend.engineering import geometry,validate_inputs,layout,parse_wind,wind_summary,power,energy,finance
from backend.catalog import load

AOI={'type':'Polygon','coordinates':[[[1.0,54.0],[1.5,54.0],[1.5,54.3],[1.0,54.3],[1.0,54.0]]]}
@pytest.fixture
def inputs():return {**copy.deepcopy(DEFAULT_INPUTS),'aoi':AOI,'capacity_mw':150,'wake_loss':.05,'electrical_loss':.03,'availability_loss':.04,'curtailment_loss':.02,'uncertainty_fraction':.1,'capex_gbp_per_kw':2500,'opex_gbp_per_kw_year':70,'decommission_gbp':1e7,'discount_rate':.06,'power_price_gbp_mwh':80}
def wind_csv(n=48,direction=270,speed=10,height=150):
    start=datetime(2025,1,1,tzinfo=timezone.utc)
    return 'timestamp_utc,wind_speed_ms,direction_deg,hub_height_m\n'+'\n'.join(f'{(start+timedelta(hours=k)).isoformat()},{speed},{direction},{height}' for k in range(n))

def test_invalid_geometry_rejected():
    bad={'type':'Polygon','coordinates':[[[1,54],[2,55],[1,55],[2,54],[1,54]]]}
    with pytest.raises(ValueError,match='Invalid AOI'):geometry(bad)
    with pytest.raises(ValueError,match='closed'):geometry({'type':'Polygon','coordinates':[[[1,54],[2,54],[2,55],[1,55]]]})
    with pytest.raises(ValueError,match='CRS'):geometry({**AOI,'crs':{'name':'EPSG:27700'}})
@pytest.mark.parametrize('key,value',[('wake_loss',-.1),('discount_rate',float('nan')),('capacity_mw',151),('design_year',2030.5),('turbine_mw',True)])
def test_bad_inputs(inputs,key,value):
    inputs[key]=value
    with pytest.raises(ValueError):validate_inputs(inputs)
@pytest.mark.parametrize('strategy',['LAYOUT_01','LAYOUT_02','LAYOUT_03','LAYOUT_04','LAYOUT_05'])
def test_layout_envelope_spacing_and_determinism(inputs,strategy):
    rows=parse_wind(wind_csv());a=layout(inputs,strategy,rows);b=layout(inputs,strategy,rows)
    assert a==b and a['count']==10 and a['capacity_mw']==150
    p,projected,fwd,_=geometry(AOI)
    for t in a['turbines']:
        assert p.contains(Point(t['lon'],t['lat']))
        assert projected.boundary.distance(Point(*fwd(t['lon'],t['lat'])))>=inputs['rotor_diameter_m']/2-1e-5
    assert a['minimum_spacing_m']>=inputs['spacing_d']*inputs['rotor_diameter_m']-1e-5
def test_layout_exclusions(inputs):
    inputs['exclusions']=[{'type':'Polygon','coordinates':[[[1.2,54.1],[1.3,54.1],[1.3,54.2],[1.2,54.2],[1.2,54.1]]]}]
    a=layout(inputs,'LAYOUT_04');ex=geometry(inputs['exclusions'][0])[0]
    assert all(not ex.covers(Point(t['lon'],t['lat'])) for t in a['turbines'])
def test_irregular_search_is_not_energy_optimizer_and_missing_wind_blocks(inputs):
    irregular=layout(inputs,'LAYOUT_04')
    assert irregular['layout_method']=='seeded_feasible_point_search' and irregular['energy_cost_optimized'] is False
    with pytest.raises(ValueError,match='joint wind'):layout(inputs,'LAYOUT_03')
def test_infeasible_capacity(inputs):
    inputs['aoi']={'type':'Polygon','coordinates':[[[1,54],[1.005,54],[1.005,54.005],[1,54.005],[1,54]]]}
    with pytest.raises(ValueError,match='positions fit|envelope'):layout(inputs,'LAYOUT_01')
def test_wind_from_convention_and_calm():
    rows=parse_wind(wind_csv(direction=270));s=wind_summary(rows)
    assert max(s['sectors'],key=lambda x:x['frequency_pct'])['direction_deg']==270
    assert sum(x['frequency_pct'] for x in s['sectors'])==100
    rows[0]['speed']=0;s=wind_summary(rows)
    assert sum(x['frequency_pct'] for x in s['sectors'])+s['calm_pct']==pytest.approx(100)
def test_wind_wrap_north():
    s=wind_summary(parse_wind(wind_csv(direction=359)))
    assert s['sectors'][0]['frequency_pct']==100
@pytest.mark.parametrize('mutation',[lambda s:s.replace('+00:00',''),lambda s:s.replace(',10,270,150',',-1,270,150'),lambda s:s+'\n'+s.splitlines()[1],lambda s:s.replace('2025-01-01T01:00:00','2025-01-05T01:00:00')])
def test_invalid_csv(mutation):
    with pytest.raises(ValueError):parse_wind(mutation(wind_csv()))
def test_energy_loss_once_calendar_and_quantiles(inputs):
    rows=parse_wind(wind_csv(speed=12));r=energy(inputs,rows)
    assert r['gross_aep_mwh']==150*8760
    assert r['net_aep_mwh']==pytest.approx(150*8760*.95*.97*.96*.98)
    assert r['p90_mwh']<r['p75_mwh']<r['p50_mwh']
    assert r['gross_aep_mwh']-sum(x['mwh'] for x in r['losses'])==pytest.approx(r['net_aep_mwh'])
    inputs['design_year']=2032;assert energy(inputs,rows)['reporting_hours']==8784
def test_no_implicit_height_extrapolation(inputs):
    with pytest.raises(ValueError,match='height'):energy(inputs,parse_wind(wind_csv(height=100)))
def test_power_curve_boundaries(inputs):
    assert power(2.9,inputs)==0 and power(25,inputs)==0
    assert power(12,inputs)==15 and power(24.9,inputs)==15
def test_financial_independent_zero_discount(inputs):
    inputs.update(discount_rate=0,lifetime_years=2,decommission_gbp=100000)
    e=100000;r=finance(inputs,e)
    capex=2500*150000;opex=70*150000
    assert r['lcoe_gbp_mwh']==pytest.approx((capex+2*opex+100000)/(2*e))
    assert r['npv_gbp']==pytest.approx(-capex+2*(e*80-opex)-100000)
    assert r['irr'] is None
def test_zero_energy_lcoe_blocked(inputs):
    with pytest.raises(ValueError,match='Positive delivered energy'):finance(inputs,0)
def test_empty_and_duplicate_disclosure_cannot_pass(inputs):
    inputs['contributions']=[{'section':'Location','human_lead':'','ai_tools':'','contribution':'','reviewed':True}]*16
    assert not disclosure_complete(inputs)
    inputs['contributions']=[{'section':t['name'],'human_lead':'Student','ai_tools':'None','contribution':'Checked sources','reviewed':True} for t in load('assessment')['topics']]
    assert disclosure_complete(inputs)
