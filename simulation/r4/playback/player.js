/* R4 recorded-state playback. No flight control, trajectory synthesis or network calls. */
'use strict';
try {
const F=window.R4_FLIGHT, D=F.frames, E=F.events, rad=Math.PI/180;
if(!window.THREE||!window.R4_CAD||!F)throw Error('Playback assets are missing. Extract the whole ZIP before opening START_HERE.html.');
const $=id=>document.getElementById(id);
const scene=new THREE.Scene();scene.background=new THREE.Color('#e8f0f5');
scene.add(new THREE.HemisphereLight(0xffffff,0x7e929e,2.2));const sun=new THREE.DirectionalLight(0xffffff,2.4);sun.position.set(4,-6,10);scene.add(sun);
const ds=new THREE.Scene();ds.background=new THREE.Color('#e8f0f5');ds.add(new THREE.HemisphereLight(0xffffff,0x7e929e,2.2));const dl=sun.clone();ds.add(dl);
function renderer(host){const r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setPixelRatio(Math.min(devicePixelRatio,2));r.outputColorSpace=THREE.SRGBColorSpace;host.appendChild(r.domElement);return r;}
const r=renderer($('world')),dr=renderer($('detail'));
const camera=new THREE.PerspectiveCamera(39,1,.02,100);camera.up.set(0,0,1);
const dc=new THREE.PerspectiveCamera(34,1,.01,30);dc.up.set(0,0,1);dc.position.set(.8,-1.12,.36);dc.lookAt(0,0,-.06);
const cache=new Map();
for(const o of window.R4_CAD){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(o.p,3));g.setIndex(o.i);g.computeVertexNormals();cache.set(o,g);}
function vehicle(){const body=new THREE.Group(),vanes=Array.from({length:4},()=>new THREE.Group());const hinge=new THREE.Vector3(0,0,.130);
 for(let k=0;k<4;k++){vanes[k].position.copy(hinge).sub(new THREE.Vector3(...F.cg));body.add(vanes[k]);}
 for(const o of window.R4_CAD){const g=cache.get(o);const mat=new THREE.MeshStandardMaterial({color:o.color,metalness:o.name.includes('tube')?.35:.15,roughness:.65,side:THREE.DoubleSide});const mesh=new THREE.Mesh(g,mat);
  if(o.moving&&o.station>=0){mesh.position.copy(hinge).multiplyScalar(-1);vanes[o.station].add(mesh);}else{mesh.position.set(-F.cg[0],-F.cg[1],-F.cg[2]);body.add(mesh);}}
 return {body,vanes};}
