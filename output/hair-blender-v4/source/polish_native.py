"""Final framing and library spacing; does not alter baked motion geometry."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1];P=json.loads((B/'scene-plan.json').read_text())
for c in P['cuts']:
 if c['paragraph']==3 and 36.075<=c['start']<38.713:
  cam=bpy.data.objects[c['camera']];target=Vector((1.60,0,.34));cam.location=target+Vector((-1.1,-2.4,.75));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=64;cam.data.dof.focus_distance=(target-cam.location).length
for o in bpy.data.collections['ASSET_LIBRARY_HELD_6'].objects:
 if o.name.startswith('Short roller'):
  o.location.x=math.copysign(1.10,o.location.x)
  if o.location.x>0:o.scale.x=-1
for m in bpy.data.materials:
 if 'contact shadow' not in m.name.lower() or not m.use_nodes:continue
 n=m.node_tree.nodes;lk=m.node_tree.links;tex=next((x for x in n if x.bl_idname=='ShaderNodeTexCoord'),None);dist=next((x for x in n if x.bl_idname=='ShaderNodeVectorMath' and x.operation=='DISTANCE'),None)
 if tex and dist:
  xy=n.new('ShaderNodeVectorMath');xy.operation='MULTIPLY';xy.inputs[1].default_value=(1,1,0);lk.new(tex.outputs['Generated'],xy.inputs[0]);lk.new(xy.outputs[0],dist.inputs[0])
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(B/'hair-animation.blend'),compress=True)
o=bpy.data.objects['36 separate animated human hairs'];ks=o.data.shape_keys
print('NATIVE ABSOLUTE KEYS',len(ks.key_blocks),'frames',ks.key_blocks[1].frame,ks.key_blocks[-1].frame,'relative',ks.use_relative,flush=True)
