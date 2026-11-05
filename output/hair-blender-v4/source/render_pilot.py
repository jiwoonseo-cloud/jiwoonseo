import bpy,ast,math,random,json,sys,os,time
from math import sin,cos,pi
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent;source=(P/'blender_pilot.py').read_text();bpy.ops.wm.open_mainfile(filepath=str(P/'hair-pilot.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.animation_data:ob.animation_data_clear()
 if ob.type in ['CURVE','CAMERA'] and ob.data.animation_data:ob.data.animation_data_clear()
roller=bpy.data.objects['main brush rotating group'];hair=bpy.data.objects['80 distinct long hair curves'];cam=s.camera;focus=bpy.data.objects['physical focus target'];Y=-.065;Z=.02305
rng=random.Random(3403)
for _ in range(3840*4):rng.random()
strand_specs=[(rng.uniform(.34,.48),rng.uniform(-.0045,.0045),rng.uniform(-.0012,.0012),rng.uniform(-.00014,.00014)) for _ in range(80)]
NP=144;start=21.455;wrap_start=23.102708;slide_start=27.693625;finish=31.375458
for node in ast.parse(source).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['ease','pose']:exec(ast.get_source_segment(source,node))
s.render.engine='CYCLES';s.cycles.samples=int(os.environ.get('SAMPLES','2'));s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=1;s.cycles.adaptive_threshold=.12;s.render.use_persistent_data=True;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='16';s.view_layers[0].cycles.denoising_store_passes=True
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];frames=[int(x) for x in args] if args else list(range(1,241))
for f in frames:
 s.frame_set(f);pose((f-1)/24);hair.data.update_tag();bpy.context.view_layer.update();print('POSEDEBUG', f, hair.data.splines[0].points[100].co[:], hair.location[:], hair.matrix_world.translation[:], cam.location[:],flush=True);s.render.filepath=str(P/f'pilot-frames/{f:04}.exr');t=time.time();bpy.ops.render.render(write_still=True);(P/f'pilot-frames/{f:04}.ready').touch();print('FRAME',f,'SECONDS',round(time.time()-t,3),flush=True)
(P/'PILOT_RENDER_DONE').write_text(str(len(frames)))
