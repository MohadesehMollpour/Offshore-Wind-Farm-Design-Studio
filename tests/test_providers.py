import copy,hashlib,json
from datetime import datetime,timezone,timedelta
import httpx
import pytest
from backend.providers import Fetcher,ProviderError,era5,marine,arcgis,validate_geojson,reference_from_wind,PROVIDERS,bathymetry
from backend.engineering import parse_wind,wind_summary
from tests.test_engineering import wind_csv

POINT={'lat':53.88,'lon':1.89,'label':'Test regional reference','scope':'regional_reference_only'}

def archive_response():
    times=[f'2025-01-01T{k:02}:00' for k in range(24)]
    hourly={'time':times}
    for height in [10,100]:hourly[f'wind_speed_{height}m']=[8 if height==10 else 10]*24;hourly[f'wind_direction_{height}m']=[270]*24
    return {'latitude':54,'longitude':2,'utc_offset_seconds':0,'hourly':hourly,'hourly_units':{'wind_speed_10m':'m/s','wind_speed_100m':'m/s','wind_direction_10m':'°','wind_direction_100m':'°'}}

def test_fetcher_preserves_bytes_hash_url_and_cache(tmp_path):
    calls=[]
    def response(request):calls.append(request);return httpx.Response(200,json={'real':'payload'},headers={'ETag':'test'})
    f=Fetcher(tmp_path,transport=httpx.MockTransport(response))
    first=f.get('https://api.neso.energy/test',{'id':'abc'});second=f.get('https://api.neso.energy/test',{'id':'abc'})
    assert first==second and len(calls)==1 and f.cache_hits==1
    asset=f.assets[0];assert hashlib.sha256((tmp_path/asset['path']).read_bytes()).hexdigest()==asset['sha256'];assert 'id=abc' in asset['url'];f.close()

def test_force_failure_keeps_last_good_with_stale_warning(tmp_path):
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'data':1})));original=f.get('https://api.neso.energy/test');f.close()
    f=Fetcher(tmp_path,force=True,transport=httpx.MockTransport(lambda r:httpx.Response(404)))
    assert f.get('https://api.neso.energy/test')==original
    assert any('STALE' in w for w in f.warnings);f.close()

def test_bad_cache_checksum_not_used(tmp_path):
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'data':1})));f.get('https://api.neso.energy/test');(tmp_path/f.assets[0]['path']).write_bytes(b'corrupt');f.close()
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(404)))
    with pytest.raises(ProviderError,match='retrieval failed'):f.get('https://api.neso.energy/test')
    f.close()

@pytest.mark.parametrize('url',['http://api.neso.energy/test','https://untrusted.example/file','https://127.0.0.1/private'])
def test_url_allowlist(tmp_path,url):
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:pytest.fail('Disallowed request was made')))
    with pytest.raises(ProviderError,match='allowlist'):f.get(url)
    f.close()

def test_redirect_to_private_host_blocked(tmp_path):
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(302,headers={'Location':'http://127.0.0.1/secret'})))
    with pytest.raises(ProviderError,match='allowlist'):f.get('https://api.neso.energy/test')
    f.close()

def test_era5_units_grid_and_scope(tmp_path):
    requests=[]
    def response(r):requests.append(r);return httpx.Response(200,json=archive_response())
    f=Fetcher(tmp_path,transport=httpx.MockTransport(response));data=era5(f,POINT,'2025-01-01','2025-01-01')
    assert data['sample_hours']==24 and set(data['heights'])=={'10','100'}
    assert data['grid_point']!={'lat':POINT['lat'],'lon':POINT['lon']}
    assert data['heights']['100']['summary']['sectors'][12]['frequency_pct']==100
    assert requests[0].url.params['cell_selection']=='sea' and requests[0].url.params['wind_speed_unit']=='ms' and requests[0].url.params['models']=='era5'
    assert data['heights']['100']['rows'][0]['timestamp_utc'].endswith('+00:00');f.close()

@pytest.mark.parametrize('mutation',[lambda j:j['hourly']['wind_speed_100m'].__setitem__(0,None),lambda j:j['hourly_units'].__setitem__('wind_speed_100m','km/h'),lambda j:j['hourly']['time'].pop(),lambda j:j.__setitem__('utc_offset_seconds',3600),lambda j:j['hourly_units'].__setitem__('wind_direction_100m','radians'),lambda j:j['hourly'].__setitem__('time',[t.replace('2025','2024') for t in j['hourly']['time']])])
def test_era5_invalid_data_not_promoted(tmp_path,mutation):
    payload=archive_response();mutation(payload);f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(200,json=payload)))
    with pytest.raises(ProviderError):era5(f,POINT,'2025-01-01','2025-01-01')
    f.close()

