import copy,hashlib,io,json,zipfile
import pytest
import shapefile
from pyproj import CRS
from shapely.geometry import box,shape
from backend import environment,ingestion,store
from backend.environment import SOURCES,parse_grid,read_boundaries,read_features,collect_environment,relief_status
from backend.providers import ProviderError,Fetcher
from tests.test_ingestion import client,create

POINT={'lat':53.8,'lon':1.9,'label':'Synthetic test reference'}

def boundary_zip(records,crs=4326):
    shp,shx,dbf=io.BytesIO(),io.BytesIO(),io.BytesIO()
    with shapefile.Writer(shp=shp,shx=shx,dbf=dbf) as writer:
        for name in ['SITE_CODE','SITE_NAME','SITE_STATU','Agency']:writer.field(name,'C')
        writer.field('AREA_HA','N',decimal=4)
        for code,name,status,geometry in records:
            writer.shape(geometry.__geo_interface__);writer.record(code,name,status,'Test publisher',geometry.area*100)
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w') as z:
        for name,raw in [('map.shp',shp.getvalue()),('map.shx',shx.getvalue()),('map.dbf',dbf.getvalue()),('map.prj',CRS.from_epsg(crs).to_wkt().encode())]:z.writestr(name,raw)
    return output.getvalue()

def grid_table():
    return {'columnNames':['latitude','longitude','elevation'],'columnUnits':['degrees_north','degrees_east','m'],
            'rows':[[53.6,1.7,None],[53.6,2.,0.],[53.6,2.2,-10.],[53.8,1.7,-20.],[53.8,2.,-30.],[53.8,2.2,-40.],[54.,1.7,-50.],[54.,2.,-60.],[54.,2.2,-70.]]}

def test_grid_north_up_zero_and_nodata():
    terrain=parse_grid(grid_table(),POINT)
    assert terrain['elevation_m'][0]==[-50.,-60.,-70.]
    assert terrain['elevation_m'][-1]==[None,0.,-10.]
    assert terrain['valid_cells']==8 and terrain['missing_cells']==1
    assert terrain['elevation_max_m']==0 and terrain['datum']=='Lowest Astronomical Tide (LAT)'

@pytest.mark.parametrize('mutate',[
 lambda t:t['columnUnits'].__setitem__(2,'feet'),
 lambda t:t['rows'].__setitem__(3,t['rows'][2]),
 lambda t:t['rows'][2].__setitem__(2,float('nan')),
 lambda t:t['rows'][2].__setitem__(2,True),
 lambda t:t['rows'].pop(),
 lambda t:[r.__setitem__(2,None) for r in t['rows']],
])
def test_invalid_relief_not_accepted(mutate):
    table=grid_table();mutate(table)
    with pytest.raises(ProviderError):parse_grid(table,POINT)

def test_jncc_archive_schema_bbox_and_management_unknown():
    raw=boundary_zip([('UKTEST','Synthetic designation','SAC',box(1.5,53.5,2.2,54)),('UKFAR','Distant test','SPA',box(-5,58,-4,59))])
    records=read_boundaries(raw,SOURCES[0],(1.,53.,3.,55.))
    assert len(records)==1 and records[0]['site_code']=='UKTEST'
    assert records[0]['designation']=='SAC' and records[0]['iucn_category'] is None
    assert records[0]['iucn_coverage']=='not_provided_by_source'
    with pytest.raises(ProviderError,match='WGS84'):read_boundaries(boundary_zip([('X','X','SAC',box(1,2,3,4))],3857),SOURCES[0],(0,0,5,5))

def test_feature_populations_and_raw_labels_preserved(monkeypatch):
    from backend import overview_data
    cells={'A1':'Site code','I1':'Marine features protected','A2':'UKX','F2':' Species ','I2':'Calidris alba','J2':'Sanderling','K2':'reproducing ', 'A3':'UKX','F3':'Species','I3':'Calidris alba','K3':'wintering'}
    monkeypatch.setattr(overview_data,'workbook_cells',lambda raw:{SOURCES[2]['sheet']:cells})
    rows=read_features(b'test',SOURCES[2])
    assert len(rows)==2 and {r['population_type'] for r in rows}=={'reproducing','wintering'}
    assert all(r['feature_type']=='species' for r in rows)
    assert rows[0]['source_row']==2 and rows[0]['feature_code']==''
    cells['I1']='Changed schema'
    with pytest.raises(ProviderError,match='schema'):read_features(b'test',SOURCES[2])

