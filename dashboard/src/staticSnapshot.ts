// GitHub Pages build (VITE_STATIC_SNAPSHOT=1): answer /api requests from the exported read-only snapshot
// written by scripts/export_pages_snapshot.py. The local build leaves fetch untouched.
type Entry={file:string,type:string,gzip:boolean,status:number,filename:string|null};
type Manifest={generated_at:string,source_commit:string|null,default:{project:string,scenario:string|null,view:string}|null,entries:Record<string,Entry>,posts:Record<string,Record<string,Entry>>};
export const STATIC_SNAPSHOT=import.meta.env.VITE_STATIC_SNAPSHOT==='1';
export const ROUTE_BASE=import.meta.env.BASE_URL.replace(/\/$/,'');
const BASE=import.meta.env.BASE_URL;
const READ_ONLY='This GitHub Pages site is a read-only snapshot. Calculations, saving and data collection need the local studio; see the README.';
const MISSING='This item is not included in the GitHub Pages snapshot. Run the local studio to open it.';
const nativeFetch=window.fetch.bind(window);
let manifest:Promise<Manifest>|undefined;
function load(){return manifest??=nativeFetch(BASE+'snapshot/manifest.json').then(r=>{if(!r.ok)throw Error('The snapshot manifest could not be loaded');return r.json();});}
// Decompress only when the bytes are still gzip, in case a host already applied Content-Encoding.
async function open(entry:Entry){
  const r=await nativeFetch(BASE+'snapshot/'+entry.file);if(!r.ok)throw Error('Snapshot file is missing: '+entry.file);
  const bytes=new Uint8Array(await r.arrayBuffer()),stream=new Blob([bytes]).stream();
  return entry.gzip&&bytes[0]===0x1f&&bytes[1]===0x8b?stream.pipeThrough(new DecompressionStream('gzip')):stream;
}
function problem(status:number,detail:string){return new Response(JSON.stringify({detail}),{status,headers:{'Content-Type':'application/json'}});}
// Images and source files are linked from JSON responses; point those links at their static copies.
function relink(text:string,m:Manifest){return text.replace(/"(\/api\/[^"]+)"/g,(all,path:string)=>{const e=m.entries[path];return e&&!e.gzip?JSON.stringify(BASE+'snapshot/'+e.file):all;});}
async function respond(entry:Entry,m:Manifest){
  const stream=await open(entry),headers={'Content-Type':entry.type};
  if(entry.type!=='application/json')return new Response(stream,{status:entry.status,headers});
  return new Response(relink(await new Response(stream).text(),m),{status:entry.status,headers});
}
async function snapshotFetch(input:RequestInfo|URL,init?:RequestInit):Promise<Response>{
  const url=new URL(input instanceof Request?input.url:String(input),location.href);
  if(url.origin!==location.origin||!url.pathname.startsWith('/api/'))return nativeFetch(input,init);
  init?.signal?.throwIfAborted();
  const m=await load(),method=(init?.method||(input instanceof Request?input.method:'GET')).toUpperCase();
  if(method==='GET'){const e=m.entries[url.pathname+url.search];return e?respond(e,m):problem(404,MISSING);}
  const e=m.posts[url.pathname]?.[typeof init?.body==='string'?init.body:''];
  return e?respond(e,m):problem(403,READ_ONLY);
}
// Download links (reports, CSV/JSON exports) point at /api; serve the exported file under its original name.
async function download(path:string){
  const m=await load(),e=m.entries[path];
  if(!e||e.status!==200){window.alert(e?await new Response(await open(e)).json().then((d:{detail?:string})=>d.detail||MISSING,()=>MISSING):MISSING);return;}
  const href=URL.createObjectURL(new Blob([await new Response(await open(e)).blob()],{type:e.type})),a=document.createElement('a');
  a.href=href;a.download=e.filename||path.split('/').pop()||'download';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(href),30000);
}
function intercept(event:MouseEvent){const a=(event.target as Element|null)?.closest?.('a[href^="/api/"]');if(!a||event.button>1)return;event.preventDefault();void download(a.getAttribute('href')!);}
function repository(){const owner=location.hostname.endsWith('.github.io')?location.hostname.split('.')[0]:'';return import.meta.env.VITE_REPO_URL||(owner?`https://github.com/${owner}/${ROUTE_BASE.slice(1)}`:'https://github.com');}
function note(text:string,m?:Manifest){
  const box=document.createElement('div'),link=document.createElement('a');box.className='snapshot-note';box.setAttribute('role','note');
  const date=m?new Date(m.generated_at).toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'}):'';
  link.href=repository()+'#readme';link.textContent='run it locally';box.append(text.replace('{date}',date),link,'.');document.body.prepend(box);
}
export const snapshotReady:Promise<void>=STATIC_SNAPSHOT?load().then(m=>{
  window.fetch=snapshotFetch;document.addEventListener('click',intercept,true);document.addEventListener('auxclick',intercept,true);
  if(m.default&&!/\/projects\//.test(location.pathname))history.replaceState({},'',`${BASE}projects/${m.default.project}/${m.default.view}${m.default.scenario?'?scenario='+m.default.scenario:''}`);
  note('Read-only snapshot exported {date}: browse every saved revision, chart and 3D view. To calculate, save or collect data, ',m);
},error=>note(`The snapshot data could not be loaded (${error.message}). To use the studio, `)):Promise.resolve();
