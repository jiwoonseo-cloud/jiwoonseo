import * as T from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
const W=1080,H=1920,PI=Math.PI;
const renderer=new T.WebGLRenderer({antialias:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.shadowMap.enabled=false;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;document.body.appendChild(renderer.domElement);
const scene=new T.Scene();scene.background=new T.Color('#b8bdbd');scene.environment=new T.PMREMGenerator(renderer).fromScene(new RoomEnvironment(),.05).texture;scene.environmentIntensity=.5;
const camera=new T.PerspectiveCamera(39,W/H,.01,80);
scene.add(new T.HemisphereLight(0xd5e2ee,0x42403b,1.0));
const key=new T.DirectionalLight(0xfff1df,3.4);key.position.set(-3,6,4);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-4;key.shadow.camera.right=4;key.shadow.camera.top=4;key.shadow.camera.bottom=-4;key.shadow.normalBias=.015;scene.add(key);
const fill=new T.DirectionalLight(0xaacbff,.7);fill.position.set(4,3,-3);scene.add(fill);
function noiseTex(){const c=document.createElement('canvas');c.width=c.height=256;const x=c.getContext('2d');const a=x.createImageData(256,256);let seed=211;for(let i=0;i<a.data.length;i+=4){seed=(seed*1664525+1013904223)>>>0;const v=125+(seed%15);a.data.set([v,v,v,255],i);}x.putImageData(a,0,0);const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(7,7);return t;}
const noise=noiseTex();
const white=new T.MeshPhongMaterial({color:0xd6d8d7,shininess:35,specular:0x333333,bumpMap:noise,bumpScale:.0007});
const graphite=new T.MeshPhongMaterial({color:0x11191b,shininess:10,specular:0x151515,bumpMap:noise,bumpScale:.001});
const brushMat=new T.MeshLambertMaterial({color:0xaaaaaa});
const teal=new T.MeshPhongMaterial({color:0x13635f,shininess:28,specular:0x333333,bumpMap:noise,bumpScale:.001});
const steel=new T.MeshPhongMaterial({color:0x9aa9ad,shininess:100,specular:0xdddddd,bumpMap:noise,bumpScale:.0002});
const copper=new T.MeshPhongMaterial({color:0x6b3b21,shininess:70,specular:0x888888});
const furmat=new T.MeshPhongMaterial({color:0x6e4c2b,roughness:.5,emissive:0x77552c,emissiveIntensity:.1});
const glass=new T.MeshPhongMaterial({color:0xaed8df,transparent:true,opacity:.09,roughness:.13,depthWrite:false,side:T.DoubleSide});
function mesh(g,m,p,parent=scene){const o=new T.Mesh(g,m);o.position.set(...p);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
function box(size,pos,mat,parent=scene,r=.025){return mesh(new RoundedBoxGeometry(...size,2,r),mat,pos,parent);}
function cylinder(r,h,pos,mat,parent=scene,axis='y'){const o=mesh(new T.CylinderGeometry(r,r,h,40,1),mat,pos,parent);if(axis==='x')o.rotation.z=PI/2;if(axis==='z')o.rotation.x=PI/2;return o;}
function torus(r,t,pos,mat,parent=scene,axis='x'){const o=mesh(new T.TorusGeometry(r,t,8,48),mat,pos,parent);if(axis==='x')o.rotation.y=PI/2;if(axis==='y')o.rotation.x=PI/2;return o;}
function tube(points,r,mat,parent=scene,segments=80){return mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),segments,r,6,false),mat,[0,0,0],parent);}
function updateTube(o,points,r){o.geometry.dispose();o.geometry=new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),Math.max(16,points.length*2),r,6,false);}
const groundMat=new T.MeshBasicMaterial({color:0xb8bdbd,toneMapped:false});
const floor=mesh(new T.PlaneGeometry(600,600),groundMat,[0,-.02,0]);floor.rotation.x=-PI/2;floor.receiveShadow=true;floor.castShadow=false;
const robot=new T.Group();scene.add(robot);robot.position.y=.46;
const caseGroup=new T.Group();robot.add(caseGroup);
const profile=[new T.Vector2(0,-.07),new T.Vector2(1.32,-.07),new T.Vector2(1.39,-.025),new T.Vector2(1.405,.04),new T.Vector2(1.40,.14),new T.Vector2(1.35,.20),new T.Vector2(0,.20)];
mesh(new T.LatheGeometry(profile,128),white,[0,0,0],caseGroup);
const rim=torus(1.385,.018,[0,-.045,0],graphite,robot,'y');


