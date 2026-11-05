import bpy,math,random,ast,json,os
from pathlib import Path
from math import sin,cos,pi
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'hair-pilot.blend'));s=bpy.context.scene
source=(P/'blender_pilot.py').read_text()
for node in ast.parse(source).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['mat','mesh','box','lathe','torus','empty','curves']:exec(ast.get_source_segment(source,node))
white=bpy.data.materials['injection molded ivory ABS'];black=bpy.data.materials['carbon rubber micrograin'];teal=bpy.data.materials['molded flexible teal elastomer'];steel=bpy.data.materials['machined bearing steel'];nylon=bpy.data.materials['fine black nylon bristles'];hairmat=bpy.data.materials['chestnut keratin filaments'];wood=bpy.data.materials['warm ash work surface']
for original in list(s.objects):original['core_original']=True
ROOT=empty('ROBOT_ROOT');floor=bpy.data.objects['ash wood living room floor'];focus=bpy.data.objects['physical focus target']
for o in list(s.objects):
 if o!=ROOT and o.parent is None and o.type in ['MESH','CURVE','EMPTY'] and o not in [floor,focus]:o.parent=ROOT
roller=bpy.data.objects['main brush rotating group'];hair=bpy.data.objects['80 distinct long hair curves'];partial=bpy.data.objects['circular white robot cover rear cutaway']
# Separate end fittings into articulated brush assemblies.
capgroups=[];bearinggroups=[]
for sign in [-1,1]:
 cg=empty('CAP_'+('R' if sign==1 else 'L'));cg.parent=ROOT;cg.location=(0,-.065,.02305);bg=empty('BEARING_'+('R' if sign==1 else 'L'));bg.parent=ROOT;bg.location=(0,-.065,.02305);bpy.context.view_layer.update()
 for o in list(ROOT.children):
  if o in [cg,bg]:continue
  cx=sum((o.matrix_world@Vector(q)).x for q in o.bound_box)/8 if o.type=='MESH' else o.location.x
  if ('end cap' in o.name or 'endcap grip' in o.name) and cx*sign>0:o.parent=cg;o.matrix_parent_inverse=cg.matrix_world.inverted()
  if ('bearing outer race' in o.name or 'bearing inner race' in o.name or 'bearing steel ball' in o.name) and o.location.x*sign>0:o.parent=bg;o.matrix_parent_inverse=bg.matrix_world.inverted()
 capgroups.append(cg);bearinggroups.append(bg)
