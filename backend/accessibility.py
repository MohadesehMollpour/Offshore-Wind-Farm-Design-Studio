"""Regional joint metocean screening; missing criteria never become approvals."""
import calendar,math
from collections import Counter
from datetime import date,datetime,timedelta
from .providers import finite,ProviderError
from .wind_history import recent_complete_year,month_boxes

DEFAULT_ACCESS={'active':['W','SH','L'],'wind_max_ms':10,'wave_max_m':1.5,'current_max_ms':1,'visibility_min_m':1000,'rain_max_mm_h':2,'duration_h':12,'work_h':4,'vessel_speed_knots':20,'daylight_required':True}
CRITERIA={'V':('Visibility','visibility_m'),'C':('Current','current_ms'),'SH':('Significant wave height','hs_m'),'L':('Daylight','is_day'),'W':('Wind at 10 m','wind_ms'),'R':('Rain','rain_mm_h')}

def validate_access(cfg):
    if not isinstance(cfg,dict) or set(cfg)!=set(DEFAULT_ACCESS):raise ValueError('Accessibility preferences require all declared criteria and window parameters')
    if not isinstance(cfg['active'],list) or not cfg['active'] or any(not isinstance(k,str) or k not in CRITERIA for k in cfg['active']) or len(cfg['active'])!=len(set(cfg['active'])):raise ValueError('Select unique criteria from V, C, SH, L, W, R')
    for k,lo,hi in [('wind_max_ms',0,60),('wave_max_m',0,20),('current_max_ms',0,10),('visibility_min_m',0,100000),('rain_max_mm_h',0,200),('duration_h',1,168),('work_h',0,48),('vessel_speed_knots',1,60)]:
        if isinstance(cfg[k],bool):raise ValueError('Accessibility limits must be numeric')
        cfg[k]=finite(cfg[k],k,lo,hi)
    if int(cfg['duration_h'])!=cfg['duration_h']:raise ValueError('Window duration must be a whole number of hours')
    cfg['duration_h']=int(cfg['duration_h'])
    if not isinstance(cfg['daylight_required'],bool):raise ValueError('Daylight setting must be boolean')
    return cfg

