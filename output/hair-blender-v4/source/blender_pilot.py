import bpy,math,random,json,sys,os,time
from mathutils import Vector
from math import sin,cos,pi
from pathlib import Path
P=Path(__file__).resolve().parent;(P/'pilot-frames').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine=os.environ.get('ENGINE','BLENDER_EEVEE_NEXT');s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=240
s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='16';s.view_layers[0].cycles.denoising_store_passes=True;s.render.film_transparent=False;s.render.use_persistent_data=True
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
if s.render.engine=='BLENDER_EEVEE_NEXT':s.eevee.taa_render_samples=int(os.environ.get('SAMPLES','8'));s.eevee.use_raytracing=False
else:s.cycles.samples=int(os.environ.get('SAMPLES','8'));s.cycles.use_denoising=False;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=1;s.cycles.glossy_bounces=2;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.12;s.cycles.adaptive_min_samples=1
w=bpy.data.worlds.new('neutral studio ambience');s.world=w;w.use_nodes=True;w.node_tree.nodes.get('Background').inputs[0].default_value=(.14,.17,.20,1);w.node_tree.nodes.get('Background').inputs[1].default_value=.3
rng=random.Random(3403)
def mat(n,c,rough=.4,metal=0,grain=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if grain:
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(P/'assets/rubber.png'),check_existing=True);tex.image.colorspace_settings.name='Non-Color';tex.projection='BOX';tex.projection_blend=.25;tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Generated'],tex.inputs['Vector'])
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=grain;nt.links.new(tex.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 return m
white=mat('injection molded ivory ABS',(.68,.71,.70),.30,0,.00007);black=mat('carbon rubber micrograin',(.006,.009,.010),.52,0,.00010);teal=mat('molded flexible teal elastomer',(.008,.090,.075),.36,0,.000035)
steel=mat('machined bearing steel',(.42,.47,.50),.21,.95,.000004);steel.node_tree.nodes.get('Principled BSDF').inputs['Anisotropic'].default_value=.55
nylon=mat('fine black nylon bristles',(.004,.006,.007),.40,0,0)
black.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.22
hairmat=mat('chestnut keratin filaments',(.065,.022,.009),.26,0,0);hb=hairmat.node_tree.nodes.get('Principled BSDF');hb.inputs['Anisotropic'].default_value=.8;hb.inputs['Coat Weight'].default_value=.18
wood=mat('warm ash work surface',(.25,.17,.105),.5,0,0);nt=wood.node_tree;tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=6;tex.inputs['Detail'].default_value=3;tc=nt.nodes.new('ShaderNodeTexCoord');mp=nt.nodes.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(.8,70,3);nt.links.new(tc.outputs['Generated'],mp.inputs[0]);nt.links.new(mp.outputs[0],tex.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.10,.055,.026,1);ramp.color_ramp.elements[1].color=(.34,.23,.13,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00018;bump.inputs['Strength'].default_value=.2;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);o.data.materials.append(m)
 for p in me.polygons:p.use_smooth=True
 return o
def box(n,loc,size,m,bevel=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('manufactured radiused corners','BEVEL');b.width=bevel;b.segments=4;o.modifiers.new('weighted face normals','WEIGHTED_NORMAL');return o
def lathe(n,prof,x,y,z,m):
 v=[];f=[];N=64
 for xx,r in prof:
  for k in range(N):a=k*2*pi/N;v.append((xx+x,y+r*cos(a),z+r*sin(a)))
 for j in range(len(prof)-1):
  for k in range(N):f.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 return mesh(n,v,f,m)
def torus(n,major,minor,loc,m):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=8,location=loc,major_radius=major,minor_radius=minor,rotation=(0,pi/2,0));o=bpy.context.object;o.name=n;o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def empty(n,loc=(0,0,0)):
 o=bpy.data.objects.new(n,None);s.collection.objects.link(o);o.location=loc;return o
def curves(n,lines,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=0;cu.resolution_u=1
 for line in lines:
  sp=cu.splines.new('POLY');sp.points.add(len(line)-1)
  for point,co in zip(sp.points,line):point.co=(*co,1)
 ob=bpy.data.objects.new(n,cu);s.collection.objects.link(ob);cu.materials.append(m);return ob
Y=-.065;Z=.02305
roller=empty('main brush rotating group',(0,Y,Z))
prof=[(-.124,0),(-.124,.0145),(-.122,.016),(-.120,.0166),(.120,.0166),(.122,.016),(.124,.0145),(.124,0)]
core=lathe('tapered rubber roller with end shoulders',prof,0,0,0,black);core.parent=roller
# Four extruded helical fins with curved lip cross-sections, not round ropes.
for k in range(4):
 v=[];f=[];cross=[(-.0018,.0165),(.0005,.0169),(.0016,.0182),(.0015,.0203),(.0008,.0208),(-.0002,.0198)]
 for j in range(161):
  x=-.119+.238*j/160;a=k*pi/2+x*34
  for dx,r in cross:v.append((x+dx,r*cos(a),r*sin(a)))
 for j in range(160):
  for q in range(6):f.append((j*6+q,j*6+(q+1)%6,(j+1)*6+(q+1)%6,(j+1)*6+q))
 o=mesh('flexible helical molded lip',v,f,teal);o.parent=roller
# Thousands of fine nylon curves with varied length and natural tip splay.
lines=[]
for k in range(4):
 for j in range(80):
  x=-.117+.234*j/79;a=k*pi/2+x*34+.35
  for q in range(12):
   xx=x+rng.uniform(-.0011,.0011);aa=a+rng.uniform(-.035,.035);end=rng.uniform(.0215,.0230);bend=rng.uniform(-.0007,.0007)
   lines.append([(xx,.0168*cos(aa),.0168*sin(aa)),(xx+bend*.3,.019*cos(aa),.019*sin(aa)),(xx+bend,end*cos(aa+.025),end*sin(aa+.025))])
bristles=curves('3840 separate nylon bristle curves',lines,.000045,nylon);bristles.parent=roller
axle=lathe('stainless axle and keyed ends',[(-.149,0),(-.149,.003),(-.138,.003),(-.136,.004),(.136,.004),(.138,.003),(.149,.003),(.149,0)],0,Y,Z,steel)
for sign in [-1,1]:
 x=sign*.135
 torus('bearing outer race machined groove',.0085,.0011,(x,Y,Z),steel);torus('bearing inner race',.0048,.00065,(x,Y,Z),steel)
 for k in range(10):
  a=k*2*pi/10;bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.0011,location=(x,Y+.0065*cos(a),Z+.0065*sin(a)));o=bpy.context.object;o.name='bearing steel ball';o.data.materials.append(steel)
 cap=lathe('scalloped removable rubber end cap',[(-.0035,0),(-.0035,.008),(-.0025,.011),(.002,.011),(.0035,.009),(.0035,0)],sign*.146,Y,Z,black)
 for j in range(20):
  a=j*2*pi/20;o=box('molded endcap grip rib',(sign*.146,Y+.0108*cos(a),Z+.0108*sin(a)),(.005,.00055,.00075),black,.0002);o.rotation_euler[0]=a
# The same robot's service bay remains in the scene, giving the macro a physical context.
box('white ABS brush mounting bridge',(0,-.031,.048),(.292,.008,.012),white,.003)
for sign in [-1,1]:
 box('end bearing pocket molded into service frame',(sign*.155,Y,.035),(.012,.055,.030),white,.004)
 for yy in [-.087,-.042]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.0028,depth=.0011,location=(sign*.153,yy,.051));o=bpy.context.object;o.name='recessed stainless screw';o.data.materials.append(steel);box('screwdriver slot',(sign*.153,yy,.05158),(.0034,.0006,.00012),black,.0001)
