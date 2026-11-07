import copy,io,math,csv
from datetime import datetime,timedelta,timezone
import pytest
from backend import overview_data as model,ingestion
from backend.engine import DEFAULT_INPUTS,analyze
from backend.engineering import validate_inputs
from tests.test_ingestion import client,create

@pytest.fixture
def inputs():return {**copy.deepcopy(DEFAULT_INPUTS),'regional_screening_case':model.CASE_DEFAULTS.copy()}

@pytest.fixture
def sources():
    cost={'commissioning_year':2030,'predevelopment_gbp_kw':170,'construction_gbp_kw':2500,'fixed_om_gbp_mw_year':46000,'insurance_gbp_mw_year':8900,'connection_gbp_mw_year':86700,'decommission_gbp_mw':265200,'discount_rate':.089,'variable_om_gbp_mwh':0,'source_column':'N','published_lcoe_gbp_mwh':103}
    start=datetime(2025,1,1,tzinfo=timezone.utc)
    rows=[{'timestamp_utc':(start+timedelta(hours=h)).isoformat(),'speed':10,'direction':0,'height':100} for h in range(8760)]
    return {'overview_inputs':{'data':{'costs':[cost],'curve':[{'speed_ms':3,'power_mw':0},{'speed_ms':10,'power_mw':10},{'speed_ms':25,'power_mw':15}],
             'turbine':{'name':'Test-only reference fixture','turbine_mw':15,'hub_height_m':150,'rotor_diameter_m':240},'curve_type':'synthetic_test_fixture','loss_benchmarks':{'wake_loss':.08,'availability_loss':.041},'limitations':['Synthetic unit-test fixture.']},'meta':{'dataset_id':'fixture-reference','provider_id':'overview_inputs'}},
            'era5_wind':{'data':{'heights':{'100':{'rows':rows},'10':{'rows':[{**r,'speed':8,'height':10} for r in rows]}}},'meta':{'dataset_id':'fixture-wind','provider_id':'era5_wind'}}}

def test_explicit_case_required_and_site_import_preferred(inputs,sources):
    s={'inputs':{**inputs,'regional_screening_case':None}}
    assert model.regional_case(s,sources) is None
    s['inputs']=inputs;inputs['wind_dataset_id']='site-observations'
    assert model.regional_case(s,sources) is None

def test_height_curve_loss_and_monthly_reconciliation(inputs,sources):
    data,provenance,gaps=model.regional_case({'inputs':inputs},sources)
    alpha=math.log(10/8)/math.log(10);power=10+(10*1.5**alpha-10)/3
    gross=power*66*8760;net=gross*.92*.97*.959*.98
    assert data['shear_exponent']==pytest.approx(alpha)
    assert data['gross_aep_mwh']==pytest.approx(gross)
    assert data['net_aep_mwh']==pytest.approx(net)
    assert sum(r['net_mwh'] for r in data['monthly_estimates'])==pytest.approx(net)
    assert gross-sum(r['mwh'] for r in data['losses'])==pytest.approx(net)
    assert data['annual_estimates'][0]['net_aep_mwh']==pytest.approx(net)
    assert [r['net_aep_mwh'] for r in data['energy_sensitivity']]==sorted(r['net_aep_mwh'] for r in data['energy_sensitivity'])
    assert data['data_scope']=='regional_model_only' and len(provenance)==2 and gaps
    assert not {'p90_mwh','npv_gbp','irr','cashflows'}.intersection(data)
    assert data['price_year']==2024

def test_cost_all_operating_components_and_decommissioning(inputs,sources):
    d,*_=model.regional_case({'inputs':inputs},sources)
    assert d['capex_gbp']==2670*990000
    assert d['annual_opex_gbp']==141600*990
    assert d['decommission_gbp']==265200*990
    assert sum(r['value'] for r in d['cost_components_lcoe'])==pytest.approx(d['lcoe_gbp_mwh'])
    assert d['cost_sensitivity'][0]['lcoe_gbp_mwh']>d['cost_sensitivity'][-1]['lcoe_gbp_mwh']

def test_zero_discount_lcoe_independent_arithmetic():
    result,parts=model.lcoe_components(1000,100,2,200,0,2,50)
    assert result==pytest.approx((1000+200+200)/100+2)
    with pytest.raises(ValueError):model.lcoe_components(1000,100,2,200,.1,2,0)

def test_curve_interpolation_and_shutdown():
    curve=[{'speed_ms':3,'power_mw':1},{'speed_ms':10,'power_mw':15},{'speed_ms':25,'power_mw':15}]
    assert model.curve_power(2.99,curve)==0 and model.curve_power(25,curve)==0
    assert model.curve_power(6.5,curve)==8 and model.curve_power(24,curve)==15

@pytest.mark.parametrize('edit',[{'hub_height_m':100},{'turbine_mw':12},{'design_year':2031},{'capex_gbp_per_kw':3000,'price_year':2026}])
def test_incompatible_models_and_price_years_rejected(inputs,sources,edit):
    with pytest.raises(ValueError):model.regional_case({'inputs':{**inputs,**edit}},sources)

def test_short_or_unaligned_wind_rejected(inputs,sources):
    sources['era5_wind']['data']['heights']['10']['rows'].pop()
    with pytest.raises(ValueError,match='aligned'):model.regional_case({'inputs':inputs},sources)

