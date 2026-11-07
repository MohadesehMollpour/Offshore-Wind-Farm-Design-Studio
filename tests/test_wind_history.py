import copy,hashlib,json
from datetime import date,datetime,timedelta,timezone
import pytest
from backend import wind_history as history,ingestion,references
from backend.engine import DEFAULT_INPUTS,digest
from backend.engineering import validate_inputs,wind_summary
from tests.test_ingestion import client,create
from tests.test_overview_data import sources

@pytest.mark.parametrize('today,start,end',[(date(2026,11,1),'2025-10-01','2026-09-30'),(date(2026,11,15),'2025-11-01','2026-10-31'),(date(2026,1,2),'2024-12-01','2025-11-30')])
def test_recent_twelve_complete_months_respect_publication_lag(today,start,end):
    assert history.recent_complete_year(today)==(start,end)

def rows(values,start='2024-02-01'):
    origin=datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    return [{'timestamp_utc':(origin+timedelta(hours=h)).isoformat(),'speed':v,'height':10,'direction':0} for h,v in enumerate(values)]

def test_quartiles_use_linear_interpolation():
    assert history.quantile([], .5) is None
    assert history.quantile([7], .25)==7
    assert history.quantile([1,2,3,4], .25)==1.75
    assert history.quantile([1,2,3,4], .5)==2.5

def test_iqr_whiskers_outliers_leap_hours_and_missingness():
    sample=rows([1,2,3,4,5,6,7,8,9,100]);original=copy.deepcopy(sample)
    box=history.month_boxes(sample,'2024-02-01','2024-02-29')[0]
    assert box['q1_ms']==3.25 and box['median_ms']==5.5 and box['q3_ms']==7.75
    assert box['whisker_low_ms']==1 and box['whisker_high_ms']==9
    assert box['outliers_ms']==[100] and box['n']==10
    assert box['expected_hours']==696 and box['missing_hours']==686
    assert sample==original and len(box['values_ms'])==10

def test_constant_and_empty_month_are_distinct_from_zero():
    boxes=history.month_boxes(rows([0]*24,start='2025-01-01'),'2025-01-01','2025-02-28')
    assert boxes[0]['median_ms']==0 and boxes[0]['outliers_ms']==[]
    assert boxes[1]['median_ms'] is None and boxes[1]['n']==0 and boxes[1]['missing_hours']==672

def test_height_and_period_sets_keep_source_identity(sources):
    for h in sources['era5_wind']['data']['heights'].values():h['summary']=wind_summary(h['rows'])
    external={'era5_wind':sources['era5_wind'],'operations_wind':{**sources['era5_wind'],'meta':{'dataset_id':'recent-wind','source_name':'Recent test source'}}}
    data,meta=history.boxplot_data({'inputs':{}},{'external':external})
    recent=next(r for r in data['boxplot_sets'] if r['id']=='recent:10')
    assert recent['source_dataset_id']=='recent-wind' and recent['sample_hours']==8760 and recent['missing_hours']==0
    assert data['wind_plot_preferences']['period']=='recent' and data['wind_plot_preferences']['height_m']==10
    assert len({r['id'] for r in data['boxplot_sets']})==len(data['boxplot_sets'])
    assert {p['dataset_id'] for p in meta}=={'fixture-wind','recent-wind'}

def test_imported_height_is_preserved_without_extrapolation():
    sample=rows([5]*24);sample=[{**r,'height':150} for r in sample]
    data,meta=history.boxplot_data({'inputs':{}},{'wind':sample,'wind_meta':{'dataset_id':'imported'}})
    assert {r['height_m'] for r in data['boxplot_sets']}=={150}
    assert data['wind_plot_preferences']['height_m']==150
    assert data['wind_plot_preferences']['threshold_height_m']==10