# Rear half of circular top cover, shown as a purposeful cutaway.
v=[];f=[];N=100
for z in [.043,.075]:
 for j in range(N+1):a=j*pi/N;v.append((.172*cos(a),.172*sin(a)+.005,z))
for j in range(N):f.append((j,j+1,N+2+j,N+1+j))
v.extend([(0,.005,.075)]);c=len(v)-1
for j in range(N):f.append((c,N+1+j,N+2+j))
case=mesh('circular white robot cover rear cutaway',v,f,white);sol=case.modifiers.new('molded cover thickness','SOLIDIFY');sol.thickness=.0025;be=case.modifiers.new('soft housing edge','BEVEL');be.width=.0015;be.segments=3
box('ash wood living room floor',(0,0,-.006),(4,4,.012),wood,.001)
# Fine keratin strands with a length-preserving winding/axial migration animation.
NHAIR=80;NP=144;lines=[[(0,0,0)]*NP for _ in range(NHAIR)];hair=curves('80 distinct long hair curves',lines,.000035,hairmat)
strand_specs=[(rng.uniform(.34,.48),rng.uniform(-.0045,.0045),rng.uniform(-.0012,.0012),rng.uniform(-.00014,.00014)) for _ in range(NHAIR)]
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
# Actual public narration segment: contact -> winding -> migration.
start=21.455;wrap_start=23.102708;slide_start=27.693625;finish=31.375458
# Native +10% TTS with exact word boundaries; no audio post-speedup.
def pose(t):
 absolute=start+t;u=ease((absolute-wrap_start)/1.6);shift=ease((absolute-slide_start)/(finish-slide_start));base=-.055+.185*shift
 radius=.023-.0165*ease((base-.126)/.004);contact=ease((absolute-start)/(wrap_start-start));gap=.012*(1-contact);wound=(.25+1.92*u)*2*pi*.023*ease((contact-.70)/.30);theta=wound/radius
 spin=2*pi*3*max(0,absolute-wrap_start-1.6);roller.rotation_euler[0]=-(2*pi*3*(absolute-start)+theta)
 for i,(sp,(L,dx,dy,dz)) in enumerate(zip(hair.data.splines,strand_specs)):
  x=base+dx*(1-.65*shift);r=radius+dz*.8+.0008*u*(1-shift)*(i%7)/7+(.0014*(.5+.5*sin(i))*(shift**4) if i%5==0 else 0);arc=max(0,wound-(i%9)*.045*r);free=max(.025,L-arc);nfree=36;phase=.9*sin(i*3.1)*u
  for j,point in enumerate(sp.points):
   if j<nfree:
    q=j/(nfree-1);xx=x+.008*(1-q)*sin(i*.7)+.002*sin(q*6*pi+i)*(1-q)**2;yy=Y+gap+r*cos(-pi/2-spin+phase)*ease(q)+free*(1-q);zz=.000045+(Z+r*sin(-pi/2-spin+phase)-.000045)*ease(q)+.00001*sin(i+.4*q);co=(xx,yy,zz)
   else:
    q=(j-nfree)/(NP-nfree-1);aa=-pi/2-spin+phase-arc/r*q;xx=x+q*.0004*(arc/(2*pi*r))+(.00022+.0014*u*(1-shift))*sin(q*7*pi+i)*sin(q*pi);co=(xx,Y+gap+r*cos(aa)+dy*.08,Z+r*sin(aa))
   point.co=(*co,1)
 # Distinct camera language; same hair state continues across every cut.
 if t<(wrap_start-start):target=Vector((base,Y+.006,.0035));off=Vector((.055,.105,.040));lens=65;fstop=32
 elif t<4.1:target=Vector((base,Y,.014));off=Vector((-.055,-.145,.035));lens=60;fstop=32
 elif t<6.1:target=Vector((base,Y,.015));off=Vector((-.03,-.17,.19));lens=40;fstop=32
 elif t<8.1:target=Vector((.015,Y-.09,.012));off=Vector((0,-.05,.60));lens=35;fstop=24
 else:target=Vector((.115,Y,.020));off=Vector((.045,-.095,.065));lens=45;fstop=32
 cam.location=target+off;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;viewnorm=max(.0001,(off.y**2+off.z**2)**.5);focus.location=(Vector((base,Y+.005,.0005)) if t<(wrap_start-start) else Vector((base if t<8 else .132,Y+(radius if t<8 else .007)*off.y/viewnorm,Z+(radius if t<8 else .007)*off.z/viewnorm)));cam.data.dof.aperture_fstop=fstop
 return base,radius
