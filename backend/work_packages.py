"""Editable planning work packages. Evidence registers never establish approval."""
import copy,math,re
from collections import Counter,defaultdict
from .catalog import load,BY_ID
from .engineering import finite

DEFINITIONS=load('work_packages')
STATUSES=['missing','requested','received','reviewed']

def defaults(cid):
    d=DEFINITIONS[cid]
    return {'settings':{f['key']:f['default'] for f in d['settings']},'evidence':copy.deepcopy(d['requirements']),'notes':'',**{key:copy.deepcopy(d[key]) for key in ['risks','tasks','stakeholders'] if key in d}}

def validate_work_inputs(all_inputs):
    if not isinstance(all_inputs,dict) or any(cid not in DEFINITIONS for cid in all_inputs):raise ValueError('Unknown category work package')
    for cid,draft in all_inputs.items():
        template=defaults(cid)
        if not isinstance(draft,dict) or set(draft)!=set(template):raise ValueError(f'{cid}: use the declared settings, evidence and register fields')
        if not isinstance(draft['settings'],dict) or set(draft['settings'])!=set(template['settings']):raise ValueError(f'{cid}: unknown or missing setting')
        for f in DEFINITIONS[cid]['settings']:
            value=draft['settings'][f['key']]
            if value is None and f['default'] is not None:raise ValueError(f['label']+' is required for this calculation')
            if value is not None:
                if isinstance(value,bool):raise ValueError('Planning settings must be numeric')
                draft['settings'][f['key']]=finite(value,f['label'],f['min'],f['max'])
                if f['step']==1 and f['unit'] in ['turbines','units','circuits','people','whole years'] and value!=int(float(value)):raise ValueError(f['label']+' must be an integer')
        if not isinstance(draft['notes'],str) or len(draft['notes'])>10000:raise ValueError('Notes must be text of at most 10000 characters')
        for key in ['evidence','risks','tasks','stakeholders']:
            if key not in template:continue
            rows=draft[key]
            if not isinstance(rows,list) or len(rows)>200:raise ValueError('Registers are limited to 200 rows')
            expected=set(template[key][0]);ids=[]
            for row in rows:
                if not isinstance(row,dict) or set(row)!=expected:raise ValueError(f'{cid}: invalid {key} row fields')
                if not isinstance(row['id'],str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',row['id']):raise ValueError('Use short alphanumeric register identifiers')
                ids.append(row['id'])
                for field,value in row.items():
                    if field in ['likelihood','severity','residual_likelihood','residual_severity','influence','interest']:
                        if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float)) or not 1<=value<=5 or int(value)!=value):raise ValueError('Ordinal scores must be integers 1–5 or unassessed')
                    elif field=='duration_months':
                        if isinstance(value,bool):raise ValueError('Task duration must be numeric')
                        row[field]=finite(value,'task duration',0,360)
                    elif field=='depends_on':
                        if not isinstance(value,list) or any(not isinstance(v,str) for v in value) or len(set(value))!=len(value):raise ValueError('Task predecessors must be unique identifiers')
                    elif not isinstance(value,str) or len(value)>2000:raise ValueError('Register text is limited to 2000 characters')
                if key=='evidence' and (row['status'] not in STATUSES or row['status'] in ['received','reviewed'] and not row['source'].strip()):raise ValueError('Received/reviewed evidence requires a source reference')
                if key=='evidence' and row['status']=='reviewed' and not row['owner'].strip():raise ValueError('Reviewed evidence requires an owner')
                if key=='risks' and row['status'] not in ['unassessed','open','controls_proposed','reviewed']:raise ValueError('Unknown risk review state')
                if key=='risks' and row['status']=='reviewed' and (not row['evidence'].strip() or not row['owner'].strip() or not row['controls'].strip() or row['likelihood'] is None or row['severity'] is None):raise ValueError('Reviewed risks require initial scores, controls, an owner and evidence')
                if key=='stakeholders' and row['status'] not in ['not_contacted','planned','engaged','reviewed']:raise ValueError('Unknown engagement state')
                if key=='stakeholders' and row['status'] in ['engaged','reviewed'] and not row['evidence'].strip():raise ValueError('Engagement requires a user-supplied record')
            if len(ids)!=len(set(ids)):raise ValueError('Register identifiers must be unique')
            if key=='evidence' and set(ids)!={r['id'] for r in template[key]}:raise ValueError('Keep all required evidence rows')
        if 'tasks' in draft:schedule(draft['tasks'])
    return all_inputs

