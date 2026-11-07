import copy,math
import pytest
from backend import store
from backend.engine import DEFAULT_INPUTS,analyze
from backend.work_packages import DEFINITIONS,defaults,validate_work_inputs,package,schedule
from backend.sensitivity import cash_case,analyze_sensitivity
from tests.test_overview_data import sources
from tests.test_ingestion import client,create

def scenario(cid=None,settings=None):
    i=copy.deepcopy(DEFAULT_INPUTS)
    if cid:
        d=defaults(cid);d['settings'].update(settings or {});i['category_inputs']={cid:d}
    return {'id':'test-scenario','hash':'test-hash','project_id':'test-project','site_id':'SITE_01','layout_id':'LAYOUT_01','revision':1,'inputs':i}

def test_definitions_validate_and_do_not_invent_evidence():
    for cid in DEFINITIONS:
        d=defaults(cid);validate_work_inputs({cid:d})
        assert all(r['status']=='missing' and not r['source'] for r in d['evidence'])
    assert all(r['likelihood'] is None and r['severity'] is None for r in defaults('C62')['risks'])

@pytest.mark.parametrize('mutation',[
 lambda d:d['settings'].update(price=float('nan')),
 lambda d:d['settings'].update(unknown=1),
 lambda d:d['settings'].update(variation_pct=None),
 lambda d:d['evidence'][0].update(status='reviewed'),
 lambda d:d.update(unknown='field'),
 lambda d:d['settings'].update(delay_years=1.5)])
def test_invalid_drafts_rejected(mutation):
    d=defaults('C61');mutation(d)
    with pytest.raises(ValueError):validate_work_inputs({'C61':d})

def test_unknown_review_source_and_owner_guards():
    d=defaults('C62');d['risks'][0].update(status='reviewed',likelihood=2,severity=5)
    with pytest.raises(ValueError,match='controls'):validate_work_inputs({'C62':d})
    d['risks'][0].update(controls='User-assessed controls',owner='Responsible reviewer',evidence='User test record')
    validate_work_inputs({'C62':d});d['risks'][0]['likelihood']=True
    with pytest.raises(ValueError):validate_work_inputs({'C62':d})

def test_risk_scores_are_explicit_ordinal_assessments():
    s=scenario('C62');row=s['inputs']['category_inputs']['C62']['risks'][0]
    before=package('C62',s,{'external':{}})[0]['work_package'];assert all(r['score'] is None for r in before['risks'])
    row.update(likelihood=4,severity=5,residual_likelihood=2,residual_severity=5)
    wp=package('C62',s,{'external':{}})[0]['work_package']
    assert wp['risks'][0]['score']==20 and wp['risks'][0]['residual_score']==10
    assert wp['risks'][0]['status']=='unassessed' # A score never auto-approves controls.

def test_critical_path_parallel_tasks_float_and_cycle():
    rows,finish=schedule(defaults('C65')['tasks']);by={t['id']:t for t in rows}
    assert finish==81 and by['grid']['float_months']==12 and not by['grid']['critical']
    assert by['consent']['critical'] and by['procurement']['start_month']==36
    d=defaults('C65');d['tasks'][0]['depends_on']=['commissioning']
    with pytest.raises(ValueError,match='cycle'):validate_work_inputs({'C65':d})

def test_captured_price_changes_npv_not_lcoe_and_delay_cost():
    args={'capex':1000,'fixed':10,'variable':2,'decommission':100,'rate':.06,'life':20,'net':10}
    low=cash_case(**args,price=10);high=cash_case(**args,price=20);delayed=cash_case(**args,price=20,delay=2)
    assert low['lcoe_gbp_mwh']==high['lcoe_gbp_mwh'] and high['npv_gbp']>low['npv_gbp']
    assert delayed['lcoe_gbp_mwh']>high['lcoe_gbp_mwh'] and delayed['npv_gbp']<high['npv_gbp']
    assert cash_case(**args)['npv_gbp'] is None

