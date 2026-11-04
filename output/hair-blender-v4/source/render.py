"""Render every requested frame with Blender EEVEE at native 1080x1920/24fps.
Modes: probes (one/second test inspection), test (240 frames), full (all frames).
Frame images are streamed into FFmpeg; only contact-sheet source frames persist.
"""
import bpy,json,sys,argparse,subprocess,time
import shutil
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];WORK=BASE.parents[1]/'work/hair-blender-v4';WORK.mkdir(parents=True,exist_ok=True)
a=argparse.ArgumentParser();a.add_argument('--mode',choices=['probes','test','full'],default='probes');a.add_argument('--samples',type=int,default=1);a.add_argument('--chunk',type=int,default=0);a.add_argument('--chunks',type=int,default=1);a.add_argument('--limit',type=int,default=0);a.add_argument('--benchmark-fast',action='store_true');a.add_argument('--post-dof',action='store_true');args=a.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(BASE/'source'));from kinematics import evaluate
plan=json.loads((BASE/'scene-plan.json').read_text());cuts=plan['cuts'];sc=bpy.context.scene;sc.eevee.taa_render_samples=args.samples
def cut_at(f):return next((c for c in cuts if c['start_frame']<=f+1<c['end_frame_exclusive']),cuts[-1])
focus_node=None
if args.post_dof:
 # Native-resolution depth-aware DOF in Blender's compositor. All motion still
 # comes from independently rendered EEVEE frames and each frame's true Z pass.
 for ob in bpy.data.objects:
  if ob.type=='CAMERA':ob.data.dof.use_dof=False
 sc.view_layers[0].use_pass_z=True;sc.use_nodes=True;nt=sc.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');blur=nt.nodes.new('CompositorNodeBlur');blur.filter_type='GAUSS';blur.size_x=9;blur.size_y=9
 focus_node=nt.nodes.new('CompositorNodeValue');sub=nt.nodes.new('CompositorNodeMath');sub.operation='SUBTRACT';ab=nt.nodes.new('CompositorNodeMath');ab.operation='ABSOLUTE';mp=nt.nodes.new('CompositorNodeMapRange');mp.inputs['From Min'].default_value=.18;mp.inputs['From Max'].default_value=1.0;mp.use_clamp=True
 mix=nt.nodes.new('CompositorNodeMixRGB');out=nt.nodes.new('CompositorNodeComposite');lk=nt.links
 lk.new(rl.outputs['Image'],blur.inputs[0]);lk.new(rl.outputs['Depth'],sub.inputs[0]);lk.new(focus_node.outputs[0],sub.inputs[1]);lk.new(sub.outputs[0],ab.inputs[0]);lk.new(ab.outputs[0],mp.inputs[0]);lk.new(mp.outputs[0],mix.inputs[0]);lk.new(rl.outputs['Image'],mix.inputs[1]);lk.new(blur.outputs[0],mix.inputs[2]);lk.new(mix.outputs[0],out.inputs[0])