def settings_for(s,cid):return {**defaults(cid)['settings'],**s['inputs'].get('category_inputs',{}).get(cid,{}).get('settings',{})}

def regional_model(s,ctx):
    key=(s['id'],s['hash'])
    if ctx.get('_regional_model_key')!=key:
        from .overview_data import regional_case
        calculated=regional_case(s,ctx.get('external',{}));ctx['_regional_model']=calculated;ctx['_regional_model_key']=key
    result=ctx['_regional_model']
    return (copy.deepcopy(result[0]),list(result[1]),list(result[2])) if result else None

def schedule(tasks):
    byid={t['id']:t for t in tasks};ordered=[];visited=set();active=set()
    def visit(key):
        if key not in byid:raise ValueError('Unknown programme predecessor: '+key)
        if key in active:raise ValueError('Programme dependencies contain a cycle')
        if key in visited:return
        active.add(key)
        for dep in byid[key]['depends_on']:visit(dep)
        active.remove(key);visited.add(key);ordered.append(key)
    for key in byid:visit(key)
    out={}
    for key in ordered:
        t=byid[key];start=max((out[d]['finish_month'] for d in t['depends_on']),default=0);out[key]={**t,'start_month':start,'finish_month':start+t['duration_months']}
    finish=max((t['finish_month'] for t in out.values()),default=0)
    for key in reversed(ordered):
        successors=[t for t in out.values() if key in t['depends_on']];latest=min((t['latest_start'] for t in successors),default=finish);out[key]['latest_start']=latest-out[key]['duration_months'];out[key]['float_months']=out[key]['latest_start']-out[key]['start_month'];out[key]['critical']=abs(out[key]['float_months'])<1e-8
    return list(out.values()),finish

