"""Transparent preliminary calculations. No live feeds or design certification."""
import calendar,csv,io,math,random
from datetime import datetime,timezone
from shapely.geometry import shape,Point,mapping
from shapely.ops import transform
from shapely.validation import explain_validity
from pyproj import CRS,Transformer

def finite(value,name,lo=None,hi=None):
    try: v=float(value)
    except (ValueError,TypeError): raise ValueError(f'{name} must be numeric')
    if not math.isfinite(v) or lo is not None and v<lo or hi is not None and v>hi:
        raise ValueError(f'{name} must be finite and in [{lo}, {hi}]')
    return v

def geometry(geo):
    if not isinstance(geo,dict): raise ValueError('Import a GeoJSON Polygon in EPSG:4326 (longitude, latitude)')
    if geo.get('crs'): raise ValueError('Legacy GeoJSON CRS is not supported; reproject to EPSG:4326')
    if geo.get('type')=='Feature':geo=geo['geometry']
    if geo.get('type')!='Polygon':raise ValueError('Only a GeoJSON Polygon is supported in this release')
    for ring in geo.get('coordinates',[]):
        if len(ring)<4 or ring[0]!=ring[-1]:raise ValueError('Each polygon ring needs at least four coordinates and must be closed')
        for xy in ring:
            if len(xy)!=2:raise ValueError('Coordinates must contain longitude and latitude only')
            finite(xy[0],'longitude',-180,180);finite(xy[1],'latitude',-80,84)
    try:p=shape(geo)
    except Exception as e:raise ValueError('Invalid polygon coordinates') from e
    if p.is_empty or not p.is_valid:raise ValueError('Invalid AOI: '+explain_validity(p))
    x,y=p.centroid.coords[0]
    if p.bounds[2]-p.bounds[0]>6 or p.bounds[3]-p.bounds[1]>6:raise ValueError('AOI exceeds local projection limits; use a smaller site')
    crs=CRS.from_proj4(f'+proj=aeqd +lat_0={y} +lon_0={x} +datum=WGS84 +units=m')
    forward=Transformer.from_crs(4326,crs,always_xy=True).transform
    inverse=Transformer.from_crs(crs,4326,always_xy=True).transform
    projected=transform(forward,p)
    if projected.area<10000:raise ValueError('AOI area must be at least 0.01 km²')
    return p,projected,forward,inverse

