"""Keep the suction actor visible during the two dust-explanation cuts."""
import bpy
from pathlib import Path
B=Path(__file__).resolve().parents[1];S=bpy.context.scene;o=bpy.data.objects['36 separate animated human hairs']
for prop in ['hide_render','hide_viewport']:
 setattr(o,prop,True);o.keyframe_insert(prop,frame=1698);setattr(o,prop,False);o.keyframe_insert(prop,frame=1792)
for fc in o.animation_data.action.fcurves:
 if fc.data_path in ['hide_render','hide_viewport']:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
for o in bpy.data.objects:
 if o.name.startswith('Animated household dust grain'):
  for f,scale in [(1,1),(1698,1.8),(1792,1)]:o.scale=(scale,)*3;o.keyframe_insert('scale',frame=f)
  for fc in o.animation_data.action.fcurves:
   if fc.data_path=='scale':
    for k in fc.keyframe_points:k.interpolation='CONSTANT'
mat=next(m for m in bpy.data.materials if m.name.startswith('Matte household dust grains'));col=mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']
for f,color in [(1,(.31,.25,.18,1)),(1698,(.65,.48,.26,1)),(1792,(.31,.25,.18,1))]:col.default_value=color;col.keyframe_insert('default_value',frame=f)
for fc in mat.node_tree.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='CONSTANT'
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(B/'hair-animation.blend'),compress=True)
