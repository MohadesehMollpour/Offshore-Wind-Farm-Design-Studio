"""Monthly wind distributions and explicitly scoped operational screening."""
import calendar,math
from datetime import date,timedelta

PLOT_DEFAULTS={'period':'recent','height_m':10,'threshold_height_m':10,'sailing_limit_ms':12,'om_limit_ms':10,'unit':'ms','threshold_basis':'Illustrative planning limits; replace with vessel/task-approved limits.'}
GUIDANCE_URL='https://www.energyinst.org/technical/publications/sectors/renewables/good-practice-guideline-offshore-wind-farm-transfer'

def recent_complete_year(today=None):
    cutoff=(today or date.today())-timedelta(days=7)
    end=cutoff.replace(day=1)-timedelta(days=1)
    start_year=end.year-1 if end.month<12 else end.year
    start_month=end.month+1 if end.month<12 else 1
    return date(start_year,start_month,1).isoformat(),end.isoformat()

def quantile(values,p):
    if not values:return None
    rank=(len(values)-1)*p;lo=math.floor(rank);hi=math.ceil(rank)
    return values[lo]+(values[hi]-values[lo])*(rank-lo)

def month_boxes(rows,start,end):
    groups={};y,m=map(int,start[:7].split('-'))
    while f'{y:04}-{m:02}'<=end[:7]:
        groups[f'{y:04}-{m:02}']=[]
        y,m=(y+1,1) if m==12 else (y,m+1)
    for row in rows:
        if start<=row['timestamp_utc'][:10]<=end and row['timestamp_utc'][:7] in groups:groups[row['timestamp_utc'][:7]].append(row['speed'])
    result=[]
    for key,values in groups.items():
        values.sort();y,m=map(int,key.split('-'));expected=calendar.monthrange(y,m)[1]*24
        q1,median,q3=[quantile(values,p) for p in [.25,.5,.75]]
        if values:
            iqr=q3-q1;inside=[v for v in values if q1-1.5*iqr<=v<=q3+1.5*iqr]
            low,high=inside[0],inside[-1];outliers=[v for v in values if v<low or v>high]
        else:low=high=None;outliers=[]
        result.append({'month':key,'label':calendar.month_abbr[m],'n':len(values),'expected_hours':expected,'missing_hours':max(0,expected-len(values)),'q1_ms':q1,'median_ms':median,'q3_ms':q3,'whisker_low_ms':low,'whisker_high_ms':high,'outliers_ms':outliers,'values_ms':values,'mean_ms':sum(values)/len(values) if values else None})
    return result

def boxplot_data(s,context):
    external=context.get('external',{});sets=[];provenance=[]
    if context.get('wind'):
        rows=context['wind'];meta=context['wind_meta'];heights={str(rows[0]['height']):{'rows':rows}};sources=[('imported',heights,meta)]
    else:
        sources=[(pid,external[pid]['data']['heights'],external[pid]['meta']) for pid in ['operations_wind','era5_wind'] if pid in external]
    for pid,heights,meta in sources:
        provenance.append(meta)
        first=next(iter(heights.values()))['rows'];start,end=first[0]['timestamp_utc'][:10],first[-1]['timestamp_utc'][:10]
        periods=[]
        if pid=='operations_wind':periods.append(('recent','Latest twelve complete available months',start,end))
        for year in range(int(start[:4]),int(end[:4])+1):
            a,b=f'{year}-01-01',f'{year}-12-31'
            if start<=a and end>=b:periods.append((str(year),str(year)+' calendar year',a,b))
        if not periods:periods=[('sample','Imported sample (coverage may be partial)',start,end)]
        for period,label,a,b in periods:
            for height,entry in heights.items():
                identity=f'{period}:{float(height):g}'
                if any(x['id']==identity for x in sets):continue
                months=month_boxes(entry['rows'],a,b)
                sets.append({'id':identity,'period':period,'label':label,'height_m':float(height),'start':a,'end':b,'months':months,'source_dataset_id':meta['dataset_id'],'source_name':meta.get('source_name'),'sample_hours':sum(x['n'] for x in months),'missing_hours':sum(x['missing_hours'] for x in months)})
    if not sets:return {},[]
    periods=list(dict.fromkeys(x['period'] for x in sets));default='recent' if 'recent' in periods else max(periods)
    prefs={**PLOT_DEFAULTS,'period':default,**s['inputs'].get('wind_plot_preferences',{})}
    if prefs['period'] not in periods:prefs['period']=default
    heights=sorted({x['height_m'] for x in sets if x['period']==prefs['period']})
    if prefs['height_m'] not in heights:prefs['height_m']=heights[0]
    return {'boxplot_sets':sets,'wind_plot_preferences':prefs,'boxplot_method':'Q1, median and Q3 use linear interpolation at rank (n−1)p. Whiskers end at observed values within 1.5×IQR of Q1/Q3. Values outside the whiskers are plotted as outliers. UTC calendar months; missing hours are not filled.','operational_guidance_url':GUIDANCE_URL,'threshold_limitations':['Default 12 m/s sailing and 10 m/s O&M lines are illustrative planning assumptions, not published universal safe limits.','Limits are compared only at their declared reference height. 10 m wind cannot be treated as turbine hub-height wind.','Hourly reanalysis cannot resolve gusts or establish a safe voyage, transfer or maintenance window.','Wave height, period/direction, currents, visibility, vessel response, task duration and approved procedures must also be assessed.']},provenance