def validate_inputs(i):
    allowed={'capacity_mw','turbine_mw','rotor_diameter_m','hub_height_m','turbine_name','spacing_d','cross_spacing_d','rotation_deg','seed','aoi','exclusions','geometry_source','geometry_license','geometry_reviewed','wind_dataset_id','wind_height_m','cut_in_ms','rated_speed_ms','cut_out_ms','wake_loss','electrical_loss','availability_loss','curtailment_loss','uncertainty_fraction','capex_gbp_per_kw','opex_gbp_per_kw_year','decommission_gbp','discount_rate','lifetime_years','power_price_gbp_mwh','price_year','design_year','currency','assumption_note','site_name','jurisdiction','contributions'}
    allowed.update({'screening_point','data_bindings','site_preferences','regional_screening_case','wind_plot_preferences','access_preferences','category_inputs','location_preferences'})
    unknown=set(i)-allowed
    if unknown:raise ValueError('Unknown input fields: '+', '.join(sorted(unknown)))
    if i.get('category_inputs') is not None:
        from .work_packages import validate_work_inputs
        validate_work_inputs(i['category_inputs'])
    if i.get('access_preferences') is not None:
        from .accessibility import validate_access
        validate_access(i['access_preferences'])
    if i.get('wind_plot_preferences') is not None:
        prefs=i['wind_plot_preferences']
        required={'period','height_m','threshold_height_m','sailing_limit_ms','om_limit_ms','unit','threshold_basis'}
        if not isinstance(prefs,dict) or set(prefs)!=required:raise ValueError('Wind plot preferences require period, heights, sailing/O&M limits, unit and threshold basis')
        if not isinstance(prefs['period'],str) or not (prefs['period'] in ['recent','sample'] or len(prefs['period'])==4 and prefs['period'].isdigit()):raise ValueError('Invalid wind plot period')
        if prefs['unit'] not in ['ms','knots']:raise ValueError('Wind plot unit must be ms or knots')
        if not isinstance(prefs['threshold_basis'],str) or not 1<=len(prefs['threshold_basis'].strip())<=500:raise ValueError('Record a threshold basis (1–500 characters)')
        for key,lo,hi in [('height_m',1,300),('threshold_height_m',1,300),('sailing_limit_ms',0,60),('om_limit_ms',0,60)]:
            if isinstance(prefs[key],bool):raise ValueError('Wind plot parameters must be numeric')
            prefs[key]=finite(prefs[key],key,lo,hi)
    if i.get('regional_screening_case') is not None:
        case=i['regional_screening_case']
        if not isinstance(case,dict) or set(case)!={'enabled','electrical_loss','curtailment_loss'} or not isinstance(case['enabled'],bool):raise ValueError('Regional screening case requires enabled, electrical_loss and curtailment_loss')
        for key in ['electrical_loss','curtailment_loss']:
            if isinstance(case[key],bool):raise ValueError('Regional loss fractions must be numeric')
            case[key]=finite(case[key],key,0,.8)
    if i.get('location_preferences') is not None:
        location=i['location_preferences']
        if not isinstance(location,dict) or set(location)!={'country','max_coast_km'} or location['country']!='UK':raise ValueError('Location preferences require country UK and max_coast_km')
        if isinstance(location['max_coast_km'],bool):raise ValueError('Maximum UK coast distance must be numeric')
        location['max_coast_km']=finite(location['max_coast_km'],'maximum UK coast distance',1,500)
    if i.get('site_preferences') is not None:
        prefs=i['site_preferences']
        if not isinstance(prefs,dict) or not isinstance(prefs.get('weights'),dict):raise ValueError('Site preferences require a weights object')
        if set(prefs['weights'])!={'port_km','coast_km','shipping'}:raise ValueError('Weights must contain port_km, coast_km and shipping')
        for key,value in prefs['weights'].items():
            if isinstance(value,bool):raise ValueError('Weights must be numbers')
            prefs['weights'][key]=finite(value,key,0,100)
        if sum(prefs['weights'].values())<=0:raise ValueError('At least one positive preference weight is required')
        if prefs.get('year') not in [2023,2024]:raise ValueError('Choose an available AIS year: 2023 or 2024')
        for key,default,lo,hi in [('density_threshold',1,0,1000),('vessel_speed_knots',20,1,60)]:
            if isinstance(prefs.get(key),bool):raise ValueError(f'{key} must be numeric, not boolean')
            prefs[key]=finite(prefs.get(key,default),key,lo,hi)
    if i.get('screening_point'):
        point=i['screening_point']
        if not isinstance(point,dict):raise ValueError('Screening point must be an object')
        point['lat']=finite(point.get('lat'),'reference latitude',-80,84)
        point['lon']=finite(point.get('lon'),'reference longitude',-180,180)
    if not isinstance(i.get('data_bindings',{}),dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in i.get('data_bindings',{}).items()):raise ValueError('Data bindings must map provider IDs to dataset IDs')
    for k in ['capacity_mw','turbine_mw','rotor_diameter_m','hub_height_m','spacing_d','cross_spacing_d','rotation_deg','seed','cut_in_ms','rated_speed_ms','cut_out_ms','lifetime_years','price_year','design_year']:
        if k in i and i[k] is None:raise ValueError(f'{k} is a required design input and cannot be blank')
    bounds={'capacity_mw':(1,10000),'turbine_mw':(.1,30),'rotor_diameter_m':(20,400),'hub_height_m':(20,300),'spacing_d':(3,30),'cross_spacing_d':(3,30),'rotation_deg':(-360,360),'seed':(0,1000000),'cut_in_ms':(0,10),'rated_speed_ms':(5,25),'cut_out_ms':(15,50),'wake_loss':(0,.9),'electrical_loss':(0,.9),'availability_loss':(0,.9),'curtailment_loss':(0,.9),'uncertainty_fraction':(0,.5),'capex_gbp_per_kw':(1,20000),'opex_gbp_per_kw_year':(0,2000),'decommission_gbp':(0,1e11),'discount_rate':(0,.5),'lifetime_years':(1,60),'power_price_gbp_mwh':(-1000,2000),'price_year':(2020,2100),'design_year':(2020,2100)}
    for k,(lo,hi) in bounds.items():
        if i.get(k) is not None:
            if isinstance(i[k],bool):raise ValueError(f'{k} must be numeric, not boolean')
            i[k]=finite(i[k],k,lo,hi)
    for k in ['lifetime_years','price_year','design_year','seed']:
        if i.get(k) is not None and float(i[k])!=int(i[k]):raise ValueError(f'{k} must be a whole number')
        if i.get(k) is not None:i[k]=int(i[k])
    if i.get('currency','GBP')!='GBP':raise ValueError('This release supports GBP real-basis calculations only')
    if i.get('aoi'):
        p,_,_,_=geometry(i['aoi'])
        for ex in i.get('exclusions',[]):
            ep,*_=geometry(ex)
            if not ep.intersects(p):raise ValueError('An exclusion polygon does not intersect the AOI')
    if all(i.get(k) is not None for k in ['cut_in_ms','rated_speed_ms','cut_out_ms']):
        if not i['cut_in_ms']<i['rated_speed_ms']<i['cut_out_ms']:raise ValueError('Require cut-in < rated speed < cut-out')
    if i.get('turbine_mw') and i.get('capacity_mw'):
        count=i['capacity_mw']/i['turbine_mw']
        if abs(count-round(count))>1e-7:raise ValueError('Capacity must be an integer multiple of turbine rating')
        if count>1500:raise ValueError('This preliminary geometry engine supports up to 1500 turbines')
    if not isinstance(i.get('contributions',[]),list):raise ValueError('Contributions must be a list')
    for row in i.get('contributions',[]):
        if not isinstance(row,dict) or any(not isinstance(row.get(k,''),str) for k in ['section','human_lead','ai_tools','contribution']):raise ValueError('Each contribution needs text section, human lead, AI tools and contribution fields')

