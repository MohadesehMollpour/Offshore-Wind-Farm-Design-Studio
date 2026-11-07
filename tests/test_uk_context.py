import copy,math
import pytest
from shapely.geometry import shape
from backend.engine import DEFAULT_INPUTS
from backend.engineering import validate_inputs
from backend.uk_context import uk_context,cartography

POINT={'lon':1.9,'lat':53.8,'label':'Synthetic offshore reference'}
def sample(distance=114):
 s={'inputs':{'location_preferences':{'country':'UK','max_coast_km':100}}}
 data={'reference_point':POINT,'bounds':[-.4,52.5,4.2,55.3]}
 external={'site_screening':{'data':{'coast':{'distance_km':distance,'lon':1.274669,'lat':52.929185},'ports':[{'country':'UK','name':'Synthetic port','lon':0,'lat':53},{'country':'NL','name':'Non-UK port','lon':4,'lat':53}],'benchmarks':[{'id':'A','coast_km':88,'eligibility':'reference_only_existing_agreement'}]}}}
 return s,data,external

def test_user_distance_preference_does_not_move_reference_or_create_site():
 s,data,e=sample();before=copy.deepcopy((s,data,e));c=uk_context(s,data,e)
 assert c['preference_status']=='outside_limit' and c['coast']['distance_km']==114
 assert c['benchmarks'][0]['within_distance_preference'] is True
 assert c['benchmarks'][0]['eligibility']=='reference_only_existing_agreement'
 assert len(c['ports'])==1 and shape(c['coastal_band']['geometry']).area>0
 assert (s,data,e)==before

def test_distance_boundary_and_missing_or_non_uk_coast():
 s,data,e=sample(100);assert uk_context(s,data,e)['preference_status']=='within_limit'
 e['site_screening']['data']['coast'].update(lon=5,lat=60)
 assert uk_context(s,data,e)['preference_status']=='unavailable'
 assert uk_context(s,data,{})['preference_status']=='unavailable'
 s['inputs']={};c=uk_context(s,data,{})
 assert c['preference_status']=='not_set' and c['coastal_band'] is None

@pytest.mark.parametrize('value',[True,0,501,float('nan')])
def test_invalid_coast_preference_rejected(value):
 with pytest.raises(ValueError):validate_inputs({**DEFAULT_INPUTS,'location_preferences':{'country':'UK','max_coast_km':value}})

def test_location_preference_country_and_fields_are_explicit():
 validate_inputs({**DEFAULT_INPUTS,'location_preferences':{'country':'UK','max_coast_km':100}})
 for prefs in [{'country':'Denmark','max_coast_km':100},{'country':'UK'},{'country':'UK','max_coast_km':100,'approved':True}]:
  with pytest.raises(ValueError):validate_inputs({**DEFAULT_INPUTS,'location_preferences':prefs})

def test_cartography_has_actual_uk_and_regional_land_not_nodata_inference():
 data,meta=cartography();uk=next(f for f in data['features'] if f['properties']['code']=='GBR')
 assert shape(uk['geometry']).is_valid and 'natural-earth' in meta['source_url']
 s,d,e=sample();c=uk_context(s,d,e)
 assert any(f['properties']['code']=='GBR' for f in c['regional_land']['features'])
