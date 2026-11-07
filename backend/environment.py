"""Publisher-backed protected-area screening and sampled seabed relief, not an EIA."""
import hashlib,io,json,math,re,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import shapefile
from pyproj import CRS,Geod,Transformer
from shapely import make_valid
from shapely.geometry import Point,Polygon,box,mapping,shape
from shapely.ops import transform,nearest_points,unary_union
from .providers import ProviderError,validate_geojson
from .site_data import COAST_URL
from .catalog import ROOT

GEOD=Geod(ellps='WGS84')
JNCC='https://data.jncc.gov.uk/data/'
SOURCES=[
 {'id':'offshore','resource':'ade43f34-54d6-4084-b66a-64f0b4a5ef27','vintage':'2025-12-03','zip':'c20251203-OffshoreMPAs-WGS84.zip','xlsx':'UKOffshoreMPAs-20251203-LIVE-WEB.xlsx','sheet':'Protected Features','scope':'UK offshore and straddling MPAs'},
 {'id':'sac','resource':'598a60db-9323-4781-b5a8-dcf0ca3b29f9','vintage':'2024-12-13','zip':'c20241213-UKSACswithMarineComponents-WGS84.zip','xlsx':'UKSACswithMarineComponents-20241213-LIVE-WEB.xlsx','sheet':'SAC Marine Interest Features','scope':'UK SACs with marine components'},
 {'id':'spa','resource':'07078ed3-496d-432b-974e-1754b47536c7','vintage':'2026-06-19','zip':'c20260619-UKSPAswithMarineComponents-WGS84.zip','xlsx':'UKSPAswithMarineComponents-20260710-LIVE-WEB.xlsx','sheet':'SPA Marine Interest Features','scope':'UK SPAs with marine components'},
]
GRID_ROOT='https://erddap.emodnet.eu/erddap/griddap/bathymetry_dtm_2024'
NE_ITEMS='https://environment.data.gov.uk/spatialdata/marine-conservation-zones-england/ogc/features/v1/collections/Marine_Conservation_Zones_England/items'
NE_RESOURCE='https://environment.data.gov.uk/dataset/c0061c93-d444-481c-a14e-653b8a8e2b1a'
LIMITATIONS=[
 'UK publisher-boundary screening, not a full EIA, conservation assessment, consent or development-rights decision.',
 'The 150 km reference disc includes land and sea; its percentage is not a percentage of UK marine waters. AOI intersection estimates use explicitly labelled display simplification.',
 'Areas dissolve overlapping designations before totals. Display boundaries are simplified at 150 m; numeric areas/distances use unsimplified geometry.',
 'JNCC inshore boundaries and qualifying features can lag country-body updates. Published qualifying features are not site survey observations, abundance or collision/noise estimates.',
 'IUCN management categories are not supplied by these JNCC datasets. SAC, SPA and MCZ types must not be converted into IUCN categories.',
 'Boundary coverage is JNCC UK marine SAC/SPA and offshore/straddling MPAs plus Natural England England MCZs. Inshore-only Scottish national MPAs, other country-level types and SSSI/ASSI are not a complete part of this inventory.',
 'EMODnet 2024 sampled elevation is metres relative to Lowest Astronomical Tide (LAT), not a geotechnical survey or navigation surface. Missing cells remain missing; vertical exaggeration is visual only.',
]

def projection(point):
    crs=CRS.from_proj4(f'+proj=laea +lat_0={point["lat"]} +lon_0={point["lon"]} +datum=WGS84 +units=m')
    return Transformer.from_crs(4326,crs,always_xy=True).transform,Transformer.from_crs(crs,4326,always_xy=True).transform

def region(point,radius_km=150):
    pts=[GEOD.fwd(point['lon'],point['lat'],a,radius_km*1000)[:2] for a in range(0,360,2)]
    return Polygon(pts)

def designation(status):
    status=str(status).upper()
    if 'HPMA' in status:return 'HPMA'
    if 'SAC' in status or status=='SCI':return 'SAC'
    if 'SPA' in status:return 'SPA'
    if 'MCZ' in status:return 'MCZ'
    if 'MPA' in status:return 'NCMPA'
    return 'Other'