def test_wrong_arcgis_owner_rejected_before_service_fetch(tmp_path):
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'owner':'unverified_republisher'})))
    with pytest.raises(ProviderError,match='owner'):arcgis(f,'tce_wind')
    f.close()

@pytest.mark.parametrize('payload',[{'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[100000,6000000]},'properties':{}}]},{'type':'wrong','features':[]}])
def test_bad_source_geometry_rejected(payload):
    with pytest.raises(ProviderError):validate_geojson(payload)

def test_declared_projected_crs_cannot_pass_as_wgs84():
    with pytest.raises(ProviderError,match='CRS'):validate_geojson({'type':'FeatureCollection','features':[],'crs':{'properties':{'name':'EPSG:3857'}}})

def test_reference_point_is_from_official_geometry():
    geo={'type':'Polygon','coordinates':[[[1,53],[2,53],[2,54],[1,54],[1,53]]]}
    data={'geojson':{'type':'FeatureCollection','features':[{'geometry':geo,'properties':{'Name_Prop':'Hornsea 1 (Centre)','OBJECTID':38}}]},'source_url':'https://www.arcgis.com/home/item.html?id=test'}
    p=reference_from_wind(data,'official-snapshot')
    assert p['lat']==53.5 and p['lon']==1.5 and p['is_proposed_site'] is False and p['source_dataset_id']=='official-snapshot'

def test_marine_nulls_reported_and_forecast_labelled(tmp_path):
    payload={'latitude':54,'longitude':2,'utc_offset_seconds':0,'hourly_units':{'wave_height':'m','wave_period':'s'},'hourly':{'time':['2026-11-01T00:00','2026-11-01T01:00'],'wave_height':[1.5,None],'wave_period':[7,8],'wave_direction':[270,280]}}
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(200,json=payload)));d=marine(f,POINT)
    assert d['record_count']==1 and d['missing_count']==1 and d['measurement_type']=='forecast';f.close()

def test_all_missing_marine_not_a_success(tmp_path):
    payload={'latitude':54,'longitude':2,'utc_offset_seconds':0,'hourly_units':{'wave_height':'m','wave_period':'s'},'hourly':{'time':['2026-11-01T00:00'],'wave_height':[None],'wave_period':[None],'wave_direction':[None]}}
    f=Fetcher(tmp_path,transport=httpx.MockTransport(lambda r:httpx.Response(200,json=payload)))
    with pytest.raises(ProviderError,match='only missing'):marine(f,POINT)
    f.close()

def test_bathymetry_axis_order_and_signed_depth(tmp_path):
    calls=[]
    def response(r):
        calls.append(r)
        if r.url.params['request']=='GetCapabilities':return httpx.Response(200,text='<WMS_Capabilities xmlns="http://www.opengis.net/wms"><Capability><Layer><Name>emodnet:mean</Name><Title>Mean depth</Title></Layer></Capability></WMS_Capabilities>')
        return httpx.Response(200,json={'features':[{'properties':{'Depth':-31.2}}]})
    f=Fetcher(tmp_path,transport=httpx.MockTransport(response));d=bathymetry(f,POINT)
    assert d['water_depth_m']==31.2 and d['signed_dtm_value_m']==-31.2
    p=calls[1].url.params;assert p['version']=='1.1.1' and p['srs']=='EPSG:4326';assert float(p['bbox'].split(',')[0])==pytest.approx(POINT['lon']-.01);f.close()

def test_arcgis_id_paging_count_guard(tmp_path):
    def response(r):
        if '/content/items/' in r.url.path:return httpx.Response(200,json={'owner':'TheCrownEstate','url':'https://services2.arcgis.com/test/FeatureServer'})
        if r.url.path.endswith('/FeatureServer'):return httpx.Response(200,json={'layers':[{'id':0}]})
        if r.url.path.endswith('/0'):return httpx.Response(200,json={'maxRecordCount':1,'fields':[]})
        if r.url.params.get('returnIdsOnly'):return httpx.Response(200,json={'objectIds':[1,2]})
        return httpx.Response(200,json={'type':'FeatureCollection','features':[]})
    f=Fetcher(tmp_path,transport=httpx.MockTransport(response))
    with pytest.raises(ProviderError,match='record count'):arcgis(f,'tce_wind')
    f.close()