const v=vehicle(),dv=vehicle();scene.add(v.body);ds.add(dv.body);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(12,12),new THREE.MeshStandardMaterial({color:0xdde7ed,roughness:1}));floor.position.z=-.002;scene.add(floor);
const grid=new THREE.GridHelper(12,24,0xaac0ce,0xc2d1da);grid.rotation.x=Math.PI/2;grid.position.z=.001;scene.add(grid);
const lineMat=new THREE.LineBasicMaterial({color:0x5b8199,transparent:true,opacity:.65});
function line(points,material=lineMat){const l=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points.map(p=>new THREE.Vector3(...p))),material);scene.add(l);return l;}
function ring(z,radius){return line(Array.from({length:97},(_,i)=>[radius*Math.cos(i*Math.PI/48),radius*Math.sin(i*Math.PI/48),z]));}
ring(.006,1);ring(5-F.floorZ,.55);
line([[-1.25,.8,0],[-1.25,.8,5-F.floorZ]]);
function label(text,pos){const c=document.createElement('canvas');c.width=256;c.height=64;const x=c.getContext('2d');x.font='40px system-ui';x.fillStyle='#375a70';x.textAlign='center';x.fillText(text,128,46);const tex=new THREE.CanvasTexture(c),s=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,depthTest:false,transparent:true}));s.position.set(...pos);s.scale.set(1.28,.32,1);scene.add(s);return s;}
for(let z=0;z<=5;z++){const h=z-F.floorZ;line([[-1.32,.8,h],[-1.18,.8,h]]);label(z+' m',[-1.62,.8,h]);}
label('1 m radius',[.7,-1.1,.08]);label('Launch',[0,0,.04]);
const wind=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(-1.2,-1.3,.18),.8,0x66899f,.14,.08);scene.add(wind);label('Wind 1 m/s',[-.8,-1.3,.4]);
const points=D.filter((_,i)=>i%3===0).map(a=>new THREE.Vector3(a[1],a[2],a[3]-F.floorZ));
const trail=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:0x126a9b,transparent:true,opacity:.75}));scene.add(trail);
const projection=new THREE.Mesh(new THREE.RingGeometry(.045,.065,40),new THREE.MeshBasicMaterial({color:0x126a9b,side:THREE.DoubleSide}));projection.position.z=.009;scene.add(projection);
const drop=line([[0,0,0],[0,0,1]],new THREE.LineDashedMaterial({color:0x87a8bd,dashSize:.1,gapSize:.07}));drop.computeLineDistances();
let az=-1.03,el=.20,dist=10.5;const target=new THREE.Vector3(0,0,2.63);
function updateCamera(){camera.position.set(target.x+dist*Math.cos(el)*Math.cos(az),target.y+dist*Math.cos(el)*Math.sin(az),target.z+dist*Math.sin(el));camera.lookAt(target);}
updateCamera();let pointer=null;
r.domElement.addEventListener('pointerdown',e=>{pointer=[e.clientX,e.clientY];r.domElement.setPointerCapture(e.pointerId);});
r.domElement.addEventListener('pointermove',e=>{if(!pointer)return;az-=(e.clientX-pointer[0])*.008;el=Math.max(-.02,Math.min(1.25,el+(e.clientY-pointer[1])*.006));pointer=[e.clientX,e.clientY];updateCamera();});
r.domElement.addEventListener('pointerup',()=>pointer=null);
r.domElement.addEventListener('wheel',e=>{e.preventDefault();dist=Math.max(3,Math.min(20,dist*Math.exp(e.deltaY*.001)));updateCamera();},{passive:false});
function resize(){for(const [rr,cam,host] of [[r,camera,$('world')],[dr,dc,$('detail')]]){const w=host.clientWidth,h=rr.domElement.clientHeight;rr.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();}draw();}
let time=D[0][0],playing=false,last=null;
$('seek').min=D[0][0];$('seek').max=D[D.length-1][0];
function sample(t){let lo=0,hi=D.length-1;while(hi-lo>1){let mid=(lo+hi)>>1;if(D[mid][0]<=t)lo=mid;else hi=mid;}const a=D[lo],b=D[hi],u=Math.max(0,Math.min(1,(t-a[0])/(b[0]-a[0])));return a.map((n,i)=>n+(b[i]-n)*u);}
function phase(t){return t<E.liftoff_s?'Liftoff ready':t<E.hover_start_s?'Climb':t<E.land_request_s?'Hover':t<E.touchdown_s?'Descent':t<E.native_disarm_s?'Ground / settling':'Disarmed';}
function attitude(body,a){body.quaternion.setFromEuler(new THREE.Euler(a[4]*rad,a[5]*rad,a[6]*rad,'ZYX'));}
function vane(ve,a){for(let k=0;k<4;k++){const phi=k*Math.PI/2;ve.vanes[k].quaternion.setFromAxisAngle(new THREE.Vector3(Math.cos(phi),Math.sin(phi),0),-a[8+k]*rad);}}
function draw(){const a=sample(time);v.body.position.set(a[1],a[2],a[3]-F.floorZ);attitude(v.body,a);attitude(dv.body,a);vane(v,a);vane(dv,a);
 projection.position.set(a[1],a[2],.009);drop.geometry.setFromPoints([new THREE.Vector3(a[1],a[2],.01),new THREE.Vector3(a[1],a[2],a[3]-F.floorZ)]);drop.computeLineDistances();trail.geometry.setDrawRange(0,Math.max(2,Math.floor((time-D[0][0])/(D[D.length-1][0]-D[0][0])*points.length)));
 r.render(scene,camera);dr.render(ds,dc);
 $('phase').textContent=phase(time);$('height').textContent=a[3].toFixed(2)+' m';$('drift').textContent=Math.hypot(a[1],a[2]).toFixed(3)+' m';$('vertical').textContent=a[12].toFixed(2)+' m/s';$('thrust').textContent=a[7].toFixed(1)+' N';$('seek').value=time;$('clock').textContent=time.toFixed(1)+' s after liftoff';
 $('angles').textContent=`CAD tilt X ${a[4].toFixed(2)}° · tilt Y ${a[5].toFixed(2)}° · axial rotation Z ${a[6].toFixed(2)}°  |  Vanes ${a.slice(8,12).map(n=>n.toFixed(1)+'°').join(' / ')}`;
 for(const c of cursors)c.setAttribute('x1',plotX(time)),c.setAttribute('x2',plotX(time));
 return a;}
