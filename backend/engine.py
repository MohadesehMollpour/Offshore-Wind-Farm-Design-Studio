from datetime import datetime,timezone
import hashlib,json,uuid
from .catalog import BY_ID,CATEGORIES,load
from .engineering import geometry,layout,wind_summary,power,energy,finance

VERSION='0.2.0'
def now():return datetime.now(timezone.utc).isoformat()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

DEFAULT_INPUTS={'capacity_mw':990,'turbine_mw':15,'turbine_name':'User-defined 15 MW proxy','rotor_diameter_m':240,'hub_height_m':150,'spacing_d':7,'cross_spacing_d':7,'rotation_deg':0,'seed':42,'aoi':None,'exclusions':[],'geometry_source':'','geometry_license':'','geometry_reviewed':False,'wind_dataset_id':None,'cut_in_ms':3,'rated_speed_ms':12,'cut_out_ms':25,'wake_loss':None,'electrical_loss':None,'availability_loss':None,'curtailment_loss':None,'uncertainty_fraction':None,'capex_gbp_per_kw':None,'opex_gbp_per_kw_year':None,'decommission_gbp':None,'discount_rate':None,'lifetime_years':30,'power_price_gbp_mwh':None,'price_year':2026,'design_year':2030,'currency':'GBP','assumption_note':'Turbine parameters and 990 MW capacity are editable planning assumptions, not a selected manufacturer or approved project.','site_name':'','jurisdiction':'','contributions':[]}
DEFAULT_INPUTS.update(screening_point=None,data_bindings={})

ENERGY_FIELDS=['wake_loss','electrical_loss','availability_loss','curtailment_loss','uncertainty_fraction']
FINANCE_FIELDS=['capex_gbp_per_kw','opex_gbp_per_kw_year','decommission_gbp','discount_rate','power_price_gbp_mwh']
def missing(i,keys):return [f'Supply {k}' for k in keys if i.get(k) is None]
def disclosure_complete(i):
    topics={t['name'] for t in load('assessment')['topics']};rows=i.get('contributions',[])
    return len(rows)==16 and {r.get('section') for r in rows}==topics and all(all(str(r.get(k,'')).strip() for k in ['human_lead','ai_tools','contribution']) and r.get('reviewed') is True for r in rows)