# Physical softboxes, with real geometric reflections in metal and rubber.
def area(n,pos,energy,size,color,target=(0,Y,.02),size_y=None):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=n;o.data.energy=energy;o.data.shape='RECTANGLE';o.data.size=size;o.data.size_y=size_y or size;o.data.color=color;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('large soft studio key',(-.18,-.14,.34),3,.25,(1,.91,.80),size_y=.15)
area('cool strip reflection',(.12,.12,.25),1.5,.18,(.76,.86,1),size_y=.025)
area('hair edge softbox',(-.08,.04,.12),1.2,.12,(1,.72,.48),size_y=.015)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='PERSP';cam.data.sensor_width=36;cam.data.clip_start=.001;cam.data.clip_end=10;cam.data.dof.use_dof=True;focus=empty('physical focus target');cam.data.dof.focus_object=focus
# Save keyframed geometry in an editable .blend, not only evaluated images.
keyframes=[1,22,61,120,144,181,216,240]
for frame in keyframes:
 t=(frame-1)/24;pose(t);roller.keyframe_insert('rotation_euler',frame=frame);cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame);cam.data.keyframe_insert('lens',frame=frame);focus.keyframe_insert('location',frame=frame)
# Curves receive full per-frame control-point keys, preserving the designed winding path.
for frame in keyframes:
 pose((frame-1)/24)
 for sp in hair.data.splines:
  for point in sp.points:point.keyframe_insert('co',frame=frame)
# Linear interpolation prevents overshooting through the brush between saved poses.
for act in bpy.data.actions:
 for fc in act.fcurves:
  for key in fc.keyframe_points:key.interpolation='LINEAR'
pose(0);s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'hair-pilot.blend'),compress=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if args and args[0]=='still':frames=[int(a) for a in args[1:]] or [48]
else:frames=list(range(1,241))
for frame in frames:
 s.frame_set(frame);pose((frame-1)/24);s.render.filepath=str(P/f'pilot-frames/{frame:04}.exr');clock=time.time();bpy.ops.render.render(write_still=True);print('PILOT_FRAME',frame,'SECONDS',round(time.time()-clock,3),flush=True)
sys.stdout.flush();os._exit(0)
