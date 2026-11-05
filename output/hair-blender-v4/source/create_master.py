from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;(O/'source').mkdir(exist_ok=True)
code=(P/'full_scene.py').read_text();exec(compile(code[:code.index("s.render.engine='CYCLES'")],str(P/'full_scene.py'),'exec'))
s.frame_set(1);full_pose(0)
for ob in [hair,fur,halfA,halfB,thread]:ob.data.update_tag()
bpy.context.view_layer.update();s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.resolution_percentage=100;s.render.fps=24
for ob in s.objects:ob.hide_set(ob.hide_render)
if bpy.context.screen:
 for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/master-scene.blend'),compress=True)