@pytest.mark.parametrize('cfg',[{'enabled':True},{'enabled':1,'electrical_loss':.03,'curtailment_loss':.02},{'enabled':True,'electrical_loss':float('nan'),'curtailment_loss':.02},{'enabled':True,'electrical_loss':True,'curtailment_loss':.02}])
def test_case_validation(cfg):
    with pytest.raises(ValueError):validate_inputs({**copy.deepcopy(DEFAULT_INPUTS),'regional_screening_case':cfg})

def cost_workbook():
    cells={'A1':'Technology','A3':'Reference plant size','A6':'Operating lifetime','A7':'Pre-development Cost','A19':'Construction Cost','A34':'Fixed O&M','A36':'Insurance','A37':'Connection and use of system charges','A38':'Hurdle Rate','A42':'Decommissioning Cost','N1':'Fixed Offshore Wind','B8':'Medium','B20':'Medium','B39':'Medium','B43':'Medium','C3':'MW','C6':'years','C7':'£/kW','C19':'£/kW','C34':'£/MW/year','C35':'£/MWh','C36':'£/MW/year','C37':'£/MW/year','C38':'%','C42':'£/MW'}
    sheets={'Home':{'C25':'All costs are in real 2024 GBP'},'Technical and Cost Assumptions':cells}
    for c,y in zip('NOPQR',[2030,2035,2040,2045,2050]):
        cells.update({c+'2':str(y),c+'3':'1296.7',c+'4':'48%11',c+'6':'30'})
        cells.update({c+str(r):str(v) for r,v in {7:110,8:170,9:240,19:2100,20:2500,21:3100,34:46000,35:0,36:8900,37:86700,38:.073,39:.089,40:.106,43:265200}.items()})
        sheets[f'Additional Estimates {y}']={'E4':'Fixed Offshore Wind5','B15':'£/MWh','E15':'103'}
    return sheets

def test_published_table_units_and_conversion(monkeypatch):
    workbook=cost_workbook();monkeypatch.setattr(model,'workbook_cells',lambda raw:workbook)
    rows=model.parse_costs(b'fixture')
    assert rows[0]['net_load_factor']==.48 and rows[0]['construction_gbp_kw']==2500
    assert rows[0]['fixed_om_gbp_mw_year']==46000 and rows[0]['discount_rate']==.089
    workbook['Technical and Cost Assumptions']['C34']='£/kW/year'
    with pytest.raises(ValueError,match='units'):model.parse_costs(b'fixture')

def test_missing_value_is_not_zero_and_text_is_not_a_number(monkeypatch):
    workbook=cost_workbook();monkeypatch.setattr(model,'workbook_cells',lambda raw:workbook)
    workbook['Technical and Cost Assumptions']['N34']=None
    with pytest.raises(ValueError,match='Missing'):model.parse_costs(b'fixture')

def test_api_preparation_activates_only_new_snapshot(client,monkeypatch,sources):
    p,s=create(client)
    monkeypatch.setattr(ingestion,'collect',lambda pid,*a,**kw:sources[pid]['data'])
    response=client.post(f'/api/scenarios/{s["id"]}/overview/prepare',json={})
    assert response.status_code==202,response.text
    job=client.get('/api/data-jobs/'+response.json()['id']).json()
    assert job['status']=='completed',job
    result=client.get('/api/scenarios/'+job['result_scenario_id']).json()
    assert result['scenario']['inputs']['regional_screening_case']['enabled']
    assert result['scenario']['inputs']['aoi'] is None and result['scenario']['inputs']['wind_dataset_id'] is None
    assert result['results']['C27']['data']['net_aep_mwh']>0
    assert result['results']['C60']['data']['lcoe_gbp_mwh']>0
    assert result['results']['C27']['evidence_maturity']=='published_data_with_modelling_assumptions'
    old=client.get('/api/scenarios/'+s['id']).json()
    assert old['results']=={} and old['scenario']['inputs'].get('regional_screening_case') is None

def test_api_preparation_period_guard(client):
    _,s=create(client)
    assert client.post(f'/api/scenarios/{s["id"]}/overview/prepare',json={'start_date':'2025-01-01','end_date':'2025-01-02'}).status_code==422

def test_preserved_file_download_checks_integrity(client,tmp_path,monkeypatch):
    import backend.app as application
    raw=b'original published source fixture';path=application.DATA_ROOT/'external_raw/test.bin';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    import hashlib
    ds={'data':{'files':{'source.csv':'https://example.com/source.csv'}},'meta':{'raw_assets':[{'url':'https://example.com/source.csv','path':'external_raw/test.bin','sha256':hashlib.sha256(raw).hexdigest(),'content_type':'text/csv'}]}}
    monkeypatch.setattr(ingestion,'get_dataset',lambda did:ds)
    r=client.get('/api/datasets/test/files/source.csv')
    assert r.status_code==200 and r.content==raw
    assert 'source.csv' in r.headers['content-disposition']
    assert client.get('/api/datasets/test/files/missing.csv').status_code==404
    path.write_bytes(b'changed')
    assert client.get('/api/datasets/test/files/source.csv').status_code==422

def test_workbook_reader_uses_cached_values_without_external_execution():
    import zipfile
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        z.writestr('xl/sharedStrings.xml','<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Published value</t></si></sst>')
        z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Table" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr('xl/worksheets/sheet1.xml','<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row><c r="A1" t="s"><v>0</v></c><c r="B1"><f>[External]Sheet!A1</f><v>0</v></c><c r="C1" t="e"><v>#REF!</v></c></row></sheetData></worksheet>')
    cells=model.workbook_cells(stream.getvalue())['Table']
    assert cells=={'A1':'Published value','B1':'0','C1':None}