# Hollow, beveled manufactured body; underside service opening remains real geometry.
body=lathe('closed round ABS upper shell',[(.009,0),(.009,.164),(.014,.174),(.020,.176),(.064,.175),(.074,.168),(.076,0)],0,0,0,white);body.rotation_euler.y=-pi/2;body.parent=ROOT
cut=box('temporary service cavity cutter',(0,-.065,.028),(.306,.077,.061),black,.004)
import bmesh
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bm.to_mesh(body.data);bm.free()
mod=body.modifiers.new('open main brush bay','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
bumper=lathe('bumper seam and sensor band',[(.030,.173),(.031,.177),(.035,.177),(.036,.173)],0,0,0,black);bumper.rotation_euler.y=-pi/2;bumper.parent=ROOT
lidar=lathe('lidar turret with rounded lip',[(0,0),(0,.026),(.002,.028),(.016,.028),(.020,.024),(.020,0)],0,0,0,white);lidar.rotation_euler.y=-pi/2;lidar.location=(0,.030,.076);lidar.parent=ROOT
lidarseam=lathe('lidar dark sensor seam',[(.005,.0281),(.008,.0281)],0,0,0,black);lidarseam.rotation_euler.y=-pi/2;lidarseam.location=(0,.030,.076);lidarseam.parent=ROOT
for x in [-.008,.008]:
 b=lathe('unmarked tactile button',[(0,0),(0,.005),(.001,.005),(.0015,.004),(.0015,0)],0,0,0,steel);b.rotation_euler.y=-pi/2;b.location=(x,-.077,.076);b.parent=ROOT
underside=lathe('dark underside service plate',[(.009,0),(.009,.164),(.012,.164),(.012,0)],0,0,0,black);underside.rotation_euler.y=-pi/2;underside.parent=ROOT
bm=bmesh.new();bm.from_mesh(underside.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bm.to_mesh(underside.data);bm.free()
cut=box('temporary underside opening',(0,-.065,.010),(.31,.081,.025),black,.003);mod=underside.modifiers.new('service bay aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=underside;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for sign in [-1,1]:
 wheel=empty('DRIVE_WHEEL_'+str(sign));wheel.location=(sign*.145,.025,.025);wheel.parent=ROOT
 tire=lathe('treaded rubber drive tire',[(-.011,0),(-.011,.019),(-.009,.024),(.009,.024),(.011,.019),(.011,0)],0,0,0,black);tire.parent=wheel
 for k in range(30):
  a=k*2*pi/30;o=box('tire traction block',(0,.024*cos(a),.024*sin(a)),(.022,.003,.0028),black,.0005);o.rotation_euler.x=a;o.parent=wheel
 hub=lathe('wheel hub',[(-.0115,0),(-.0115,.011),(-.013,.011),(-.013,0)],0,0,0,steel);hub.parent=wheel
caster=empty('CASTER');caster.location=(0,.126,.016);caster.parent=ROOT
for x in [-.008,.008]:o=box('caster fork',(x,0,.010),(.003,.017,.023),white,.003);o.parent=caster
ob=lathe('front caster wheel',[(-.006,0),(-.006,.013),(.006,.013),(.006,0)],0,0,0,black);ob.parent=caster
side=empty('SIDE_BRUSH');side.location=(-.105,.091,.007);side.parent=ROOT
ob=lathe('side brush hub',[(0,0),(0,.012),(.005,.012),(.005,0)],0,0,0,black);ob.rotation_euler.y=-pi/2;ob.parent=side
for k in range(3):
 a=k*2*pi/3
 lines=[]
 for j in range(30):
  aa=a+(j-15)*.004;lines.append([(.008*cos(aa),.008*sin(aa),0),(.034*cos(aa),.034*sin(aa),-.001),(.050*cos(aa),.050*sin(aa),-.003)])
 ob=curves('side brush individual fibers',lines,.00007,nylon);ob.parent=side
# Organic nitrile gloves, remeshed into continuous anatomical surfaces.
glovemat=mat('black nitrile glove',(.012,.015,.017),.38,0,.00004)
def glove(name,sign):
 group=empty(name);group.location=(sign*.182,-.025,.040);group.parent=ROOT;parts=[]
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=(.030,0,.008));p=bpy.context.object;p.scale=(.023,.036,.013);p.name='glove palm';p.data.materials.append(glovemat);parts.append(p)
 for k in range(4):
  y=-.026+k*.017;pts=[(.022,y,.014),(.003,y,.022),(-.014,y,.012),(-.012,y,-.009)]
  ob=curves('curved anatomical gloved finger',[pts],.0065,glovemat)
  for j,q in enumerate(ob.data.splines[0].points):q.radius=1-j*.09
  parts.append(ob)
 ob=curves('opposable glove thumb',[[[.037,-.029,.003],[.014,-.044,-.001],[-.005,-.039,-.012]]],.008,glovemat);parts.append(ob)
 ob=box('glove wrist cuff',(.064,0,.006),(.043,.042,.020),glovemat,.009);parts.append(ob)
 for o in parts:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  if o.type=='CURVE':bpy.ops.object.convert(target='MESH')
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hand=bpy.context.object;hand.name=name+'_MESH';bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);rem=hand.modifiers.new('seamless gloved anatomy','REMESH');rem.mode='VOXEL';rem.voxel_size=.0022;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name);sm=hand.modifiers.new('soft tissue smoothing','SMOOTH');sm.factor=.5;sm.iterations=3;hand.modifiers.new('smooth glove surface','SUBSURF').levels=1
 # Geometry was authored in local hand space.
 hand.parent=group
 if sign<0:group.scale.x=-1
 return group
glove('HAND_R',1);glove('HAND_L',-1)
# A real two-leaf pair of scissors with tapered blade profiles and oval finger rings.
scissors=empty('SCISSORS');scissors.parent=ROOT
for sign in [-1,1]:
 leaf=empty('SCISSOR_LEAF_'+str(sign));leaf.parent=scissors
 poly=[(-.004,.006),(.003,.006),(.0025,-.053),(0,-.068),(-.002,-.053)]
 v=[(x,y,z) for z in [-.0005,.0005] for x,y in poly];N=len(poly);f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
 blade=mesh('tapered precision scissor blade',v,f,steel);blade.parent=leaf;be=blade.modifiers.new('polished blade edges','BEVEL');be.width=.00025;be.segments=2
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=10,major_radius=.009,minor_radius=.0014,location=(0,.023,sign*.0007));ring=bpy.context.object;ring.scale.y=1.4;ring.data.materials.append(steel);ring.parent=leaf
 ob=box('scissor handle shank',(0,.010,sign*.0007),(.003,.018,.0015),steel,.0007);ob.parent=leaf
bolt=lathe('scissor pivot rivet',[(-.001,0),(-.001,.0023),(.001,.0023),(.001,0)],0,0,0,steel);bolt.rotation_euler.y=-pi/2;bolt.parent=scissors
# Opposed short roller teaching insert, derived from the same manufactured brush asset.
duo=empty('DUO');duo.location=(0,-.065,.02305);duo.parent=ROOT
for sign in [-1,1]:
 half=empty('DUO_HALF_'+str(sign));half.location.x=sign*.067;half.scale.x=.44;half.parent=duo
 for original in list(roller.children):
  ob=original.copy();ob.data=original.data.copy();s.collection.objects.link(ob);ob.parent=half
