import {useEffect,useRef,useState} from 'react';
import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

type Mode='surface'|'expression';
type Manifest={source:string;asset:string|null;morph_names:string[];vertices:number;triangles:number};
type Controls={mode:(m:Mode)=>void;expression:(n:number,name:string)=>void;reset:()=>void};
const labels:Record<string,string>={jaw_open:'Open mouth',smile:'Smile',pucker:'Pucker',wink_left:'Left wink'};

export default function GNMFaceViewer(){
 const host=useRef<HTMLDivElement>(null),controls=useRef<Controls|null>(null);
 const [active,setActive]=useState(false),[ready,setReady]=useState(false),[fallback,setFallback]=useState(false);
 const [mode,setMode]=useState<Mode>('surface'),[amount,setAmount]=useState(0),[pose,setPose]=useState('jaw_open');
 const [poses,setPoses]=useState<string[]>([]);
 useEffect(()=>{const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){setActive(true);observer.disconnect()}},{rootMargin:'150px'});observer.observe(host.current!);return()=>observer.disconnect()},[]);
 useEffect(()=>{
  if(!active)return;
  const el=host.current!,media=matchMedia('(prefers-reduced-motion: reduce)');
  if(media.matches){setFallback(true);return}
  let renderer:T.WebGLRenderer;
  try{renderer=new T.WebGLRenderer({antialias:true,alpha:true,powerPreference:'low-power'})}catch{setFallback(true);return}
  let disposed=false,frame=0,visible=true,dragging=false,x=0,y=0,targetYaw=-.16,targetPitch=-.03;
  const scene=new T.Scene(),camera=new T.PerspectiveCamera(34,1,.01,100);
  camera.position.set(0,0,6.5);
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0x141413,1);renderer.outputColorSpace=T.SRGBColorSpace;
  const canvas=renderer.domElement;canvas.tabIndex=0;canvas.style.touchAction='none';canvas.setAttribute('aria-label','Interactive head. Drag or use arrow keys to rotate.');el.appendChild(canvas);
  scene.add(new T.HemisphereLight(0xfff8ec,0x48453f,1.8));
  const key=new T.DirectionalLight(0xfff5e8,2.5);key.position.set(-3,4,5);scene.add(key);
  const fill=new T.DirectionalLight(0xeeeae2,.7);fill.position.set(3,1,4);scene.add(fill);
  const rim=new T.DirectionalLight(0xc5b49c,1.8);rim.position.set(3,1,-2);scene.add(rim);
  const pivot=new T.Group(),content=new T.Group();pivot.add(content);scene.add(pivot);pivot.rotation.set(targetPitch,targetYaw,0);
  const meshes:T.Mesh[]=[];
  const root=new T.Group();content.add(root);
  let slowFrames=0;
  function render(){
   if(disposed||!visible)return;
   const start=performance.now();renderer.render(scene,camera);const elapsed=performance.now()-start;
   if(elapsed>180)slowFrames++;else slowFrames=0;if(slowFrames>=5)setFallback(true);
   canvas.dataset.yaw=pivot.rotation.y.toFixed(3);canvas.dataset.drawCalls=String(renderer.info.render.calls);canvas.dataset.triangles=String(renderer.info.render.triangles);canvas.dataset.renderMs=elapsed.toFixed(2);
  }
  function animate(){cancelAnimationFrame(frame);const step=()=>{if(disposed)return;pivot.rotation.y+=(targetYaw-pivot.rotation.y)*.2;pivot.rotation.x+=(targetPitch-pivot.rotation.x)*.2;render();if(Math.abs(targetYaw-pivot.rotation.y)+Math.abs(targetPitch-pivot.rotation.x)>.0005)frame=requestAnimationFrame(step)};frame=requestAnimationFrame(step)}
  function fit(){
   const box=new T.Box3();const point=new T.Vector3();
   for(const mesh of meshes){if(!mesh.visible)continue;const index=mesh.geometry.index;const used=index?new Set(Array.from(index.array)):new Set(Array.from({length:mesh.geometry.attributes.position.count},(_,i)=>i));for(const i of used){mesh.getVertexPosition(i,point);box.expandByPoint(point)}}
   if(box.isEmpty())return;
   const center=box.getCenter(new T.Vector3()),size=box.getSize(new T.Vector3());const scale=2.85/Math.max(size.x,size.y,size.z);
   content.scale.setScalar(scale);content.position.copy(center.multiplyScalar(-scale));
   render();
  }
  function applyExpression(value:number,name:string){
   let displacement=0;
   for(const mesh of meshes){mesh.morphTargetInfluences?.fill(0);const index=mesh.morphTargetDictionary?.[name];if(index!==undefined&&mesh.morphTargetInfluences){mesh.morphTargetInfluences[index]=value;const attribute=mesh.geometry.morphAttributes.position?.[index];if(attribute){const base=mesh.geometry.attributes.position;for(let i=0;i<base.count;i+=17)displacement=Math.max(displacement,Math.abs(attribute.getY(i))*value)}}}
   canvas.dataset.expression=name;canvas.dataset.expressionAmount=String(value);canvas.dataset.expressionDelta=String(displacement);render();
  }
  controls.current={
   mode:m=>{if(m!=='expression')applyExpression(0,'jaw_open');render()},
   expression:applyExpression,
   reset:()=>{targetYaw=-.16;targetPitch=-.03;animate()},
  };
  const down=(e:PointerEvent)=>{if(e.button!==0)return;dragging=true;x=e.clientX;y=e.clientY;canvas.setPointerCapture(e.pointerId)};
  const move=(e:PointerEvent)=>{if(!dragging)return;targetYaw=T.MathUtils.clamp(targetYaw+(e.clientX-x)*.006,-.65,.65);targetPitch=T.MathUtils.clamp(targetPitch+(e.clientY-y)*.004,-.25,.25);x=e.clientX;y=e.clientY;animate()};
  const up=()=>{dragging=false};const keyboard=(e:KeyboardEvent)=>{if(!e.key.startsWith('Arrow'))return;e.preventDefault();targetYaw=T.MathUtils.clamp(targetYaw+(e.key==='ArrowLeft'?-.1:e.key==='ArrowRight'?.1:0),-.65,.65);targetPitch=T.MathUtils.clamp(targetPitch+(e.key==='ArrowUp'?-.1:e.key==='ArrowDown'?.1:0),-.25,.25);animate()};
  const lost=(e:Event)=>{e.preventDefault();setFallback(true)};
  canvas.addEventListener('pointerdown',down);canvas.addEventListener('pointermove',move);canvas.addEventListener('pointerup',up);canvas.addEventListener('pointercancel',up);canvas.addEventListener('keydown',keyboard);canvas.addEventListener('webglcontextlost',lost);
  const resize=new ResizeObserver(()=>{camera.aspect=el.clientWidth/el.clientHeight;camera.updateProjectionMatrix();renderer.setSize(el.clientWidth,el.clientHeight);render()});resize.observe(el);
  const visibility=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)render()});visibility.observe(el);
  const reduced=()=>{if(media.matches)setFallback(true)};media.addEventListener('change',reduced);
  const abort=new AbortController();
  fetch('/assets/face-manifest.json',{signal:abort.signal}).then(r=>{if(!r.ok)throw new Error('manifest');return r.json() as Promise<Manifest>}).then(async manifest=>{
   if(!manifest.asset)throw new Error('No GNM asset');
   const gltf=await new GLTFLoader().loadAsync(manifest.asset);if(disposed)return;
   gltf.scene.traverse(object=>{if(object instanceof T.Mesh){meshes.push(object);const materials=Array.isArray(object.material)?object.material:[object.material];for(const material of materials){if(material instanceof T.MeshStandardMaterial){material.polygonOffset=true;material.polygonOffsetFactor=1;material.polygonOffsetUnits=1;if(material.transparent)material.depthWrite=false}}}});
   root.add(gltf.scene);fit();const available=manifest.morph_names.filter(name=>name!=='wide_smile');setPoses(available);if(available.length)setPose(available[0]);canvas.dataset.source='google/GNM';setReady(true);render();
  }).catch(error=>{if(error.name!=='AbortError'&&!disposed)setFallback(true)});
  return()=>{disposed=true;abort.abort();cancelAnimationFrame(frame);resize.disconnect();visibility.disconnect();media.removeEventListener('change',reduced);canvas.removeEventListener('pointerdown',down);canvas.removeEventListener('pointermove',move);canvas.removeEventListener('pointerup',up);canvas.removeEventListener('pointercancel',up);canvas.removeEventListener('keydown',keyboard);canvas.removeEventListener('webglcontextlost',lost);scene.traverse(object=>{if(object instanceof T.Mesh||object instanceof T.LineSegments){object.geometry.dispose();const materials=Array.isArray(object.material)?object.material:[object.material];materials.forEach(m=>m.dispose())}});renderer.dispose();canvas.remove();controls.current=null};
 },[active]);
 function change(next:Mode){setMode(next);controls.current?.mode(next);const value=next==='expression'?75:0;setAmount(value);controls.current?.expression(value/100,pose)}
 function selectPose(name:string){setPose(name);setAmount(100);controls.current?.expression(1,name)}
 return <div className="face-study">
  <div className="face-viewport" ref={host} style={fallback?{display:'none'}:undefined}/>
  {fallback&&<div className="face-viewport"><img src="/assets/face-poster.png" alt="Official GNM neutral head, rendered from the exported template"/></div>}
  <div className="face-caption"><span>{fallback?'Static preview':ready?'Drag to rotate · arrow keys supported':'Loading GNM template…'}</span><button onClick={()=>controls.current?.reset()} disabled={fallback||!ready}>Reset ↺</button></div>
  <div className="face-controls" role="group" aria-label="Face rendering mode">{(['surface','expression'] as Mode[]).map(m=><button key={m} disabled={fallback||!ready} aria-pressed={mode===m} onClick={()=>change(m)}>{m[0].toUpperCase()+m.slice(1)}</button>)}</div>
  {mode==='expression'&&!fallback&&<div className="expression">{poses.length?<><label htmlFor="pose">Expression<select id="pose" value={pose} onChange={e=>selectPose(e.target.value)}>{poses.map(p=><option key={p} value={p}>{labels[p]||p.replaceAll('_',' ')}</option>)}</select></label><label htmlFor="expression">Neutral → pose <output>{amount}%</output></label><input id="expression" type="range" min="0" max="100" value={amount} onChange={e=>{const n=+e.target.value;setAmount(n);controls.current?.expression(n/100,pose)}}/></>:<p className="face-note">This export has no validated expression targets.</p>}</div>}
 </div>
}