def layout(i,layout_id,wind=None):
    p,area,fwd,inv=geometry(i.get('aoi'))
    rotor=i['rotor_diameter_m'];n=round(i['capacity_mw']/i['turbine_mw']);spacing=i['spacing_d']*rotor;cross=i['cross_spacing_d']*rotor
    # Full rotor envelope must stay in AOI and outside user-declared exclusions.
    permitted=area.buffer(-rotor/2)
    for ex in i.get('exclusions',[]):permitted=permitted.difference(transform(fwd,geometry(ex)[0]).buffer(rotor/2))
    if permitted.is_empty:raise ValueError('No permissible rotor envelope remains in this AOI')
    angle=i.get('rotation_deg',0)
    if layout_id=='LAYOUT_03':
        if not wind:raise ValueError('Wind-informed layout requires imported joint wind speed/direction data')
        sector=max(wind_summary(wind)['sectors'],key=lambda x:x['frequency_pct'])['direction_deg']
        angle=(90-sector)%360
    rad=math.radians(angle);co,si=math.cos(rad),math.sin(rad)
    minx,miny,maxx,maxy=permitted.bounds;radius=math.hypot(maxx-minx,maxy-miny)/2+spacing;cx=(minx+maxx)/2;cy=(miny+maxy)/2
    if (2*radius/spacing+1)*(2*radius/cross+1)>200000:raise ValueError('AOI is too large for this spacing; reduce AOI or increase spacing')
    candidates=[]
    if layout_id=='LAYOUT_04':
        # Seeded feasible-point search; deliberately not an energy/cost optimizer.
        rng=random.Random(i.get('seed',42));clearance=max(spacing,cross);buckets={}
        for _ in range(min(300000,max(10000,n*1000))):
            point=Point(rng.uniform(minx,maxx),rng.uniform(miny,maxy))
            if not permitted.covers(point):continue
            key=(math.floor(point.x/clearance),math.floor(point.y/clearance))
            nearby=[p for dx in [-1,0,1] for dy in [-1,0,1] for p in buckets.get((key[0]+dx,key[1]+dy),[])]
            if any(point.distance(p)<clearance for p in nearby):continue
            candidates.append(point);buckets.setdefault(key,[]).append(point)
            if len(candidates)==n:break
        if len(candidates)<n:raise ValueError(f'Seeded feasible-point search found {len(candidates)} of {n} positions within its search budget; change seed, spacing or AOI. This does not prove global infeasibility.')
    else:
        for row in range(-math.ceil(radius/cross),math.ceil(radius/cross)+1):
            for col in range(-math.ceil(radius/spacing),math.ceil(radius/spacing)+1):
                x=col*spacing+(spacing/2 if layout_id=='LAYOUT_02' and row%2 else 0);y=row*cross
                if layout_id=='LAYOUT_05' and abs(x)<spacing:continue
                point=Point(cx+x*co-y*si,cy+x*si+y*co)
                if permitted.covers(point):candidates.append(point)
    candidates.sort(key=lambda x:x.distance(Point(cx,cy)))
    if len(candidates)<n:raise ValueError(f'Only {len(candidates)} positions fit; {n} requested. Reduce capacity or spacing, or expand the AOI.')
    chosen=candidates[:n]
    if layout_id=='LAYOUT_05' and not (any(q.x<cx for q in chosen) and any(q.x>cx for q in chosen)):raise ValueError('AOI cannot accommodate both separated blocks')
    minimum=min((a.distance(b) for k,a in enumerate(chosen) for b in chosen[k+1:]),default=None)
    if minimum is not None and minimum+1e-5<min(spacing,cross):raise ValueError('Generated geometry fails minimum spacing')
    points=[{'id':f'T{k+1:03}','lon':inv(q.x,q.y)[0],'lat':inv(q.x,q.y)[1]} for k,q in enumerate(chosen)]
    nearest=[min(q.distance(other) for other in chosen if other is not q) for q in chosen] if n>1 else []
    return {'turbines':points,'count':n,'capacity_mw':n*i['turbine_mw'],'minimum_spacing_m':minimum,'nearest_spacing_m':nearest,'area_km2':area.area/1e6,'geometry_status':'computationally_valid_only','rotation_deg':angle,'layout_method':'seeded_feasible_point_search' if layout_id=='LAYOUT_04' else 'geometric_grid_strategy','energy_cost_optimized':False,'limitations':'User-declared exclusions only. Lease rights, environmental layers and seabed suitability are not verified. Irregular search uses conservative isotropic clearance equal to the larger declared spacing; no energy/cost optimum is claimed.'}

