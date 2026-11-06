"""Separate the maintenance work space from the robot footprint."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1];S=bpy.context.scene;P=json.loads((B/'scene-plan.json').read_text())
robot=bpy.data.objects['Stopped robot on maintenance mat'];robot.location.y=3.0
brush=bpy.data.objects['Removable maintenance brush']
for fc in brush.animation_data.action.fcurves:
 if fc.data_path=='location' and fc.array_index==1:
  for k in fc.keyframe_points:
   if abs(k.co.y-.8)<.001:k.co.y=2.3
  fc.update()
layout_applied=bool(S.get('maintenance_layout',False))
hand=bpy.data.objects['Hand lifts roller and removes hair']
for fc in hand.animation_data.action.fcurves:
 if fc.data_path=='location' and fc.array_index==0:
  for k in fc.keyframe_points:
   if not layout_applied and 46.58*24<=k.co.x<=66.89*24 and k.co.y>0:k.co.y+=.6
  fc.update()
def cam(c,tar,off,lens):
 o=bpy.data.objects[c['camera']];t=Vector(tar);v=Vector(off);o.location=t+v;o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.dof.focus_distance=v.length
for c in P['cuts']:
 if c['id']=='P4-C01':cam(c,(0,-.35,.5),(3,-5.5,3.8),38)
 if c['id']=='P4-C02':cam(c,(0,-.35,.5),(.4,-6,4.4),40)
 if c['id']=='P4-C03':cam(c,(1.7,-.35,.44),(.7,-3.2,1.5),50)
 if c['id']=='P8-C04':cam(c,(0,2.3,1.0),(3.6,-6.8,4.5),38)
 if c['id']=='P8-C05':cam(c,(0,-.35,.8),(3,-6,4),38)
 if c['id']=='P8-C11':cam(c,(0,1.1,.8),(4,-7,4.5),35)
 if c['id']=='P8-C12':cam(c,(0,2.3,.8),(3.8,-5,3),36)
S['maintenance_layout']='separate robot rear footprint and front brush work space'
for o in bpy.data.objects:
 if o.name.startswith('Physically separated cut hair fragment'):
  for prop in ['hide_render','hide_viewport']:
   setattr(o,prop,True);o.keyframe_insert(prop,frame=3117);o.keyframe_insert(prop,frame=3199)
  for fc in o.animation_data.action.fcurves:
   if fc.data_path in ['hide_render','hide_viewport']:
    for k in fc.keyframe_points:k.interpolation='CONSTANT'
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(B/'hair-animation.blend'),compress=True)
