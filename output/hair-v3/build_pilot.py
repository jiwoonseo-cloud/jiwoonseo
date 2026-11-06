"""Original procedural CGI prototype. Blender 4.3; no stock animation.
Run: blender -b -t 5 --python build_pilot.py -- --shot flip --render-stills
Pilot frames are directly evaluated at 24fps, never interpolated or retimed.
"""
import bpy, math, random, sys, argparse
from mathutils import Vector
from pathlib import Path
random.seed(19)
ap=argparse.ArgumentParser();ap.add_argument('--shot',choices=['flip','catch','suction'],default='flip');ap.add_argument('--render-stills',action='store_true');ap.add_argument('--animate',action='store_true');ap.add_argument('--size',type=int,default=540);ap.add_argument('--samples',type=int,default=24);ap.add_argument('--engine',default='CYCLES');ap.add_argument('--motion-preview',action='store_true')
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
BASE=Path(__file__).resolve().parent;WORK=BASE.parent.parent/'work/hair-v3/render';WORK.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.render.engine=a.engine;sc.cycles.samples=a.samples;sc.cycles.use_denoising=False
sc.cycles.max_bounces=3;sc.cycles.diffuse_bounces=1;sc.cycles.glossy_bounces=1;sc.cycles.transmission_bounces=1
sc.render.resolution_x=a.size;sc.render.resolution_y=round(a.size*16/9);sc.render.resolution_percentage=100
sc.render.fps=24;sc.frame_start=1;sc.frame_end=72
sc.world.color=(.18,.18,.18);sc.view_settings.view_transform='AgX'
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
def mat(name,col,rough=.4,metal=0,noise=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  tx=n.new('ShaderNodeTexNoise');tx.inputs['Scale'].default_value=170;tx.inputs['Detail'].default_value=3
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=noise;bump.inputs['Distance'].default_value=.008;m.node_tree.links.new(tx.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
ivory=mat('Satin warm ivory / micro moulded ABS',(.68,.69,.66),.26,noise=.12)
dark=mat('Graphite textured underbody',(.035,.044,.048),.38,noise=.2)
rubber=mat('Matte EPDM rubber',(.015,.019,.020),.69,noise=.35)
teal=mat('Individual teal nylon bristles',(.055,.21,.20),.38)
steel=mat('Machined steel bearing race',(.39,.43,.45),.24,.86,noise=.1)
bronze=mat('Anodized champagne trim',(.32,.23,.12),.29,.72)
hairmat=mat('Fine brown hair',(.26,.115,.042),.27)
hairlight=mat('Short tawny pet hair',(.47,.30,.14),.4)
black=mat('Optical glass',(.006,.011,.015),.12,.3)
fabric=mat('Soft blue grey maintenance gloves',(.13,.18,.21),.77,noise=.28)
def finish(o,m,parent=None):
 o.data.materials.append(m)
 if parent:o.parent=parent
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o
def bevel(o,r=.03):
 mod=o.modifiers.new('Manufactured edge radii','BEVEL');mod.width=r;mod.segments=3
 o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def cube(name,loc,scale,m,parent=None,r=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,m,parent);return bevel(o,r)
def cyl(name,loc,r,depth,m,parent=None,axis='Z',verts=96):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name
 if axis=='X':o.rotation_euler[1]=math.pi/2
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 finish(o,m,parent);return bevel(o,min(r*.08,.015))
def uv(name,loc,scale,m,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;return finish(o,m,parent)
def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);sc.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def curves(name,paths,r,m,parent=None):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=r;cu.bevel_resolution=2
 for pts in paths:
  sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
  for v,p in zip(sp.points,pts):v.co=(*p,1)
 ob=bpy.data.objects.new(name,cu);sc.collection.objects.link(ob);finish(ob,m,parent);return ob
def screw(loc,parent=None):
 cyl('Recessed Torx fastener',loc,.047,.014,steel,parent)
 cube('Fastener slot',tuple(Vector(loc)+Vector((0,0,.009))),(.055,.009,.003),dark,parent,r=.002)
def brush(loc=(0,0,0),length=2.1,parent=None,section=False):
 root=empty('Brush assembly',loc,parent);rot=empty('Rotating nylon and helical elastomer',parent=root)
 cyl('Rubber brush core',(-length/4 if section else 0,0,0),.154,length/2 if section else length,rubber,rot,'X')
 for i in range(6):
  pts=[]
  for j in range(100):
   x=-length/2+length*j/99;t=x*3.5+i*math.tau/6
   if not section or x<=0:pts.append((x,.183*math.cos(t),.183*math.sin(t)))
  curves('Continuous helical rubber fin',[pts],.022,rubber,rot)
 br=[]
 for i in range(1400):
  x=random.uniform(-length/2,0 if section else length/2);ph=x*3.5+random.choice([1,3,5])*math.tau/6+random.uniform(-.15,.15);rr=random.uniform(.218,.238)
  br.append([(x,.16*math.cos(ph),.16*math.sin(ph)),(x+.012,rr*math.cos(ph+.03),rr*math.sin(ph+.03))])
 curves('1400 separate nylon filaments',br,.0015,teal,rot)
 for side in ([-1] if section else [-1,1]):
  x=side*(length/2+.055)
  cyl('Removable end cap',(x,0,0),.19,.09,dark,root,'X')
  cyl('Bearing outer race',(x+side*.057,0,0),.105,.025,steel,root,'X')
  cyl('Bearing seal',(x+side*.072,0,0),.069,.026,rubber,root,'X')
  cyl('Axle stub',(x+side*.09,0,0),.035,.05,steel,root,'X')
 return root,rot
def wood():
 m=mat('Warm oak with directional grain',(.33,.19,.09),.43)
 nd=m.node_tree.nodes;lk=m.node_tree.links;p=nd.get('Principled BSDF');tc=nd.new('ShaderNodeTexCoord');mp=nd.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(2,90,12);lk.new(tc.outputs['Generated'],mp.inputs[0]);tx=nd.new('ShaderNodeTexNoise');tx.inputs['Scale'].default_value=4;tx.inputs['Detail'].default_value=3;lk.new(mp.outputs[0],tx.inputs['Vector']);r=nd.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.10,.047,.017,1);r.color_ramp.elements[1].color=(.42,.25,.12,1);lk.new(tx.outputs['Fac'],r.inputs[0]);lk.new(r.outputs[0],p.inputs['Base Color']);return m
oak=wood()
for i in range(-7,8):cube('Individual oak floor plank',(i*1.05,0,-.10),(1.044,18,.18),oak,r=.006)
def light(name,loc,power,col,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=col;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler()
light('Large window daylight',(-3,-4,6),650,(.82,.90,1),5)
light('Warm practical rim',(3,2,4),900,(1,.73,.45),3)
light('Soft white fill',(-1,4,3),350,(.8,1,1),3)
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.lens=56
def camera(loc,target,lens=56):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 cam.data.dof.use_dof=True;f=empty('Focus target',target);cam.data.dof.focus_object=f;cam.data.dof.aperture_fstop=5.6
if a.shot=='flip':
 sage=mat('Woven sage upholstery',(.14,.21,.17),.85,noise=.3)
 cube('Sofa back',(0,4,1.7),(7,.7,2.0),sage,r=.2);cube('Sofa seat',(0,3.45,.65),(7,1.5,.5),sage,r=.17)
 cube('Oak maintenance tabletop',(0,0,.07),(5.1,3.8,.16),oak,r=.05)
 robot=empty('Fixed hero robot product',(0,0,.74))
 cyl('Lower bumper',(0,0,-.07),1.59,.37,dark,robot)
 cyl('Ivory upper chassis',(0,0,.12),1.60,.26,ivory,robot)
 cyl('Champagne bumper seam',(0,0,.035),1.606,.018,bronze,robot)
 cyl('Top access cover',(0,0,.27),1.44,.035,ivory,robot)
 cyl('LiDAR black surround',(0,.42,.34),.38,.16,dark,robot)
 cyl('LiDAR satin lid',(0,.42,.435),.36,.03,ivory,robot)
 cube('Front glass sensor panel',(0,-1.49,.03),(.83,.16,.12),black,robot,r=.05)
 for x in [-.92,.92]:
  cyl('Treaded drive wheel',(x,.38,-.24),.31,.24,rubber,robot,'X')
  for j in range(26):
   t=j*math.tau/26;o=cube('Individual tyre tread',(x,.38+.306*math.cos(t),-.24+.306*math.sin(t)),(.25,.038,.033),rubber,robot,r=.008);o.rotation_euler[0]=t
 cube('Main brush recessed cavity',(0,-.49,-.275),(2.42,.66,.065),black,robot,r=.10)
 root,rot=brush((0,-.49,-.285),parent=robot)
 for x in [-1.24,1.24]:cube('Brush retaining latch',(x,-.49,-.31),(.12,.42,.05),bronze,robot,r=.025)
 # Underside access plates, sensor windows, motor vents, side brush and caster.
 cube('Underside battery service panel',(0,.40,-.272),(1.12,.64,.025),dark,robot,r=.045)
 for x,y in [(-.50,.65),(.50,.65),(-.50,.15),(.50,.15)]:
  cyl('Underside screw head',(x,y,-.292),.033,.018,steel,robot)
  cube('Underside screw slot',(x,y,-.303),(.04,.008,.006),black,robot,r=.001)
 for x,y in [(-1.19,-.87),(1.19,-.87),(0,1.32)]:cube('Recessed cliff sensor',(x,y,-.27),(.20,.12,.022),black,robot,r=.03)
 cyl('Caster housing',(0,1.02,-.27),.19,.06,dark,robot)
 cyl('Rubber caster wheel',(0,1.02,-.36),.12,.12,rubber,robot,'X')
 cyl('Side brush mount',(-1.1,-.68,-.30),.12,.07,dark,robot)
 for j in range(3):
  ph=j*math.tau/3;paths=[]
  for k in range(25):
   ph2=ph+(k-12)*.012
   paths.append([(-1.1+.08*math.cos(ph2),-.68+.08*math.sin(ph2),-.35),(-1.1+.53*math.cos(ph2),-.68+.53*math.sin(ph2),-.36)])
  curves('Fine side brush bristles',paths,.0018,teal,robot)
 for j in range(12):cube('Underbody ventilation groove',(-.31+j*.055,.88,-.281),(.017,.22,.013),black,robot,r=.006)
 cube('Soft top power button',(-.30,-.38,.300),(.19,.31,.016),dark,robot,r=.06)
 cube('Soft top dock button',(.02,-.38,.300),(.19,.31,.016),dark,robot,r=.06)
 # Existing hair remains stationary relative to brush during discovery.
 paths=[]
 for i in range(32):
  pts=[]
  for j in range(160):
   t=j/159*math.tau*3+i*.19;x=.78+random.uniform(-.06,.06)+.08*j/159
   pts.append((x,-.49+.193*math.cos(t),-.285+.193*math.sin(t)))
  paths.append(pts)
 curves('Fine tangled hair at right end',paths,.0015,hairmat,robot)
 for side in [-1,1]:
  hand=empty('Supporting gloved hand',parent=robot)
  uv('Glove palm',(side*1.64,0,-.04),(.18,.39,.13),fabric,hand)
  for k in range(4):
   yy=-.27+k*.16
   curves('Gloved supporting finger',[[(side*1.72,yy,-.05),(side*1.64,yy,-.23),(side*1.43,yy,-.26)]],.075,fabric,hand)
  curves('Glove thumb',[[(side*1.68,-.30,.03),(side*1.52,-.39,.15),(side*1.37,-.31,.21)]],.09,fabric,hand)
  curves('Glove sleeve',[[(side*1.8,.1,-.02),(side*2.15,.18,.04),(side*2.6,.25,.06)]],.20,fabric,hand)
 camera((4,-8.5,6.2),(0,0,1.05),50)
 def animate(f):
  t=(f-1)/71;p=max(0,min(1,(t-.15)/.67));p=p*p*(3-2*p)
  robot.rotation_euler[1]=math.pi*p;robot.location.z=.74+1.5*math.sin(math.pi*p)-.09*p
elif a.shot in ['catch','suction']:
 root,rot=brush((0,0,.255),length=1.75,section=a.shot=='suction')
 if a.shot=='suction':
  rug=mat('Flat charcoal low pile contact surface',(.027,.035,.043),.87,noise=.12)
  cube('Flat dark rug under contact point',(0,-.45,-.010),(3.5,3.8,.018),rug,r=.007)
 # Real opening, opaque housing lip; objects terminate inside it.
 cube('Dark suction chamber behind brush',(0,.33,.39),(2.05,.22,.56),dark,r=.045)
 cube('Black intake opening',(0,.195,.41),(1.55,.025,.34),black,r=.035)
 cube('Upper intake lip',(0,.165,.61),(1.82,.12,.07),ivory,r=.025)
 cube('Left housing cheek',(-1.02,.07,.31),(.12,.72,.61),ivory,r=.06)
 cube('Right housing cheek',(1.02,.07,.31),(.12,.72,.61),ivory,r=.06)
 if a.shot=='catch':
  camera((1.25,-2.0,1.18),(.18,-.12,.22),60)
  long=curves('One continuous fine hair',[[(0,0,0)]*180],.0014,hairmat)
  def animate(f):
   t=(f-1)/71;rot.rotation_euler[0]=t*math.tau*2.3
   progress=max(0,min(1,(t-.22)/.70))
   radius=.239;angle=progress*math.tau*1.4;total_length=2.8
   wrapped=radius*angle/total_length
   pts=[]
   for j in range(180):
    s=j/179
    if s<wrapped and wrapped>0:
     u=s/wrapped;ph=-math.pi/2+(1-u)*angle
     x=-.12+.20*(1-u)+.45*progress;y=radius*math.cos(ph);z=.255+radius*math.sin(ph)
    else:
     u=(s-wrapped)/max(.01,1-wrapped)
     # The free tail leaves at the floor tangent; no chord through the core.
     remaining=total_length-radius*angle
     x=-.12+.45*progress+.035*math.sin(u*8);y=-remaining*u;z=.016
    pts.append((x,y,max(.012,z)))
   for p,q in zip(long.data.splines[0].points,pts):p.co=(*q,1)
 else:
  camera((.95,-1.65,1.00),(.22,-.02,.25),61)
  hairs=[]
  for i in range(17):
   x=random.uniform(.17,.58);y=random.uniform(-.65,-.30)
   o=curves('Short pet hair floor to intake',[[(x+j*.006,y+.025*math.sin(j*.3),.014) for j in range(15)]],.0025,hairlight)
   hairs.append((o,x,y,i*.022))
  wrap=[]
  for k in range(6):wrap.append([(-.55+.018*k+.03*j/100,.244*math.cos(j/100*math.tau*2+k),.255+.244*math.sin(j/100*math.tau*2+k)) for j in range(101)])
  curves('Long hair remains on roller',wrap,.0015,hairmat,root)
  def animate(f):
   t=(f-1)/71;rot.rotation_euler[0]=t*math.tau*3.5
   for o,x,y,delay in hairs:
    u=max(0,min(1,(t-.12-delay)/.45))
    if u<.25:
     v=u/.25;yy=y*(1-v);zz=.014
    elif u<.90:
     ph=-math.pi/2+(u-.25)/.65*(math.pi*.73)
     yy=.252*math.cos(ph);zz=.255+.252*math.sin(ph)
    else:
     v=(u-.90)/.10;ph=-math.pi/2+math.pi*.73
     yy=.252*math.cos(ph)*(1-v)+.32*v;zz=(.255+.252*math.sin(ph))*(1-v)+.43*v
    o.location=(0,yy-y,zz-.014);o.hide_render=u>=.99
def update(scene):animate(scene.frame_current)
bpy.app.handlers.frame_change_pre.append(update)
animate(1)
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/f'pilot-{a.shot}.blend'))
if a.render_stills:
 for f in [1,24,48,72]:
  sc.frame_set(f);sc.render.filepath=str(WORK/f'{a.shot}-{f:03d}.png');bpy.ops.render.render(write_still=True)
if a.animate:
 sc.render.filepath=str(WORK/f'{a.shot}/');bpy.ops.render.render(animation=True)
if a.motion_preview:
 # Reduced resolution *test*, directly rendered at every final-time frame.
 sc.render.filepath=str(WORK/f'preview-{a.shot}/');bpy.ops.render.render(animation=True)