def parse_wind(text):
    if len(text)>15_000_000:raise ValueError('Wind CSV is limited to 15 MB')
    reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
    required={'timestamp_utc','wind_speed_ms','direction_deg','hub_height_m'}
    if not required.issubset(reader.fieldnames or []):raise ValueError('CSV requires '+', '.join(sorted(required)))
    rows=[];seen=set()
    for k,row in enumerate(reader,2):
        try:
            dt=datetime.fromisoformat(row['timestamp_utc'].replace('Z','+00:00'))
            if dt.tzinfo is None or dt.utcoffset().total_seconds()!=0:raise ValueError('timestamps must explicitly use UTC')
            key=dt.isoformat()
            if key in seen:raise ValueError('duplicate timestamp')
            seen.add(key)
            rows.append({'timestamp_utc':key,'speed':finite(row['wind_speed_ms'],'speed',0,100),'direction':finite(row['direction_deg'],'direction',0,360)%360,'height':finite(row['hub_height_m'],'height',10,300)})
        except (ValueError,KeyError,TypeError) as e:raise ValueError(f'CSV line {k}: {e}') from e
    if len(rows)<24:raise ValueError('At least 24 records are needed for exploratory statistics')
    rows.sort(key=lambda r:r['timestamp_utc'])
    if len({r['height'] for r in rows})!=1:raise ValueError('Import one hub height per dataset')
    deltas=[(datetime.fromisoformat(b['timestamp_utc'])-datetime.fromisoformat(a['timestamp_utc'])).total_seconds() for a,b in zip(rows,rows[1:])]
    if any(abs(d-3600)>1 for d in deltas):raise ValueError('This release requires regular hourly observations without gaps')
    return rows

