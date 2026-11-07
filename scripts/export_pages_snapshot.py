"""Export a read-only GitHub Pages snapshot of the studio API from a copy of the local database.

The live database is only read (copied with SQLite's backup API). Every exported response is stored
content-addressed under the output folder; text is gzip-compressed and decompressed in the browser.
Course materials served by /api/sources/ are deliberately excluded from the public snapshot.
"""
import argparse,gzip,hashlib,json,os,re,shutil,sqlite3,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REFERENCE_SCENARIO='05c163c0-c50f-412c-bdbf-324d0ae9cf04'
# The embedded overview preview posts '{}'; the full twin posts its initial parameters (Farm3D.tsx `initial`).
TWIN_BODIES=['{}','{"wind_ms":10,"wind_from_deg":270,"hs_m":1.5,"tp_s":8,"wave_from_deg":270,"ct":0.8,"k":0.04}']
EXTENSIONS={'application/json':'.json','text/csv':'.csv','text/markdown':'.md','text/plain':'.txt','image/png':'.png','image/svg+xml':'.svg','application/pdf':'.pdf','application/x-yaml':'.yaml','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':'.xlsx'}
TEXT={'application/json','text/csv','text/markdown','text/plain','application/x-yaml'}
FOLLOW=re.compile(r'^/api/(datasets/[^/]+/(files/[^/]+|environment-relief/[^/]+|download\.json)|references/[a-z-]+/original)$')
PRIVATE=re.compile(r'^/api/sources/')
MAX_BYTES=25_000_000

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'pages_snapshot')
    parser.add_argument('--download-revisions',default='19,20',help='Comma-separated revisions whose report, CSV, JSON and dataset downloads are included')
    args=parser.parse_args()
    downloads={int(r) for r in args.download_revisions.split(',') if r.strip()}
    (ROOT/'work').mkdir(exist_ok=True)
    scratch=Path(tempfile.mkdtemp(prefix='pages-export-',dir=ROOT/'work'));db=scratch/'snapshot.sqlite'
    source=sqlite3.connect(f'file:{(ROOT/"data/studio.sqlite").as_posix()}?mode=ro',uri=True);target=sqlite3.connect(db)
    source.backup(target);target.close();source.close()
    os.environ['WIND_STUDIO_DB']=str(db);sys.path.insert(0,str(ROOT))
    from fastapi.testclient import TestClient
    from backend.app import app
    out=args.output.resolve()
    if out.exists():shutil.rmtree(out)
    (out/'files').mkdir(parents=True)
    entries,posts,skipped=[{},{},[]]
    def store(response):
        ctype=response.headers.get('content-type','application/octet-stream').split(';')[0].strip()
        body=response.content;name=hashlib.sha256(body).hexdigest()[:24]+EXTENSIONS.get(ctype,'.bin')
        compressed=ctype in TEXT
        if compressed:name+='.gz'
        path=out/'files'/name
        if not path.exists():path.write_bytes(gzip.compress(body,9,mtime=0) if compressed else body)
        disposition=re.search(r'filename="([^"]+)"',response.headers.get('content-disposition',''))
        return {'file':'files/'+name,'type':ctype,'gzip':compressed,'status':response.status_code,'filename':disposition.group(1) if disposition else None}
    def links(value,found):
        if isinstance(value,str) and value.startswith('/api/'):found.add(value)
        elif isinstance(value,list):[links(v,found) for v in value]
        elif isinstance(value,dict):[links(v,found) for v in value.values()]
        return found
    with TestClient(app) as client:
        def get(path,required=True):
            if path in entries or PRIVATE.match(path):return None
            response=client.get(path)
            if required and response.status_code!=200:raise RuntimeError(f'{path} returned {response.status_code}: {response.text[:300]}')
            if len(response.content)>MAX_BYTES:skipped.append(f'{path} ({len(response.content)/1e6:.1f} MB)');return None
            entries[path]=store(response)
            if response.status_code==200 and response.headers.get('content-type','').startswith('application/json'):
                for link in sorted(links(response.json(),set())):
                    if FOLLOW.match(link):get(link,required=False)
                    elif not PRIVATE.match(link) and link not in entries:skipped.append(f'{link} (not followed)')
                return response.json()
            return None
        for path in ['/api/catalog','/api/providers','/api/references/hornsea-farms','/api/references/lattice-supply','/api/references/lattice-supply/data.json','/api/references/lattice-supply/original']:get(path,required=False)
        projects=get('/api/projects');default=None;scenario_count=0
        for project in projects:
            pid=project['id'];scenarios=get(f'/api/projects/{pid}/scenarios');get(f'/api/projects/{pid}/history')
            for job in get(f'/api/projects/{pid}/data-jobs'):get(f'/api/data-jobs/{job["id"]}',required=False)
            for site in sorted({s['site_id'] for s in scenarios}):get(f'/api/projects/{pid}/datasets?site_id={site}')
            for s in scenarios:
                sid=s['id'];scenario_count+=1
                if sid==REFERENCE_SCENARIO:default={'project':pid,'scenario':sid,'view':'overview'}
                get(f'/api/scenarios/{sid}');get(f'/api/scenarios/{sid}/readiness',required=False);bound=get(f'/api/scenarios/{sid}/datasets')
                for body in TWIN_BODIES:
                    response=client.post(f'/api/scenarios/{sid}/farm-preview',content=body,headers={'Content-Type':'application/json'})
                    posts.setdefault(f'/api/scenarios/{sid}/farm-preview',{})[body]=store(response)
                if s['revision'] in downloads:
                    for path in [f'/api/scenarios/{sid}/export.json',f'/api/scenarios/{sid}/report.md',f'/api/scenarios/{sid}/accessibility/history.csv']:get(path,required=False)
                    for category in json.loads((ROOT/'config/categories.json').read_text(encoding='utf-8')):get(f'/api/scenarios/{sid}/categories/{category["id"]}/export.csv',required=False)
                    for item in bound:get(f'/api/datasets/{item["dataset_id"]}/download.json',required=False)
        if not default and projects:default={'project':projects[0]['id'],'scenario':None,'view':'overview'}
    commit=subprocess.run(['git','-c',f'safe.directory={ROOT.as_posix()}','rev-parse','--short','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip() or None
    manifest={'format':1,'generated_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'source_commit':commit,'default':default,'scenarios':scenario_count,
              'note':'Read-only export of the local studio API. Course materials (/api/sources/) are excluded. POST requests other than the recorded twin previews are unavailable.',
              'entries':entries,'posts':posts}
    (out/'manifest.json').write_text(json.dumps(manifest,separators=(',',':'),sort_keys=True),encoding='utf-8')
    shutil.rmtree(scratch,ignore_errors=True)
    size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    private=[p.name for p in (out/'files').iterdir() if p.suffix=='.gz' and re.search(rb'[A-Za-z]:(?:\\\\|\\|/)Users',gzip.decompress(p.read_bytes()))]
    print(f'Exported {len(entries)} GET responses and {sum(map(len,posts.values()))} recorded twin previews for {scenario_count} scenarios to {out} ({size/1e6:.1f} MB on disk).')
    if skipped:print('Not exported:',*sorted(set(skipped))[:40],sep='\n  ')
    if private:print('WARNING: local user paths found in',*private,sep='\n  ')

if __name__=='__main__':main()
