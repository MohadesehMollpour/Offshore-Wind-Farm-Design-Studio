"""Public read-only data adapters. Endpoints and metadata verified 2026-11-01.

All coordinates are screening references. Nothing here certifies a proposed site.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import math
import re
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
from pyproj import Geod
from shapely.geometry import shape

from .engine import digest, now
from .engineering import finite, parse_wind, wind_summary

PROVIDERS = {
    'access_metocean': {'name':'Historical accessibility wind, waves, currents and daylight','categories':['C56'],'kind':'joint_historical_model_screening','refresh_hours':168,'docs':'https://open-meteo.com/en/docs/marine-weather-api','license':'CC BY 4.0; Open-Meteo educational access; Copernicus/ECMWF/Meteo-France attribution retained','attribution':'Open-Meteo / ERA5 / ERA5-Ocean / Copernicus Marine / Meteo-France.','point_required':True},
    'operations_wind': {'name':'Recent operational wind history via ERA5','categories':['C07'],'kind':'recent_hourly_reanalysis','refresh_hours':168,'docs':'https://open-meteo.com/en/docs/historical-weather-api','license':'CC BY 4.0; educational non-commercial access','attribution':'Open-Meteo.com / ERA5 / Copernicus Climate Change Service.','point_required':True},
    'overview_inputs': {'name':'UK cost benchmarks and IEA 15 MW turbine curve','categories':['C21','C26','C27','C29','C58','C59','C60','C61'],'kind':'published_reference_model_inputs','refresh_hours':720,'docs':'https://www.gov.uk/government/publications/electricity-generation-costs-2025','license':'DESNZ Open Government Licence v3.0; turbine archive BSD-3-Clause (preserved)','attribution':'DESNZ / Arup; IEA Wind Task 37 / NREL turbine archive.','point_required':False},
    'site_screening': {'name':'Coast, ports and vessel-density screening','categories':['C03','C04','C05'],'kind':'published_multisource_screening','refresh_hours':720,'docs':'https://emodnet.ec.europa.eu/en/human-activities','license':'EMODnet CC BY 4.0; Natural Earth public domain; individual component licences retained','attribution':'EMODnet Human Activities / Cogea / Eurostat; Made with Natural Earth.','point_required':True},
    'tce_wind': {'name':'The Crown Estate wind-site agreements','categories':['C02','C37'],'kind':'published_GIS','refresh_hours':168,'docs':'https://www.thecrownestate.co.uk/about-us/freedom-of-information','license':'The Crown Estate Open Data Licence (GIS) v1.1','attribution':'Contains data provided by The Crown Estate that is protected by copyright and database rights.','item':'22a1be6fb0c5416e9369f97743f387b1','owner':'TheCrownEstate','point_required':False},
    'repd': {'name':'DESNZ Renewable Energy Planning Database','categories':['C37'],'kind':'quarterly_register','refresh_hours':168,'docs':'https://www.gov.uk/government/publications/renewable-energy-planning-database-quarterly-extract','license':'Open Government Licence v3.0; see original publication','attribution':'Contains public sector information licensed under the Open Government Licence v3.0.','point_required':False},
    'era5_wind': {'name':'ERA5 wind via Open-Meteo','categories':['C07','C08','C09'],'kind':'historical_reanalysis','refresh_hours':720,'docs':'https://open-meteo.com/en/docs/historical-weather-api','license':'CC BY 4.0; free endpoint for non-commercial educational use','attribution':'Weather data by Open-Meteo.com; ERA5 / Copernicus Climate Change Service.','point_required':True},
    'marine': {'name':'Open-Meteo marine forecast','categories':['C13'],'kind':'forecast','refresh_hours':6,'docs':'https://open-meteo.com/en/docs/marine-weather-api','license':'CC BY 4.0; free endpoint for non-commercial educational use','attribution':'Weather data by Open-Meteo.com; underlying wave model as documented by provider.','point_required':True},
    'bathymetry': {'name':'EMODnet bathymetry','categories':['C16'],'kind':'published_DTM','refresh_hours':720,'docs':'https://emodnet.ec.europa.eu/en/emodnet-web-service-documentation','license':'CC BY 4.0 (EMODnet data product); not for navigation','attribution':'EMODnet Bathymetry consortium; data product owned by the EU, CC BY 4.0.','point_required':True},
    'neso_tec': {'name':'NESO Transmission Entry Capacity register','categories':['C34','C35'],'kind':'connection_register','refresh_hours':72,'docs':'https://www.neso.energy/data-portal/transmission-entry-capacity-tec-register','license':'NESO Open Data Licence','attribution':'National Energy System Operator, TEC Register.','point_required':False},
    'nsta_fields': {'name':'NSTA offshore hydrocarbon fields','categories':['C39'],'kind':'published_GIS','refresh_hours':168,'docs':'https://www.nstauthority.co.uk/data-and-insights/about-nsta-data/how-to-access-our-data/','license':'As stated in preserved NSTA ArcGIS item metadata','attribution':'Contains North Sea Transition Authority information; see item licence.','item':'ba711a4be08449329a871d37ae910735','owner':'NSTA_GIS','point_required':True},
    'nsta_platforms': {'name':'NSTA offshore infrastructure surface points','categories':['C44'],'kind':'published_GIS','refresh_hours':168,'docs':'https://www.nstauthority.co.uk/data-and-insights/about-nsta-data/how-to-access-our-data/','license':'As stated in preserved NSTA ArcGIS item metadata','attribution':'Contains North Sea Transition Authority information; see item licence.','item':'a97ed4fcd8b34ef2b4527957114cda46','owner':'NSTA_GIS','point_required':True},
    'nsta_carbon': {'name':'NSTA current carbon-storage licence polygons','categories':['C41'],'kind':'published_GIS','refresh_hours':168,'docs':'https://www.nstauthority.co.uk/regulatory-information/carbon-storage/carbon-storage-public-register/','license':'As stated in preserved NSTA ArcGIS item metadata','attribution':'Contains North Sea Transition Authority information; see item licence.','item':'ae0b0c44c6214112a0612ee66cf493dc','owner':'NSTA_GIS','point_required':True},
}

# No caller-supplied URL is fetched. Metadata-discovered downloads stay on these hosts.
ALLOWED_HOSTS={'www.gov.uk','assets.publishing.service.gov.uk','www.arcgis.com','services2.arcgis.com','services-eu1.arcgis.com','archive-api.open-meteo.com','marine-api.open-meteo.com','ows.emodnet-bathymetry.eu','api.neso.energy'}
ALLOWED_HOSTS.update({'ows.emodnet-humanactivities.eu','raw.githubusercontent.com'})
ALLOWED_HOSTS.update({'jncc.gov.uk','data.jncc.gov.uk','erddap.emodnet.eu','environment.data.gov.uk'})
PROVIDERS['environment_screening']={'name':'JNCC / Natural England protection, qualifying features and EMODnet relief','categories':['C16','C48','C49','C50'],'kind':'published_environmental_screening','refresh_hours':720,'docs':'https://jncc.gov.uk/our-work/uk-marine-protected-area-datasets-for-download/','license':'JNCC / CNCBs and Natural England Open Government Licence v3.0; EMODnet data attribution and use constraints preserved','attribution':'Contains JNCC, Natural England and country nature conservation body data, including Ordnance Survey rights; EMODnet Bathymetry consortium / EU; Natural Earth public domain.','point_required':True}

class ProviderError(ValueError): pass

class Fetcher:
    """Small bounded GET client with raw-response preservation and request cache."""
    def __init__(self, root:Path, force=False, transport=None):
        self.root=Path(root);self.force=force;self.assets=[];self.warnings=[];self.cache_hits=0
        self.client=httpx.Client(timeout=httpx.Timeout(50,connect=15),follow_redirects=False,transport=transport,headers={'User-Agent':'OffshoreWindStudio/0.2 (educational regional screening)','Accept':'application/json, application/xml, text/csv, text/html;q=0.8'})
    def close(self): self.client.close()
    def get(self,url,params=None,ttl_hours=24,max_bytes=25_000_000):
        if type(max_bytes) is not int or not 1<=max_bytes<=100_000_000:raise ProviderError('Invalid configured response size limit')
        key=digest({'url':url,'params':params or {}})
        cache=self.root/'http_cache'/f'{key}.json'
        prior=None
        if cache.exists():
            try:
                prior=json.loads(cache.read_text(encoding='utf-8'))
                p=self.root/prior['path']
                if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=prior['sha256']:prior=None
            except (OSError,ValueError,KeyError):prior=None
        def cached(stale=False):
            if prior.get('bytes',0)>max_bytes:raise ProviderError('Cached provider response exceeds the configured limit')
            self.assets.append(prior);self.cache_hits+=1
            if stale:self.warnings.append('STALE: provider failed; reused a preserved response from '+prior['retrieved_at'])
            return (self.root/prior['path']).read_bytes()
        if prior and not self.force:
            age=datetime.now(timezone.utc)-datetime.fromisoformat(prior['retrieved_at'])
            if age.total_seconds()<ttl_hours*3600:return cached()
        last=''
        for attempt in range(3):
            try:
                current=url;response=None
                for _ in range(5):
                    target=urlparse(current)
                    if target.scheme!='https' or target.hostname not in ALLOWED_HOSTS:raise ProviderError('Provider URL is outside the configured HTTPS allowlist')
                    response=self.client.get(current,params=params if current==url else None)
                    if response.status_code in [301,302,303,307,308]:
                        from urllib.parse import urljoin
                        current=urljoin(str(response.url),response.headers['location']);continue
                    break
                if response is None or response.is_redirect:raise ProviderError('Too many provider redirects')
                if response.status_code==429 or response.status_code>=500:
                    last=f'Provider HTTP {response.status_code}'
                    if attempt<2:time.sleep(min(4,2**attempt));continue
                response.raise_for_status()
                if len(response.content)>max_bytes:raise ProviderError('Provider response exceeds the configured size limit')
                content=response.content;sha=hashlib.sha256(content).hexdigest();path=Path('external_raw')/f'{sha}.bin';dest=self.root/path;dest.parent.mkdir(parents=True,exist_ok=True)
                if not dest.exists():dest.write_bytes(content)
                asset={'url':str(response.url),'retrieved_at':now(),'sha256':sha,'path':path.as_posix(),'bytes':len(content),'content_type':response.headers.get('content-type',''),'etag':response.headers.get('etag'),'last_modified':response.headers.get('last-modified')}
                cache.parent.mkdir(parents=True,exist_ok=True);tmp=cache.with_name(key+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(asset,indent=2),encoding='utf-8');tmp.replace(cache)
                self.assets.append(asset);return content
            except (httpx.HTTPError,OSError,ProviderError) as exc:
                last=str(exc)
                if isinstance(exc,ProviderError):break
                if isinstance(exc,httpx.HTTPStatusError) and exc.response.status_code<500 and exc.response.status_code!=429:break
                if attempt<2:time.sleep(min(4,2**attempt))
        if prior:return cached(stale=True)
        raise ProviderError('Source retrieval failed: '+last)
    def json(self,url,params=None,ttl_hours=24):
        raw=self.get(url,params,ttl_hours)
        try:j=json.loads(raw)
        except ValueError as exc:raise ProviderError('Provider returned non-JSON content') from exc
        if isinstance(j,dict) and (j.get('error') or j.get('success') is False):raise ProviderError('Provider returned an application error: '+str(j.get('error') or j.get('reason'))[:350])
        return j

def plain(value):return html.unescape(re.sub('<[^>]+>',' ',value or '')).strip()
def iso_millis(v):return datetime.fromtimestamp(v/1000,timezone.utc).isoformat() if v else None
def check_point(point):
    if not point:raise ProviderError('A source-backed regional reference point or user AOI is required')
    finite(point.get('lat'),'latitude',-80,84);finite(point.get('lon'),'longitude',-180,180)
    return point
def validate_geojson(j):
    if j.get('type')!='FeatureCollection' or not isinstance(j.get('features'),list):raise ProviderError('Expected a GeoJSON FeatureCollection')
    crs=j.get('crs')
    if crs and crs.get('properties',{}).get('name') not in ['EPSG:4326','urn:ogc:def:crs:OGC:1.3:CRS84','urn:ogc:def:crs:EPSG::4326']:raise ProviderError('Source GeoJSON CRS is not WGS84 longitude/latitude')
    for feature in j['features']:
        if not feature.get('geometry'):continue
        g=shape(feature['geometry'])
        if g.is_empty or not g.is_valid:raise ProviderError('Source returned an empty or invalid geometry')
        if not(-180<=g.bounds[0]<=g.bounds[2]<=180 and -90<=g.bounds[1]<=g.bounds[3]<=90):raise ProviderError('Source geometry is not longitude/latitude EPSG:4326')
    return j

def arcgis(fetch:Fetcher,pid,point=None,radius_km=150):
    cfg=PROVIDERS[pid];item=fetch.json(f'https://www.arcgis.com/sharing/rest/content/items/{cfg["item"]}',{'f':'json'},cfg['refresh_hours'])
    if item.get('owner')!=cfg['owner']:raise ProviderError('ArcGIS dataset owner differs from the configured publisher')
    service_url=item.get('url','');service=fetch.json(service_url,{'f':'json'},cfg['refresh_hours'])
    layers=service.get('layers',[])
    if len(layers)!=1:raise ProviderError('Expected one published feature layer; review source schema')
    layer=service_url+'/'+str(layers[0]['id']);meta=fetch.json(layer,{'f':'json'},cfg['refresh_hours'])
    params={'f':'json','where':'1=1','returnIdsOnly':'true'}
    if point:
        check_point(point);delta=radius_km/111.32;dlon=delta/max(.2,math.cos(math.radians(point['lat'])))
        params.update(geometry=json.dumps({'xmin':point['lon']-dlon,'ymin':point['lat']-delta,'xmax':point['lon']+dlon,'ymax':point['lat']+delta,'spatialReference':{'wkid':4326}}),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects')
    ids=fetch.json(layer+'/query',params,cfg['refresh_hours']).get('objectIds',[])
    ids=sorted(ids or [])
    if len(ids)>10000:raise ProviderError('Source selection exceeds 10,000 features; narrow the search')
    features=[];batch=min(1000,int(meta.get('maxRecordCount',1000)))
    for start in range(0,len(ids),batch):
        page=fetch.json(layer+'/query',{'f':'geojson','objectIds':','.join(map(str,ids[start:start+batch])),'outFields':'*','outSR':4326,'returnGeometry':'true'},cfg['refresh_hours'])
        validate_geojson(page)
        if page.get('exceededTransferLimit'):raise ProviderError('ArcGIS response was truncated; narrower paging is required')
        features.extend(page['features'])
    if len(features)!=len(ids):raise ProviderError('ArcGIS record count changed during retrieval; refresh the source')
    return {'geojson':{'type':'FeatureCollection','features':features},'feature_count':len(features),'query_extent':'regional bounding envelope' if point else 'England, Wales and Northern Ireland published wind agreements','radius_km':radius_km if point else None,'field_names':[x['name'] for x in meta.get('fields',[])],'publisher_item_id':cfg['item'],'publisher_owner':item['owner'],'publisher_modified':iso_millis(item.get('modified')),'license_text':plain(item.get('licenseInfo')),'attribution':plain(item.get('accessInformation')) or cfg['attribution'],'source_url':f'https://www.arcgis.com/home/item.html?id={cfg["item"]}','feature_service_url':layer,'limitations':['Bounding-envelope discovery is not an AOI intersection or permitted development area.','Reported status is publisher metadata, not an independent commercial or engineering certification.']}

def reference_from_wind(data,dataset_id):
    # Existing official Hornsea polygon is a reference, never a proposed site.
    f=next((f for f in data['geojson']['features'] if f['properties'].get('Name_Prop')=='Hornsea 1 (Centre)'),None)
    if not f:raise ProviderError('Official Hornsea 1 (Centre) agreement polygon not found; select another reference')
    p=shape(f['geometry']).representative_point()
    return {'lat':p.y,'lon':p.x,'label':'Hornsea 1 (Centre) existing lease reference','source_dataset_id':dataset_id,'source_feature_id':f['properties']['OBJECTID'],'source_url':data['source_url'],'method':'Interior representative point of the official existing wind-site agreement polygon','scope':'regional_reference_only','is_proposed_site':False}

def repd(fetch):
    cfg=PROVIDERS['repd'];page=fetch.get(cfg['docs'],ttl_hours=168).decode('utf-8')
    links=re.findall(r'href="(https://assets\.publishing\.service\.gov\.uk/[^\"]+\.csv)"',page)
    if not links:raise ProviderError('No official CSV download found on the REPD publication page')
    url=html.unescape(links[0]);raw=fetch.get(url,ttl_hours=168)
    try:text=raw.decode('utf-8-sig')
    except UnicodeDecodeError:text=raw.decode('cp1252')
    reader=csv.DictReader(io.StringIO(text));required={'Site Name','Technology Type','Ref ID','Development Status','Installed Capacity (MWelec)'}
    if not required.issubset(reader.fieldnames or []):raise ProviderError('REPD CSV schema changed')
    rows=[r for r in reader if r['Technology Type'].strip()=='Wind Offshore']
    hornsea=[r for r in rows if 'hornsea' in r['Site Name'].lower()]
    if not hornsea:raise ProviderError('No Hornsea offshore records found in REPD')
    return {'records':rows,'hornsea_records':hornsea,'record_count':len(rows),'download_url':url,'vintage_label':url.rsplit('/',1)[-1],'limitations':['Quarterly planning-register snapshot, not live operating status.','Capacity, turbine count and turbine rating may refer to different planning revisions; do not assume they reconcile.','REPD coordinates can be approximate, duplicated or onshore reference points. They are not AOI or lease geometry.']}

def era5(fetch,point,start,end):
    check_point(point);a=date.fromisoformat(start);b=date.fromisoformat(end)
    if a>b or (b-a).days>1826 or a<date(1940,1,1) or b>date.today()-timedelta(days=7):raise ProviderError('Choose 1–5 years of historical dates between 1940 and at least seven days ago')
    params={'latitude':round(point['lat'],6),'longitude':round(point['lon'],6),'start_date':start,'end_date':end,'hourly':'wind_speed_10m,wind_direction_10m,wind_speed_100m,wind_direction_100m','wind_speed_unit':'ms','timezone':'GMT','models':'era5','cell_selection':'sea','elevation':'nan'}
    j=fetch.json('https://archive-api.open-meteo.com/v1/archive',params,720);h=j.get('hourly',{});times=h.get('time',[])
    if j.get('utc_offset_seconds')!=0:raise ProviderError('ERA5 API did not return UTC')
    expected=((b-a).days+1)*24
    if len(times)!=expected:raise ProviderError(f'ERA5 coverage incomplete: {len(times)} of {expected} hours')
    heights={}
    for height in [10,100]:
        speed=h.get(f'wind_speed_{height}m',[]);direction=h.get(f'wind_direction_{height}m',[])
        if len(speed)!=expected or len(direction)!=expected:raise ProviderError('Wind arrays do not match the requested time axis')
        if j.get('hourly_units',{}).get(f'wind_speed_{height}m')!='m/s':raise ProviderError('Wind speed units are not m/s')
        if j.get('hourly_units',{}).get(f'wind_direction_{height}m') not in ['°','degree','degrees']:raise ProviderError('Wind direction units are not degrees')
        text='timestamp_utc,wind_speed_ms,direction_deg,hub_height_m\n'+'\n'.join(f'{t}+00:00,{v},{d},{height}' for t,v,d in zip(times,speed,direction))
        try:rows=parse_wind(text)
        except ValueError as exc:raise ProviderError('Invalid ERA5 series: '+str(exc)) from exc
        if rows[0]['timestamp_utc']!=start+'T00:00:00+00:00' or rows[-1]['timestamp_utc']!=end+'T23:00:00+00:00':raise ProviderError('ERA5 returned a different date interval from the requested period')
        heights[str(height)]={'rows':rows,'summary':wind_summary(rows)}
    return {'heights':heights,'start_date':start,'end_date':end,'sample_hours':expected,'grid_point':{'lat':j['latitude'],'lon':j['longitude']},'requested_point':point,'horizontal_resolution':'ERA5 0.25° grid; provider-selected sea cell','models':'era5','measurement_type':'reanalysis','units':j['hourly_units'],'limitations':['Regional gridded reanalysis, not a physical sensor or bankable wind assessment.','10 m and 100 m only; no implicit extrapolation to the assumed 150 m turbine hub.','This reference point is not the proposed wind-farm AOI.']}

def marine(fetch,point):
    check_point(point)
    j=fetch.json('https://marine-api.open-meteo.com/v1/marine',{'latitude':round(point['lat'],6),'longitude':round(point['lon'],6),'hourly':'wave_height,wave_period,wave_direction','forecast_days':7,'timezone':'GMT','cell_selection':'sea'},6)
    h=j.get('hourly',{});times=h.get('time',[])
    if not times or j.get('utc_offset_seconds')!=0:raise ProviderError('Marine API returned no UTC hourly timeline')
    if j.get('hourly_units',{}).get('wave_height')!='m' or j.get('hourly_units',{}).get('wave_period')!='s':raise ProviderError('Unexpected marine units')
    if any(len(h.get(k,[]))!=len(times) for k in ['wave_height','wave_period','wave_direction']):raise ProviderError('Marine arrays have inconsistent lengths')
    rows=[];missing=0
    for t,height,period,direction in zip(times,h['wave_height'],h['wave_period'],h['wave_direction']):
        if height is None or period is None or direction is None:missing+=1;continue
        rows.append({'timestamp_utc':t+'+00:00','wave_height_m':finite(height,'wave height',0,50),'wave_period_s':finite(period,'wave period',0,60),'wave_direction_deg':finite(direction,'wave direction',0,360)})
    if not rows:raise ProviderError('Marine API returned only missing values at the requested point')
    return {'rows':rows,'record_count':len(rows),'missing_count':missing,'grid_point':{'lat':j['latitude'],'lon':j['longitude']},'measurement_type':'forecast','start':times[0]+'+00:00','end':times[-1]+'+00:00','limitations':['Seven-day model forecast; not an observed or long-term wave climate.','No installation weather-window, safety or monthly access conclusion can be inferred from this short forecast.']}

def bathymetry(fetch,point):
    check_point(point);url='https://ows.emodnet-bathymetry.eu/wms'
    xml=ET.fromstring(fetch.get(url,{'service':'WMS','request':'GetCapabilities','version':'1.3.0'},720));ns={'w':'http://www.opengis.net/wms'}
    layers=[e.findtext('w:Name',namespaces=ns) for e in xml.findall('.//w:Layer',ns)]
    if 'emodnet:mean' not in layers:raise ProviderError('EMODnet mean-depth layer is no longer advertised')
    p=point;params={'service':'WMS','version':'1.1.1','request':'GetFeatureInfo','layers':'emodnet:mean','query_layers':'emodnet:mean','srs':'EPSG:4326','bbox':f'{p["lon"]-.01},{p["lat"]-.01},{p["lon"]+.01},{p["lat"]+.01}','width':101,'height':101,'x':50,'y':50,'info_format':'application/json','feature_count':1}
    j=fetch.json(url,params,720);features=j.get('features',[])
    if not features or features[0].get('properties',{}).get('Depth') is None:raise ProviderError('EMODnet returned no valid depth at the reference point')
    depth=finite(features[0]['properties']['Depth'],'signed DTM depth',-12000,9000)
    return {'signed_dtm_value_m':depth,'water_depth_m':-depth if depth<0 else None,'point':point,'layer':'emodnet:mean','wms_url':url,'layer_titles':[e.findtext('w:Title',namespaces=ns) for e in xml.findall('.//w:Layer',ns) if e.findtext('w:Name',namespaces=ns)=='emodnet:mean'],'limitations':['Single DTM raster-cell query; no bathymetric survey, slope or seabed cross-section.','Negative published Depth is below the product datum; reference-datum and source quality require review.','Not for navigation or foundation design.']}

def neso(fetch):
    base='https://api.neso.energy/api/3/action/'
    j=fetch.json(base+'package_show',{'id':'cbd45e54-e6e2-4a38-99f1-8de6fd96d7c1'},72);package=j['result']
    resource=next((r for r in package['resources'] if r.get('name')=='TEC Register' and r.get('datastore_active')),None)
    if not resource:raise ProviderError('NESO current TEC datastore resource not found')
    records=[];offset=0
    while True:
        page=fetch.json(base+'datastore_search',{'resource_id':resource['id'],'q':'Hornsea','limit':1000,'offset':offset},72)['result']
        records.extend(page['records']);offset+=len(page['records'])
        if offset>=page['total']:break
        if not page['records'] or offset>10000:raise ProviderError('NESO paging did not complete')
    return {'records':records,'record_count':len(records),'resource_id':resource['id'],'publisher_modified':package.get('metadata_modified'),'source_url':'https://www.neso.energy/data-portal/transmission-entry-capacity-tec-register','license_url':package.get('license_url'),'resource_description':plain(resource.get('description')),'limitations':['Hornsea name-filtered register records, not spare grid headroom or an offer to connect this project.','Stages, technology types and cumulative capacities may duplicate or overlap; do not sum cumulative rows.','Register status can differ from planning/lease records; retain the original vintages and labels.']}

def collect(pid,fetch,point=None,start='2025-01-01',end='2025-12-31',radius_km=150):
    if pid not in PROVIDERS:raise ProviderError('Unknown data provider')
    if pid=='environment_screening':
        from .environment import collect_environment
        return collect_environment(fetch,check_point(point))
    if pid=='access_metocean':
        from .accessibility import collect_access
        return collect_access(fetch,check_point(point))
    if pid=='operations_wind':
        from .wind_history import recent_complete_year
        a,b=recent_complete_year()
        data=era5(fetch,point,a,b);data['period_selection']='Latest twelve whole calendar months ending before the ERA5 seven-day availability allowance.'
        data['limitations']+=['Hourly wind-only planning context; no gust, wave or vessel/task approval is inferred.']
        return data
    if pid=='overview_inputs':
        from .overview_data import collect_overview
        return collect_overview(fetch)
    if pid=='site_screening':
        from .site_data import collect_site_screening
        return collect_site_screening(fetch,check_point(point))
    if pid=='repd':return repd(fetch)
    if pid=='era5_wind':return era5(fetch,point,start,end)
    if pid=='marine':return marine(fetch,point)
    if pid=='bathymetry':return bathymetry(fetch,point)
    if pid=='neso_tec':return neso(fetch)
    return arcgis(fetch,pid,None if pid=='tce_wind' else check_point(point),radius_km)
