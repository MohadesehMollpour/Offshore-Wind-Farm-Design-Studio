import {useEffect, useRef, useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

type Obj=Record<string,any>;
const COLORS:Obj={SAC:'#02a5bb',SPA:'#edae32',MCZ:'#7f9f28',HPMA:'#926ac5',NCMPA:'#5aaa67',Other:'#8b9aa2'};

export function EnvironmentTerrain({data,selected,types,onSelect,exaggeration,showWater,showFarms}:{data:Obj,selected:string,types:string[],onSelect:(id:string)=>void,exaggeration:number,showWater:boolean,showFarms:boolean}){
 const host=useRef<HTMLDivElement>(null),latest=useRef({selected,types,onSelect,exaggeration,showWater,showFarms}),reset=useRef<()=>void>(()=>{}),[error,setError]=useState('');
 latest.current={selected,types,onSelect,exaggeration,showWater,showFarms};
 useEffect(()=>{
  const node=host.current;if(!node)return;let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});}catch{setError('WebGL is unavailable. Use the 2D map and the downloadable rayshader render.');return;}
  const scene=new THREE.Scene();scene.background=new THREE.Color('#eaf2f3');scene.fog=new THREE.Fog('#eaf2f3',85,180);
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;node.appendChild(renderer.domElement);
  const camera=new THREE.PerspectiveCamera(36,1,.05,300),controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.maxPolarAngle=Math.PI*.475;controls.minDistance=5;controls.maxDistance=110;
  const t=data.terrain,w=t.width,h=t.height,lat=t.latitude as number[],lon=t.longitude as number[];
  const midLat=(lat[0]+lat[h-1])/2,midLon=data.uk_context?(data.uk_context.context_bounds[0]+data.uk_context.context_bounds[2])/2:(lon[0]+lon[w-1])/2,scale=10000;
  const toXY=(p:number[])=>[(p[0]-midLon)*111320*Math.cos(midLat*Math.PI/180)/scale,(p[1]-midLat)*111132/scale];
  const spanX=(lon[w-1]-lon[0])*111320*Math.cos(midLat*Math.PI/180)/scale,spanZ=(lat[0]-lat[h-1])*111132/scale,span=Math.max(spanX,spanZ,data.uk_context?(data.uk_context.context_bounds[2]-data.uk_context.context_bounds[0])*111320*Math.cos(midLat*Math.PI/180)/scale:0);
  reset.current=()=>{camera.position.set(span*.25,span*.95,span*1.05);controls.target.set(0,-.55,0);controls.update();};reset.current();
  scene.add(new THREE.HemisphereLight('#ffffff','#7795a1',2.3));const sun=new THREE.DirectionalLight('#fff1d7',3.1);sun.position.set(-20,35,14);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-25;sun.shadow.camera.right=25;sun.shadow.camera.top=25;sun.shadow.camera.bottom=-25;scene.add(sun);
  const pos=new Float32Array(w*h*3),colors=new Float32Array(w*h*3),uv=new Float32Array(w*h*2),indices:number[]=[];const valid=(x:number,y:number)=>t.elevation_m[y][x]!==null;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   const i=y*w+x,[east,north]=toXY([lon[x],lat[y]]),e=t.elevation_m[y][x];pos[i*3]=east;pos[i*3+1]=(e??0)*latest.current.exaggeration/scale;pos[i*3+2]=-north;
   const c=new THREE.Color().lerpColors(new THREE.Color('#133f57'),new THREE.Color('#b2d3c8'),Math.max(0,Math.min(1,((e??-100)+100)/110)));colors.set([c.r,c.g,c.b],i*3);uv.set([x/(w-1),1-y/(h-1)],i*2);
   if(x<w-1&&y<h-1){const a=i,b=i+1,c=i+w,d=i+w+1;if(valid(x,y)&&valid(x,y+1)&&valid(x+1,y))indices.push(a,c,b);if(valid(x+1,y)&&valid(x,y+1)&&valid(x+1,y+1))indices.push(b,c,d);}
  }
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(pos,3));geometry.setAttribute('color',new THREE.BufferAttribute(colors,3));geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2));geometry.setIndex(indices);geometry.computeVertexNormals();
  const material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.92,metalness:.03,side:THREE.DoubleSide});const terrain=new THREE.Mesh(geometry,material);terrain.receiveShadow=true;scene.add(terrain);
  let alive=true;const textures:THREE.Texture[]=[];
  if(data.relief?.available)new THREE.TextureLoader().load(data.relief.texture_url,(texture)=>{if(!alive){texture.dispose();return;}textures.push(texture);texture.colorSpace=THREE.SRGBColorSpace;texture.minFilter=THREE.LinearFilter;texture.magFilter=THREE.LinearFilter;material.map=texture;material.alphaTest=.05;material.vertexColors=false;material.needsUpdate=true;},undefined,()=>{if(alive)setError('The rayshader texture could not load; this view retains the actual elevation colours.');});
  const base=new THREE.Mesh(new THREE.BoxGeometry(spanX+.25,.18,spanZ+.25),new THREE.MeshStandardMaterial({color:'#c3d1d8',roughness:1}));base.position.x=toXY([(lon[0]+lon[w-1])/2,midLat])[0];base.position.y=t.elevation_min_m*300/scale-.3;base.receiveShadow=true;scene.add(base);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(span*6,span*6),new THREE.MeshStandardMaterial({color:'#cfE5ea',roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=base.position.y-.1;floor.receiveShadow=true;scene.add(floor);
  const water=new THREE.Mesh(new THREE.PlaneGeometry(spanX,spanZ),new THREE.MeshPhysicalMaterial({color:'#66a4ba',transparent:true,opacity:.19,roughness:.23,metalness:.08,side:THREE.DoubleSide,depthWrite:false}));water.rotation.x=-Math.PI/2;water.position.x=toXY([(lon[0]+lon[w-1])/2,midLat])[0];water.position.y=.015;water.renderOrder=2;scene.add(water);
  const overlay=new THREE.Group(),farmLayer=new THREE.Group();scene.add(overlay,farmLayer);const picks:THREE.Object3D[]=[];
  function addPolygons(feature:Obj,group:THREE.Group,farm=false){
   const geom=feature.geometry;if(!['Polygon','MultiPolygon'].includes(geom.type))return;
   const polygons=geom.type==='Polygon'?[geom.coordinates]:geom.coordinates;
   for(const rings of polygons){
    const paths=rings.map((ring:number[][])=>ring.map(p=>{const [x,y]=toXY(p);return new THREE.Vector2(x,y);}));if(paths[0].length<3)continue;
    const shape=new THREE.Shape(paths[0]);for(const hole of paths.slice(1))shape.holes.push(new THREE.Path(hole));
    const mat=new THREE.MeshBasicMaterial({color:farm?'#e9f5f4':COLORS[feature.properties.designation]||COLORS.Other,transparent:true,opacity:farm?.03:.23,depthWrite:false,depthTest:false,side:THREE.DoubleSide});
    const mesh=new THREE.Mesh(new THREE.ShapeGeometry(shape),mat);mesh.rotation.x=-Math.PI/2;mesh.position.y=farm?.075:.05;mesh.renderOrder=6;mesh.userData={id:feature.id,type:feature.properties.designation,farm};group.add(mesh);if(!farm)picks.push(mesh);
    for(const path of paths){const pts=path.map((p:THREE.Vector2)=>new THREE.Vector3(p.x,mesh.position.y+.005,-p.y));const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:farm?'#566c77':COLORS[feature.properties.designation]||COLORS.Other,transparent:true,opacity:farm?.65:.92,depthTest:false}));line.renderOrder=7;line.userData={...mesh.userData};group.add(line);}
   }
  }
  const labelTextures:THREE.Texture[]=[];
  function label(text:string,lon:number,lat:number,size=1.3){const canvas=document.createElement('canvas');canvas.width=640;canvas.height=100;const ctx=canvas.getContext('2d')!;ctx.font='600 29px Arial';ctx.textAlign='center';ctx.textBaseline='middle';ctx.lineWidth=7;ctx.strokeStyle='#f9fcf7';ctx.strokeText(text,320,50);ctx.fillStyle='#284c40';ctx.fillText(text,320,50);const texture=new THREE.CanvasTexture(canvas);labelTextures.push(texture);const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,depthTest:false,transparent:true}));const [x,y]=toXY([lon,lat]);sprite.position.set(x,.65,-y);sprite.scale.set(size*6.4,size,1);sprite.renderOrder=10;scene.add(sprite);}
  const context=data.uk_context;
  if(context){
   context.regional_land.features.forEach((f:Obj)=>{const g=f.geometry;if(!['Polygon','MultiPolygon'].includes(g.type))return;for(const rings of g.type==='Polygon'?[g.coordinates]:g.coordinates){const points=rings.map((ring:number[][])=>ring.map(p=>{const [x,y]=toXY(p);return new THREE.Vector2(x,y);}));const outline=new THREE.Shape(points[0]);points.slice(1).forEach((hole:THREE.Vector2[])=>outline.holes.push(new THREE.Path(hole)));const land=new THREE.Mesh(new THREE.ShapeGeometry(outline),new THREE.MeshBasicMaterial({color:f.properties.code==='GBR'?'#b4cca0':'#dbe2d2',side:THREE.DoubleSide,depthTest:false}));land.rotation.x=-Math.PI/2;land.position.y=.09;land.renderOrder=3;scene.add(land);}});
   context.labels.forEach((p:Obj)=>{const b=context.context_bounds;if(p.lon>=b[0]&&p.lon<=b[2]&&p.lat>=b[1]&&p.lat<=b[3])label(p.name,p.lon,p.lat,p.name==='UNITED KINGDOM'?1.35:1.05);});
   context.ports.slice(0,3).forEach((p:Obj,i:number)=>{if(i===1)return;label(p.name,p.lon,p.lat-.12,1.05);const [x,y]=toXY([p.lon,p.lat]);const port=new THREE.Mesh(new THREE.SphereGeometry(.11,10,8),new THREE.MeshBasicMaterial({color:'#254f62',depthTest:false}));port.position.set(x,.3,-y);port.renderOrder=9;scene.add(port);});
   if(context.coast){const a=toXY([data.reference_point.lon,data.reference_point.lat]),b=toXY([context.coast.lon,context.coast.lat]);const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(a[0],.3,-a[1]),new THREE.Vector3(b[0],.3,-b[1])]),new THREE.LineDashedMaterial({color:'#aa7321',dashSize:.4,gapSize:.2,depthTest:false}));line.computeLineDistances();line.renderOrder=9;scene.add(line);label(context.coast.distance_km.toFixed(1)+' km to UK coast',(data.reference_point.lon+context.coast.lon)/2+.15,(data.reference_point.lat+context.coast.lat)/2,1.15);}
  }
  label('Regional reference',data.reference_point.lon,data.reference_point.lat+.14,1.1);
  data.geojson.features.forEach((f:Obj)=>addPolygons(f,overlay));(data.wind_agreements?.features||[]).forEach((f:Obj)=>addPolygons(f,farmLayer,true));
  function addLine(points:number[][],color:string){const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points.map(p=>{const [x,y]=toXY(p);return new THREE.Vector3(x,.085,-y);})),new THREE.LineBasicMaterial({color,transparent:true,opacity:.95,depthTest:false}));scene.add(line);}
  data.coastline.features.forEach((f:Obj)=>{if(f.geometry.type==='LineString')addLine(f.geometry.coordinates,'#315d40');else if(f.geometry.type==='MultiLineString')f.geometry.coordinates.forEach((p:number[][])=>addLine(p,'#315d40'));});
  addLine(data.reference_disc.coordinates[0],'#d49d3b');
  const [rx,rn]=toXY([data.reference_point.lon,data.reference_point.lat]);const marker=new THREE.Mesh(new THREE.SphereGeometry(.15,20,12),new THREE.MeshStandardMaterial({color:'#ffcf70',emissive:'#7e530b',emissiveIntensity:.4}));marker.position.set(rx,.55,-rn);scene.add(marker);const stem=new THREE.Mesh(new THREE.CylinderGeometry(.015,.015,.5,6),new THREE.MeshBasicMaterial({color:'#ae7c25'}));stem.position.set(rx,.3,-rn);scene.add(stem);
  const north=new THREE.ArrowHelper(new THREE.Vector3(0,0,-1),new THREE.Vector3(-spanX*.46,.1,spanZ*.42),2,'#2f5963',.3,.15);scene.add(north);
  const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();let down:[number,number]=[0,0];
  const start=(e:PointerEvent)=>{down=[e.clientX,e.clientY];};const click=(e:PointerEvent)=>{if(Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const r=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects(picks).find(h=>h.object.visible);if(hit)latest.current.onSelect(hit.object.userData.id);};
  renderer.domElement.addEventListener('pointerdown',start);renderer.domElement.addEventListener('pointerup',click);
  const resize=()=>{const r=node.getBoundingClientRect();renderer.setSize(r.width,r.height,false);camera.aspect=r.width/Math.max(1,r.height);camera.updateProjectionMatrix();};const observer=new ResizeObserver(resize);observer.observe(node);resize();let raf=0,lastExaggeration=exaggeration;
  function draw(){if(!alive)return;const state=latest.current;
   if(lastExaggeration!==state.exaggeration){for(let y=0;y<h;y++)for(let x=0;x<w;x++)pos[(y*w+x)*3+1]=(t.elevation_m[y][x]??0)*state.exaggeration/scale;geometry.attributes.position.needsUpdate=true;geometry.computeVertexNormals();lastExaggeration=state.exaggeration;}
   overlay.children.forEach(o=>{o.visible=state.types.includes(o.userData.type);const mat=(o as THREE.Mesh).material as THREE.MeshBasicMaterial;if(mat?.opacity!==undefined)mat.opacity=o.type==='Line' ? (o.userData.id===state.selected ? 1 : .8) : (o.userData.id===state.selected ? .35 : .17);});water.visible=state.showWater;farmLayer.visible=state.showFarms;controls.update();renderer.render(scene,camera);raf=requestAnimationFrame(draw);
  }draw();
  return()=>{alive=false;cancelAnimationFrame(raf);observer.disconnect();controls.dispose();renderer.domElement.removeEventListener('pointerdown',start);renderer.domElement.removeEventListener('pointerup',click);scene.traverse(o=>{const m=o as THREE.Mesh;m.geometry?.dispose();if(m.material)(Array.isArray(m.material)?m.material:[m.material]).forEach(x=>x.dispose());});textures.forEach(t=>t.dispose());labelTextures.forEach(t=>t.dispose());renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();};
 },[data.source_dataset_id]);
 return <div className="environment-terrain"><div ref={host} className="environment-three-canvas" role="img" aria-label="Interactive EMODnet seabed with protected-area overlays; drag to orbit and scroll to zoom"/>
  <div className="terrain-hud"><span>EMODnet 2024 · LAT</span><strong>{exaggeration}× vertical geometry</strong><small>{data.relief?.available?`Rayshader ${data.relief.rayshader_version} texture · ${data.relief.shading_exaggeration}× shading`:'Source elevation colours'} · NoData omitted</small></div>
  <button className="terrain-reset" onClick={()=>reset.current()}>Reset camera</button>{error&&<div className="terrain-error" role="status">{error}</div>}
 </div>;
}