class FixtureFetcher:
    def get(self,url,**kwargs):
        if url.endswith('.zip'):
            if 'SACs' in url:return boundary_zip([('UKA','A','SAC',box(1.5,53.5,2.,54))])
            if 'SPAs' in url:return boundary_zip([('UKB','B','SPA',box(1.8,53.5,2.2,54))])
            return boundary_zip([('UKA','A','SAC',box(1.5,53.5,2.,54))])
        if url.endswith('.das'):return b'Lowest Astronomical Tide datum'
        return b'fixture'
    def json(self,url,**kwargs):
        if 'bathymetry_dtm_2024' in url:return {'table':grid_table()}
        if url.startswith(environment.NE_ITEMS):return {'type':'FeatureCollection','numberMatched':0,'features':[]}
        return {'type':'FeatureCollection','features':[]}

def fixture_data(monkeypatch):
    monkeypatch.setattr(environment,'read_features',lambda raw,s:[{'site_code':'UKA','feature_type':'species','feature':'Synthetic interest','population_type':'wintering','feature_code':'1351' if s['id']=='offshore' else '', 'common_name':'Test only','source_id':s['id']}])
    return collect_environment(FixtureFetcher(),POINT)

def test_union_dissolves_overlap_and_deduplicates_site_codes(monkeypatch):
    d=fixture_data(monkeypatch)
    assert d['record_count']==2
    assert d['protected_union_km2']<sum(r['area_in_reference_disc_km2'] for r in d['records'])
    assert sum(r['reference_inside'] for r in d['records'])==2
    assert next(r for r in d['records'] if r['site_code']=='UKA')['source_vintage']=='2025-12-03'
    features=next(r for r in d['records'] if r['site_code']=='UKA')['qualifying_features']
    assert len(features)==1 and features[0]['feature_code']=='1351'
    assert d['iucn_coverage']['supplied']==0 and d['iucn_coverage']['unknown']==2

def test_non_uk_request_not_presented_as_empty_environment():
    with pytest.raises(ProviderError,match='Danish/EU'):collect_environment(FixtureFetcher(),{'lat':56,'lon':8})

def test_natural_england_metadata_and_truncation():
    class NEFetch:
        count=1
        def json(self,*args,**kwargs):return {'type':'FeatureCollection','numberMatched':self.count,'features':[{'type':'Feature','geometry':box(1,53,2,54).__geo_interface__,'properties':{'mcz_code':'UKMCZ0035','mcz_name':'Synthetic inshore MCZ','status':'Designated','mcz_area':1234,'gis_date':'2016'}}]}
    fetch=NEFetch();rows=environment.collect_england_mcz(fetch,(1,53,2,54))
    assert len(rows)==1 and rows[0]['source_area_km2']==12.34
    assert rows[0]['site_code']=='UKMCZ0035' and rows[0]['iucn_category'] is None
    assert rows[0]['geometry_entered_date']=='2016' # Never relabel this as designation date.
    fetch.count=2
    with pytest.raises(ProviderError,match='truncated'):environment.collect_england_mcz(fetch,(1,53,2,54))

def test_rayshader_cache_is_bound_to_exact_terrain(tmp_path,monkeypatch):
    d=fixture_data(monkeypatch);monkeypatch.setattr(environment,'ROOT',tmp_path)
    assert not relief_status(d)['available']
    broken=copy.deepcopy(d);broken['terrain']['elevation_m'][0][0]=123
    with pytest.raises(ProviderError,match='checksum'):relief_status(broken)

def test_collection_revision_source_scope_and_environment_api(client,monkeypatch):
    d=fixture_data(monkeypatch);p,s=create(client)
    monkeypatch.setattr(ingestion,'collect',lambda *a,**kw:d)
    monkeypatch.setattr(environment,'build_relief',lambda data:{'available':False})
    monkeypatch.setattr(environment,'ROOT',ingestion.DATA_ROOT.parent)
    response=client.post(f'/api/scenarios/{s["id"]}/collect',json={'providers':['environment_screening']})
    assert response.status_code==202,response.text
    job=client.get('/api/data-jobs/'+response.json()['id']).json()
    assert job['status']=='completed',job
    new=client.get('/api/scenarios/'+job['result_scenario_id']).json()
    assert new['scenario']['id']!=s['id'] and 'environment_screening' not in store.get_scenario(s['id'])['inputs']['data_bindings']
    for cid in ['C16','C48','C49','C50']:
        result=new['results'][cid]
        assert result['scenario_id']==new['scenario']['id']
        assert result['data']['record_count']==2 and result['status']=='needs-review'
    assert all(r['status']=='missing' for r in new['results']['C48']['data']['evidence_workspace']['draft']['evidence'])
    did=new['scenario']['inputs']['data_bindings']['environment_screening']
    assert client.get(f'/api/datasets/{did}/environment-relief/terrain-relief.png').status_code==404
    assert client.get(f'/api/datasets/{did}/environment-relief/unlisted.png').status_code==404
    wrong=copy.deepcopy(new['scenario']);wrong['inputs']['screening_point']['lat']+=.1
    with pytest.raises(ProviderError,match='scope'):ingestion.attached_data(wrong)