@pytest.mark.parametrize('change',[{'sailing_limit_ms':-1},{'om_limit_ms':True},{'unit':'mph'},{'height_m':float('nan')},{'period':'../../secret'},{'threshold_basis':''}])
def test_plot_preference_validation(change):
    with pytest.raises(ValueError):validate_inputs({**copy.deepcopy(DEFAULT_INPUTS),'wind_plot_preferences':{**history.PLOT_DEFAULTS,**change}})

def test_refresh_after_plot_save_retains_overview_and_old_snapshot(client,monkeypatch,sources):
    p,s=create(client);wind=sources['era5_wind']['data']
    for entry in wind['heights'].values():entry['summary']=wind_summary(entry['rows'])
    wind.update(grid_point={'lat':54,'lon':2},limitations=['Synthetic test-only wind fixture.'])
    monkeypatch.setattr(ingestion,'collect',lambda pid,*a,**kw:sources['overview_inputs']['data'] if pid=='overview_inputs' else wind)
    initial=client.post(f'/api/scenarios/{s["id"]}/overview/prepare',json={}).json()
    previous=client.get('/api/data-jobs/'+initial['id']).json()['result_scenario_id']
    job=client.post(f'/api/scenarios/{previous}/collect',json={'providers':['operations_wind']}).json()
    sid=client.get('/api/data-jobs/'+job['id']).json()['result_scenario_id']
    before=client.get('/api/scenarios/'+sid).json()
    prefs={**history.PLOT_DEFAULTS,'sailing_limit_ms':11}
    new=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':sid,'inputs':{'wind_plot_preferences':prefs}}).json()
    response=client.post(f'/api/scenarios/{new["id"]}/refresh-evidence',json={})
    assert response.status_code==200,response.text
    result=response.json()['results']
    assert result['C07']['data']['wind_plot_preferences']['sailing_limit_ms']==11
    assert result['C07']['data']['boxplot_sets']
    assert result['C27']['data']['net_aep_mwh']==before['results']['C27']['data']['net_aep_mwh']
    assert result['C60']['data']['lcoe_gbp_mwh']==before['results']['C60']['data']['lcoe_gbp_mwh']
    assert client.get('/api/scenarios/'+sid).json()['scenario']['inputs'].get('wind_plot_preferences') is None

def reference_fixture():
    return {'farms':[{'id':'test','name':'Fixture','status':'operating','zone':'hornsea','lat':54,'lon':2,'mw':100,'cf12':None,'cflife':40,'path':'M0,0L1,1Z'}],'mapOnly':[],'map':{'land':'M0,0L1,1Z'}}

@pytest.mark.parametrize('change',[{'path':'<script>alert(1)</script>'},{'cf12':101},{'lat':999},{'mw':float('nan')}])
def test_reference_numeric_and_svg_validation(change):
    data=reference_fixture();data['farms'][0].update(change)
    with pytest.raises(ValueError):references.validate_farms(data)

def test_reference_api_keeps_page_as_download_and_checks_original(client,tmp_path,monkeypatch):
    path=tmp_path/'reference';path.mkdir();monkeypatch.setattr(references,'REFERENCE_DIR',path)
    original=b'<html><script>not executed by importer or API</script></html>'
    (path/'original.html').write_bytes(original);data=reference_fixture()
    record={'data':data,'metadata':{'data_sha256':digest(data),'original_filename':'original.html','original_sha256':hashlib.sha256(original).hexdigest(),'verification':'User supplied; unverified'}}
    (path/'reference.json').write_text(json.dumps(record),encoding='utf-8')
    response=client.get('/api/references/hornsea-farms');assert response.status_code==200
    assert response.json()['data']['farms'][0]['cf12'] is None
    r=client.get('/api/references/hornsea-farms/original')
    assert r.status_code==200 and r.content==original and 'attachment' in r.headers['content-disposition']
    assert r.headers['content-type']=='application/octet-stream'
    (path/'original.html').write_bytes(b'changed')
    assert client.get('/api/references/hornsea-farms/original').status_code==422
