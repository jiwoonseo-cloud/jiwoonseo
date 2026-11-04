"""Bake exact Curve geometry and set visibility into native Blender animation.
The delivered .blend plays without Python frame-change deformation handlers.
"""
import bpy,json,sys,time
import numpy as np
from pathlib import Path
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'source'));from kinematics import coordinates
S=bpy.context.scene;P=json.loads((B/'scene-plan.json').read_text());cuts=P['cuts'];ob=bpy.data.objects['36 separate animated human hairs']
frames=sorted(set(f for c in cuts if c['set']=='MECHANISM' for f in range(c['start_frame'],c['end_frame_exclusive'])))
if ob.data.shape_keys:ob.shape_key_clear()
S.frame_set(1);ob.shape_key_add(name='Basis');keys=ob.data.shape_keys;keys.use_relative=False;mapping=[];started=time.time()
for i,f in enumerate(frames):
 S.frame_set(f);co=coordinates(float(ob['wind']),float(ob['slide']))
 sk=ob.shape_key_add(name=f'Frame_{f:04d}');sk.interpolation='KEY_LINEAR';sk.data.foreach_set('co',co[:,:,:3].reshape(-1).copy());mapping.append((f,sk.frame))
 if i%100==0:print('BAKE',i,'/',len(frames),'elapsed',round(time.time()-started),flush=True)
keys.animation_data_create();action=bpy.data.actions.new('Native per-frame hair winding and end migration');keys.animation_data.action=action;fc=action.fcurves.new(data_path='eval_time');fc.keyframe_points.add(len(mapping));fc.keyframe_points.foreach_set('co',np.asarray(mapping,dtype=np.float32).reshape(-1))
for k in fc.keyframe_points:k.interpolation='LINEAR'
fc.update()
ob['baked_native']=True
def set_at(f):return next((c['set'] for c in cuts if c['start_frame']<=f<c['end_frame_exclusive']),cuts[-1]['set'])
events=sorted(set([1,S.frame_end+1]+[c['start_frame'] for c in cuts]))
for name in ['ROOM','MECHANISM','BENCH']:
 col=bpy.data.collections[name];col.hide_render=False;col.hide_viewport=False
 for o in col.objects:
  old=None
  if o.animation_data and o.animation_data.action:old=next((f for f in o.animation_data.action.fcurves if f.data_path=='hide_render'),None)
  ev=set(events)
  if old:ev.update(int(round(k.co.x)) for k in old.keyframe_points)
  default=o.hide_render;wanted=[]
  for f in sorted(ev):
   val=(bool(old.evaluate(f)) if old else default) or set_at(min(f,S.frame_end))!=name
   if not wanted or wanted[-1][1]!=val:wanted.append((f,val))
  if old:o.animation_data.action.fcurves.remove(old)
  for path in ['hide_render','hide_viewport']:
   for f,v in wanted:setattr(o,path,v);o.keyframe_insert(path,frame=f)
   for curve in o.animation_data.action.fcurves:
    if curve.data_path==path:
     for k in curve.keyframe_points:k.interpolation='CONSTANT'
bpy.data.collections['ASSET_LIBRARY_HELD_6'].hide_render=True;bpy.data.collections['ASSET_LIBRARY_HELD_6'].hide_viewport=True
S['native_animation']=True;S.frame_set(1)
(B/'bake-manifest.json').write_text(json.dumps({'hair_curve_strands':36,'points_per_strand':96,'native_absolute_shape_keys':len(frames),'baked_frames':frames,'python_deformation_handler_required':False,'native_visibility_keyframes':True,'elapsed_seconds':round(time.time()-started,2)},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(B/'hair-animation.blend'),compress=True)
print('NATIVE BAKE COMPLETE',len(frames),'frames',round(time.time()-started,2),flush=True)
