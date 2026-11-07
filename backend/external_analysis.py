"""Screening views of retrieved sources; no automatic site-feasibility promotion."""
from collections import Counter,defaultdict
from datetime import datetime
from pyproj import Geod
from shapely.geometry import shape
from shapely.ops import nearest_points
from .providers import PROVIDERS

GEOD=Geod(ellps='WGS84')

def regional_features(geojson,point,radius=150):
    if not point:return geojson
    from shapely.geometry import Point
    p=Point(point['lon'],point['lat']);features=[]
    for f in geojson.get('features',[]):
        if not f.get('geometry'):continue
        g=shape(f['geometry']);near=nearest_points(p,g)[1]
        distance=abs(GEOD.inv(p.x,p.y,near.x,near.y)[2])/1000
        if distance<=radius:
            features.append({**f,'properties':{**f['properties'],'reference_distance_km':round(distance,3)}})
    return {'type':'FeatureCollection','features':features}

def describe_feature(f):
    p=f['properties'];keys=['Name_Prop','NAME','name','FIELDNAME','FIELD_NAME','FIELD_NM','INSTALLATI','INST_NAME','PLATFORM_N','LICENCE_NO','LICREF','LICENCE','LICENCE_ID']
    title=next((str(p[k]) for k in keys if p.get(k) not in [None,'']),None)
    if not title:
        title=next((str(v) for k,v in p.items() if any(w in k.upper() for w in ['NAME','LICREF']) and v not in [None,'']),str(p.get('OBJECTID','Feature')))
    return {'name':title,'distance_km':p.get('reference_distance_km'),'properties':p}

def analyze_external(cid,s,external,context=None):
    """Return data, provenance, gaps for a specialist source-backed view."""
    if cid in ['C16','C48','C49','C50'] and 'environment_screening' in external:
        from .environment import analyze_environment
        return analyze_environment(cid,s,external)
    if cid=='C56':
        from .accessibility import analyze_access
        return analyze_access(s,external)
    from .overview_data import CATEGORIES as OVERVIEW_CATEGORIES
    from .work_packages import regional_model
    overview=regional_model(s,context if context is not None else {'external':external}) if cid in OVERVIEW_CATEGORIES else None
    if overview:return overview
    if cid in ['C03','C04','C05']:
        from .site_data import site_view,preference_scores
        result=site_view(cid,s,external)
        if result and cid=='C03':
            data,_,_=result;data['baseline_scores']=preference_scores(data['benchmarks'],data['preferences']['weights'],data['preferences']['year'])
        return result
    ids={'C02':'tce_wind','C13':'marine','C16':'bathymetry','C34':'neso_tec','C35':'neso_tec','C37':'tce_wind','C39':'nsta_fields','C41':'nsta_carbon','C44':'nsta_platforms'}
    pid=ids.get(cid)
    if not pid or pid not in external:return None
    src=external[pid];data=src['data'];meta=src['meta'];point=s['inputs'].get('screening_point');gaps=list(data.get('limitations',[]));provenance=[meta]
    if cid in ['C02','C37','C39','C41','C44']:
        fc=regional_features(data['geojson'],point);records=[describe_feature(f) for f in fc['features']]
        status_field='Inf_Status' if pid=='tce_wind' else next((key for key in data.get('field_names',[]) if 'STATUS' in key.upper()),None)
        counts=Counter(str(f['properties'].get(status_field) or 'Unspecified') for f in fc['features']) if status_field else Counter({'Source records':len(records)})
        result={'geojson':fc,'records':records,'record_count':len(records),'status_counts':[{'name':k,'value':v} for k,v in counts.items()],'reference_point':point,'source_fields':data.get('field_names',[]),'publisher_modified':data.get('publisher_modified'),'data_scope':meta['spatial_scope'],'radius_km':150,'distance_method':'Approximate WGS84 geodesic to nearest source geometry point; spatial nearest-point search in lon/lat. Screening only.'}
        if cid=='C37' and 'repd' in external:
            repd=external['repd'];result['repd_hornsea_records']=repd['data']['hornsea_records'];result['repd_vintage']=repd['data']['vintage_label'];provenance.append(repd['meta']);gaps+=repd['data']['limitations']
        if cid=='C02':gaps+=['Existing agreements are constraints and context; they are not evidence of vacant seabed or rights for this proposed project.']
        if cid in ['C39','C41','C44']:gaps+=['No reservoir injectivity, seal integrity, storage capacity, reuse permission or asset certification is inferred.']
    elif cid=='C13':
        result={**data,'reference_point':point,'data_scope':meta['spatial_scope']}
    elif cid=='C16':result={**data,'reference_point':point,'data_scope':meta['spatial_scope']}
    else:
        result={**data,'data_scope':meta['spatial_scope'],'grid_headroom_mw':None,'connection_offer_for_this_project':False}
    return result,provenance,gaps
