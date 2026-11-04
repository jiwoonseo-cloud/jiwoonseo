import bpy,math,os,sys,json,time
from mathutils import Vector
from math import sin,cos,pi
P='/workspace/work/hair-v2';os.makedirs(P+'/renders',exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.render.engine=os.environ.get('HAIR_RENDER_ENGINE','CYCLES');sc.cycles.samples=8;sc.render.use_persistent_data=True;sc.cycles.use_denoising=False
sc.render.resolution_x=720;sc.render.resolution_y=1280;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.world.color=(.12,.12,.12)
sc.view_settings.view_transform='AgX'
def mat(n,c,metal=0,rough=.35):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
white=mat('matte ivory polymer',(.68,.72,.73),0,.3);black=mat('black rubber',(.012,.018,.02),0,.43);teal=mat('deep teal molded rubber',(.012,.18,.17),0,.32);steel=mat('machined steel',(.45,.52,.55),.85,.22);copper=mat('copper brown hair',(.32,.105,.035),.15,.28);furmat=mat('short beige fur',(.6,.43,.23),0,.4);floor=mat('charcoal studio',(.025,.032,.039),0,.5)
def assign(o,m):o.data.materials.append(m);return o
def smooth(o):
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o
def cyl(n,r,d,loc,m,axis='Z',parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=d,location=loc);o=bpy.context.object;o.name=n
 if axis=='X':o.rotation_euler[1]=pi/2
 if axis=='Y':o.rotation_euler[0]=pi/2
 assign(smooth(o),m)
 bevel=o.modifiers.new('soft manufactured edges','BEVEL');bevel.width=.025;bevel.segments=2
 if parent:o.parent=parent
 return o
def box(n,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(o,m);be=o.modifiers.new('rounded','BEVEL');be.width=.08;be.segments=3;return o
def curve(n,pts,r,m,parent=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=2;s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 ob=bpy.data.objects.new(n,cu);sc.collection.objects.link(ob);assign(ob,m)
 if parent:ob.parent=parent
 return ob
def empty(n,loc=(0,0,0)):
 ob=bpy.data.objects.new(n,None);sc.collection.objects.link(ob);ob.location=loc;return ob
body=cyl('fixed white circular housing',3,.45,(0,0,.05),white)
cut=box('cavity cutter',(0,-1.3,.4),(5.0,1.55,1.1),black);mod=body.modifiers.new('open roller service cavity','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE';bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
base=box('black open roller cavity',(0,-1.25,-.08),(5.0,1.55,.25),black)
for x in [-2.55,2.55]:
 cyl('drive tire',.55,.4,(x,.1,.35),black,'X')
 for k in range(16):
  a=2*pi*k/16;box('tire tread',(x,.1+.52*sin(a),.35+.52*cos(a)),(.43,.08,.075),black)
for x,y in [(-1.8,1.8),(1.8,1.8),(-2.6,-.75),(2.6,-.75),(0,2.5)]:cyl('flush screw',.07,.025,(x,y,.3),steel)
side=empty('single grey side brush',(-1.7,1.5,.38));cyl('sidebrush hub',.22,.12,(-1.7,1.5,.38),black)
for k in range(3):
 a=2*pi*k/3
 for j in range(9):
  d=(j-4)*.018;curve('sidebrush filament',[(-1.7+.15*cos(a),1.5+.15*sin(a),.42),(-1.7+.95*cos(a)+d,1.5+.95*sin(a)+d,.42)],.008,black)
roller=empty('main roller assembly',(0,-1.25,.48))
cyl('continuous teal roller',.38,4.3,(0,0,0),teal,'X',roller)
for k in range(5):
 pts=[]
 for j in range(100):
  x=-2.15+4.3*j/99;a=k*2*pi/5+x*1.2;pts.append((x,.4*cos(a),.4*sin(a)))
 curve('helical rubber fin',pts,.06,teal,roller)
 for j in range(34):
  x=-2.1+4.2*j/33;a=k*2*pi/5+x*1.2
  for s in [-.018,.018]:curve('individual bristle',[(x+s,.41*cos(a),.41*sin(a)),(x+s,.55*cos(a),.55*sin(a))],.009,black,roller)
axle=cyl('steel axle',.12,4.95,(0,-1.25,.48),steel,'X')
caps=[]
for x in [-2.42,2.42]:
 caps.append(cyl('removable black endcap',.33,.18,(x,-1.25,.48),black,'X'))
 cyl('bearing outer race',.23,.2,(x*.97,-1.25,.48),steel,'X')
 # concentric bearing lip
 cyl('bearing inner race',.15,.22,(x*.97,-1.25,.48),black,'X')
# dust inlet behind roller, visible in top-down cutaway
inlet=box('central suction throat',(0,-.5,.12),(1.0,.5,.45),black)
box('floor',(0,0,-.55),(200,200,.1),floor)
def area(n,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,-1,.3))-o.location).to_track_quat('-Z','Y').to_euler()
area('key softbox',(-3,-4,7),650,5);area('cool fill',(5,1,5),500,4);area('rim',(0,5,6),750,3)
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=8;cam.data.lens=60
def camera(loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
dynamic=[]
def clear():
 for o in dynamic:bpy.data.objects.remove(o,do_unlink=True)
 dynamic.clear()
def hair(n,pts,r=.005,m=copper):
 o=curve(n,pts,r,m);dynamic.append(o);return o
def wrap(t,center=0,turns=3,rad=.565):
 # free tail becomes a helical wrap around the bristles, not a screen-space orbit.
 pts=[];theta0=-pi/2
 for j in range(140):
  u=j/139;theta=theta0+turns*2*pi*u;pts.append((center+.13*(u-.5),-1.25+rad*cos(theta),.48+rad*sin(theta)))
 return pts
def state(mode,t):
 clear();roller.rotation_euler[0]=t*2*pi
 caps[0].location.x=-2.42;caps[1].location.x=2.42
 if mode=='overview':
  camera((4,-7,10),(0,-.3,.1),7.6-.3*t)
  for k in range(10):hair('compressed hair ring',wrap(t,1.8+k*.017,3,.56+k*.001),.004)
 elif mode=='wrap':
  camera((2,-6,5),(0,-1.25,.48),4.7)
  turns=.15+3.3*t
  for k in range(4):
   pts=wrap(t,-.55+k*.018,turns)
   tail=pts[0];pts=[(-1.5,-2.6,.05),tail]+pts;hair('hair caught and wound',pts,.005)
 elif mode=='slide':
  center=-.9+2.85*t;camera((3.5,-5,4),(center*.35,-1.25,.48),4.5)
  for k in range(12):hair('hair slides along axle',wrap(t,center+k*.014,3,.56+k*.002),.005)
 elif mode=='separate':
  camera((3,-6,4),(0,-1.1,.6),5.0)
  glass=mat('cutaway glass duct',(.45,.62,.66),0,.12);glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.88
  verts=[];faces=[]
  for z in [.58,1.85]:
   for j in range(48):verts.append((.38*cos(j*2*pi/48),-.65+.38*sin(j*2*pi/48),z))
  for j in range(48):faces.append((j,(j+1)%48,(j+1)%48+48,j+48))
  mesh=bpy.data.meshes.new('hollow suction duct mesh');mesh.from_pydata(verts,[],faces);ob=bpy.data.objects.new('transparent open suction duct',mesh);sc.collection.objects.link(ob);assign(smooth(ob),glass);solid=ob.modifiers.new('thin wall','SOLIDIFY');solid.thickness=.018;dynamic.append(ob)
  for k in range(6):hair('long hair remains wrapped',wrap(t,.8+k*.015,2.8,.565),.005)
  for k in range(18):
   u=(t+k*.047)%1;x=(-1.6+(k%7)*.48)*(1-u)**1.6;y=-2.1+u*1.45;z=.05+1.55*u*u
   hair('short fur follows suction',[(x,y,z),(x+.04*(1-u),y+.04,z+.11*(1-u))],.006,furmat)
 elif mode=='caps':
  camera((4,-6,5),(1.3,-1.25,.4),4.4);caps[1].location.x=2.42+.95*t;caps[0].location.x=-2.42-.5*t
  for k in range(20):hair('compressed end hair',wrap(t,2.12+k*.009,3,.19+k*.002),.005)
 elif mode=='clean':
  camera((4,-7,8),(0,-.6,.3),7.1);roller.location.z=.48+1.1*t;caps[1].location.x=2.42+.7*t;caps[0].location.x=-2.42-.7*t
 elif mode=='bearing':
  camera((4,-5,3),(2.12,-1.25,.48),2.7)
  for k in range(22):hair('bearing obstruction',wrap(t,2.13+k*.006,3,.19+k*.002),.005)
 elif mode=='duo':
  camera((2,-6,6),(0,-1.25,.5),5.4)
  # original continuous roller hidden; paired two short independent rollers are teaching inserts.
  for sign in [-1,1]:
   par=empty('short roller assembly',(sign*1.15,-1.25,.48));dynamic.append(par)
   ob=cyl('short teal roller',.38,1.95,(0,0,0),teal,'X',par);dynamic.append(ob)
   for k in range(4):
    pts=[]
    for j in range(40):
     x=-.96+1.92*j/39;a=k*pi/2+sign*x*2+sign*t*2*pi;pts.append((x,.44*cos(a),.44*sin(a)))
    o=curve('opposed helical fin',pts,.065,teal,par);dynamic.append(o)
   for k in range(5):
    x=sign*(1.8*(1-t)+.15)+k*.015
    pts=[(x,-1.25+.49*cos(a),.48+.49*sin(a)) for a in [j*pi*2/70 for j in range(71)]]
    hair('hair driven inward',pts,.007)
  for k in range(10):
   u=max(0,(t-.5)*2);hair('central suction hair',[(.03*k-.15,-1.2,.6+u*.8),(.03*k-.12,-.65,.7+u*1.2)],.007)
 else:camera((3,-6,6),(0,-1.25,.48),5)
 for o in [roller]+list(roller.children):o.hide_render=(mode=='duo')
 if mode!='clean':roller.location.z=.48
 sc.render.filepath=f'{P}/renders/{mode}_{int(round(t*29)):03}.png'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'wrap';count=int(args[1]) if len(args)>1 else 1
for k in range(count):
 t=k/max(1,count-1);state(mode,t);sc.render.filepath=f'{P}/renders/{mode}_{k:03}.png';bpy.ops.render.render(write_still=True)
