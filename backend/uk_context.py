"""UK cartographic context and an explicit user location preference; no site approval."""
import copy,hashlib,json,math
from functools import lru_cache
from .catalog import ROOT
from .providers import ProviderError
from .environment import projection
from shapely.geometry import shape,mapping,box,Point
from shapely.ops import transform,unary_union

@lru_cache(maxsize=1)
def cartography():
    folder=ROOT/'sources/references/uk_cartography'
    raw=(folder/'uk-land.geojson').read_bytes();meta=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if hashlib.sha256(raw).hexdigest()!=meta['derived_sha256']:raise ProviderError('UK cartographic context checksum mismatch')
    return json.loads(raw),meta

def uk_context(s,data,external):
    land,meta=cartography();point=data['reference_point'];forward,inverse=projection(point)
    uk=shape(next(f['geometry'] for f in land['features'] if f['properties']['code']=='GBR'))
    preference=copy.deepcopy(s['inputs'].get('location_preferences'))
    site=external.get('site_screening');coast=None;ports=[];benchmarks=[]
    if site:
        raw=site['data'];candidate=raw.get('coast')
        # Existing matched 1:10m coast distance is reused only with a UK land-country check.
        if candidate and transform(forward,uk).distance(Point(*forward(candidate['lon'],candidate['lat'])))<=5000:coast=copy.deepcopy(candidate)
        ports=[copy.deepcopy(p) for p in raw.get('ports',[]) if p.get('country') in ['UK','GB','United Kingdom']][:8]
        benchmarks=copy.deepcopy(raw.get('benchmarks',[]))
    limit=preference['max_coast_km'] if preference else None
    status='not_set' if limit is None else 'unavailable' if coast is None else 'within_limit' if coast['distance_km']<=limit else 'outside_limit'
    # Explicitly cartographic band, clipped to regional source extent. Never used for distance tests.
    b=data['bounds'];context_bounds=[min(b[0],point['lon']-3.8),b[1]-.35,b[2],b[3]+.25]
    band=None
    if limit is not None:
        all_land=unary_union([transform(forward,shape(f['geometry'])) for f in land['features']])
        sea_band=transform(forward,uk).buffer(limit*1000).difference(all_land).intersection(transform(forward,box(*context_bounds)))
        band={'type':'Feature','properties':{'method':'Approximate cartographic offshore band from Natural Earth 1:50m UK land; not an eligibility polygon'},'geometry':mapping(transform(inverse,sea_band).simplify(.003,preserve_topology=True))}
    for ref in benchmarks:ref['within_distance_preference']=None if limit is None else ref.get('coast_km') is not None and ref['coast_km']<=limit
    return {'land':land,'regional_land':{'type':'FeatureCollection','features':[{**f,'geometry':mapping(shape(f['geometry']).intersection(box(*context_bounds)))} for f in land['features'] if shape(f['geometry']).intersects(box(*context_bounds))]},'cartography_source':meta,'coast':coast,'ports':ports,'benchmarks':benchmarks,'preference':preference,'preference_status':status,'coastal_band':band,'context_bounds':context_bounds,'labels':[{'name':'UNITED KINGDOM','lon':-1.4,'lat':54.4},{'name':'East Yorkshire','lon':-.65,'lat':54.05},{'name':'Norfolk','lon':.65,'lat':52.65},{'name':'NORTH SEA','lon':2.5,'lat':54.65}], 'distance_note':'Generalized 1:10m coastline and straight-line distance, not a surveyed boundary or navigable route; source-country checked against 1:50m UK land.'}