def read_boundaries(raw,source,bounds):
    """No disk extraction; one bounded archive at a time, with independent seekable parts."""
    result=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist();shps=[n for n in names if n.lower().endswith('.shp')]
        if len(shps)!=1 or sum(i.file_size for i in z.infolist())>500_000_000:raise ProviderError('Unexpected protected-area archive layout/size')
        stem=shps[0][:-4]
        lookup={n.lower():n for n in names}
        def part(ext):return z.open(lookup[(stem+ext).lower()])
        with part('.prj') as f:crs=CRS.from_wkt(f.read().decode('utf-8'))
        if not crs.equals(CRS.from_epsg(4326),ignore_axis_order=True):raise ProviderError('JNCC source is not WGS84')
        # PyShp 2.3 can misread ZIP_STORED ZipExtFile header seeks on Python 3.13.
        # Independent BytesIO parts also avoid shared ZIP-stream seek state.
        streams={k:io.BytesIO(z.read(lookup[(stem+'.'+k).lower()])) for k in ['shp','dbf','shx']}
        try:
            with shapefile.Reader(**streams,encoding='utf-8',encodingErrors='replace') as reader:
                fields={f[0] for f in reader.fields[1:]}
                if not {'SITE_CODE','SITE_NAME','SITE_STATU'}<=fields:raise ProviderError('JNCC boundary field schema changed')
                for row in reader.iterShapeRecords(bbox=bounds):
                    p=row.record.as_dict();g=shape(row.shape.__geo_interface__)
                    if g.is_empty:continue
                    repaired=not g.is_valid
                    if repaired:g=make_valid(g)
                    if g.geom_type not in ['Polygon','MultiPolygon']:raise ProviderError('JNCC source contains unsupported repaired geometry')
                    if not all(math.isfinite(v) for v in g.bounds):raise ProviderError('Non-finite protected-area coordinates')
                    code=str(p['SITE_CODE']).strip()
                    if not code:raise ProviderError('Missing protected-area site code')
                    status=str(p['SITE_STATU']).strip();kind=designation(status)
                    area=p.get('AREA_HA');area=float(area)/100 if area is not None else None
                    result.append({'id':code+':'+kind,'site_code':code,'name':str(p['SITE_NAME']).strip(),'designation':kind,'publisher_status':status,'country':p.get('Country'),'agency':p.get('Agency'),'source_area_km2':area,'wdpa_code':str(p.get('WDPA_CODE') or '').removesuffix('.0'),'iucn_category':None,'iucn_coverage':'not_provided_by_source','source_id':source['id'],'source_vintage':source['vintage'],'source_url':'https://jncc.gov.uk/resources/'+source['resource'],'geometry_repaired':repaired,'geometry':g})
        finally:
            for stream in streams.values():stream.close()
    return result

def read_features(raw,source):
    from .overview_data import workbook_cells
    sheets=workbook_cells(raw)
    if source['sheet'] not in sheets:raise ProviderError('JNCC qualifying-feature sheet changed')
    cells=sheets[source['sheet']]
    if cells.get('A1')!='Site code':raise ProviderError('JNCC feature header changed')
    is_sac=source['id']=='sac';column='G' if is_sac else 'I'
    expected='Qualifying marine interest features' if is_sac else 'Marine features protected'
    if cells.get(column+'1')!=expected:raise ProviderError('JNCC feature schema changed')
    rows=[]
    for r in sorted({int(re.search(r'\d+$',key)[0]) for key in cells if re.search(r'\d+$',key)}):
        if r==1:continue
        def get(c):return str(cells.get(c+str(r)) or '').strip()
        code=get('A');feature=get(column)
        if not code or not feature:continue
        rows.append({'site_code':code,'feature_type':get('F').lower(),'specific_type':get('G') if not is_sac else '', 'feature_code':get('H') if not is_sac else '', 'feature':feature,'common_name':get('H' if is_sac else 'J'),'population_type':get('K').lower() if not is_sac else '', 'source_id':source['id'],'source_row':r,'source_url':JNCC+source['resource']+'/'+source['xlsx']})
    if not rows:raise ProviderError('JNCC qualifying-feature dataset was empty')
    return rows