def collect_access(fetch,point):
    start,end=recent_complete_year();base={'latitude':round(point['lat'],6),'longitude':round(point['lon'],6),'start_date':start,'end_date':end,'timezone':'GMT','cell_selection':'sea'}
    wind=fetch.json('https://archive-api.open-meteo.com/v1/archive',{**base,'models':'era5','elevation':'nan','wind_speed_unit':'ms','hourly':'wind_speed_10m,wind_direction_10m,wind_speed_100m,wind_direction_100m,precipitation,is_day,visibility'},720)
    waves=fetch.json('https://marine-api.open-meteo.com/v1/marine',{**base,'models':'era5_ocean','hourly':'wave_height,wave_period,wave_direction'},720)
    expected=((date.fromisoformat(end)-date.fromisoformat(start)).days+1)*24
    times=wind.get('hourly',{}).get('time',[])
    if len(times)!=expected or len(set(times))!=expected or wind.get('utc_offset_seconds')!=0 or waves.get('utc_offset_seconds')!=0 or waves.get('hourly',{}).get('time')!=times:raise ProviderError('Wind/wave history must have the same complete UTC hourly time axis')
    expected_times=[(datetime.fromisoformat(start)+timedelta(hours=i)).isoformat(timespec='minutes') for i in range(expected)]
    if times!=expected_times:raise ProviderError('Joint history timestamps are not the requested consecutive hours')
    wu=wind.get('hourly_units',{});su=waves.get('hourly_units',{})
    if any(wu.get(k)!='m/s' for k in ['wind_speed_10m','wind_speed_100m']) or wu.get('precipitation')!='mm' or su.get('wave_height')!='m' or su.get('wave_period')!='s':raise ProviderError('Unexpected metocean units')
    for obj in [wind,waves]:
        if any(len(v)!=expected for v in obj['hourly'].values()):raise ProviderError('Joint metocean arrays have inconsistent lengths')
    notes=[];current=None
    try:
        current=fetch.json('https://marine-api.open-meteo.com/v1/marine',{**base,'models':'meteofrance_currents','hourly':'ocean_current_velocity,ocean_current_direction'},720)
        if current.get('utc_offset_seconds')!=0 or current.get('hourly',{}).get('time')!=times or any(len(v)!=expected for v in current['hourly'].values()):raise ProviderError('Current history is not aligned with the wind/wave UTC timeline')
        if current['hourly_units'].get('ocean_current_velocity') not in ['km/h','m/s']:raise ProviderError('Unexpected current velocity units')
    except Exception as exc:notes.append('Current history unavailable: '+str(exc)[:200]);current=None
    w=wind['hourly'];h=waves['hourly'];c=current['hourly'] if current else {};factor=1/3.6 if current and current['hourly_units']['ocean_current_velocity']=='km/h' else 1
    def value(arr,i,name,lo,hi):
        v=arr[i] if arr is not None else None
        return None if v is None else finite(v,name,lo,hi)
    visibility=w.get('visibility',[None]*expected)
    if any(v is not None for v in visibility) and wu.get('visibility')!='m':raise ProviderError('Visibility values have unexpected units')
    rows=[]
    for i,t in enumerate(times):
        r={'time':t+':00+00:00','wind_ms':value(w['wind_speed_10m'],i,'10 m wind',0,100),'wind_dir':value(w['wind_direction_10m'],i,'wind direction',0,360),'wind100_ms':value(w['wind_speed_100m'],i,'100 m wind',0,100),'wind100_dir':value(w['wind_direction_100m'],i,'100 m wind direction',0,360),'hs_m':value(h['wave_height'],i,'significant wave height',0,30),'tp_s':value(h['wave_period'],i,'wave period',0,40),'wave_dir':value(h['wave_direction'],i,'wave direction',0,360),'rain_mm_h':value(w['precipitation'],i,'hourly rain',0,500),'is_day':value(w['is_day'],i,'daylight flag',0,1),'visibility_m':value(visibility,i,'visibility',0,100000),'current_ms':None,'current_dir':None}
        if r['is_day'] not in [0,1,None]:raise ProviderError('Daylight flag must be binary or missing')
        if current:
            v=value(c['ocean_current_velocity'],i,'current velocity',0,40);r['current_ms']=v*factor if v is not None else None;r['current_dir']=value(c['ocean_current_direction'],i,'current direction',0,360)
        rows.append(r)
    coverage={key:sum(r[field] is not None for r in rows) for key,(_,field) in CRITERIA.items()}
    if not any(r['wind_ms'] is not None and r['hs_m'] is not None for r in rows):raise ProviderError('No matched valid wind and wave hours; accessibility cannot be calculated')
    if not coverage['V']:notes.append('ERA5 archive does not provide visibility at this location/period; V remains unknown when selected.')
    notes.append('R uses total hourly precipitation (rain and snow equivalent), a conservative rain proxy rather than a rain-only measurement. Wave period is the source mean period, not spectral peak period.')
    return {'rows':rows,'record_count':len(rows),'start_date':start,'end_date':end,'coverage':coverage,'reference_point':point,'grid_points':{'wind':{'lat':wind['latitude'],'lon':wind['longitude'],'resolution':'ERA5 0.25°'},'wave':{'lat':waves['latitude'],'lon':waves['longitude'],'resolution':'ERA5-Ocean 0.5° (about 50 km)'},'current':{'lat':current['latitude'],'lon':current['longitude'],'resolution':'Meteo-France SMOC about 8 km'} if current else None},'models':['ERA5','ERA5-Ocean','Meteo-France SMOC currents'],'current_conversion':'Source km/h divided by 3.6' if factor!=1 else 'Source m/s','limitations':notes+['Regional model histories, not live instrument observations or operational approval.','Wave and wind grid cells differ in position and resolution; a time join does not establish farm-scale spatial shelter.','Visibility remains unavailable; no missing criterion is replaced by an assumed good condition.','Daylight uses the provider binary day/night flag; twilight, task lighting and vessel procedures are not inferred.','Thresholds and continuous-window requirements are editable planning assumptions; waves, gusts, vessel motion and approved procedures need review.']}