inlet=empty('INLET');inlet.parent=ROOT
for x in [-.024,.024]:o=box('suction duct side wall',(x,-.006,.054),(.003,.077,.045),white,.003);o.parent=inlet
ob=box('suction duct dark roof',(0,-.006,.077),(.051,.077,.003),black,.001);ob.parent=inlet
# Transparent scientific cutaway window; no claim that an actual product uses a clear duct.
glass=mat('cutaway translucent wall',(.35,.5,.55),.2,0,0);glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.75;glass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.18
ob=box('transparent explanatory duct window',(0,-.041,.054),(.046,.001,.043),glass,.001);ob.parent=inlet
central=lathe('central short roller intake throat',[(0,.011),(.028,.011)],0,0,0,black);central.rotation_euler.y=-pi/2;central.location=(0,-.065,.035);central.parent=inlet
fur=curves('SHORT_FUR',[[(0,0,0)]*8 for _ in range(36)],.00005,hairmat);fur.parent=ROOT
partsA=curves('CUT_HALF_A',[[(0,0,0)]*72 for _ in range(80)],.000035,hairmat);partsA.parent=ROOT
partsB=curves('CUT_HALF_B',[[(0,0,0)]*72 for _ in range(80)],.000035,hairmat);partsB.parent=ROOT
comb=empty('CUTTER_COMB');comb.parent=ROOT
ob=box('hardened cutting comb back',(0,-.090,.023),(.242,.004,.004),black,.001);ob.parent=comb
for j in range(30):
 x=-.116+j*.008
 v=[(x-.002,-.088,.021),(x+.002,-.088,.021),(x+.001,-.084,.027),(x-.001,-.084,.027),(x-.002,-.087,.021),(x+.002,-.087,.021),(x+.001,-.083,.027),(x-.001,-.083,.027)]
 ob=mesh('individual sharpened cutting tooth',v,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],steel);ob.parent=comb
motor=empty('MOTOR');motor.location=(.123,.003,.045);motor.parent=ROOT
rot=empty('MOTOR_ROTOR');rot.parent=motor
ob=lathe('brushed motor steel rotor',[(-.018,0),(-.018,.009),(-.016,.012),(.016,.012),(.018,.009),(.018,0)],0,0,0,steel);ob.parent=rot
copper=mat('varnished copper windings',(.27,.085,.027),.24,.85,0)
for k in range(12):
 a=k*2*pi/12
 for j in range(5):o=torus('individual motor winding',.0025,.00022,(-.009+j*.004,.010*cos(a),.010*sin(a)),copper);o.parent=rot
belt=curves('motor transmission belt',[[[.123,-.005,.055],[.123,-.075,.031],[.123,-.071,.016],[.123,.012,.035],[.123,-.005,.055]]],.0008,black);belt.parent=motor;belt.location=-motor.location
# Familiar spool comparison is a separate event, not another copy of the brush-winding clip.
spool=empty('SPOOL');spool.location=(0,-.13,.035);spool.parent=ROOT
ob=lathe('thread bobbin with radiused flanges',[(-.024,0),(-.024,.023),(-.022,.024),(-.020,.022),(-.019,.012),(.019,.012),(.020,.022),(.022,.024),(.024,.023),(.024,0)],0,0,0,white);ob.parent=spool
thread=curves('SPOOL_THREAD',[[(0,0,0)]*100 for _ in range(12)],.00006,hairmat);thread.parent=ROOT
# Living-room context is physical geometry, softly out of focus in macro shots.
room=empty('ROOM')
fabric=mat('warm linen sofa fabric',(.34,.31,.26),.85,0,0)
for x in [-.72,.72]:
 ob=box('sofa timber leg',(x,1.25,.20),(.06,.06,.4),wood,.008);ob.parent=room
for x in [-.42,.42]:
 ob=box('rounded upholstered seat cushion',(x,1.25,.47),(.82,.70,.18),fabric,.08);ob.parent=room
ob=box('soft sofa back',(0,1.60,.73),(1.75,.18,.60),fabric,.09);ob.parent=room
wallmat=mat('warm painted room wall',(.63,.62,.58),.9,0,0);ob=box('living room back wall',(0,2.0,1.3),(5,.06,2.6),wallmat,.001);ob.parent=room
ob=box('white timber baseboard',(0,1.96,.045),(5,.025,.09),white,.004);ob.parent=room
bpy.ops.object.light_add(type='AREA',location=(-1,-1,2.5));window=bpy.context.object;window.name='broad living room window';window.data.energy=350;window.data.shape='DISK';window.data.size=1.8;window.rotation_euler=(Vector((0,0,0))-window.location).to_track_quat('-Z','Y').to_euler()
# Named base transforms permit deterministic per-frame resets.
for o in s.objects:
 o['base_location']=list(o.location);o['base_rotation']=list(o.rotation_euler);o['base_scale']=list(o.scale)
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.pack()
  except Exception:pass
bpy.ops.wm.save_as_mainfile(filepath=str(P/'hair-full-assets.blend'),compress=True)
print('FULL_ASSETS_READY',len(s.objects),flush=True)