root=WORK/('test-frames' if args.mode!='full' else 'contact-frames');root.mkdir(exist_ok=True)
test_start=round((24.288+4.2125)*24);test_end=test_start+240
if args.mode=='probes':frames=list(range(test_start,test_end,24))
elif args.mode=='test':frames=list(range(test_start,test_end))
else:frames=list(range(round(plan['duration_audio']*24)))
frames=frames[len(frames)*args.chunk//args.chunks:len(frames)*(args.chunk+1)//args.chunks]
if args.limit:frames=frames[:args.limit]
if args.benchmark_fast:
 for o in bpy.data.objects:
  if o.type=='LIGHT':o.data.use_shadow=False
  if o.type=='CAMERA':o.data.dof.use_dof=False
  if o.type=='MESH' and ('Rubber core' in o.name or 'rubber core' in o.name or 'Spiral rubber vane' in o.name):o.data.materials[0]=bpy.data.materials['EPDM soft rubber']
ff=None
if args.mode!='probes':
 out=WORK/(f'{args.mode}-silent-{args.chunk}.mp4')
 ff=subprocess.Popen(['ffmpeg','-v','error','-y','-threads','1','-f','image2pipe','-framerate','24','-i','-','-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
started=time.time();last=None;stats=[]
if args.mode!='probes':
 # One animation render keeps EEVEE's renderer and GPU buffers alive between
 # frames. Repeated still-render calls unnecessarily rebuilt the whole engine.
 folder=WORK/f'animation-{args.mode}-{args.chunk}';folder.mkdir(exist_ok=True)
 sc.render.filepath=str(folder)+'/';sc.frame_start=frames[0]+1;sc.frame_end=frames[-1]+1
 previous_frame=[None];timer=[time.time()]
 def prepare(scene,dependency_graph=None):
  f=scene.frame_current-1
  if previous_frame[0]==f:return
  previous_frame[0]=f;sec=f/24;c=cut_at(f)
  changed=(scene.camera is None or scene.camera.name!=c['camera'])
  if not scene.get('native_animation',False):
   for name in ['ROOM','MECHANISM','BENCH','ASSET_LIBRARY_HELD_6']:
    coll=bpy.data.collections[name];v=name!=c['set']
    if coll.hide_render!=v:coll.hide_render=v
  if changed:scene.camera=bpy.data.objects[c['camera']]
  if focus_node:focus_node.outputs[0].default_value=scene.camera.data.dof.focus_distance
  evaluate(scene)
  if dependency_graph is not None and changed:dependency_graph.update()
  timer[0]=time.time()
 def written(scene):
  f=scene.frame_current-1;sec=f/24;c=cut_at(f);path=Path(scene.render.frame_path(frame=scene.frame_current))
  ff.stdin.write(path.read_bytes())
  if (args.mode=='test' and (f-test_start)%24==0) or (args.mode=='full' and f%24==0):shutil.copyfile(path,root/f'{f:06d}.png')
  path.unlink();stats.append({'frame':f,'sec':sec,'cut':c['id'],'camera':scene.camera.name,'render_seconds':round(time.time()-timer[0],3)})
  if len(stats)%24==0:print('PROGRESS',args.mode,len(stats),'/',len(frames),'elapsed',round(time.time()-started),flush=True)
 bpy.app.handlers.frame_change_post.append(prepare);bpy.app.handlers.render_write.append(written)
 sc.frame_set(frames[0]+1);prepare(sc);bpy.context.view_layer.update();bpy.ops.render.render(animation=True)
 ff.stdin.close();assert ff.wait()==0
 (BASE/f'render-log-{args.mode}-{args.chunk}.json').write_text(json.dumps({'mode':args.mode,'frames':len(stats),'native_resolution':[1080,1920],'fps':24,'elapsed_seconds':round(time.time()-started,2),'test_start_seconds':test_start/24,'stats':stats},indent=2))
 print('RENDER COMPLETE',args.mode,len(stats),round(time.time()-started,2),flush=True)
 sys.exit(0)
for i,f in enumerate(frames):
 sec=f/24;cut=cut_at(f);sc.frame_set(f+1);evaluate(sc)
 if cut['id']!=last:
  for name in ['ROOM','MECHANISM','BENCH','ASSET_LIBRARY_HELD_6']:bpy.data.collections[name].hide_render=name!=cut['set']
  last=cut['id']
 sc.camera=bpy.data.objects[cut['camera']]
 save=root/f'{f:06d}.png' if args.mode=='probes' or (args.mode=='test' and (f-test_start)%24==0) or (args.mode=='full' and f%24==0) else WORK/f'current-frame-{args.chunk}.png'
 sc.render.filepath=str(save);before=time.time();bpy.ops.render.render(write_still=True)
 if ff:ff.stdin.write(save.read_bytes())
 stats.append({'frame':f,'sec':sec,'camera':sc.camera.name,'cut':cut['id'],'render_seconds':round(time.time()-before,3)})
 if i%12==0:print('PROGRESS',args.mode,i+1,'/',len(frames),'elapsed',round(time.time()-started),flush=True)
if ff:ff.stdin.close();assert ff.wait()==0,'FFmpeg encoding failed'
(BASE/f'render-log-{args.mode}-{args.chunk}.json').write_text(json.dumps({'mode':args.mode,'frames':len(frames),'native_resolution':[1080,1920],'fps':24,'elapsed_seconds':round(time.time()-started,2),'test_start_seconds':test_start/24,'stats':stats},indent=2))
print('RENDER COMPLETE',args.mode,len(frames),round(time.time()-started,2),flush=True)