def parse_grid(table,point):
    if table.get('columnNames')!=['latitude','longitude','elevation'] or table.get('columnUnits')!=['degrees_north','degrees_east','m']:raise ProviderError('EMODnet grid schema/units changed')
    rows=table.get('rows',[])
    if not rows or len(rows)>100_000:raise ProviderError('Unexpected relief grid size')
    lat=sorted({float(r[0]) for r in rows},reverse=True);lon=sorted({float(r[1]) for r in rows})
    if len(lat)<2 or len(lon)<2 or len(rows)!=len(lat)*len(lon):raise ProviderError('Incomplete/duplicate relief grid')
    if not all(math.isfinite(v) for v in lat+lon) or min(lat)<-90 or max(lat)>90 or min(lon)<-180 or max(lon)>180:raise ProviderError('Invalid relief coordinates')
    by={};valid=[]
    for a,b,v in rows:
        if (a,b) in by:raise ProviderError('Duplicate relief cell')
        if v is not None:
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not -12000<=v<=9000:raise ProviderError('Invalid elevation value')
            valid.append(v)
        by[a,b]=v
    if not valid:raise ProviderError('No valid EMODnet elevations in this region')
    dx=abs(GEOD.inv(lon[0],point['lat'],lon[1],point['lat'])[2]);dy=abs(GEOD.inv(point['lon'],lat[0],point['lon'],lat[1])[2])
    return {'width':len(lon),'height':len(lat),'longitude':lon,'latitude':lat,'elevation_m':[[by[a,b] for b in lon] for a in lat],'spacing_x_m':dx,'spacing_y_m':dy,'horizontal_spacing_m':(dx+dy)/2,'datum':'Lowest Astronomical Tide (LAT)','native_cell_degrees':1/960,'sampling_method':'ERDDAP nearest grid indices at explicit strides; not an averaged or surveyed surface','valid_cells':len(valid),'missing_cells':len(rows)-len(valid),'elevation_min_m':min(valid),'elevation_max_m':max(valid),'source_url':GRID_ROOT+'.html'}

def collect_england_mcz(fetch,bounds):
    params={'bbox':','.join(f'{v:.6f}' for v in bounds),'f':'application/geo+json','limit':100}
    url=NE_ITEMS;seen=set();features=[];expected=None
    for _ in range(30):
        if url in seen or not url.startswith(NE_ITEMS):raise ProviderError('Unexpected MCZ pagination link')
        seen.add(url);page=validate_geojson(fetch.json(url,params=params if url==NE_ITEMS else None,ttl_hours=720));features+=page['features']
        if expected is None:expected=page.get('numberMatched')
        next_url=next((link['href'] for link in page.get('links',[]) if link.get('rel')=='next'),None)
        if not next_url:break
        url=next_url
    else:raise ProviderError('MCZ pagination did not finish')
    if expected is not None and expected!='unknown' and int(expected)!=len(features):raise ProviderError('MCZ boundary response was truncated')
    out=[]
    for feature in features:
        p=feature['properties']
        if not {'mcz_code','mcz_name','status','mcz_area'}<=set(p):raise ProviderError('Natural England MCZ schema changed')
        if not str(p['mcz_code']).strip():raise ProviderError('Missing Natural England site code')
        out.append({'id':str(p['mcz_code']).strip()+':MCZ','site_code':str(p['mcz_code']).strip(),'name':p['mcz_name'],'designation':'MCZ','publisher_status':p['status'],'country':'England','agency':'Natural England','source_area_km2':float(p['mcz_area'])/100 if p['mcz_area'] is not None else None,'wdpa_code':'','iucn_category':None,'iucn_coverage':'not_provided_by_source','source_id':'natural_england_mcz','source_vintage':'dataset revision 2023-07-15; live OGC service','source_url':NE_RESOURCE,'geometry_entered_date':p.get('gis_date'),'geometry_repaired':False,'geometry':shape(feature['geometry'])})
    return out

