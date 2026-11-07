"""Imported user references are contextual snapshots, separate from provider evidence."""
import hashlib,json,math,re
from .catalog import ROOT
from .engine import digest

REFERENCE_DIR=ROOT/'sources/references/hornsea_farms'

def validate_farms(data):
    if not isinstance(data,dict) or not isinstance(data.get('farms'),list) or not isinstance(data.get('mapOnly'),list):raise ValueError('Expected embedded farms/mapOnly reference arrays')
    farms=data['farms']+data['mapOnly'];ids=set()
    if len(farms)>200:raise ValueError('Reference contains too many farms')
    for f in farms:
        if not isinstance(f.get('id'),str) or f['id'] in ids:raise ValueError('Reference farm IDs must be unique strings')
        ids.add(f['id'])
        if f.get('status') not in ['operating','construction','consented','discontinued'] or f.get('zone') not in ['hornsea','dogger','wash','norfolk']:raise ValueError('Unexpected reference status or zone')
        for key in ['name','owner','model','year','note']:
            if f.get(key) is not None and (not isinstance(f[key],str) or len(f[key])>500):raise ValueError('Invalid reference text')
        for key in ['lat','lon','mw','areaKm2','coastKm','distKm','bearing','cf12','cflife','turbines','gwh']:
            value=f.get(key)
            if value is not None and (isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value)):raise ValueError('Invalid reference numeric value')
        if not -90<=f['lat']<=90 or not -180<=f['lon']<=180:raise ValueError('Reference coordinates outside WGS84')
        for key in ['cf12','cflife']:
            if f.get(key) is not None and not 0<=f[key]<=100:raise ValueError('Capacity factor outside 0–100%')
        if f.get('path') and not re.fullmatch(r'[MmLlHhVvCcSsQqTtAaZz0-9eE+.,\s-]+',f['path']):raise ValueError('Reference contains an invalid SVG path')
    if not re.fullmatch(r'[MmLlHhVvCcSsQqTtAaZz0-9eE+.,\s-]+',data['map']['land']):raise ValueError('Reference coastline is not a plain SVG path')
    return data

def load_hornsea_reference():
    path=REFERENCE_DIR/'reference.json'
    if not path.exists():return None
    record=json.loads(path.read_text(encoding='utf-8'))
    if digest(record['data'])!=record['metadata']['data_sha256']:raise ValueError('Hornsea reference data checksum mismatch')
    validate_farms(record['data'])
    return record

def original_reference():
    record=load_hornsea_reference()
    if not record:raise KeyError('Hornsea reference is not imported')
    path=(REFERENCE_DIR/record['metadata']['original_filename']).resolve()
    if not path.is_relative_to(REFERENCE_DIR.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=record['metadata']['original_sha256']:raise ValueError('Original attached page checksum mismatch')
    return path