def analyze(cid,s,context):
    cat=BY_ID[cid];i=s['inputs'];rows=context.get('wind')
    external=context.get('external',{});regional_wind=False
    wind_provider='operations_wind' if cid=='C07' and 'operations_wind' in external else 'era5_wind'
    if not rows and cid in ['C07','C08','C09'] and wind_provider in external:
        rows=external[wind_provider]['data']['heights']['100']['rows'];regional_wind=True
    result={'category_id':cid,'scenario_id':s['id'],'project_id':s['project_id'],'site_id':s['site_id'],'layout_id':s['layout_id'],'site_revision':s['revision'],'layout_revision':s['revision'],'scenario_revision':s['revision'],'scenario_hash':s['hash'],'method_version':VERSION,'prompt_version':'0.1.0','spec_version':'0.1.0','run_id':str(uuid.uuid4()),'run_time':now(),'status':'needs-review','evidence_maturity':'unavailable','gaps':[],'data':{},'provenance':[],'interpretation':'','limitations':[],'owners':cat['owners']}
    data={};gaps=[];external_view=None
    if rows:result['provenance'].append(external[wind_provider]['meta'] if regional_wind else context['wind_meta'])
    try:
        from .external_analysis import analyze_external
        if cid=='C61':
            from .sensitivity import analyze_sensitivity
            external_view=analyze_sensitivity(s,context)
        else:external_view=analyze_external(cid,s,external,context)
        from .work_packages import DEFINITIONS,package
        if not external_view and cid in DEFINITIONS and not (cid=='C28' and context.get('wind')):external_view=package(cid,s,context)
        if external_view:
            data,provenance,gaps=external_view;result['provenance']=provenance
        elif cid in ['C03','C04','C05','C56']:
            gaps=['Collect '+('Historical accessibility metocean' if cid=='C56' else 'Regional site screening')+' under Data sources & APIs for this exact region/AOI and reference point. Previously collected data from another region cannot be substituted.']
        elif cid=='C01':
            if not i.get('aoi'):gaps=['Draw or import an EPSG:4326 AOI polygon. Regional presets do not provide lease boundaries.']
            else:
                p,projected,_,_=geometry(i['aoi']);data={'area_km2':projected.area/1e6,'centroid_lon':p.centroid.x,'centroid_lat':p.centroid.y,'boundary_vertices':len(p.exterior.coords)-1,'geojson':i['aoi'],'geometry_valid':True,'geometry_reviewed':i['geometry_reviewed'],'legal_rights_verified':False}
                result['provenance'].append({'source':i.get('geometry_source') or 'User-drawn AOI','license':i.get('geometry_license') or 'Unspecified','verification':'not_independently_verified'})
                gaps=['Obtain authoritative lease/consent and marine constraint layers; polygon validity does not establish development rights.']
        elif cid in ['C07','C08']:
            if not rows:gaps=['Import a site-scoped hourly wind CSV with UTC timestamps, wind speed, wind FROM direction, hub height and source metadata.']
            else:
                data=wind_summary(rows)
                if cid=='C08':
                    directional=[0.0]*16
                    for row in rows:
                        if row['speed']>=.5:directional[int((row['direction']+11.25)%360/22.5)]+=power(row['speed'],i)
                    total=sum(directional)
                    data['directional_proxy_energy']=[{'direction_deg':k*22.5,'energy_share_pct':100*v/total if total else 0} for k,v in enumerate(directional)]
                    data['energy_method']='Relative energy shares use the user-defined cubic power proxy at the imported sample height. No wake model or manufacturer certification.'
                    if rows[0]['height']!=i['hub_height_m']:
                        data.pop('directional_proxy_energy');data['energy_method']='Energy contribution unavailable: sample height differs from turbine hub height.'
                if cid=='C07':data['series']=[{'time':r['timestamp_utc'],'speed_ms':r['speed']} for r in rows[::max(1,len(rows)//400)]]
                if len(rows)<8760:gaps=['Less than one year of data: directional statistics describe only this sample, not long-term resource.']
                if regional_wind:
                    source=external[wind_provider];data['reference_point']=i.get('screening_point');data['grid_point']=source['data']['grid_point'];data['data_scope']=source['meta']['spatial_scope'];data['measurement_type']='reanalysis';data['height_profile']=[{'height_m':int(h),'mean_speed_ms':v['summary']['mean_speed_ms']} for h,v in source['data']['heights'].items()]
                    gaps+=source['data']['limitations']
                if cid=='C07':
                    from .wind_history import boxplot_data
                    boxes,metas=boxplot_data(s,context);data.update(boxes)
                    known={p.get('dataset_id') for p in result['provenance']}
                    result['provenance'] += [p for p in metas if p['dataset_id'] not in known]
                    gaps+=boxes.get('threshold_limitations',[])
        elif cid=='C09' and regional_wind:
            monthly={};hourly={}
            for r in rows:
                month=r['timestamp_utc'][:7];hour=int(r['timestamp_utc'][11:13]);monthly.setdefault(month,[]).append(r['speed']);hourly.setdefault(hour,[]).append(r['speed'])
            data={'monthly_mean_ms':[{'month':k,'value':sum(v)/len(v)} for k,v in monthly.items()],'hourly_mean_ms':[{'hour_utc':k,'value':sum(v)/len(v)} for k,v in sorted(hourly.items())],'reference_point':i.get('screening_point'),'data_scope':external['era5_wind']['meta']['spatial_scope'],'hub_height_m':100}
            gaps=['Regional 100 m reanalysis seasonal/diurnal summaries. No return-period or turbine design-extreme inference from this sample.']
        elif cid=='C20':
            data={k:i[k] for k in ['turbine_name','turbine_mw','rotor_diameter_m','hub_height_m']};gaps=['Only a user-defined turbine is configured; import verified manufacturer specifications and alternative turbines.']
        elif cid=='C21':
            data={'curve':[{'speed_ms':v/2,'power_mw':power(v/2,i)} for v in range(0,71)],'curve_type':'assumed_cubic_proxy','rated_mw':i['turbine_mw']}
            if rows:
                data['energy_bins']=[{'speed_ms':v,'sample_power_mwh':sum(power(r['speed'],i) for r in rows if v<=r['speed']<v+1)} for v in range(35)]
            gaps=['Replace cubic proxy with a certified or explicitly justified turbine power curve before making a design claim.']
        elif cid=='C23':
            data=layout(i,s['layout_id'],rows);gaps=['Marine rights, complete exclusion layers, seabed and permitting need independent review.']
        elif cid in ['C26','C27','C28']:
            gaps=missing(i,ENERGY_FIELDS) if cid!='C26' else []
            if not rows:gaps+=['Import hourly wind observations for this AOI and hub height.']
            if not i.get('aoi'):gaps+=['Define the AOI and generate a feasible turbine layout.']
            if not gaps:
                layout(i,s['layout_id'],rows)
                if cid=='C26':
                    ei={**i,**{f:0 for f in ENERGY_FIELDS}};allenergy=energy(ei,rows);data={'gross_aep_mwh':allenergy['gross_aep_mwh'],'reporting_hours':allenergy['reporting_hours'],'per_turbine_mwh':allenergy['gross_aep_mwh']/round(i['capacity_mw']/i['turbine_mw']),'method':allenergy['method']}
                else:data=energy(i,rows)
                gaps=['Annualized exploratory proxy. Long-term correction, measured performance and validated wake modelling are required.']
        elif cid in ['C58','C59']:
            fields=['capex_gbp_per_kw'] if cid=='C58' else ['opex_gbp_per_kw_year','decommission_gbp']
            gaps=missing(i,fields)
            if not gaps:
                data={'capacity_mw':i['capacity_mw'],'price_year':i['price_year'],'currency':'GBP',**{f:i[f] for f in fields}}
                data['total_capex_gbp' if cid=='C58' else 'annual_opex_gbp']=i[fields[0]]*i['capacity_mw']*1000
                gaps=['User assumptions are not supplier quotes; itemized cost breakdown and financing terms remain missing.']
        elif cid in ['C60','C61']:
            gaps=missing(i,ENERGY_FIELDS+FINANCE_FIELDS)
            if not rows:gaps+=['Import site-scoped wind observations.']
            if not i.get('aoi'):gaps+=['Supply AOI and feasible layout.']
            if not gaps:
                layout(i,s['layout_id'],rows);en=energy(i,rows);data=finance(i,en['net_aep_mwh']);data['energy']=en
                if cid=='C61':
                    sens=[]
                    for field in ['capex_gbp_per_kw','opex_gbp_per_kw_year','discount_rate','power_price_gbp_mwh']:
                        low=finance({**i,field:i[field]*.8},en['net_aep_mwh']);high=finance({**i,field:i[field]*1.2},en['net_aep_mwh'])
                        sens.append({'parameter':field,'low_npv_gbp':low['npv_gbp'],'high_npv_gbp':high['npv_gbp']})
                    data['sensitivity']=sens
                gaps=['Preliminary assumption case; independent energy, costs, grid, permits and human review remain necessary.']
        elif cid=='C67':
            results=context.get('results',{})
            data={'succeeded':sum(r['status']=='succeeded' for r in results.values()),'needs_review':sum(r['status']=='needs-review' for r in results.values()),'not_run':70-len(results),'checks':[{'name':'All 70 categories evaluated','passed':len(results)==70},{'name':'AOI supplied','passed':bool(i.get('aoi'))},{'name':'Wind dataset supplied','passed':bool(rows)},{'name':'Financial assumptions complete','passed':not missing(i,FINANCE_FIELDS)},{'name':'Human section contributions declared and reviewed','passed':disclosure_complete(i)}]};gaps=['Unresolved evidence and domain checks prevent investment approval.']
        elif cid=='C68':
            data={'sections':i.get('contributions',[]),'required_topics':load('assessment')['topics'],'ai_disclosure':load('assessment')['ai_disclosure']};gaps=['Complete the human lead, AI tools, contribution and review record for every section.'] if not disclosure_complete(i) else []
        elif cid=='C69':
            data={'nodes':[{'id':c['id'],'title':c['title'],'domain':c['domain'],'status':context.get('results',{}).get(c['id'],{}).get('status','not_run')} for c in CATEGORIES],'edges':[{'source':dep,'target':c['id'],'type':'engineering_dependency','confidence':'documented_model_structure','causal_estimate':False} for c in CATEGORIES for dep in c['dependencies']]};gaps=['Graph edges show model dependencies, not quantified causal effects or validated importance weights.']
        elif cid=='C70':
            data={'topics':load('assessment')['topics'],'completed_packages':len(context.get('results',{})),'total_packages':70,'report_status':'draft_only'};gaps=['Investor approval and evidence-backed technical annexes are incomplete. Draft exports remain available.']
        else:gaps=[f'Required: {x}' for x in cat['inputs']]+['Domain-specific transformation and provider adapter are not yet implemented.']
    except (ValueError,KeyError,TypeError) as e:gaps=[str(e)]
    result['data']=data;result['gaps']=gaps
    result['status']='succeeded' if data and not gaps else 'needs-review'
    result['evidence_maturity']='user_supplied_or_assumed' if data else 'unavailable'
    if data and (regional_wind or external_view):
        from .ingestion import dataset_status
        result['evidence_maturity']='publisher_api_screening'
        if any(dataset_status(p)=='stale' for p in result['provenance'] if p.get('provider_id')):
            result['evidence_maturity']='stale_publisher_data';result['gaps'].insert(0,'STALE: refresh the source before using this result for a current decision.')
    synthetic=data and (context.get('wind_meta',{}).get('measurement_type')=='synthetic_demo_only' or any(isinstance(p,dict) and p.get('measurement_type')=='synthetic_demo_only' for p in result['provenance']))
    if data.get('estimate_type')=='regional_reference_estimate' and result['evidence_maturity']!='stale_publisher_data':result['evidence_maturity']='published_data_with_modelling_assumptions'
    if data.get('work_package') and result['evidence_maturity']!='stale_publisher_data':result['evidence_maturity']='source_and_planning_assumptions' if result['provenance'] else 'planning_workspace_not_verified'
    if synthetic:result['evidence_maturity']='synthetic_demo_only'  # Applied last: no later rule may upgrade synthetic demo evidence.
    result['limitations']=['Local preliminary assessment. Provider-backed screening is separate from autonomous LLM execution.','Neither model completion nor a valid polygon establishes engineering, regulatory or investment approval.']
    result['interpretation']=(f'{cat["title"]} is scoped to {s["site_id"]}, {s["layout_id"]}, revision {s["revision"]}. '+('The calculation uses the selected inputs and the source records shown below. Values describe a preliminary planning case. ' if data else 'No quantitative result is available because required evidence or the specialist computation is missing. ')+(' '.join(gaps))+ ' '+ 'A change in the AOI, turbine parameters, observation period or assumptions creates a new snapshot. Earlier results remain in their original snapshot and cannot be used as current conclusions. Inspect the input units, provenance and method before comparing alternatives. Consider independent measurements, authoritative spatial layers and a technical review to resolve the stated gaps. The required visualizations are specified below; a chart remains empty when its underlying data is unavailable. A high result in one category cannot override an exclusion, missing legal right or unresolved engineering constraint elsewhere.')
    return result
