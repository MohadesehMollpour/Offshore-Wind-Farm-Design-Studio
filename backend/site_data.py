"""Source-backed C03/C04/C05 reference comparisons and spatial screening."""
import math
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

from pyproj import CRS,Geod,Transformer
from shapely.geometry import Point,shape,mapping,box
from shapely.ops import transform,nearest_points,unary_union

from .providers import arcgis,validate_geojson,finite,ProviderError

GEOD=Geod(ellps='WGS84')
HUMAN_WMS='https://ows.emodnet-humanactivities.eu/wms'
COAST_URL='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_coastline.geojson'
DENSITY_UNITS='vessel-hours/km²/month (annual mean)'

def metric_transform(point):
    crs=CRS.from_proj4(f'+proj=aeqd +lat_0={point["lat"]} +lon_0={point["lon"]} +datum=WGS84 +units=m')
    return Transformer.from_crs(4326,crs,always_xy=True).transform,Transformer.from_crs(crs,4326,always_xy=True).transform

def coast_distance(point,coast):
    forward,inverse=metric_transform(point);p=Point(*forward(point['lon'],point['lat']))
    projected=transform(forward,coast);near=nearest_points(p,projected)[1];lon,lat=inverse(near.x,near.y)
    km=abs(GEOD.inv(point['lon'],point['lat'],lon,lat)[2])/1000
    return {'distance_km':km,'lon':lon,'lat':lat,'method':'Nearest point in local azimuthal-equidistant projection; endpoint WGS84 geodesic distance','source_scale':'Natural Earth 1:10 million generalized coastline'}

def point_distance(a,b):return abs(GEOD.inv(a['lon'],a['lat'],b['lon'],b['lat'])[2])/1000

def density_point(fetch,point,year):
    # CRS:84 and WMS 1.1.1 are explicit longitude/latitude, independently of EPSG axis rules.
    lon,lat=round(point['lon'],6),round(point['lat'],6)
    params={'service':'WMS','version':'1.1.1','request':'GetFeatureInfo','layers':'vesseldensity_allavg','query_layers':'vesseldensity_allavg','srs':'EPSG:4326','bbox':f'{lon-.003},{lat-.003},{lon+.003},{lat+.003}','width':101,'height':101,'x':50,'y':50,'info_format':'application/json','feature_count':1,'time':f'{year}-01-01T00:00:00Z'}
    j=fetch.json(HUMAN_WMS,params,720);features=j.get('features',[])
    value=features[0].get('properties',{}).get('GRAY_INDEX') if features else None
    if value is None:return None
    try:value=finite(value,'vessel density')
    except ValueError as exc:raise ProviderError(str(exc)) from exc
    if value<0:return None  # Negative raster NoData must not be presented as zero traffic.
    if value>1e7:raise ProviderError('Vessel density is outside a plausible published range')
    return value