const cursors=[];const svgNS='http://www.w3.org/2000/svg',plotX=t=>40+(t-D[0][0])/(D[D.length-1][0]-D[0][0])*550;
function svgEl(tag,attrs,parent){const e=document.createElementNS(svgNS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);parent.appendChild(e);return e;}
function chart(id,ymax,get,limit){const svg=$(id);svg.setAttribute('viewBox','0 0 610 140');
 for(let k=0;k<=ymax;k+=ymax/5){const y=115-95*k/ymax;svgEl('line',{x1:40,x2:590,y1:y,y2:y,stroke:'#cddbe4'},svg);svgEl('text',{x:4,y:y+4},svg).textContent=k.toFixed(ymax<2?1:0);}
 for(let t=0;t<=40;t+=10){const x=plotX(t);svgEl('text',{x:x-5,y:136},svg).textContent=t+'s';}
 for(const event of ['hover_start_s','land_request_s','touchdown_s'])svgEl('line',{x1:plotX(E[event]),x2:plotX(E[event]),y1:15,y2:115,stroke:'#afc1cc','stroke-dasharray':'2 3'},svg);
 svgEl('path',{d:D.filter((_,i)=>i%3===0).map((a,i)=>(i?'L':'M')+plotX(a[0]).toFixed(2)+','+(115-95*get(a)/ymax).toFixed(2)).join(' '),fill:'none',stroke:'#126a9b','stroke-width':2},svg);
 if(limit)svgEl('line',{x1:40,x2:590,y1:115-95*limit/ymax,y2:115-95*limit/ymax,stroke:'#3c5667','stroke-dasharray':'5 4'},svg);
 cursors.push(svgEl('line',{x1:40,x2:40,y1:15,y2:115,stroke:'#b65d23','stroke-width':1.4},svg));}
chart('height-chart',5.5,a=>a[3]);chart('drift-chart',1.2,a=>Math.hypot(a[1],a[2]),1);
$('play').onclick=()=>{if(time>=D[D.length-1][0])time=D[0][0];playing=!playing;last=null;$('play').textContent=playing?'Pause':'Play';};
$('restart').onclick=()=>{time=D[0][0];playing=false;$('play').textContent='Play';draw();};
$('seek').oninput=()=>{time=Number($('seek').value);last=null;draw();};
document.querySelectorAll('[data-event]').forEach(b=>b.onclick=()=>{time=E[b.dataset.event];last=null;draw();});
function tick(now){if(playing&&last!==null){time=Math.min(D[D.length-1][0],time+(now-last)/1000*Number($('speed').value));if(time>=D[D.length-1][0]){playing=false;$('play').textContent='Play';}}last=now;draw();requestAnimationFrame(tick);}
window.addEventListener('resize',resize);resize();requestAnimationFrame(tick);$('ready').textContent='ready';
window.R4_PLAYER={seek(t){time=Math.max(D[0][0],Math.min(D[D.length-1][0],t));playing=false;draw();},sample,phase,render:draw,get time(){return time;},get duration(){return D[D.length-1][0]-D[0][0];},get start(){return D[0][0];},world:r.domElement,detail:dr.domElement,events:E,body:v.body,detailBody:dv.body,vanes:v.vanes};
}catch(error){document.getElementById('error').style.display='block';document.getElementById('error').textContent='Playback could not start: '+error.message;console.error(error);}