def collect_environment(fetch,point):
    if not (-15<=point['lon']<=4.5 and 49<=point['lat']<=63):raise ProviderError('This JNCC adapter covers UK marine designations. A Danish/EU or other-region source must be collected separately; UK absence is not a no-constraints result.')
    disc=region(point);bounds=disc.bounds;all_sites={};features=[];source_notes=[]
    for source in SOURCES:
        page='https://jncc.gov.uk/resources/'+source['resource']
        fetch.get(page,ttl_hours=720)
        raw=fetch.get(JNCC+source['resource']+'/'+source['zip'],ttl_hours=720,max_bytes=75_000_000)
        for record in read_boundaries(raw,source,bounds):
            current=all_sites.get(record['id'])
            if current is None or record['source_vintage']>current['source_vintage']:all_sites[record['id']]=record
        features+=read_features(fetch.get(JNCC+source['resource']+'/'+source['xlsx'],ttl_hours=720),source)
        source_notes.append({**source,'url':page,'boundary_url':JNCC+source['resource']+'/'+source['zip'],'feature_url':JNCC+source['resource']+'/'+source['xlsx']})
    fetch.get(NE_RESOURCE,ttl_hours=720)
    for record in collect_england_mcz(fetch,bounds):
        prior=next((r for r in all_sites.values() if r['site_code']==record['site_code']),None)
        if prior:
            record.update(id=prior['id'],designation=prior['designation'],agency=prior['agency'],wdpa_code=prior['wdpa_code'])
        all_sites[record['id']]=record
    source_notes.append({'id':'natural_england_mcz','scope':'Natural England England MCZ boundaries','vintage':'dataset revision 2023-07-15; catalogue updated 2026-07-13','url':NE_RESOURCE,'boundary_url':NE_ITEMS,'feature_url':None})
    forward,inverse=projection(point);p=Point(0,0);metric_disc=transform(forward,disc);clip=box(*bounds);out=[];records=[];full=[];groups=defaultdict(list)
    joined=defaultdict(dict)
    for row in features:
        key=(row['feature_type'],row['feature'],row['population_type'])
        prior=joined[row['site_code']].get(key)
        if prior is None or (row['feature_code'] and not prior['feature_code']):joined[row['site_code']][key]=row
    for record in all_sites.values():
        g=record.pop('geometry');gm=transform(forward,g)
        if not gm.intersects(metric_disc):continue
        near=nearest_points(p,gm)[1];nl,nla=inverse(near.x,near.y);distance=abs(GEOD.inv(point['lon'],point['lat'],nl,nla)[2])/1000
        protected=gm.intersection(metric_disc);full.append(protected);groups[record['designation']].append(protected)
        interests=list(joined[record['site_code']].values())
        record.update(distance_km=distance,reference_inside=bool(g.covers(Point(point['lon'],point['lat']))),area_in_reference_disc_km2=protected.area/1e6,qualifying_features=interests,feature_coverage='source_rows_available' if interests else 'not_loaded_for_this_boundary')
        view=transform(inverse,gm.simplify(150,preserve_topology=True)).intersection(clip)
        out.append({'type':'Feature','id':record['id'],'properties':{k:v for k,v in record.items() if k!='qualifying_features'},'geometry':mapping(view)})
        records.append(record)
    records.sort(key=lambda r:r['distance_km']);union=unary_union(full) if full else Polygon()
    # Uniform index strides, bounded to roughly 160 cells per axis; retain actual returned axes.
    west,south,east,north=bounds;lat_stride=max(1,math.ceil((north-south)*960/150));lon_stride=max(1,math.ceil((east-west)*960/170))
    query=f'elevation[({south:.6f}):{lat_stride}:({north:.6f})][({west:.6f}):{lon_stride}:({east:.6f})]'
    grid_metadata=fetch.get(GRID_ROOT+'.das',ttl_hours=720).decode('utf-8')
    if 'Lowest Astronomical Tide' not in grid_metadata:raise ProviderError('EMODnet elevation datum changed')
    grid=fetch.json(GRID_ROOT+'.json?'+query,ttl_hours=720)
    terrain=parse_grid(grid['table'],point)
    # Small generalized coastline for readable maps even if online basemap tiles are unavailable.
    coastline=validate_geojson(fetch.json(COAST_URL,ttl_hours=8760));coast=[]
    for f in coastline['features']:
        g=shape(f['geometry'])
        if g.intersects(clip):
            clipped=g.intersection(clip)
            if not clipped.is_empty:coast.append({'type':'Feature','properties':{},'geometry':mapping(clipped)})
    result={'geojson':{'type':'FeatureCollection','features':out},'records':records,'record_count':len(records),'terrain':terrain,'coastline':{'type':'FeatureCollection','features':coast},'reference_point':point,'reference_disc':mapping(disc),'bounds':list(bounds),'radius_km':150,'reference_disc_area_km2':metric_disc.area/1e6,'protected_union_km2':union.area/1e6,'protected_union_pct':100*union.area/metric_disc.area,'designation_counts':[{'name':k,'value':sum(r['designation']==k for r in records),'area_union_km2':unary_union(v).area/1e6} for k,v in sorted(groups.items())],'sources':source_notes,'source_url':'https://jncc.gov.uk/our-work/uk-marine-protected-area-datasets-for-download/','publisher_modified':'JNCC boundaries 2024-12-13 / 2025-12-03 / 2026-06-19; feature table SPA 2026-07-10; EMODnet DTM 2024','license_text':'JNCC: Open Government Licence v3.0, including relevant CNCB/UKHO/Ordnance Survey copyright holders. EMODnet Bathymetry attribution and dataset use constraints preserved in raw metadata. Natural Earth is public domain.','iucn_coverage':{'supplied':0,'unknown':len(records),'note':'The JNCC source has no IUCN management category; no categories inferred.'},'limitations':LIMITATIONS}
    result['terrain_sha256']=hashlib.sha256(json.dumps(terrain,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    return result

def relief_directory(data):
    sha=hashlib.sha256(json.dumps(data['terrain'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    if data.get('terrain_sha256')!=sha:raise ProviderError('Relief terrain checksum mismatch')
    return ROOT/'data/processed/environment-relief'/sha

def build_relief(data):
    """Optional, real R renderer. Never install software or change global R from the API."""
    import subprocess,sys
    directory=relief_directory(data);directory.mkdir(parents=True,exist_ok=True)
    # Optional derivatives may be missing/corrupt after a partial restore. A bad
    # cache must not prevent a retry or invalidate the original elevation data.
    cached=relief_status(data)
    if cached.get('available'):return cached
    runtime=ROOT/'work/rayshader/runtime/app/bin/x64/Rscript.exe'
    if not runtime.is_file():return {'available':False,'note':'Rayshader runtime is not installed here; the live Three.js view still uses actual elevations.'}
    path=directory/'input.json';path.write_text(json.dumps({'terrain':data['terrain'],'geojson':data['geojson'],'reference_point':data['reference_point']}),encoding='utf-8')
    flags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0
    process=subprocess.run([sys.executable,str(ROOT/'scripts/run_environment_rayshader.py'),str(path),str(directory),'--exaggeration','8'],cwd=ROOT,capture_output=True,text=True,timeout=330,creationflags=flags)
    if process.returncode:raise ProviderError('Rayshader render failed: '+process.stderr[-700:])
    meta=json.loads((directory/'terrain-relief.metadata.json').read_text(encoding='utf-8'))
    if meta['input_md5']!=hashlib.md5(path.read_bytes()).hexdigest() or meta['width']!=data['terrain']['width'] or meta['height']!=data['terrain']['height']:raise ProviderError('Rayshader output identity mismatch')
    manifest={'terrain_sha256':data['terrain_sha256'],'renderer':'rayshader','rayshader_version':meta['rayshader_version'],'r_version':meta['r_version'],'shading_exaggeration':meta['vertical_exaggeration'],'datum':data['terrain']['datum'],'nodata_policy':meta['nodata_policy'],'files':{name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in ['terrain-relief.png','terrain-relief-preview.png','terrain-relief.metadata.json']}}
    pending=directory/'manifest.pending.json'
    pending.write_text(json.dumps(manifest,indent=2),encoding='utf-8');pending.replace(directory/'manifest.json')
    return relief_status(data)

def relief_status(data,dataset_id=None):
    # A changed source terrain is an integrity failure, not a rendering fallback.
    directory=relief_directory(data);path=directory/'manifest.json'
    if not path.exists():return {'available':False,'note':'Rayshader texture has not been generated for this terrain; Three.js uses the source elevation grid.'}
    try:
        meta=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(meta,dict) or meta.get('terrain_sha256')!=data['terrain_sha256']:raise ValueError('product scope mismatch')
        expected={'terrain-relief.png','terrain-relief-preview.png','terrain-relief.metadata.json'}
        files=meta.get('files')
        if not isinstance(files,dict) or set(files)!=expected:raise ValueError('incomplete product manifest')
        for name,sha in files.items():
            if not isinstance(sha,str) or re.fullmatch('[0-9a-f]{64}',sha) is None:raise ValueError('invalid product checksum')
            if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=sha:raise ValueError('product checksum mismatch')
        if meta.get('renderer')!='rayshader' or not all(isinstance(meta.get(k),str) and meta[k] for k in ['rayshader_version','r_version','datum','nodata_policy']):raise ValueError('incomplete renderer metadata')
        exaggeration=meta.get('shading_exaggeration')
        if isinstance(exaggeration,bool) or not isinstance(exaggeration,(int,float)) or not math.isfinite(exaggeration) or exaggeration<=0:raise ValueError('invalid shading exaggeration')
        rendered=json.loads((directory/'terrain-relief.metadata.json').read_text(encoding='utf-8'))
        if not isinstance(rendered,dict) or rendered.get('width')!=data['terrain']['width'] or rendered.get('height')!=data['terrain']['height'] or rendered.get('datum')!=data['terrain']['datum']:raise ValueError('rendered grid identity mismatch')
    except (OSError,ValueError,TypeError,KeyError) as exc:
        reason=str(exc) if isinstance(exc,ValueError) and not isinstance(exc,json.JSONDecodeError) else type(exc).__name__
        return {'available':False,'note':'The rayshader cache is unavailable; Three.js uses the source elevation grid.','warning':'Rayshader derivative cache unavailable: '+reason}
    return {**meta,'available':True,**({'texture_url':f'/api/datasets/{dataset_id}/environment-relief/terrain-relief.png','preview_url':f'/api/datasets/{dataset_id}/environment-relief/terrain-relief-preview.png','metadata_url':f'/api/datasets/{dataset_id}/environment-relief/terrain-relief.metadata.json'} if dataset_id else {})}

def analyze_environment(cid,s,external):
    entry=external.get('environment_screening')
    if not entry:return None
    import copy
    data=copy.deepcopy(entry['data']);data.update(data_scope=entry['meta']['spatial_scope'],source_dataset_id=entry['meta']['dataset_id'])
    data['relief']=relief_status(data,entry['meta']['dataset_id'])
    provenance=[entry['meta']]
    from .uk_context import uk_context
    data['uk_context']=uk_context(s,data,external)
    if 'site_screening' in external:provenance.append(external['site_screening']['meta'])
    if 'tce_wind' in external:
        from .external_analysis import regional_features
        farms=regional_features(external['tce_wind']['data']['geojson'],data['reference_point'])
        data['wind_agreements']=farms
        provenance.append(external['tce_wind']['meta'])
    if s['inputs'].get('aoi'):
        forward,inverse=projection(data['reference_point']);aoi=transform(forward,shape(s['inputs']['aoi']));hits=[]
        # Display geometry has 150 m simplification; do not pretend it is exact AOI-intersection evidence.
        for f in data['geojson']['features']:
            g=transform(forward,shape(f['geometry']));overlap=g.intersection(aoi)
            if not overlap.is_empty:hits.append({'id':f['id'],'name':f['properties']['name'],'approximate_overlap_km2':overlap.area/1e6})
        data['aoi_screening']={'intersections':hits,'method':'Approximate intersection of supplied AOI and displayed 150 m-simplified boundaries; original GIS review required.'}
    if cid in ['C48','C49','C50']:
        from .work_packages import package
        data['evidence_workspace']=package(cid,s,{'external':external})[0]['work_package']
    gaps=list(data['limitations'])
    if not s['inputs'].get('aoi'):gaps.append('No proposed AOI supplied: distances, containing designations and union area describe the reference disc, not a proposed farm footprint.')
    if cid=='C49':gaps.append('Qualifying species/features identify protected interests, not survey presence, abundance, seasonal movement, collision or noise impacts at turbine positions.')
    if cid=='C50':gaps.append('Cumulative impact and mitigation effectiveness are not inferred from coincident project/protection polygons; project-specific assessment remains open.')
    data['limitations']=gaps
    return data,provenance,gaps