def collect_site_screening(fetch,point):
    coast=validate_geojson(fetch.json(COAST_URL,ttl_hours=8760))
    clip=box(point['lon']-5,point['lat']-3,point['lon']+5,point['lat']+3)
    lines=[shape(f['geometry']).intersection(clip) for f in coast['features'] if shape(f['geometry']).intersects(clip)]
    if not lines:raise ProviderError('No coastline coverage near this reference; expand the source extent')
    coastline=unary_union(lines)
    # WFS 1.0 uses x/y coordinate order for the geographic BBOX.
    ports=validate_geojson(fetch.json('https://ows.emodnet-humanactivities.eu/wfs',{'service':'WFS','version':'1.0.0','request':'GetFeature','typeName':'emodnet:portlocations','outputFormat':'application/json','srsName':'EPSG:4326','bbox':f'{point["lon"]-4},{point["lat"]-2},{point["lon"]+2},{point["lat"]+2}','maxFeatures':1000},720))
    if ports.get('numberMatched',len(ports['features'])) not in [len(ports['features']),'unknown']:raise ProviderError('Port response was truncated')
    port_records=[]
    for feature in ports['features']:
        p=feature['properties'];g=shape(feature['geometry'])
        if g.geom_type!='Point':continue
        target={'id':str(p.get('port_id') or feature.get('id')),'name':p.get('portname') or p.get('port') or 'Published port','lon':g.x,'lat':g.y,'kind':'port','source':'EMODnet main ports','country':p.get('country')}
        target['distance_km']=point_distance(point,target)
        if target['distance_km']<=350:port_records.append(target)
    port_records.sort(key=lambda x:x['distance_km'])
    if not port_records:raise ProviderError('No published ports within 350 km of the screening reference')
    wind=arcgis(fetch,'tce_wind')
    expected=['Hornsea 1 (Centre)','Hornsea Project 2 - Phase 1 (Breesea)','Hornsea Project 3 (HOW03)','Hornsea 4']
    benchmark=[]
    for name in expected:
        f=next((f for f in wind['geojson']['features'] if f['properties'].get('Name_Prop')==name),None)
        if f is None:continue
        g=shape(f['geometry']);p=g.representative_point()
        if point_distance(point,{'lon':p.x,'lat':p.y})>250:continue
        reference={'id':f'REF_{f["properties"]["OBJECTID"]}','name':name,'lon':p.x,'lat':p.y,'geometry':f['geometry'],'source_feature_id':f['properties']['OBJECTID'],'eligibility':'reference_only_existing_agreement','lease_status':f['properties'].get('Lease_Stat'),'published_status':f['properties'].get('Inf_Status')}
        reference['coast_km']=coast_distance(reference,coastline)['distance_km']
        nearest=min(port_records,key=lambda target:point_distance(reference,target));reference['port_km']=point_distance(reference,nearest);reference['nearest_port']=nearest['name']
        benchmark.append(reference)
    xml=ET.fromstring(fetch.get(HUMAN_WMS,{'service':'WMS','version':'1.3.0','request':'GetCapabilities'},720));ns={'w':'http://www.opengis.net/wms'}
    layer=next((l for l in xml.findall('.//w:Layer',ns) if l.findtext('w:Name',namespaces=ns)=='vesseldensity_allavg'),None)
    if layer is None:raise ProviderError('The annual all-vessel-density layer is not advertised')
    dimension=layer.find('w:Dimension[@name="time"]',ns)
    advertised=dimension.text if dimension is not None else ''
    years=[year for year in [2023,2024] if str(year) in advertised]
    if not years:raise ProviderError('Expected AIS density vintages are no longer advertised; review the source')
    # 5×5 regular reference sampling grid, 10 km offsets; this is not a permitted AOI.
    samples=[];forward,inverse=metric_transform(point)
    for row in range(5):
        for col in range(5):
            x=(col-2)*10000;y=(row-2)*10000;lon,lat=inverse(x,y)
            samples.append({'id':f'S{row*5+col+1:02}','name':f'Cell {row+1},{col+1}','lon':lon,'lat':lat,'offset_east_km':x/1000,'offset_north_km':y/1000,'density':{}})
    for ref in benchmark:ref['density']={}
    tasks=[(sample,year) for sample in samples+benchmark for year in years]
    def query(task):
        sample,year=task
        try:return sample,str(year),density_point(fetch,sample,year),None
        except Exception as exc:return sample,str(year),None,str(exc)[:300]
    errors=[]
    with ThreadPoolExecutor(max_workers=4) as executor:
        for sample,year,value,error in executor.map(query,tasks):
            sample['density'][year]=value
            if error:errors.append({'sample_id':sample['id'],'year':year,'error':error})
    if not any(v is not None for s in samples for v in s['density'].values()):raise ProviderError('No valid shipping-density samples returned; no traffic exposure can be calculated')
    coast_result=coast_distance(point,coastline)
    coast_target={'id':'COAST','name':'Nearest generalized coastline','kind':'coast',**coast_result}
    return {'reference_point':point,'coastline':mapping(coastline),'coast':coast_target,'ports':port_records,'grid_points':[],'grid_coordinates_status':'not_connected','grid_gap':'The TEC register supplies connection-site names but no operator-verified coordinates. No grid distance or headroom is invented.','benchmarks':benchmark,'samples':samples,'years':years,'default_year':2023 if 2023 in years else years[0],'wms_url':HUMAN_WMS,'wms_layer':'vesseldensity_allavg','density_units':DENSITY_UNITS,'density_grid_spacing_km':10,'density_cell_count':25,'query_errors':errors,'aviation_status':'not_connected','components':[{'name':'Natural Earth coastline 1:10 million','url':COAST_URL,'licence':'Public domain','limitation':'Generalized cartographic coastline, not a survey or marine-route network.'},{'name':'EMODnet main ports','url':'https://emodnet.ec.europa.eu/en/human-activities','licence':'CC BY 4.0','limitation':'Published port locations; completeness and wind-port capabilities not verified.'},{'name':'EMODnet vessel density','url':'https://ows.emodnet-humanactivities.eu/geonetwork/srv/api/records/0f2f3ff1-30ef-49e1-96e7-8ca78d58a07c','licence':'CC BY 4.0','limitation':'Vessel-hours/km²/month, annual average. 2024 lost satellite coverage from June; avoid direct interannual trend inference.'},{'name':'The Crown Estate wind-site agreements','url':wind['source_url'],'licence':'The Crown Estate Open Data Licence (GIS) v1.1','limitation':'Existing agreements used as reference benchmarks only, not new development candidates.'}],'limitations':['Regional reference screening; no proposed AOI, environmental consent or available seabed is established.','Geodesic coast/port distances are not navigable sea routes, export cable routes or vessel access times.','AIS samples are 25 raster-cell point queries on a 10 km-spaced grid, not an area-weighted AOI exposure or collision-risk assessment.','A missing AIS value is unavailable, not zero traffic.','2024 satellite coverage decreased from June; 2023 is the default comparison vintage.','Operator-verified substation coordinates and aviation restrictions remain unavailable.','Reference-area preference scores do not override existing leases, environmental exclusions or unassessed hard constraints.']}

