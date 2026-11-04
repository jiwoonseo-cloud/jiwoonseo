from pathlib import Path
import json
P=Path('/workspace/work/hair-v3');p=P/'scene.js';s=p.read_text()
s=s.replace("({remain:'short',duoflow:'duo',path:'duo',accumulate:'slide'})", "({remain:'short',duoflow:'duo',path:'duo'})")
s=s.replace("const p=(u*1.3+i/7)%1;", "const p=T.MathUtils.clamp(u*1.8-i*.105,0,1);")
s=s.replace("o.visible=p<.96;", "o.visible=p<.96&&s.mode!=='remain';")
s=s.replace("o.visible=i===0||i===2;updateTube(o,pts,.0018);", "o.visible=(i===0||i===2)&&s.mode!=='duo';updateTube(o,pts,.0018);")
# Additional semantic actions, not crops of a repeated wrapping clip.
s=s.replace("}else if(m==='center'){", """}else if(m==='pinned'){
  caseGroup.visible=false;underside.visible=false;rim.visible=false;side.visible=false;wheels.forEach(o=>o.visible=false);duct.visible=true;roll.rotation.x=t*11;
  strands.forEach((o,i)=>{o.visible=i===0;updateTube(o,wrapped(.1,2.8,.248,-t*11),.0018);});
  fur.forEach((o,i)=>{const p=T.MathUtils.clamp(u*1.7-i*.09,0,1);const a=airPath.getPoint(p),b=airPath.getPoint(Math.min(.999,p+.006));updateTube(o,[[a.x+(i-3)*.05,a.y,a.z],[b.x+(i-3)*.05,b.y,b.z]],.003);o.visible=p<.98;});cam(local([0,-.15,-.45]),[1.4,1.3,1.9]);
 }else if(m==='accumulate'){
  strands.forEach((o,i)=>{o.visible=i<3;const p=wrapped(.88+i*.025,3,.10+i*.008,-t*5);updateTube(o,p,.0018);});roll.rotation.x=t*5;caps[1].position.x+=.35;
  endHair.scale.set(1,1+u*.12,1+u*.12);cam(local([1.05,-.25,-.5]),[.55,.85,.8]);
 }else if(m==='overview'){
  caseGroup.position.y=.40*ease(u);underside.visible=true;roll.rotation.x=t*8;cam(local([0,-.2,-.35]),[2.1,3.4,3.0]);
 }else if(m==='center'){""")
s=s.replace("robot.visible=true;robot.position", "caseGroup.position.y=0;endHair.scale.set(1,1,1);robot.visible=true;robot.position")
p.write_text(s)
p=P/'timeline.json';a=json.loads(p.read_text())
for x in a:
 if x['para']==4 and x['mode'] in ['wrap','slide','remain']:x['mode']='pinned'
 if x['para']==6 and x['mode']=='slide':x['mode']='accumulate'
 if x['para']==7 and x['mode']=='wrap':x['mode']='overview'
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));Path('/workspace/jiwoonseo/output/hair-v3/shot-list.json').write_text(p.read_text())