def wind_summary(rows):
    bins=[0]*16;stacks=[[0]*5 for _ in range(16)];calms=0
    for r in rows:
        if r['speed']<.5:calms+=1;continue
        s=int((r['direction']+11.25)%360/22.5);bins[s]+=1
        stacks[s][min(int(r['speed']//5),4)]+=1
    return {'mean_speed_ms':sum(r['speed'] for r in rows)/len(rows),'sample_count':len(rows),'hub_height_m':rows[0]['height'],'start':rows[0]['timestamp_utc'],'end':rows[-1]['timestamp_utc'],'calm_pct':100*calms/len(rows),'sectors':[{'direction_deg':k*22.5,'frequency_pct':100*v/len(rows),'speed_bins_pct':[100*x/len(rows) for x in stacks[k]]} for k,v in enumerate(bins)],'convention':'Meteorological wind FROM; clockwise from north. Frequencies use all observations; calms <0.5 m/s excluded from directional bins.'}

def power(v,i):
    # Explicit cubic proxy; never a certified manufacturer power curve.
    a,b,c=i['cut_in_ms'],i['rated_speed_ms'],i['cut_out_ms'];rated=i['turbine_mw']
    if v<a or v>=c:return 0
    if v>=b:return rated
    return rated*(v**3-a**3)/(b**3-a**3)

def energy(i,rows):
    if rows[0]['height']!=i['hub_height_m']:raise ValueError('Wind sample height must match turbine hub height; no implicit shear correction')
    n=round(i['capacity_mw']/i['turbine_mw']);hours=8784 if calendar.isleap(i['design_year']) else 8760
    gross=sum(power(r['speed'],i) for r in rows)/len(rows)*hours*n
    net=gross;losses=[]
    for key in ['wake_loss','electrical_loss','availability_loss','curtailment_loss']:
        loss=net*i[key];net-=loss;losses.append({'name':key,'fraction':i[key],'mwh':loss})
    sigma=net*i['uncertainty_fraction']
    return {'gross_aep_mwh':gross,'net_aep_mwh':net,'capacity_factor':net/(i['capacity_mw']*hours),'reporting_hours':hours,'losses':losses,'p50_mwh':net,'p75_mwh':max(0,net-.67448975*sigma),'p90_mwh':max(0,net-1.28155157*sigma),'method':'Annualized sample mean using an assumed cubic power curve and user-specified multiplicative losses. Normal approximation to exceedance quantiles, floored at zero. Not a bankable yield assessment.','sample_hours':len(rows)}

def finance(i,net_mwh):
    r=i['discount_rate'];years=i['lifetime_years'];capex=i['capex_gbp_per_kw']*i['capacity_mw']*1000;opex=i['opex_gbp_per_kw_year']*i['capacity_mw']*1000
    annual=net_mwh*i['power_price_gbp_mwh']-opex
    flows=[-capex]+[annual-(i['decommission_gbp'] if t==years else 0) for t in range(1,years+1)]
    def npv(rate):return sum(v/(1+rate)**t for t,v in enumerate(flows))
    discounted_energy=sum(net_mwh/(1+r)**t for t in range(1,years+1))
    if discounted_energy<=0:raise ValueError('Positive delivered energy is required for LCOE')
    cost=capex+sum(opex/(1+r)**t for t in range(1,years+1))+i['decommission_gbp']/(1+r)**years
    # Only report IRR for conventional cashflows with a unique positive-to-negative NPV bracket.
    irr=None
    if annual>0 and flows[-1]>=0:
        lo,hi=-.95,10.0
        if npv(lo)*npv(hi)<0:
            for _ in range(100):
                mid=(lo+hi)/2
                if npv(mid)>0:lo=mid
                else:hi=mid
            irr=(lo+hi)/2
    cumulative=-capex;cash=[];payback=None
    for t,v in enumerate(flows):
        if t:cumulative+=v
        cash.append({'year':t,'cashflow_gbp':v,'cumulative_gbp':cumulative})
    for t in range(1,years+1):
        if all(x['cumulative_gbp']>=0 for x in cash[t:]):payback=t;break
    return {'capex_gbp':capex,'annual_opex_gbp':opex,'lcoe_gbp_mwh':cost/discounted_energy,'npv_gbp':npv(r),'irr':irr,'undiscounted_payback_year':payback,'cashflows':cash,'currency':'GBP','price_year':i['price_year'],'method':'Unlevered real cashflow, initial CAPEX at t=0, constant annual energy, price and OPEX, end-year costs, terminal decommissioning. Excludes tax, debt, inflation, degradation and construction phasing.'}