def checks(row,cfg):
    out={}
    for key in cfg['active']:
        val=row.get(CRITERIA[key][1])
        if key=='L' and not cfg['daylight_required']:out[key]=True
        elif val is None:out[key]=None
        elif key=='V':out[key]=val>=cfg['visibility_min_m']
        elif key=='L':out[key]=not cfg['daylight_required'] or val==1
        else:out[key]=val<=cfg[{'W':'wind_max_ms','SH':'wave_max_m','C':'current_max_ms','R':'rain_max_mm_h'}[key]]
    return out

def evaluate_access(data,cfg):
    cfg=validate_access(dict(cfg));rows=data['rows'];states=[];counts=Counter();monthly={}
    for row in rows:
        vals=checks(row,cfg);state='fail' if False in vals.values() else 'unknown' if None in vals.values() else 'pass'
        states.append(state);counts[state]+=1;m=monthly.setdefault(row['time'][:7],{'pass':0,'fail':0,'unknown':0,'hours':0,'window_starts':0});m[state]+=1;m['hours']+=1
    runs=[];starts=[];begin=None
    for i,state in enumerate(states+['fail']):
        if state=='pass' and begin is None:begin=i
        if state!='pass' and begin is not None:
            length=i-begin;runs.append(length)
            for j in range(begin,max(begin,i-cfg['duration_h']+1)):starts.append(j);monthly[rows[j]['time'][:7]]['window_starts']+=1
            begin=None
    wave_rows=[{'timestamp_utc':r['time'],'speed':r['hs_m']} for r in rows if r['hs_m'] is not None]
    boxes=month_boxes(wave_rows,data['start_date'],data['end_date']);boxes=[{k.replace('_ms',''):v for k,v in b.items()} for b in boxes]
    return {'preferences':cfg,'total_hours':len(rows),'eligible_hours':counts['pass'],'ineligible_hours':counts['fail'],'unknown_hours':counts['unknown'],'eligible_pct':100*counts['pass']/len(rows),'monthly':[{'month':k,**v,'eligible_pct':100*v['pass']/v['hours']} for k,v in sorted(monthly.items())],'window_starts':len(starts),'window_start_indices':starts,'longest_run_h':max(runs,default=0),'window_lengths_h':runs,'wave_boxes':boxes,'criteria_coverage':[{'id':k,'name':name,'valid_hours':sum(r.get(field) is not None for r in rows),'missing_hours':sum(r.get(field) is None for r in rows)} for k,(name,field) in CRITERIA.items()],'states':states,'interpretation':'Eligible means the selected hourly criteria are met. A continuous window requires every hour to pass. Failed known conditions are ineligible; missing conditions never count as eligible. Overlapping candidate starts are not independent trips.'}

def analyze_access(s,external):
    if 'access_metocean' not in external:return None
    entry=external['access_metocean'];data=entry['data'];cfg={**DEFAULT_ACCESS,**s['inputs'].get('access_preferences',{})};out={**data,**evaluate_access(data,cfg),'data_scope':'regional_accessibility_screening','source_dataset_id':entry['meta']['dataset_id'],'method_version':'accessibility-1.0.0'}
    ports=external.get('site_screening',{}).get('data',{}).get('ports',[]);out['ports']=ports
    out['limitations']=data['limitations']+['No farm-scale wave reduction or vessel-access credit is inferred from turbine wakes.']
    return out,[entry['meta']],out['limitations']
