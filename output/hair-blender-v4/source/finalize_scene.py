"""Finish non-pilot shots: hold end states and frame the actually spoken actor.
The pilot frames 685–924 retain their baked geometry and camera settings.
"""
import bpy,json,sys,math,re,itertools
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'source'));from kinematics import coordinates
S=bpy.context.scene;P=json.loads((B/'scene-plan.json').read_text());O=bpy.data.objects['36 separate animated human hairs'];cuts=P['cuts'];D=json.loads((B/'source/voice-measurements.json').read_text())['ko-KR-HyunsuMultilingualNeural']['paragraph_seconds'];offset={};v=0
for p in [1,2,3,4,5,7,8]:offset[p]=v;v+=D[f'{p:02}']
def cue(p,t,end=False):
 ev=json.loads((B/'audio'/f'{p:02}.json').read_text());norm=lambda x:re.sub('[^가-힣a-zA-Z0-9]','',x);s=''.join(norm(e['text']) for e in ev);n=norm(t);i=s.index(n);pos=0;sel=[]
 for e in ev:
  k=len(norm(e['text']))
  if pos+k>i and pos<i+len(n):sel.append(e)
  pos+=k
 e=sel[-1] if end else sel[0];return offset[p]+(e['offset']+(e['duration'] if end else 0))/1e7
def curves(o,path,index=None):return [c for c in o.animation_data.action.fcurves if c.data_path==path and (index is None or c.array_index==index)]
def value(o,path,index,f):return curves(o,path,index)[0].evaluate(f)
def insert(o,path,f,v,index=None):
 if index is None:setattr(o,path,v);o.keyframe_insert(path,frame=f)
 else:getattr(o,path)[index]=v;o.keyframe_insert(path,index=index,frame=f)
 for c in curves(o,path,index):
  for k in c.keyframe_points:k.interpolation='LINEAR'
# Keep arrived hair at the end, rather than interpolating back toward the next
# independent demonstration while this paragraph is still visible.
for p,start in [(3,925),(5,round(cue(5,'감김이 사라지지',True)*24)+2)]:
 last=round((offset[p]+D[f'{p:02}'])*24);prev=start-1;xyz=[value(O,'location',j,prev) for j in range(3)]
 for j,x in enumerate(xyz):insert(O,'location',prev,x,j)
 insert(O,'location',start,(1.6,0,0));insert(O,'location',last,(1.6,0,0))
 for prop in ['wind','slide']:
  path=f'["{prop}"]';old=curves(O,path)[0].evaluate(prev);O[prop]=float(old);O.keyframe_insert(path,frame=prev);O[prop]=1.;O.keyframe_insert(path,frame=start);O.keyframe_insert(path,frame=last)
  for c in curves(O,path):
   for k in c.keyframe_points:k.interpolation='LINEAR'
 flat=coordinates(1.,1.)[:,:,:3].reshape(-1).copy()
 for f in range(start,last+1):
  sk=O.data.shape_keys.key_blocks.get(f'Frame_{f:04d}')
  if sk:sk.data.foreach_set('co',flat)
 spin=next(o for o in O.parent.children if o.name.startswith('Roller spinning assembly'));old=value(spin,'rotation_euler',0,prev);insert(spin,'rotation_euler',prev,old,0);insert(spin,'rotation_euler',last,old+(last-prev)/24*math.tau*.85,0)
# Small visible end-fibre vibration is exaggerated for clarity; never below floor.
for a,b in [(cue(3,'길이가 긴'),offset[4]-.04),(cue(5,'감김이 사라지지',True),offset[7]-.04)]:
 for f in range(round(a*24)+1,round(b*24)+1,4):insert(O,'location',f,.015*math.sin((f/24-a)*math.pi/ .45)**2,2)
 insert(O,'location',round(b*24)+1,0.,2)
# Keep the inspection hand at the bearing until the wide view crosses to the other end.
hand=bpy.data.objects['Hand lifts roller and removes hair'];insert(hand,'location',round(cue(4,'확인하라고')*24)+1,(1.7,-.35,.85))
dg=bpy.context.evaluated_depsgraph_get()
def camera(cam,target,offset3,lens):
 target=Vector(target);cam.location=target+Vector(offset3);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.dof.focus_distance=Vector(offset3).length