const underside=new T.Group();robot.add(underside);
const shape=new T.Shape();shape.absarc(0,0,1.36,0,PI*2,false);
function rectHole(x,z,w,h){const p=new T.Path();p.moveTo(x,z);p.lineTo(x,z+h);p.lineTo(x+w,z+h);p.lineTo(x+w,z);p.closePath();shape.holes.push(p);}
rectHole(-1.1,-.92,2.2,.85);rectHole(-1.35,-.12,.30,.65);rectHole(1.05,-.12,.30,.65);
const plate=mesh(new T.ExtrudeGeometry(shape,{depth:.065,bevelEnabled:true,bevelThickness:.012,bevelSize:.012,bevelSegments:3,curveSegments:96}),white,[0,-.12,0],underside);plate.rotation.x=PI/2;
box([2.18,.05,.79],[0,-.075,-.50],graphite,underside);
box([2.24,.095,.055],[0,-.17,-.93],white,underside);box([2.24,.095,.055],[0,-.17,-.075],white,underside);
// Front caster rebuilt in the atlas opening, matching the master asset.
const caster=new T.Group();underside.add(caster);caster.position.z=.88;
cylinder(.235,.045,[0,-.17,0],graphite,caster);cylinder(.16,.15,[0,-.29,0],graphite,caster,'x');
for(const x of [-.12,.12]){box([.035,.18,.15],[x,-.23,0],white,caster,.015);cylinder(.036,.025,[x,-.29,0],steel,caster,'x');}
const roll=new T.Group();roll.position.set(0,-.25,-.5);robot.add(roll);
function makeRoller(parent,length=2.02,short=false){
 const core=cylinder(.205,length,[0,0,0],brushMat,parent,'x');const uv=core.geometry.attributes.uv;for(let i=0;i<uv.count;i++){const a=uv.getX(i),b=uv.getY(i);uv.setXY(i,b,a);}uv.needsUpdate=true;
 const counts=4*72*7,inst=new T.InstancedMesh(new T.CylinderGeometry(.0007,.0010,.042,4),graphite,counts);inst.castShadow=true;parent.add(inst);let n=0;const dummy=new T.Object3D();
 for(let k=0;k<4;k++){
  const pos=[],ind=[];
  for(let j=0;j<=80;j++){const x=-length/2+length*j/80,a=k*PI/2+x*2.2;for(const [dx,r] of [[-.023,.195],[.023,.195],[-.023,.232],[.023,.232]])pos.push(x+dx,r*Math.sin(a),r*Math.cos(a));if(j<80){const v=j*4;ind.push(v,v+4,v+2,v+2,v+4,v+6,v+1,v+3,v+5,v+3,v+7,v+5,v+2,v+6,v+3,v+3,v+6,v+7);}}
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setIndex(ind);g.computeVertexNormals();mesh(g,teal,[0,0,0],parent);
  for(let j=0;j<72;j++){const x=-length/2+.02+(length-.04)*j/71,a=k*PI/2+x*2.2+.40;for(let q=-3;q<=3;q++){const jitter=Math.sin(j*17.3+q*11.7+k*3.1);dummy.scale.set(1,.72+.28*(1+jitter),1);dummy.position.set(x+q*.003,.232*Math.sin(a+jitter*.01),.232*Math.cos(a+jitter*.01));dummy.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),new T.Vector3(0,Math.sin(a),Math.cos(a)));dummy.updateMatrix();inst.setMatrixAt(n++,dummy.matrix);}}
 }
 return parent;
}
makeRoller(roll);
const shaft=cylinder(.052,2.42,[0,-.25,-.5],steel,robot,'x');
const inlet=new T.Group();robot.add(inlet);torus(.105,.012,[0,-.18,-.5],steel,inlet,'y');cylinder(.105,.01,[0,.12,-.5],graphite,inlet);mesh(new T.CylinderGeometry(.105,.105,.3,48,1,true),graphite,[0,-.03,-.5],inlet);inlet.visible=false;
const caps=[],bearings=[];
for(const s of [-1,1]){
 const cap=new T.Group();cap.position.set(s*1.16,-.25,-.5);robot.add(cap);cylinder(.145,.105,[0,0,0],graphite,cap,'x');torus(.119,.014,[s*.054,0,0],steel,cap);caps.push(cap);
 const b=torus(.077,.018,[s*1.08,-.25,-.5],steel,robot);bearings.push(b);
 for(let k=0;k<24;k++){const a=k*PI/12;const o=box([.11,.011,.016],[0,.144*Math.sin(a),.144*Math.cos(a)],graphite,cap,.004);o.rotation.x=-a;}
}
const wheels=[];
for(const s of [-1,1]){const wh=new T.Group();wh.position.set(s*1.17,-.18,.23);robot.add(wh);cylinder(.265,.16,[0,0,0],graphite,wh,'x');cylinder(.135,.17,[0,0,0],steel,wh,'x');for(let k=0;k<32;k++){const a=k*PI/16;const o=box([.18,.035,.035],[0,.255*Math.sin(a),.255*Math.cos(a)],graphite,wh,.008);o.rotation.x=-a;}wheels.push(wh);}
const side=new T.Group();side.position.set(-.82,-.21,.63);robot.add(side);cylinder(.10,.06,[0,0,0],graphite,side);
for(let k=0;k<3;k++){const a=k*PI*2/3;tube([[.07*Math.cos(a),0,.07*Math.sin(a)],[.34*Math.cos(a),-.01,.34*Math.sin(a)]],.021,graphite,side,8);for(let n=0;n<12;n++){const b=a+(n-5.5)*.016;tube([[.30*Math.cos(b),-.01,.30*Math.sin(b)],[.49*Math.cos(b),-.025,.49*Math.sin(b)]],.0016,graphite,side,4);}}
for(const [x,z] of [[-.98,.7],[.98,.7],[-.9,-1],[.9,-1],[0,1.1]]){const o=cylinder(.025,.01,[x,-.195,z],steel,underside);box([.032,.012,.005],[x,-.202,z],graphite,underside,.001);}
for(const x of [-.4,.4])box([.11,.018,.08],[x,-.19,.95],steel,underside,.006);
const hair=new T.Group();robot.add(hair);const strands=[];for(let i=0;i<4;i++)strands.push(tube([[0,-.5,-1],[0,-.5,-.5]],.003,copper,hair,64));
function wrapped(center,turns=2,r=.245,phase=0){const pts=[];for(let j=0;j<100;j++){const u=j/99,a=-PI/2+turns*2*PI*u+phase;pts.push([center+(u-.5)*.055,-.25+r*Math.sin(a),-.5+r*Math.cos(a)]);}return pts;}
function caught(progress){const angle=Math.max(.01,progress*PI*3),r=.25,L=4.0,free=Math.max(.05,L-angle*r),pts=[];
 for(let j=0;j<20;j++)pts.push([.05,-.25-r,-.5-free*(1-j/19)]);
 for(let j=1;j<110;j++){const u=j/109,a=-PI/2+angle*u;pts.push([.05+.045*u,-.25+r*Math.sin(a),-.5+r*Math.cos(a)]);}return pts;
}
const endHair=new T.Group();robot.add(endHair);
for(let i=0;i<18;i++)tube(wrapped(1.052+i*.0014,3,.070+i*.0012),.0011,copper,endHair,120);
const fur=[];for(let i=0;i<7;i++)fur.push(tube([[0,-.48,-1],[.05,-.48,-1.03]],.0048,furmat,robot,10));
const airPath=new T.CatmullRomCurve3([new T.Vector3(0,-.49,-1.12),new T.Vector3(0,-.46,-.84),new T.Vector3(0,-.10,-.83),new T.Vector3(0,.10,-.50),new T.Vector3(0,.08,-.10),new T.Vector3(0,.16,.11)]);
const duct=new T.Group();robot.add(duct);box([.83,.25,.37],[0,.08,-.05],glass,duct,.04);box([.86,.018,.39],[0,.21,-.05],steel,duct,.006);duct.visible=false;
const duo=new T.Group();duo.position.copy(roll.position);robot.add(duo);const halves=[];
for(const s of [-1,1]){const g=new T.Group();g.position.x=s*.57;duo.add(g);makeRoller(g,.98,true);halves.push(g);}duo.visible=false;
const gloves=new T.Group();robot.add(gloves);const gloveMat=new T.MeshPhongMaterial({color:0x242a2d,roughness:.72,bumpMap:noise,bumpScale:.0013});
for(const s of [-1,1]){
 const hand=new T.Group();gloves.add(hand);hand.rotation.y=-s*PI/2;hand.position.x=s*.62;
 box([.39,.16,.48],[s*1.57,.035,.15],gloveMat,hand,.07);
 for(let k=0;k<4;k++){const z=-.06+k*.105;tube([[s*1.67,.09,z],[s*1.52,.20,z],[s*1.34,.17,z],[s*1.28,.08,z]],.043,gloveMat,hand,24);}
 tube([[s*1.67,-.02,.36],[s*1.46,-.12,.37],[s*1.29,-.1,.27]],.055,gloveMat,hand,24);
 box([.7,.15,.32],[s*2.02,.025,.15],gloveMat,hand,.065);
}
gloves.visible=false;
const motorUnit=new T.Group();robot.add(motorUnit);motorUnit.position.set(1.08,-.04,-.1);motorUnit.visible=false;
const motorRotor=new T.Group();motorUnit.add(motorRotor);cylinder(.10,.30,[0,0,0],steel,motorRotor,'x');
for(let k=0;k<8;k++){const a=k*PI/4;torus(.022,.006,[0,.085*Math.cos(a),.085*Math.sin(a)],copper,motorRotor);}
cylinder(.13,.045,[-.16,0,0],graphite,motorUnit,'x');cylinder(.13,.045,[.16,0,0],graphite,motorUnit,'x');
const driveGear=new T.Group();driveGear.position.set(0,-.21,-.40);motorUnit.add(driveGear);cylinder(.09,.04,[0,0,0],steel,driveGear,'x');
for(let k=0;k<20;k++){const a=k*PI/10;const tooth=box([.04,.023,.018],[0,.09*Math.cos(a),.09*Math.sin(a)],graphite,driveGear,.003);tooth.rotation.x=a;}
tube([[0,-.09,-.02],[0,-.27,-.38],[0,-.15,-.45],[0,.09,.01],[0,-.09,-.02]],.008,graphite,motorUnit,32);
const comb=new T.Group();robot.add(comb);box([1.8,.07,.08],[0,-.52,-.56],steel,comb,.01);for(let j=0;j<22;j++)box([.025,.13,.025],[-.85+j*.081,-.47,-.56],steel,comb,.003);comb.visible=false;
const scissors=new T.Group();scene.add(scissors);const silver=new T.MeshPhongMaterial({color:0xc0cbd0,metalness:1,roughness:.16});
for(const s of [-1,1]){const g=new T.Group();scissors.add(g);const blade=box([.05,.025,.50],[0,0,-.23],silver,g,.005);blade.rotation.y=s*.08;torus(.10,.016,[0,0,.26],silver,g,'y');tube([[0,0,.04],[0,0,.16]],.018,silver,g,8);}scissors.visible=false;
const ease=x=>{x=T.MathUtils.clamp(x,0,1);return x*x*(3-2*x);};
function local(p){robot.updateMatrixWorld(true);return robot.localToWorld(new T.Vector3(...p));}
function cam(target,offset){camera.position.copy(target).add(new T.Vector3(...offset));camera.lookAt(target);}
let config=[];try{const r=await fetch('/timeline.json');if(r.ok)config=await r.json();}catch{}
function find(t){return config.find(s=>s.start<=t&&t<s.end)||config.at(-1)||{mode:'flip',start:0,end:3};}
window.renderAt=(t,forced=null)=>{
 const s=forced||find(t),u=T.MathUtils.clamp((t-(s.action_start??s.start))/((s.action_end??s.end)-(s.action_start??s.start)),0,1),m=({remain:'short',duoflow:'duo',path:'duo'})[s.mode]||s.mode;
 camera.zoom=1;camera.updateProjectionMatrix();caseGroup.position.set(0,0,0);motorUnit.visible=false;endHair.scale.set(1,1,1);shaft.visible=true;inlet.visible=false;robot.visible=true;robot.position.set(0,.35,0);robot.rotation.set(PI,0,0);roll.position.set(0,-.25,-.5);roll.rotation.x=0;side.rotation.y=0;caseGroup.visible=true;underside.visible=true;gloves.visible=false;hair.visible=true;endHair.visible=true;duct.visible=false;duo.visible=false;roll.visible=true;fur.forEach(f=>f.visible=false);comb.visible=false;scissors.visible=false;rim.visible=true;wheels.forEach(o=>o.visible=true);side.visible=true;caps.forEach((c,i)=>c.position.set(i?1.16:-1.16,-.25,-.5));groundMat.color.set(0xb8bdbd);
 strands.forEach((o,i)=>{o.visible=i===0;updateTube(o,wrapped(.73+i*.007,2.5,.246+i*.002),.0018);});
 if(m==='home'){
  robot.rotation.x=0;robot.position.y=.46;robot.position.z=.6*(1-ease(Math.min(u/.55,1)));side.rotation.y=u<.55?t*14:0;roll.rotation.x=u<.55?t*17:0;groundMat.color.set(0x7d6c55);cam(new T.Vector3(0,.25,0),[3.0,6.0,6.0]);
 }else if(m==='flip'){
  robot.position.y=.50+1.3*Math.sin(PI*u);robot.rotation.x=PI*ease(u);gloves.visible=true;cam(new T.Vector3(0,robot.position.y,0),[.3,6.7,3.4]);
 }else if(m==='reveal'){
  cam(local([.7,-.25,-.5]),[1.5-1.0*ease(u),2.0-1.1*ease(u),1.8-1.0*ease(u)]);
 }else if(m==='contact'||m==='wrap'){
  caseGroup.visible=false;underside.visible=false;rim.visible=false;wheels.forEach(o=>o.visible=false);side.visible=false;robot.rotation.x=0;robot.position.y=.5;endHair.visible=false;roll.rotation.x=t*6.5;
  const p=m==='contact'?.1+.20*u:.2+.8*u;strands.forEach((o,i)=>{o.visible=i===0;updateTube(o,caught(p),.0018);});cam(local([.05,-.30,-.73]),[1.5,.75,-1.85]);
 }else if(m==='slide'){
  caseGroup.visible=false;underside.visible=false;rim.visible=false;wheels.forEach(o=>o.visible=false);side.visible=false;roll.rotation.x=t*5.5;const x=.1+ease(u)*.95;strands.forEach((o,i)=>updateTube(o,wrapped(x+i*.006,2.5,.247-.167*ease((u-.95)/.05)+i*.001,-t*5.5),.0018));cam(local([x*.7,-.25,-.5]),[.7,1.0,1.15]);
 }else if(m==='short'||m==='suction'){
  caseGroup.visible=false;underside.visible=false;rim.visible=false;wheels.forEach(o=>o.visible=false);side.visible=false;robot.rotation.x=0;robot.position.y=.5;duct.visible=true;endHair.visible=false;roll.rotation.x=t*10;
  fur.forEach((o,i)=>{const p=T.MathUtils.clamp(u*1.8-i*.105,0,1);const a=airPath.getPoint(p),b=airPath.getPoint(Math.min(.999,p+.035));const x=(i%3-1)*.19*(1-p);updateTube(o,[[a.x+x,a.y,a.z],[b.x+x+.015,b.y,b.z]],.0028);o.visible=p<.96&&s.mode!=='remain';});cam(local([0,-.10,-.42]),[2.7,1.05,-1.6]);
 }else if(m==='pinned'){
  caseGroup.visible=false;underside.visible=false;rim.visible=false;side.visible=false;wheels.forEach(o=>o.visible=false);duct.visible=true;roll.rotation.x=t*11;
  strands.forEach((o,i)=>{o.visible=i===0;updateTube(o,wrapped(.1,2.8,.248,-t*11),.0018);});
  fur.forEach((o,i)=>{const p=T.MathUtils.clamp(u*1.7-i*.09,0,1);const a=airPath.getPoint(p),b=airPath.getPoint(Math.min(.999,p+.006));updateTube(o,[[a.x+(i-3)*.05,a.y,a.z],[b.x+(i-3)*.05,b.y,b.z]],.003);o.visible=p<.98;});cam(local([0,-.15,-.45]),[1.4,1.3,1.9]);
 }else if(m==='accumulate'){
  strands.forEach((o,i)=>{o.visible=i<3;const p=wrapped(.88+i*.025,3,.10+i*.008,-t*5);updateTube(o,p,.0018);});roll.rotation.x=t*5;caps[1].position.x+=.35;
  endHair.scale.set(1,1+u*.12,1+u*.12);cam(local([1.05,-.25,-.5]),[.55,.85,.8]);
 }else if(m==='overview'){
  caseGroup.visible=false;underside.visible=false;motorUnit.visible=true;motorRotor.rotation.x=t*13;driveGear.rotation.x=t*8;roll.rotation.x=t*8;cam(local([0,-.2,-.35]),[3.0,4.8,4.5]);
 }else if(m==='center'){
  strands.forEach(o=>o.visible=false);cam(local([-.50+u*.95,-.25,-.5]),[.55,1.05,1.1]);
 }else if(m==='cap'||m==='bearing'){
  strands.forEach(o=>o.visible=false);const p=ease(u);caps[1].position.x+=m==='cap'?.45*p:.45;if(m==='cap')caps[0].position.x-=.45*p;if(m==='cap'&&s.angle===0)cam(local([0,-.25,-.5]),[3.0,6.0,6.0]);else cam(local([1.08,-.25,-.5]),[.47,.55,.67]);
 }else if(m==='motor'){
  strands.forEach(o=>o.visible=false);caseGroup.visible=false;underside.visible=false;motorUnit.visible=true;motorRotor.rotation.x=t*13;driveGear.rotation.x=t*7;cam(local([1.08,-.1,-.3]),[.8,1.2,1.0]);roll.rotation.x=t*7;
 }else if(m==='duo'){
  caseGroup.visible=false;underside.visible=false;rim.visible=false;wheels.forEach(o=>o.visible=false);side.visible=false;duct.visible=true;duo.visible=true;roll.visible=false;shaft.visible=false;inlet.visible=true;endHair.visible=false;halves.forEach((o,i)=>o.rotation.x=(i?1:-1)*t*7);
  strands.forEach((o,i)=>{const sign=i<2?-1:1,x=sign*(.90*(1-ease(Math.min(1,u/.68))))+.015*sign;const pts=wrapped(x,1.2,.248*(1-.92*ease((u-.68)/.32)),sign*t*7);for(const p of pts){p[1]+=.40*ease((u-.72)/.28);p[2]+=.35*ease((u-.72)/.28);}o.visible=(i===0||i===2)&&s.mode!=='duo';updateTube(o,pts,.0018);});
  cam(local([0,-.25,-.5]),[1.2,3.8,4.3]);
 }else if(m==='cut'){
  caseGroup.visible=false;underside.visible=false;rim.visible=false;wheels.forEach(o=>o.visible=false);side.visible=false;comb.visible=true;comb.position.y=.04*Math.sin(t*16);roll.rotation.x=t*5;
  strands.forEach((o,i)=>{o.visible=i<2;const pts=wrapped(.35+i*.03,1.5,.25);if(u>.5){if(i===0)pts.splice(48);else {pts.splice(0,48);for(const p of pts){p[1]-=(u-.5)*.7;p[2]+=(u-.5)*.4;}}}updateTube(o,pts,.0018);});cam(local([.3,-.3,-.5]),[.7,.65,.9]);
 }else if(m==='remove'){
  strands.forEach(o=>o.visible=false);gloves.visible=true;roll.position.y-=.45*ease(u);caps.forEach((o,i)=>o.position.x+=(i?1:-1)*.25*ease(u));cam(local([0,-.35,-.5]),[3.0,4.8,5.6]);
 }else if(m==='snip'){
  strands.forEach(o=>o.visible=false);caps[1].position.x+=.45;scissors.visible=true;const target=local([1.08,-.25,-.5]);scissors.position.copy(target).add(new T.Vector3(.08,.05,.20));scissors.rotation.set(PI/2,0,-.6);scissors.children.forEach((o,i)=>o.rotation.y=(i?1:-1)*(.15+.22*Math.abs(Math.cos(u*PI))));endHair.visible=u<.60;cam(target,[.6,.75,.9]);
 }else if(m==='assemble'||m==='clean'){
  strands.forEach(o=>o.visible=false);endHair.visible=false;roll.position.y-=.38*(1-ease(u));caps.forEach((o,i)=>o.position.x+=(i?1:-1)*.36*(1-ease(u)));cam(local([0,-.25,-.5]),[3.0,4.8,5.6]);
 }else{cam(local([0,-.2,-.5]),[3.0,4.8,5.6]);}
 if(s.angle){const target=new T.Vector3();camera.getWorldDirection(target);target.multiplyScalar(camera.position.distanceTo(local([0,-.25,-.5]))).add(camera.position);const offset=camera.position.clone().sub(target);offset.applyAxisAngle(new T.Vector3(0,1,0),s.angle===1?.22:-.18);camera.position.copy(target).add(offset);camera.lookAt(target);}
 if(m==='duo'&&s.mode!=='path'){camera.rotateZ(.9);camera.zoom=1.35;camera.updateProjectionMatrix();}
 renderer.render(scene,camera);return {mode:m,t,u};
};
const loader=new T.TextureLoader();
const [under,top,rubber,glove]=await Promise.all(['/assets/underside.png','/assets/lid.png','/assets/rubber.png','/assets/glove.jpg'].map(u=>loader.loadAsync(u)));
for(const t of [under,top,rubber,glove]){t.colorSpace=T.SRGBColorSpace;t.anisotropy=4;}
const uv=plate.geometry.attributes.uv,pa=plate.geometry.attributes.position;
for(let i=0;i<uv.count;i++)uv.setXY(i,(pa.getX(i)+1.40)/2.8,(pa.getY(i)+1.40)/2.8);uv.needsUpdate=true;
plate.material=new T.MeshBasicMaterial({map:under,color:0xffffff});
const topCard=mesh(new T.CircleGeometry(1.365,96),new T.MeshBasicMaterial({map:top,color:0xffffff}),[0,.205,0],caseGroup);topCard.rotation.x=-PI/2;
const fiber=await loader.loadAsync('/assets/fiber.png');fiber.colorSpace=T.SRGBColorSpace;fiber.wrapS=fiber.wrapT=T.RepeatWrapping;fiber.repeat.set(2,1);fiber.anisotropy=8;brushMat.map=fiber;brushMat.bumpMap=fiber;brushMat.bumpScale=.002;brushMat.roughness=.85;brushMat.emissive.set(0xffffff);brushMat.emissiveMap=fiber;brushMat.emissiveIntensity=.18;
rubber.wrapS=rubber.wrapT=T.RepeatWrapping;rubber.repeat.set(12,3);graphite.bumpMap=rubber;graphite.bumpScale=.0018;gloveMat.map=glove;
// Batch fixed geometry per articulated part; motion groups remain separate.
function batch(g){for(const c of [...g.children])if(c.isGroup)batch(c);const buckets=new Map();for(const c of [...g.children]){if(!c.isMesh||c.isInstancedMesh||Array.isArray(c.material)||c===plate||c===topCard)continue;c.updateMatrix();const key=c.material.uuid;if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(c);}for(const list of buckets.values()){if(list.length<2)continue;const geos=list.map(c=>{const z=c.geometry.clone().applyMatrix4(c.matrix);for(const key of Object.keys(z.attributes))if(!['position','normal','uv'].includes(key))z.deleteAttribute(key);return z.toNonIndexed();});const merged=mergeGeometries(geos,false);if(!merged)continue;const o=new T.Mesh(merged,list[0].material);g.add(o);for(const c of list)g.remove(c);}}
for(const g of [caseGroup,underside,roll,...halves,...caps,...wheels,side,gloves,comb])batch(g);
window.renderAt(0);window.ready=true;

window.captureJPEG=()=>renderer.domElement.toDataURL("image/jpeg",.94).split(",")[1];