def site_view(cid,s,external):
    if 'site_screening' not in external:return None
    entry=external['site_screening'];data=entry['data'];out={**data,'data_scope':entry['meta']['spatial_scope']}
    out['preferences']=s['inputs'].get('site_preferences') or {'weights':{'port_km':40,'coast_km':30,'shipping':30},'year':data['default_year'],'density_threshold':1.0,'vessel_speed_knots':20}
    out['grid_connection_names']=sorted({r.get('Connection Site') for r in external.get('neso_tec',{}).get('data',{}).get('records',[]) if r.get('Connection Site')})
    return out,[entry['meta']],list(data['limitations'])

def preference_scores(benchmarks,weights,year):
    keys=['port_km','coast_km','shipping'];rows=[]
    for b in benchmarks:
        values={'port_km':b.get('port_km'),'coast_km':b.get('coast_km'),'shipping':b.get('density',{}).get(str(year))}
        rows.append({'id':b['id'],'values':values,'eligible':False})
    total=sum(weights.get(k,0) for k in keys)
    if total<=0:raise ValueError('At least one positive preference weight is required')
    for r in rows:
        missing=any(r['values'][k] is None and weights.get(k,0)>0 for k in keys)
        r['score']=None if missing else 0.0
        if missing:continue
        for key in keys:
            if not weights.get(key,0):continue
            vals=[x['values'][key] for x in rows if x['values'][key] is not None];lo,hi=min(vals),max(vals)
            normalized=.5 if hi==lo else (hi-r['values'][key])/(hi-lo)
            r['score']+=100*weights[key]/total*normalized
    return sorted(rows,key=lambda r:-(r['score'] if r['score'] is not None else -1))
