"""Refresh machine-readable chart bindings and meaningful agent ownership tests."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
bindings={
 'C01':[['data.geojson'],['data.area_km2','data.boundary_vertices','data.geometry_valid']],
 'C07':[['data.series'],['data.mean_speed_ms','data.hub_height_m']],
 'C08':[['data.sectors','data.calm_pct'],['data.sectors[*].speed_bins_pct','data.directional_proxy_energy']],
 'C20':[[],['data.turbine_name','data.turbine_mw','data.rotor_diameter_m','data.hub_height_m']],
 'C21':[['data.curve'],['data.energy_bins']],
 'C23':[['data.turbines','scenario.inputs.aoi'],['data.nearest_spacing_m']],
 'C26':[['data.per_turbine_mwh'],['data.gross_aep_mwh']],
 'C27':[['data.gross_aep_mwh','data.net_aep_mwh'],['data.losses']],
 'C28':[['data.p50_mwh','data.p75_mwh','data.p90_mwh'],['scenario.inputs.uncertainty_fraction']],
 'C58':[['data.total_capex_gbp'],[]], 'C59':[['data.annual_opex_gbp'],[]],
 'C60':[['data.lcoe_gbp_mwh','data.npv_gbp','data.irr'],['data.cashflows']],
 'C61':[['data.sensitivity'],['data.cashflows']],
 'C67':[['data.succeeded','data.needs_review','data.not_run'],['data.checks']],
 'C69':[['catalog.categories','results'],['results']],
}
cats=json.loads((ROOT/'config/categories.json').read_text(encoding='utf-8'))
for c in cats:
    b=bindings.get(c['id'],[[],[]])
    config={'category_id':c['id'],'contract_version':'0.1.0','charts':[{'id':f'{c["id"]}-{k+1}','required_title':title,'data_paths':b[k],'status':'preliminary_data_bound' if b[k] else 'missing_data_or_method','empty_state':'Display required missing input and acquisition action; never substitute invented values.','note':'The first release may use preliminary bars/tables in place of the final specialist visualization; see docs/STATUS.md.'} for k,title in enumerate(c['charts'])]}
    (ROOT/'categories'/c['id']/'CHARTS.yaml').write_text(json.dumps(config,indent=2),encoding='utf-8')
for a in json.loads((ROOT/'config/agents.json').read_text(encoding='utf-8')):
    code=f'''from backend.catalog import load,BY_ID
def test_ownership_contract():
    agent=next(a for a in load('agents') if a['id']=={a['id']!r})
    assert agent['instructions'].strip()
    assert agent['categories']
    for cid in agent['categories']:
        assert agent['id'] in BY_ID[cid]['owners']
'''
    (ROOT/a['folder']/'tests/test_contract.py').write_text(code,encoding='utf-8')
print('Updated chart bindings and agent ownership contracts')
