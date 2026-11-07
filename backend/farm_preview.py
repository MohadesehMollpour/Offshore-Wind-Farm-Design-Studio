"""Planning geometry and an explicit hub-point Jensen wake illustration."""
import math,random,json
from pyproj import CRS,Transformer

def arrangement(s,layout_result=None,prevailing_from=270):
    i=s['inputs'];n=round(i['capacity_mw']/i['turbine_mw']);D=i['rotor_diameter_m'];height=i['hub_height_m'];source=(layout_result or {}).get('data',{}).get('turbines',[])
    point=i.get('screening_point');origin=point or {'lat':0,'lon':0}
    if source:
        lon=sum(t['lon'] for t in source)/len(source);lat=sum(t['lat'] for t in source)/len(source);crs=CRS.from_proj4(f'+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m');tr=Transformer.from_crs(4326,crs,always_xy=True)
        turbines=[{'id':t['id'],'x_m':tr.transform(t['lon'],t['lat'])[0],'y_m':tr.transform(t['lon'],t['lat'])[1],'lat':t['lat'],'lon':t['lon']} for t in source];basis='Selected snapshot C23 computed turbine coordinates; engineering and rights remain unverified.'
    else:
        cols=math.ceil(math.sqrt(n)*1.1);sx=i['spacing_d']*D;sy=i['cross_spacing_d']*D;angle=i['rotation_deg']
        if s['layout_id']=='LAYOUT_03':angle=(90-prevailing_from)%360
        rng=random.Random(i['seed']);raw=[]
        for index in range(n):
            row,col=divmod(index,cols);x=col*sx;y=row*sy
            if s['layout_id']=='LAYOUT_02' and row%2:x+=sx/2
            if s['layout_id']=='LAYOUT_04':x+=rng.uniform(-.12,.12)*sx;y+=rng.uniform(-.12,.12)*sy
            if s['layout_id']=='LAYOUT_05' and col>=cols//2:x+=4*D
            raw.append((x,y))
        cx=sum(x for x,y in raw)/n;cy=sum(y for x,y in raw)/n;a=math.radians(angle)
        turbines=[{'id':f'T{j+1:03}','x_m':(x-cx)*math.cos(a)-(y-cy)*math.sin(a),'y_m':(x-cx)*math.sin(a)+(y-cy)*math.cos(a),'lat':None,'lon':None} for j,(x,y) in enumerate(raw)]
        basis='Conceptual arrangement from turbine count, spacing and layout strategy. C23 turbine positions are unavailable; surveyed positions are not established; irregular preview does not solve constraints.'
    return {'turbines':turbines,'count':len(turbines),'rotor_diameter_m':D,'hub_height_m':height,'turbine_mw':i['turbine_mw'],'layout_id':s['layout_id'],'reference_point':point,'basis':basis,'conceptual':not bool(source),'scenario_id':s['id'],'scenario_hash':s['hash']}

def wake_factors(turbines,diameter,wind_from_deg,ct=.8,k=.04):
    direction=math.radians(wind_from_deg);dx,dy=-math.sin(direction),-math.cos(direction);a=1-math.sqrt(1-ct);out=[]
    for t in turbines:
        deficits=[]
        for other in turbines:
            x,y=t['x_m']-other['x_m'],t['y_m']-other['y_m'];along=x*dx+y*dy;cross=abs(x*dy-y*dx)
            if along>1e-6 and cross<diameter/2+k*along:deficits.append(a/(1+2*k*along/diameter)**2)
        deficit=min(.9,math.sqrt(sum(v*v for v in deficits)));out.append({'id':t['id'],'wind_ratio':1-deficit,'upstream_wakes':len(deficits),'downwind_position_m':t['x_m']*dx+t['y_m']*dy})
    return out

def preview(s,results,wind_ms=10,wind_from_deg=270,hs_m=1.5,tp_s=8,wave_from_deg=270,ct=.8,k=.04):
    from .catalog import load
    sectors=results.get('C08',{}).get('data',{}).get('sectors',[]);prevailing=max(sectors,key=lambda r:r['frequency_pct'])['direction_deg'] if sectors else 270
    out=arrangement(s,results.get('C23'),prevailing);factors=wake_factors(out['turbines'],out['rotor_diameter_m'],wind_from_deg,ct,k);byid={f['id']:f for f in factors}
    site=next((x for x in load('sites') if x['id']==s['site_id']),{});strategy=next((x for x in load('layouts') if x['id']==s['layout_id']),{})
    out.update(site_id=s['site_id'],site_name=s['inputs'].get('site_name') or site.get('name') or 'Custom study area',jurisdiction=s['inputs'].get('jurisdiction') or site.get('jurisdiction'),layout_name=strategy.get('name',s['layout_id']),scenario_revision=s['revision'] if 'revision' in s else None)
    out['turbines']=[{**t,**byid[t['id']],'model_hub_wind_ms':wind_ms*byid[t['id']]['wind_ratio'],'ambient_hs_m':hs_m} for t in out['turbines']]
    out.update(wind_ms=wind_ms,wind_from_deg=wind_from_deg,hs_m=hs_m,tp_s=tp_s,wave_from_deg=wave_from_deg,ct=ct,wake_expansion=k,wake_method='Illustrative hub-point Jensen top-hat wakes, constant Ct, root-sum-square deficits, capped at 90%. No wake-added turbulence, blockage, stability or validated farm calibration.',wave_method='Regional Hs is uniform across the layout; farm-scale wave shelter is not resolved. Ocean animation is a procedural visualization, not a hydrodynamic solution.',access_credit_from_wakes=False)
    return out