def test_c61_uses_regional_basis_and_all_named_sensitivities(sources):
    s=scenario('C61',{'price':100});s['inputs']['regional_screening_case']={'enabled':True,'electrical_loss':.03,'curtailment_loss':.02};ctx={'external':sources,'results':{}}
    d,_,_=analyze_sensitivity(s,ctx);f=d['work_package']['financial']
    assert {r['parameter'] for r in f['sensitivity']}=={'capex','fixed','rate','wake_loss','delay','price'}
    assert f['price_year']==2024 and len(f['heatmap'])==25
    price=next(r for r in f['sensitivity'] if r['parameter']=='price')
    assert price['low']['lcoe_gbp_mwh']==price['high']['lcoe_gbp_mwh']
    wake=next(r for r in f['sensitivity'] if r['parameter']=='wake_loss')
    assert wake['low']['lcoe_gbp_mwh']<wake['high']['lcoe_gbp_mwh'] and wake['unit']=='fraction'
    s['inputs']['category_inputs']['C61']['settings']['price']=None
    f=analyze_sensitivity(s,{'external':sources,'results':{}})[0]['work_package']['financial']
    assert f['captured_price'] is None and f['heatmap']==[] and f['base']['npv_gbp'] is None

def test_incompatible_turbine_keeps_a_useful_workspace_and_does_not_poison_cache(sources):
    from backend.work_packages import regional_model
    s=scenario('C61');s['inputs'].update(turbine_mw=18,capacity_mw=990,regional_screening_case={'enabled':True,'electrical_loss':.03,'curtailment_loss':.02});ctx={'external':sources,'results':{}}
    data,_,gaps=analyze_sensitivity(s,ctx)
    assert data['work_package']['kind']=='financial_sensitivity' and any('matching curve' in g for g in gaps)
    assert 'financial' not in data['work_package']
    with pytest.raises(ValueError,match='matching curve'):regional_model(s,ctx)

def test_staffing_workload_and_renewal_availability():
    wp=package('C63',scenario('C63'),{'external':{}})[0]['work_package'];metrics={m['name']:m['value'] for m in wp['metrics']}
    assert metrics['Direct maintenance labour']==66*4*8*2
    assert metrics['Rounded direct-task headcount']==math.ceil(66*4*8*2/(1600*.7))
    wp=package('C55',scenario('C55'),{'external':{}})[0]['work_package']
    assert wp['metrics'][0]['value']==pytest.approx(100*2000/(2000+48+24))

def test_preview_is_not_persisted_and_saved_revision_preserves_parent(client):
    p,s=create(client);d=defaults('C62');d['risks'][0].update(likelihood=3,severity=4)
    r=client.post(f'/api/scenarios/{s["id"]}/categories/C62/preview',json={'draft':d})
    assert r.status_code==200,r.text
    assert r.json()['draft'] and r.json()['data']['work_package']['risks'][0]['score']==12
    assert store.get_results(s['id'])=={} and 'category_inputs' not in store.get_scenario(s['id'])['inputs']
    saved=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'inputs':{'category_inputs':{'C62':d}}}).json()
    r=client.post(f'/api/scenarios/{saved["id"]}/categories/C62/run',json={}).json()
    assert r['scenario_id']==saved['id'] and r['data']['work_package']['risks'][0]['score']==12
    assert 'category_inputs' not in store.get_scenario(s['id'])['inputs']
    audit=client.get(f'/api/scenarios/{saved["id"]}/readiness').json()
    assert audit['total']==70 and audit['evaluated']==1
    assert next(x for x in audit['items'] if x['id']=='C62')['kind']=='risk_register'

def test_preview_and_model_resolve_selected_farm_and_layout(client):
    p,s=create(client);alt=client.post(f'/api/projects/{p["id"]}/scenarios',json={'parent_id':s['id'],'site_id':'SITE_02','layout_id':'LAYOUT_02','inputs':{'capacity_mw':150}}).json()
    a=client.post(f'/api/scenarios/{s["id"]}/farm-preview',json={}).json();b=client.post(f'/api/scenarios/{alt["id"]}/farm-preview',json={}).json()
    assert b['site_id']=='SITE_02' and b['site_name']=='Dogger Bank' and b['layout_name']=='Staggered / offset rows'
    assert b['scenario_id']==alt['id'] and b['scenario_hash']==alt['hash'] and b['count']==10
    assert a['turbines']!=b['turbines'] and b['reference_point'] is None

def test_all_categories_have_specific_analysis_or_acquisition_workflow(sources):
    from backend.catalog import CATEGORIES
    from backend.engine import now
    for entry in sources.values():entry['meta'].update(checked_at=now(),refresh_hours=720,stale=False)
    s=scenario();s['inputs']['regional_screening_case']={'enabled':True,'electrical_loss':.03,'curtailment_loss':.02};ctx={'external':sources,'results':{}}
    for c in CATEGORIES:
        r=analyze(c['id'],s,ctx);ctx['results'][c['id']]=r
        assert not any('not yet implemented' in g for g in r['gaps']),(c['id'],r['gaps'])
        assert r['data'] or r['gaps']