def package(cid,s,ctx):
    d=DEFINITIONS[cid];draft=copy.deepcopy(s['inputs'].get('category_inputs',{}).get(cid,defaults(cid)));cfg=draft['settings'];ex=ctx.get('external',{});i=s['inputs'];n=round(i['capacity_mw']/i['turbine_mw'])
    wp={'kind':d['kind'],'definition':d,'draft':draft,'metrics':[],'series':[],'method':'A structured evidence and review register for the selected snapshot. Missing inputs remain missing.','sources':d.get('sources',[]),'assumptions':[{'name':f['label'],'value':cfg[f['key']],'unit':f['unit'],'basis':f['basis']} for f in d['settings']]}
    provenance=[];gaps=[]
    def metric(name,value,unit):wp['metrics'].append({'name':name,'value':value,'unit':unit})
    def series(title,items,unit='',kind='bars'):wp['series'].append({'title':title,'items':items,'unit':unit,'kind':kind})
    def source(pid):
        entry=ex.get(pid)
        if entry and entry['meta'] not in provenance:provenance.append(entry['meta'])
        return entry['data'] if entry else None
    def base():
        try:regional=regional_model(s,ctx)
        except ValueError as error:gaps.append(str(error));return None
        if regional:
            for meta in regional[1]:
                if meta not in provenance:provenance.append(meta)
            return regional[0]
        result=ctx.get('results',{}).get('C27',{}).get('data',{})
        return result if result.get('net_aep_mwh') is not None else None
    wind=ex.get('era5_wind',{}).get('data',{}).get('heights',{});joint=ex.get('access_metocean',{}).get('data')
    if cid in ['C10','C11','C12']:
        rows=wind.get('100',{}).get('rows') or ctx.get('wind',[])
        if rows:
            if wind:source('era5_wind')
            elif ctx.get('wind_meta'):provenance.append(ctx['wind_meta'])
            speeds=[r['speed'] for r in rows];positive=[v for v in speeds if v>0]
            if cid=='C10' and len(positive)>1 and max(positive)-min(positive)>1e-8:
                mean=sum(positive)/len(positive);variance=sum((v-mean)**2 for v in positive)/len(positive);cv2=variance/mean**2;lo,hi=.3,40
                for _ in range(100):
                    k=(lo+hi)/2;v=math.exp(math.lgamma(1+2/k)-2*math.lgamma(1+1/k))-1
                    if v>cv2:lo=k
                    else:hi=k
                k=(lo+hi)/2;scale=mean/math.gamma(1+1/k);width=max(1,math.ceil(max(speeds)/25));bins=[];fit=[]
                for a in range(0,math.ceil(max(speeds))+width,width):
                    bins.append({'name':f'{a}–{a+width}','value':100*sum(a<=v<a+width for v in speeds)/len(speeds)});fit.append({'name':f'{a}–{a+width}','value':100*len(positive)/len(speeds)*(math.exp(-(a/scale)**k)-math.exp(-((a+width)/scale)**k))})
                metric('Weibull shape k',k,'dimensionless');metric('Weibull scale c',scale,'m/s');metric('Zero-speed share',100*(len(speeds)-len(positive))/len(speeds),'%');series('Observed speed frequencies',bins,'%');series('Fitted interval probabilities',fit,'%');wp['method']='Two-parameter Weibull method of moments fitted to strictly positive speeds; calm mass retained separately. Bisection of Gamma(1+2/k)/Gamma(1+1/k)^2−1. This is a descriptive fit, not a design-wind distribution.'
            elif cid=='C10':gaps.append('Positive wind speeds have no estimable variance; a two-parameter Weibull fit is unavailable.')
            elif cid=='C11' and '10' in wind and '100' in wind:
                low=wind['10']['rows'];values=defaultdict(list)
                for a,b in zip(low,rows):
                    if a['timestamp_utc']!=b['timestamp_utc']:raise ValueError('Height samples must be aligned')
                    if a['speed']>=.5 and b['speed']>=.5:values[a['timestamp_utc'][:7]].append(math.log(b['speed']/a['speed'])/math.log(10))
                series('Monthly mean 10–100 m shear exponent',[{'name':m,'value':sum(v)/len(v)} for m,v in sorted(values.items())],'dimensionless');metric('Paired non-calm hours',sum(map(len,values.values())),'hours');wp['method']='α = ln(U100/U10)/ln(100/10) for paired hourly reanalysis speeds ≥0.5 m/s. Describes modelled vertical shear; does not measure atmospheric stability.'
            elif cid=='C12':
                ordered=sorted(speeds);metric('Maximum hourly mean in sample',max(speeds),'m/s');metric('Sample 99th percentile',ordered[int((len(ordered)-1)*.99)],'m/s');months=defaultdict(list)
                for r in rows:months[r['timestamp_utc'][:7]].append(r['speed'])
                series('Monthly maxima of hourly mean wind',[{'name':m,'value':max(v)} for m,v in sorted(months.items())],'m/s');wp['method']='Descriptive maxima of hourly model means. Ten-minute turbulence, gusts and 50-year design extremes cannot be inferred from hourly reanalysis.';gaps.append('Acquire high-frequency hub-height measurements and a justified extreme-value/stability method for turbine design.')
    elif cid in ['C14','C15'] and joint:
        source('access_metocean');rows=joint['rows'];monthly=defaultdict(list)
        for r in rows:
            if r['current_ms'] is not None:monthly[r['time'][:7]].append(r['current_ms'])
        if cid=='C14':
            series('Monthly mean regional surface current',[{'name':m,'value':sum(v)/len(v)} for m,v in sorted(monthly.items())],'m/s');series('Monthly maximum regional surface current',[{'name':m,'value':max(v)} for m,v in sorted(monthly.items())],'m/s');wp['method']='Hourly regional SMOC surface-current summaries, source km/h converted to m/s. Not a depth profile, tidal harmonic analysis or measured water-level series.';gaps.append('Tide elevations, storm surge and depth-resolved currents remain unavailable.')
        else:
            from .accessibility import DEFAULT_ACCESS,evaluate_access
            prefs={**DEFAULT_ACCESS,**i.get('access_preferences',{})};changed={**joint,'rows':[{**r,'wind_ms':r['wind_ms']*(1+cfg['wind_change_pct']/100) if r['wind_ms'] is not None else None,'hs_m':max(0,r['hs_m']+cfg['wave_change_m']) if r['hs_m'] is not None else None} for r in rows]};a=evaluate_access(joint,prefs);b=evaluate_access(changed,prefs);series('Assumed climate/weather perturbation',[{'name':'Historical reference','value':a['eligible_pct']},{'name':'User perturbation','value':b['eligible_pct']}],'% eligible hours');wp['method']='A deterministic what-if perturbation of historical wind and Hs. It is not a climate projection, return-period analysis or probabilistic forecast.'
    elif cid in ['C24','C25','C31']:
        from .farm_preview import preview
        model=preview(s,ctx.get('results',{}),wind_from_deg=cfg.get('wind_from_deg',270),wind_ms=cfg.get('wind_ms',10));wp['geometry_basis']=model['basis']
        if cid=='C24':
            series('Selected-layout hub wind ratios',[{'name':t['id'],'value':t['wind_ratio']*100} for t in model['turbines']],'ambient %');metric('Mean hub-point wind reduction',100*(1-sum(t['wind_ratio'] for t in model['turbines'])/n),'%');wp['method']=model['wake_method'];gaps.append('Neighbouring farms, turbulence and wake-added fatigue are not modelled; no wave/access credit applies.')
        elif cid=='C25':
            items=[]
            for layout in load('layouts'):
                candidate={**s,'layout_id':layout['id']};m=preview(candidate,{},wind_ms=cfg['wind_ms'],wind_from_deg=cfg['wind_from_deg']);items.append({'name':layout['name'],'value':sum(t['wind_ratio'] for t in m['turbines'])/m['count']*100})
            series('Conceptual strategies at one declared wind condition',items,'ambient hub wind %');wp['method']='Deterministic comparison of five conceptual strategies using illustrative Jensen hub-point wakes at one direction/speed. Not an AEP/LCOE optimizer or feasible-AOI ranking.'
        else:
            size=int(cfg['string_size']);turbines=sorted(model['turbines'],key=lambda t:(t['y_m'],t['x_m']));strings=[];routes=[]
            for index in range(0,n,size):
                group=turbines[index:index+size];points=[{'x_m':0,'y_m':0}]+group;length=sum(math.hypot(b['x_m']-a['x_m'],b['y_m']-a['y_m']) for a,b in zip(points,points[1:]))/1000;strings.append({'name':f'String {index//size+1}','value':length});routes.append({'id':f'S{index//size+1}','turbine_ids':[t['id'] for t in group],'length_km':length})
            series('Conceptual straight-line string lengths',strings,'km');metric('String count',len(strings),'strings');metric('Full-string current',min(size,n)*i['turbine_mw']*1000/(math.sqrt(3)*cfg['voltage_kv']*cfg['power_factor']),'A');wp['routes']=routes;wp['method']='Preliminary grouping into strings, collector assumed at local (0,0), straight segments between sorted positions. No cable ampacity, routing exclusion, burial, redundancy or protection solution.'
    elif cid=='C28':
        b=base()
        if b:
            series('Historical weather-year net estimates',[{'name':str(r['year']),'value':r['net_aep_mwh']/1000} for r in b.get('annual_estimates',[])],'GWh/year');u=cfg['uncertainty_pct']
            if u is not None:series('Assumed normal exceedance estimates',[{'name':name,'value':max(0,b['net_aep_mwh']*(1-z*u/100))/1000} for name,z in [('P50',0),('P75',.67448975),('P90',1.28155157)]],'GWh/year')
            else:gaps.append('Enter an aggregate uncertainty assumption to calculate a labelled normal P75/P90 scenario.')
            wp['method']='Weather-year spread is descriptive and is not P90. Optional exceedance estimates use a user-declared aggregate normal standard uncertainty; no bankable yield inference.'
        elif ctx.get('wind'):return None
    elif cid in ['C30','C47','C51','C66']:
        b=base()
        if b:
            net=b['net_aep_mwh'];life=i['lifetime_years']
            if cid=='C30' and cfg['price'] is not None:
                captured=cfg['price']*cfg['capture_ratio'];energy=net*(1-cfg['extra_curtailment_pct']/100);metric('Assumed captured price',captured,'GBP/MWh');series('Revenue and curtailment what-if',[{'name':'Reference at assumed captured price','value':net*captured/1e6},{'name':'With additional curtailment','value':energy*captured/1e6}],'million GBP/year');wp['method']='Annual net MWh × assumed captured price. Additional curtailment is a separate sensitivity applied to the existing net estimate; no hourly market-price/capture correlation is available.'
            elif cid=='C47' and cfg['demand_mw'] is not None:
                demand=cfg['demand_mw']*cfg['hours'];series('Annual energy balance only',[{'name':'Wind annual net estimate','value':net/1000},{'name':'Assumed platform demand','value':demand/1000}],'GWh/year');metric('Annual energy coverage (capped)',min(100,100*net/demand) if demand else None,'%');wp['method']='Annual energy balance using user-supplied electrical demand. Does not establish hourly matching, firm power, avoided fuel use or electrification consent.'
            elif cid=='C51' and cfg['embodied_mt'] is not None:
                intensity=cfg['embodied_mt']*1e12/(net*1000*life);metric('Assumed life-cycle intensity',intensity,'g CO₂e/kWh');series('Declared embodied inventory',[{'name':'Life-cycle embodied inventory','value':cfg['embodied_mt']}],'Mt CO₂e')
                if cfg['displaced_g_kwh'] is not None and cfg['displaced_g_kwh']>0:metric('Simple carbon payback',cfg['embodied_mt']*1e12/(net*1000*cfg['displaced_g_kwh']),'years')
                wp['method']='Declared embodied CO₂e divided by constant lifetime delivered electricity. Boundary completeness and displaced-grid intensity require LCA evidence; this is not a marginal dispatch assessment. Simple payback treats the declared lifecycle inventory as upfront and divides by constant annual displaced-grid emissions; no operational time profile is resolved.'
            elif cid=='C66':
                cost=b.get('decommission_gbp',i.get('decommission_gbp'));rate=b.get('discount_rate',i.get('discount_rate'))
                if cost is not None and rate is not None:
                    netcost=cost*(1+cfg['contingency_pct']/100)-cfg['salvage_gbp'];series('Terminal-cost timing sensitivity',[{'name':f'Year {life+delay}','value':netcost/(1+rate)**(life+delay)/1e6} for delay in [0,1,3]],'million real GBP at year 0');metric('Net assumed removal cost',netcost/1e6,'million real GBP');metric('Removal campaign duration',cfg['removal_months'],'months')
                wp['method']='Terminal benchmark/declared cost plus explicitly additional contingency, less assumed salvage, discounted at the declared real rate. Timing alternatives do not imply legal permission to defer removal.'
    elif cid=='C32':
        current=i['capacity_mw']*1000/(math.sqrt(3)*cfg['voltage_kv']*cfg['power_factor']);metric('Full-farm current at assumed voltage',current,'A');available=(int(cfg['transformers'])-1)*cfg['transformer_mva']*cfg['power_factor'];series('Transformer capacity screening',[{'name':'Target active power','value':i['capacity_mw']},{'name':'Installed assumed capacity','value':cfg['transformers']*cfg['transformer_mva']*cfg['power_factor']},{'name':'One transformer unavailable','value':available}],'MW');wp['method']='Balanced three-phase P=√3VI cosφ; transformer MVA converted using declared power factor. Protection, fault levels, thermal loading, harmonic/reactive studies and redundancy design remain unverified.'
    elif cid=='C33' and cfg['length_km'] is not None:
        amps=i['capacity_mw']*1000/(cfg['circuits']*math.sqrt(3)*cfg['voltage_kv']*cfg['power_factor']);loss=cfg['circuits']*3*amps**2*cfg['resistance']*cfg['length_km']/1e6;metric('Indicative resistive loss at full load',loss,'MW');metric('Indicative full-load loss fraction',loss/i['capacity_mw']*100,'%');series('Assumed route-length sensitivity',[{'name':f'{cfg["length_km"]*factor:g} km','value':loss*factor} for factor in [.8,1,1.2]],'MW loss');wp['method']='Assumed AC conductor loss: circuits × 3I²R × one-way length. No routed corridor, charging current, dielectric/reactive losses, temperature or AC/DC technology decision is established.'
    elif cid=='C36':
        if cfg['connection_months'] is not None:metric('Assumed connection lead time',cfg['connection_months'],'months')
        if cfg['reinforcement_gbp'] is not None:metric('Assumed reinforcement budget',cfg['reinforcement_gbp']/1e6,'million real GBP')
        wp['method']='User-entered connection scenario only. The TEC register does not establish a project-specific offer, reinforcement scope, cost or delivery date.'
    elif cid=='C40' and all(cfg[k] is not None for k in ['pore_volume_km3','efficiency','density']):
        capacity=cfg['pore_volume_km3']*cfg['efficiency']*cfg['density'];metric('Volumetric capacity assumption',capacity,'Mt CO₂');series('Storage-efficiency sensitivity',[{'name':f'{100*cfg["efficiency"]*f:.2f}% efficiency','value':capacity*f} for f in [.5,1,1.5] if cfg['efficiency']*f<=1],'Mt CO₂');wp['method']='Connected pore volume [km³] × storage efficiency × reservoir CO₂ density [kg/m³] gives Mt CO₂. Does not establish injectivity, containment, commercial capacity or storage rights.'
    elif cid=='C43':
        for key,label,unit in [('injected_mt','Declared injected inventory','Mt CO₂'),('annual_mt','Declared annual injection','Mt CO₂/year')]:
            if cfg[key] is not None:metric(label,cfg[key],unit)
        wp['method']='User-asserted inventory register only; no monitoring response, leakage detection, operating licence or liability transfer is inferred.'
    elif cid=='C45':
        src=source('nsta_platforms')
        if src:
            from .external_analysis import regional_features,describe_feature
            records=[describe_feature(f) for f in regional_features(src['geojson'],i.get('screening_point'))['features']];records=sorted([r for r in records if r['distance_km'] is not None],key=lambda r:r['distance_km']);series('Nearby platform inventory (not reuse approvals)',[{'name':r['name'],'value':r['distance_km']} for r in records[:12]],'km');metric('Nearby source records',len(records),'records');wp['method']='Distance screening of published surface infrastructure. Structural condition, helideck, accommodation, ownership, access and reuse permission are unknown.'
    elif cid=='C46':
        saving=(cfg['separate_days']-cfg['shared_days'])*cfg['day_rate']-cfg['coordination_cost'];metric('Assumed annual net saving',saving/1e6,'million real GBP/year');series('Declared logistics alternatives',[{'name':'Separate vessel use','value':cfg['separate_days']*cfg['day_rate']/1e6},{'name':'Shared plus coordination','value':(cfg['shared_days']*cfg['day_rate']+cfg['coordination_cost'])/1e6}],'million real GBP/year');wp['method']='Assumed vessel-days × assumed day rate; no actual shared contract, compatibility or saving is verified.'
    elif cid=='C52':
        src=source('site_screening')
        if src:series('Straight-line construction-port transit proxy',[{'name':p['name'],'value':2*p['distance_km']/(cfg['vessel_speed']*1.852)} for p in sorted(src['ports'],key=lambda p:p['distance_km'])[:12]],'return hours')
        wp['method']='Return distance proxy divided by assumed speed; no berth, draft, crane, storage, navigable route or vessel suitability is inferred.'
    elif cid=='C53':
        series('Serial installation work allowance',[{'name':label,'value':n*cfg[key]/cfg['weather_fraction']} for key,label in [('foundation_days','Foundations'),('cable_days','Cables'),('turbine_days','Turbines')]],'calendar days');wp['method']='Turbine count × declared workdays / assumed workable installation fraction. Serial task allowance, not a vessel-optimised schedule; crew-transfer weather criteria are not substituted for installation limits.'
    elif cid=='C54':
        from .supply_reference import load_supply_reference
        reference=load_supply_reference()
        wp['supply_reference']=reference
        wp['method']='Lattice supply-chain explorer: user-supplied UK directory snapshot of '+reference['metadata']['snapshot_date']+'. Confidence-weighted capability exposure and disruption scenarios are calculated locally in the explorer. They do not establish vendor qualification, capacity, delivery commitments, quotations or lead times. Procurement evidence and review states remain attached to this revision.'
        provenance.append({'source':reference['metadata']['title'],'source_type':'user_supplied_contextual_snapshot','snapshot_date':reference['metadata']['snapshot_date'],'original_sha256':reference['metadata']['original_sha256'],'data_sha256':reference['metadata']['data_sha256'],'verification':'not_independently_reverified'})
        gaps.append('Directory evidence is a contextual snapshot, not a project-specific procurement schedule. Obtain vendor quotations, qualification records and dated delivery commitments.')
    elif cid=='C55':
        available=cfg['mtbf_h']/(cfg['mtbf_h']+cfg['repair_h']+cfg['wait_h']);metric('Illustrative time availability',available*100,'%');series('Expected downtime components per renewal',[{'name':'Active repair','value':cfg['repair_h']},{'name':'Logistics/weather wait','value':cfg['wait_h']}],'hours');wp['method']='Renewal approximation A=MTBF/(MTBF+active repair+waiting). Assumed time availability is distinct from energy-weighted availability and does not alter the overview loss benchmark.'
    elif cid=='C62':
        risks=draft['risks'];scored=[r for r in risks if r['likelihood'] is not None and r['severity'] is not None];metric('Hazards awaiting assessment',len(risks)-len(scored),'hazards');metric('Risks reviewed with evidence',sum(r['status']=='reviewed' for r in risks),'hazards');wp['risks']=[{**r,'score':r['likelihood']*r['severity'] if r['likelihood'] is not None and r['severity'] is not None else None,'residual_score':r['residual_likelihood']*r['residual_severity'] if r['residual_likelihood'] is not None and r['residual_severity'] is not None else None} for r in risks];wp['method']='Editable 1–5 ordinal likelihood × consequence matrix, with separate proposed residual scores. Scores are user assessments, not measured probabilities. No score, completed form or proposed control establishes ALARP or an approved emergency plan.'
    elif cid=='C63':
        demand=n*cfg['visits']*cfg['visit_hours']*cfg['crew'];supply=cfg['annual_hours']*cfg['productive_fraction'];metric('Direct maintenance labour',demand,'person-hours/year');metric('Direct-task FTE requirement',demand/supply,'FTE');metric('Rounded direct-task headcount',math.ceil(demand/supply),'people');series('Workload vs one technician capacity',[{'name':'Direct scheduled workload','value':demand},{'name':'One technician productive capacity','value':supply}],'person-hours/year');wp['method']='Count × visits × hours × crew / productive hours per technician. Excludes failures, travel, management, shifts, leave, statutory competence and specialist contractors.'
    elif cid=='C64':
        wp['stakeholders']=draft['stakeholders'];metric('Groups requiring engagement records',sum(not r['evidence'].strip() for r in draft['stakeholders']),'groups');wp['method']='Editable influence/interest and engagement register. Named groups are a planning checklist; no contact, consultation, agreement or stakeholder preference is asserted.'
    elif cid=='C65':
        tasks,finish=schedule(draft['tasks']);wp['tasks']=tasks;metric('Indicative critical-path duration',finish,'months');metric('Critical activities',sum(t['critical'] for t in tasks),'tasks');wp['method']='Forward/backward critical-path calculation in relative months; dependencies must be acyclic. Template durations are editable assumptions, not supplier or consent commitments.'
    known=Counter(r['status'] for r in draft['evidence']);wp['evidence_summary']=[{'name':status,'value':known[status]} for status in STATUSES]
    wp['quantitative_ready']=bool(wp['metrics'] or wp['series'] or wp.get('tasks'))
    if not wp['quantitative_ready'] and d['kind']=='screening_calculation':gaps.append('Supply the required numeric inputs or connect the scoped source to calculate this screening view.')
    for row in draft['evidence']:
        if row['status']!='reviewed':gaps.append(f'{row["requirement"]}: {row["status"]}; assign an owner and supply a source/review record.')
    gaps.append('Screening calculations and user review records do not establish engineering, legal or operational approval.')
    return {'work_package':wp,'data_scope':'planning_workspace','reference_point':i.get('screening_point')},provenance,gaps