def project(cam,p):
 world=Matrix.LocRotScale(cam.location,cam.rotation_euler.to_quaternion(),Vector((1,1,1)));proj=cam.calc_matrix_camera(dg,x=1080,y=1920);q=proj@world.inverted()@Vector((*p,1));return (q.x/q.w*.5+.5,q.y/q.w*.5+.5)
def fit(cam,points):
 for _ in range(16):
  uv=[project(cam,p) for p in points]
  if all(.06<=u<=.94 and .06<=v<=.94 for u,v in uv):break
  cam.data.lens*=.91
def bbox(x0,x1,y0,y1,z0,z1):return list(itertools.product([x0,x1],[y0,y1],[z0,z1]))
short=cue(3,'짧은 털은');long=cue(3,'길이가 긴');air=cue(5,'흡입력은');hook=cue(5,'머리카락이 롤러에')
for c in cuts:
 p=c['paragraph'];cam=bpy.data.objects[c['camera']];a,b=c['start'],c['end'];idx=int(cam.name.split('_')[1])
 if p==3 and a<short-.02:continue
 if c['set']=='MECHANISM':
  floor=(p==3 and short-.02<=a<long-.02) or (p==5 and air-.02<=a<hook-.02)
  if floor:
   camera(cam,(0,-.60,.23),(.25,-2.65,2.65),35);fit(cam,bbox(-.62,.62,-1.82,.56,.002,.70))
  elif p==3 and a>=long-.02:
   camera(cam,(1.60,0,.34),[(0,-2.4,.65),(.10,-1.8,1.8)][idx%2],60)
  else:
   x0=value(O,'location',0,c['start_frame']);x1=value(O,'location',0,c['end_frame_exclusive']-1);target=Vector(((x0+x1)/2,0,.34));oldfocus=cam.location+cam.rotation_euler.to_matrix()@Vector((0,0,-cam.data.dof.focus_distance));off=cam.location-oldfocus;camera(cam,target,off,min(cam.data.lens,45) if abs(x1-x0)>.35 else cam.data.lens);fit(cam,bbox(min(x0,x1)-.10,max(x0,x1)+.10,-.36,.36,.005,.70))
 if p==4 and cue(4,'로보락')-.02<=a<cue(4,'너무')-.02:
  if a>=offset[4]+12.0:camera(cam,(0,-.35,.55),(2.5,-5.5,4.8),42);fit(cam,bbox(-2.5,2.5,-.8,.4,.1,1.1))
  else:camera(cam,(1.70,-.35,.55),[(.4,-3.2,1.5),(-.8,-2.8,1.6)][idx%2],50);fit(cam,bbox(1.25,2.30,-.65,.2,.25,1.02))
 if p==4 and a>=cue(4,'너무')-.02:camera(cam,(1.0,-.35,.38),[(.4,-3,1.35),(-.9,-2.6,1.4)][idx%2],48);fit(cam,bbox(.45,1.85,-.40,.4,.03,.76))
 if p==8 and cue(8,'일주일에')-.02<=a<cue(8,'끝단에 감겨')-.02:
  camera(cam,(0,-.35,.55),[(0,-5.2,4.7),(3.3,-5,4.8),(-3.3,-5,3.8)][idx%3],42);fit(cam,bbox(-2.5,2.5,-.8,.3,.1,1.1))
# Actual 3D dust grains share the already keyframed floor-to-intake paths.
col=bpy.data.collections['MECHANISM'];refs=[o for o in col.objects if o.name.startswith('Short hair - floor to intake')]
dust=bpy.data.materials.new('Matte household dust grains');dust.use_nodes=True;n=dust.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.31,.25,.18,1);n.inputs['Roughness'].default_value=.85
for i,ref in enumerate(refs):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=.006,location=(.008*(i%3),.02,.006));o=bpy.context.object;o.name='Animated household dust grain'
 for cc in list(o.users_collection):cc.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(dust);o.animation_data_create();o.animation_data.action=ref.animation_data.action.copy()
 for fc in list(o.animation_data.action.fcurves):
  if fc.data_path not in ['hide_render','hide_viewport']:o.animation_data.action.fcurves.remove(fc)
 constraint=o.constraints.new('COPY_LOCATION');constraint.target=ref;constraint.use_offset=True
S.frame_set(1);S['whole_scene_actor_framing_review']=True
bpy.ops.wm.save_as_mainfile(filepath=str(B/'hair-animation.blend'),compress=True)
print('WHOLE SCENE FINALIZED; pilot 685–924 preserved',flush=True)
