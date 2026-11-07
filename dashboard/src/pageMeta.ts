// Per-route <title> and meta description. Static fallbacks (keep in sync with DEFAULT_META) live in index.html for crawlers that do not run JavaScript.
export const SITE='Offshore Wind Farm Design Studio';
export const DEFAULT_META={title:'Offshore Wind Farm Design Studio · UK planning workspace',description:'Evidence-led UK offshore wind planning aid: compare screening regions and layouts, explore a 3D digital twin and trace sources across 70 work packages.'};
const AID='a local offshore wind planning aid, not an approved design';
// Page names match the sidebar labels; descriptions state what the view shows without claiming completed engineering.
const VIEWS:Record<string,[string,string]>={
 overview:['Management overview','Compare five UK offshore wind screening regions and five layout strategies, with a linked 3D preview and energy and cost evidence.'],
 twin:['Digital twin (3D view)','Explore the selected layout in 3D: turbine selection, wind-direction yaw and historical-hour replay. Illustrative, not an engineering model.'],
 packages:['Work package readiness','Audit all 70 offshore wind work packages: which have working calculations or tools and which still lack engineering evidence.'],
 compare:['Compare scenarios','Compare saved offshore wind design revisions side by side, with their assumptions, sources and evidence gaps kept visible.'],
 evidence:['Evidence & assessment','Source hierarchy, checksums and coverage of the 16 assessment topics for a UK offshore wind study. Shows available evidence, not awarded marks.'],
 data:['Data sources & APIs','Collect and inspect public UK offshore wind data, with provider, licence, retrieval time and checksum recorded for each preserved source.'],
 history:['Changes & revisions','Browse saved design revisions and the change log. Every change creates a new revision that keeps its inputs, provenance and results.']};
// First candidate within the limit; otherwise the last one cut at a word boundary.
const fit=(options:string[],max:number)=>options.find(s=>s.length<=max)||options[options.length-1].slice(0,max-1).replace(/\s+\S*$/,'')+'…';
export function pageMeta(view:string,cat?:{id:string,title:string},domain?:string):{title:string,description:string}{
 if(cat){const name=`${cat.id} ${cat.title}`;return {title:fit([`${name} · ${SITE}`,`${name} · Wind Farm Design Studio`,name],60),description:fit([...(domain?[`${name} (${domain}): inputs, sources, assumptions and evidence gaps. Part of ${AID}.`]:[]),`${name}: inputs, sources, assumptions and evidence gaps. Part of ${AID}.`,`${name}: inputs, sources and evidence gaps. Local UK offshore wind planning aid, not an approved design.`],155)};}
 const page=VIEWS[view];return page?{title:`${page[0]} · ${SITE}`,description:page[1]}:DEFAULT_META;}
export function applyPageMeta({title,description}:{title:string,description:string}){
 document.title=title;
 for(const [attr,key,value] of [['name','description',description],['property','og:title',title],['property','og:description',description],['name','twitter:title',title],['name','twitter:description',description]] as const)document.head.querySelector(`meta[${attr}="${key}"]`)?.setAttribute('content',value);}
