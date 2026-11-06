"""Blender 4.3: original geometry, keyframed mechanisms, word-aligned cameras.
No raster backplates, image slides, reused animation clips or frame interpolation.
"""
import bpy,math,random,json,csv,sys,argparse
from pathlib import Path
from mathutils import Vector
random.seed(20261104)
BASE=Path(__file__).resolve().parents[1];FPS=24
OLD=BASE/'source'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=1;S.eevee.use_raytracing=False
S.eevee.use_fast_gi=False;S.eevee.use_gtao=False;S.eevee.shadow_resolution_scale=.25;S.eevee.shadow_ray_count=1;S.eevee.shadow_step_count=2;S.eevee.bokeh_max_size=12
S.render.resolution_x=1080;S.render.resolution_y=1920;S.render.resolution_percentage=100;S.render.fps=FPS
S.render.image_settings.file_format='PNG';S.render.image_settings.compression=0;S.render.image_settings.color_mode='RGB';S.view_settings.view_transform='AgX';S.render.film_transparent=False
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.28,.34,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.45
COLS={};ACTIVE=None
def collection(name):
 global ACTIVE
 ACTIVE=bpy.data.collections.new(name);S.collection.children.link(ACTIVE);COLS[name]=ACTIVE;return ACTIVE
def add(o,name,m=None,parent=None):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 ACTIVE.objects.link(o)
 if parent:o.parent=parent
 if m:o.data.materials.append(m)
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def empty(name,parent=None):
 o=bpy.data.objects.new(name,None);ACTIVE.objects.link(o);o.parent=parent;return o
def material(name,col,rough=.4,metal=0,bump=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 p.inputs['Emission Color'].default_value=(*[c*.055 for c in col],1);p.inputs['Emission Strength'].default_value=.35
 if bump and False:  # microfinish is carried by roughness; avoid live noise aliasing on fine strands
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=350;t.inputs['Detail'].default_value=2
  b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=bump;b.inputs['Distance'].default_value=.0006;m.node_tree.links.new(t.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs[0],p.inputs['Normal'])
 return m
white=material('Warm white moulded ABS',(.79,.80,.77),.26,0,.10)
graphite=material('Graphite microtextured chassis',(.029,.038,.044),.39,0,.12)
rubber=material('EPDM soft rubber',(.012,.018,.021),.62,0,.13)
nylon=material('Individual blue green nylon',(.045,.18,.18),.35)
metal=material('Machined bearing steel',(.56,.61,.65),.22,.88,.03)
champagne=material('Fine champagne trim',(.38,.28,.14),.28,.75)
hairmat=material('Fine dark gold human hair',(.24,.115,.041),.31)
heroMat=material('One highlighted copper brown strand',(.20,.085,.025),.3)
furmat=material('Fine light pet hairs',(.61,.46,.26),.48)
gloveMat=material('Soft graphite blue maintenance glove',(.11,.17,.20),.68,0,.15)
glass=material('Smoked optical sensor glass',(.006,.012,.018),.12,.2)
felt=material('Dark slate microfibre work surface',(.026,.038,.049),.86,0,.2)
def edge(o,w=.015):
 b=o.modifiers.new('Manufactured soft edges','BEVEL');b.width=w;b.segments=3
 o.modifiers.new('Weighted split normals','WEIGHTED_NORMAL');return o
def box(name,loc,size,m,parent=None,w=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);add(o,name,m,parent);return edge(o,w)
def sphere(name,loc,size,m,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc);o=bpy.context.object;o.scale=size;return add(o,name,m,parent)
def lathe(name,profile,m,parent=None,axis='Z',segments=80):
 vs=[];fs=[]
 for r,z in profile:
  for j in range(segments):
   t=math.tau*j/segments;v=(r*math.cos(t),r*math.sin(t),z);vs.append((z,v[0],v[1]) if axis=='X' else v)
 for i in range(len(profile)-1):
  for j in range(segments):a=i*segments+j;b=i*segments+(j+1)%segments;fs.append((a,b,b+segments,a+segments))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);ACTIVE.objects.link(o);o.parent=parent;o.data.materials.append(m)
 for p in me.polygons:p.use_smooth=True
 return o
def tube(name,paths,r,m,parent=None):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1;cu.resolution_u=2
 for path in paths:
  s=cu.splines.new('POLY');s.points.add(len(path)-1)
  for p,co in zip(s.points,path):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);ACTIVE.objects.link(o);o.parent=parent;cu.materials.append(m);return o
def ring(name,x,outer,inner,width,m,parent):
 o=lathe(name,[(inner,-width/2),(outer,-width/2),(outer,width/2),(inner,width/2),(inner,-width/2)],m,parent,'X');o.location.x=x;edge(o,.007);return o
def key(o,path,values):
 for sec,v in values:
  setattr(o,path,v);o.keyframe_insert(path,frame=round(sec*FPS)+1)
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='LINEAR'
def scalar_key(socket,values):
 for sec,v in values:socket.default_value=v;socket.keyframe_insert('default_value',frame=round(sec*FPS)+1)
def frame(sec):return round(sec*FPS)+1
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def light(name,loc,power,size,color):
 bpy.ops.object.light_add(type='AREA',location=loc);o=add(bpy.context.object,name);o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.data.use_shadow_jitter=False;o.data.shadow_maximum_resolution=.025;o.data.use_shadow='key' in name;o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler();return o
def studio():
 light('Large softbox key',(-3,-4,5),1200,5,(.93,.96,1))
 for ob in ACTIVE.objects:
  if ob.type=='LIGHT':ob.data.use_shadow=False
def contact_shadow(name,loc,size):
 # Analytic soft contact shadows avoid stochastic shadow grain on fine hairs.
 m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';n=m.node_tree.nodes;lk=m.node_tree.links;n.clear()
 out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');trans=n.new('ShaderNodeBsdfTransparent');dark=n.new('ShaderNodeEmission');dark.inputs[0].default_value=(0,0,0,1)
 tex=n.new('ShaderNodeTexCoord');dist=n.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,0)
 remap=n.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=.05;remap.inputs['From Max'].default_value=.5;remap.inputs['To Min'].default_value=.36;remap.inputs['To Max'].default_value=0;remap.clamp=True
 lk.new(tex.outputs['Generated'],dist.inputs[0]);lk.new(dist.outputs['Value'],remap.inputs['Value']);lk.new(remap.outputs[0],mix.inputs[0]);lk.new(trans.outputs[0],mix.inputs[1]);lk.new(dark.outputs[0],mix.inputs[2]);lk.new(mix.outputs[0],out.inputs[0])
 bpy.ops.mesh.primitive_plane_add(size=1,location=loc);o=add(bpy.context.object,name,m);o.scale=(*size,1);return o
def screw(x,y,z,parent):
 o=lathe('Recessed steel screw',[(0,-.01),(.04,-.01),(.04,.01),(0,.01)],metal,parent);o.location=(x,y,z)
 box('Fastener recess',(x,y,z+.012),(.047,.008,.004),graphite,parent,w=.001)
def glove(name,parent=None):
 g=empty(name,parent);sphere('Sculpted glove palm',(0,0,0),(.23,.31,.105),gloveMat,g)
 for i in range(4):
  x=(i-1.5)*.112;L=[.33,.43,.46,.37][i];path=[(x,.16,.01),(x,.30,.015),(x,.30+L*.4,-.025),(x,.30+L*.72,-.12),(x,.30+L*.83,-.20)]
  # Organic articulated finger, varying cross section rather than a bare capsule.
  vs=[];fs=[]
  for k,pt in enumerate(path):
   rad=[.066,.065,.060,.050,.024][k]
   for j in range(10):t=math.tau*j/10;vs.append((pt[0]+rad*math.cos(t),pt[1],pt[2]+rad*math.sin(t)))
  for k in range(4):
   for j in range(10):a=k*10+j;b=k*10+(j+1)%10;fs.append((a,b,b+10,a+10))
  fs.append(tuple(range(40,50)));me=bpy.data.meshes.new('Glove finger anatomy');me.from_pydata(vs,[],fs);o=bpy.data.objects.new('Articulated glove finger',me);ACTIVE.objects.link(o);o.parent=g;me.materials.append(gloveMat)
  sub=o.modifiers.new('Soft glove skin','SUBSURF');sub.levels=1;sub.render_levels=1
  for p in me.polygons:p.use_smooth=True
 tube('Opposable curved glove thumb',[[(-.19,.0,0),(-.31,.15,-.01),(-.27,.29,-.10),(-.12,.32,-.17)]],.075,gloveMat,g)
 sleeve=lathe('Stitched glove cuff',[(.12,-.35),(.15,-.28),(.14,-.18)],gloveMat,g);sleeve.rotation_euler.x=math.pi/2;sleeve.location.y=-.18
 for k in [-.14,.14]:tube('Fine glove seam',[[(k,-.12,.08),(k,.08,.09),(k,.22,.07)]],.002,graphite,g)
 return g
def roller(name,parent=None,length=3.0):
 root=empty(name,parent);spin=empty('Roller spinning assembly',root)
 core=lathe('Stepped rubber core',[(0,-length/2),(.19,-length/2),(.218,-length/2+.04),(.22,0),(.218,length/2-.04),(.19,length/2),(0,length/2)],rubber,spin,'X')
 shaft=lathe('Axle visible through X-ray',[(0,-length/2-.32),(.052,-length/2-.32),(.052,length/2+.32),(0,length/2+.32)],metal,spin,'X')
 for phase in range(4):
  vs=[];fs=[]
  for j in range(121):
   x=-length/2+length*j/120;t=x*2.5+phase*math.tau/4
   for r,q in [(.215,-.045),(.286,-.016),(.287,.016),(.215,.045)]:vs.append((x,r*math.cos(t+q),r*math.sin(t+q)))
  for j in range(120):
   for k in range(3):a=j*4+k;fs.append((a,a+1,a+5,a+4))
  me=bpy.data.meshes.new('Thin helical elastomer vane');me.from_pydata(vs,[],fs);o=bpy.data.objects.new('Spiral rubber vane',me);ACTIVE.objects.link(o);o.parent=spin;me.materials.append(rubber)
  for p in me.polygons:p.use_smooth=True
 br=[]
 for i in range(900):
  x=random.uniform(-length/2+.03,length/2-.03);t=x*2.5+random.choice([0,2])*math.tau/4+.22+random.uniform(-.12,.12);r=random.uniform(.310,.330)
  br.append([(x,.224*math.cos(t),.224*math.sin(t)),(x+.006,r*math.cos(t+.025),r*math.sin(t+.025))])
 tube('900 individual nylon bristles',br,.0009,nylon,spin)
 caps=[]
 for side in [-1,1]:
  cap=empty('Removable end cap',root);cap.location.x=side*(length/2+.10)
  ring('Hollow stepped moulded end cap',0,.29,.136,.12,graphite,cap)
  ring('Cap grip ridge',side*.035,.302,.27,.025,white,cap)
  for j in range(12):
   t=j*math.tau/12;ridge=box('Individual end cap grip rib',(0,.288*math.cos(t),.288*math.sin(t)),(.10,.025,.025),rubber,cap,w=.007);ridge.rotation_euler.x=t
  caps.append(cap)
  bearing=empty('Bearing assembly',root);bearing.location.x=side*(length/2+.32)
  ring('Polished outer bearing race',0,.176,.132,.050,metal,bearing);ring('Inner bearing race',0,.097,.058,.05,metal,bearing)
  for j in range(10):t=j*math.tau/10;sphere('Individual steel bearing ball',(0,.115*math.cos(t),.115*math.sin(t)),(.019,.019,.019),metal,bearing)
 return root,spin,caps,core
def product(name,with_brush=True):
 root=empty(name)
 lathe('Contoured white upper housing',[(0,.265),(1.93,.265),(2.03,.24),(2.10,.16),(2.11,-.13),(2.05,-.22),(0,-.22)],white,root)
 lathe('Shock absorbing dark bumper',[(1.99,-.20),(2.12,-.17),(2.13,-.09),(2.125,-.06),(2.08,-.04)],graphite,root)
 lathe('Champagne perimeter seam',[(2.09,-.035),(2.12,-.035),(2.12,-.02),(2.09,-.02)],champagne,root)
 lid=lathe('Raised removable top lid',[(0,.28),(1.82,.28),(1.88,.27),(1.88,.25)],white,root)
 turret=lathe('Lidar turret with optical slit',[(0,.31),(.43,.31),(.45,.34),(.45,.49),(.42,.52),(0,.52)],graphite,root);turret.location.y=.63
 cap=lathe('Satin lidar cap',[(0,.54),(.45,.54),(.46,.51),(.44,.49)],white,root);cap.location.y=.63
 box('Smoked front obstacle sensor',(0,-2.04,.035),(.83,.13,.16),glass,root,w=.06)
 for x in [-1.30,1.30]:
  wheel=lathe('Profiled rubber tyre',[(0,-.16),(.32,-.16),(.37,-.12),(.37,.12),(.32,.16),(0,.16)],rubber,root,'X');wheel.location=(x,.52,-.22)
  for j in range(24):
   t=j*math.tau/24;o=box('Wheel traction tread',(x,.52+.368*math.cos(t),-.22+.368*math.sin(t)),(.34,.042,.024),rubber,root,w=.006);o.rotation_euler.x=t
 box('Inset underside service panel',(0,.67,-.24),(1.4,.92,.025),graphite,root,w=.08)
 for x,y in [(-.60,.30),(.60,.30),(-.60,1.0),(.60,1.0)]:screw(x,y,-.26,root)
 for x in [-1.56,1.56]:box('Cliff sensor',(x,-1.01,-.24),(.20,.27,.018),glass,root,w=.03)
 box('Brush recess',(0,-.70,-.23),(3.38,.85,.06),graphite,root,w=.12)
 for x in [-1.65,1.65]:box('Release latch',(x,-.70,-.31),(.13,.35,.06),champagne,root,w=.025)
 box('Power key',(-.25,-.40,.295),(.20,.32,.03),graphite,root,w=.07);box('Dock key',(.10,-.40,.295),(.20,.32,.03),graphite,root,w=.07)
 if with_brush:
  b,sp,cp,core=roller('Installed main roller',root);b.location=(0,-.70,-.26)
 else:b=None
 return root,b
def hair_points(wind,slide,count=36,N=96,cut=0):
 paths=[];rad=.336-(.336-.095)*smooth((slide-.76)/.24);angle=wind*4.5/rad;wrapped=wind*4.5/4.8
 for k in range(count):
  pts=[];jitter=(k-(count-1)/2)*.0015
  for j in range(N):
   s=j/(N-1);r=rad+(k%5)*.0008
   if s<wrapped and wrapped>0:
    u=s/wrapped;t=-math.pi/2+(1-u)*angle+(k%7)*.009
    x=jitter+.09*(1-u);y=r*math.cos(t);z=r*math.sin(t)
   else:
    u=(s-wrapped)/max(.001,1-wrapped);x=jitter+u*math.sin(k*2.399)*.52*(1-wind*.8)+.023*math.sin(u*11+k*.7);y=-(4.8-wind*4.5)*u*(.80+.32*(.5+.5*math.sin(k*1.77)));z=-rad-(.34-rad)*min(1,u*7)
   pts.append((x,y,z))
  paths.append(pts)
 return paths
def shape_animation(o,poses):
 o.shape_key_add(name='Basis');flat0=[p for sp in o.data.splines for p in sp.points]
 for i,(sec,paths) in enumerate(poses):
  sk=o.shape_key_add(name=f'Pose_{i:03}');flat=[p for path in paths for p in path];assert len(flat)==len(sk.data)
  for v,p in zip(sk.data,flat):v.co=p
  if i:sk.value=0;sk.keyframe_insert('value',frame=frame(poses[i-1][0]))
  sk.value=1;sk.keyframe_insert('value',frame=frame(sec))
  if i+1<len(poses):sk.value=0;sk.keyframe_insert('value',frame=frame(poses[i+1][0]))
 if o.data.shape_keys.animation_data:
  for fc in o.data.shape_keys.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='LINEAR'

# Measured narration; paragraph 6 remains explicitly held by the user.
paragraphs=[1,2,3,4,5,7,8];offsets={};total=0
durations=json.loads((OLD/'voice-measurements.json').read_text())['ko-KR-HyunsuMultilingualNeural']['paragraph_seconds']
for p in paragraphs:offsets[p]=total;total+=durations[f'{p:02}']
def cue(p,text,end=False):
 ev=json.loads((BASE/'audio'/f'{p:02}.json').read_text());alltext=''.join(e['text'] for e in ev);idx=alltext.find(text.replace(' ',''));pos=0
 # Find by normalized characters, avoiding punctuation in the event stream.
 import re
 n=lambda s:re.sub('[^가-힣a-zA-Z0-9]','',s)
 alltext=''.join(n(e['text']) for e in ev);needle=n(text);idx=alltext.find(needle);assert idx>=0,(p,text)
 selected=[]
 for e in ev:
  L=len(n(e['text']))
  if pos+L>idx and pos<idx+len(needle):selected.append(e)
  pos+=L
 e=selected[-1] if end else selected[0]
 return offsets[p]+(e['offset']+(e['duration'] if end else 0))/1e7

# SET 1: full robot and articulated hands, living-room materials.
collection('ROOM');studio()
oak=material('Warm oak floor',(.28,.16,.075),.43,0,.03)
nodes=oak.node_tree.nodes;links=oak.node_tree.links;t=nodes.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=4;co=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,100,10);links.new(co.outputs['Generated'],mapping.inputs[0]);links.new(mapping.outputs[0],t.inputs['Vector']);ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.12,.06,.025,1);ramp.color_ramp.elements[1].color=(.38,.23,.11,1);links.new(t.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
for i in range(-5,6):box('Separate oak floor board',(i*1.0,0,-.09),(.994,14,.16),oak,w=.004)
sage=material('Sage woven sofa',(.16,.23,.18),.86,0,.12)
box('Sofa seat',(0,4,.65),(7,1.4,.48),sage,w=.18);box('Sofa back',(0,4.5,1.65),(7,.60,1.65),sage,w=.20)
robot,rb=product('White round hero robot');robot.location=(0,0,.63)
shadow=contact_shadow('Robot soft contact shadow',(0,0,.006),(4.8,3.3));key(shadow,'scale',[(0,(4.8,3.3,1)),(4.97,(5.6,4.1,1)),(6.35,(4.8,3.3,1)),(total,(4.8,3.3,1))])
for side in [-1,1]:
 g=glove('Supporting maintenance hand',robot);g.location=(side*2.13,0,.02);g.rotation_euler=(math.pi/2,0,side*math.pi/2)
 # Hands close around the stationary device before it is lifted.
 key(g,'location',[(0,(side*2.9,-.1,.12)),(2.8,(side*2.13,0,.02)),(total,(side*2.13,0,.02))])
key(robot,'location',[(0,(0,0,.63)),(3.9,(0,0,.63)),(4.97,(0,0,2.35)),(6.35,(0,0,.67)),(7.7,(0,0,.82)),(9.912,(0,0,.72)),(total,(0,0,.72))])
key(robot,'rotation_euler',[(0,(0,0,0)),(4.97,(0,0,0)),(6.35,(0,math.pi,0)),(7.7,(0,math.pi+.08,0)),(9.912,(0,math.pi-.04,0)),(total,(0,math.pi-.04,0))])
rp=tube('Fine existing end tangles',hair_points(1,0,36,96),.0009,hairmat,rb);rp.location=(1.40,0,0)

# SET 2: actual contact mechanism, visible axle and many separate hair curves.
collection('MECHANISM');studio();box('Slate macro floor',(0,-.6,-.035),(10,12,.06),felt,w=.01)
brush,spin,caps,core=roller('Mechanism roller');brush.location.z=.34
for cap in caps:cap.location.x=math.copysign(1.72,cap.location.x)
contact_shadow('Roller soft contact shadow',(0,0,.004),(4.3,1.0))
box('Intake lower sill',(0,.47,.11),(3.52,.22,.18),white,w=.045)
box('Intake dark opening',(0,.58,.48),(3.30,.12,.64),graphite,w=.04)
box('Intake upper rim',(0,.48,.84),(3.55,.25,.12),white,w=.04)
coil=tube('36 separate animated human hairs',hair_points(0,0),.00085,hairmat,brush)
coil.data.materials.append(heroMat);coil.data.splines[0].material_index=1
poses=[];xkeys=[];spinkeys=[]
episodes=[(2,cue(2,'실을 감는'),cue(2,'머리카락을 축 방향으로'),offsets[3]-.05),
          (3,cue(3,'모에 걸립니다'),cue(3,'가운데에 머물지'),cue(3,'모입니다',True)),
          (5,cue(5,'머리카락이 롤러에'),cue(5,'축으로 밀어'),cue(5,'감김이 사라지지',True)),
          (7,cue(7,'여전히 끝단에'),cue(7,'회전하는 롤러'),offsets[8]-.02),
          (8,cue(8,'회전하는 롤러'),cue(8,'끝단으로'),cue(8,'미끄러지게 하는',True))]
for p,start,slidestart,end in episodes:
 # New contact events, evaluated continuously through camera cuts, not recycled clips.
 begin=offsets[p];windend=slidestart
 for j in range(41):
  sec=begin+(end-begin)*j/40;wind=smooth((sec-start)/max(.4,windend-start));slide=smooth((sec-slidestart)/max(.4,end-slidestart))
  if p==5:wind=.65+.35*wind
  if p==7:wind=.85+.15*wind
  if p==7:slide=.91+.09*smooth((sec-begin)/max(.1,end-begin))
  poses.append((sec,(wind,slide)));xkeys.append((sec,(slide*1.60,0,0)));spinkeys.append((sec,((sec-begin)*math.tau*.85,0,0)))
 # Keep this result until the next episode; other sets handle paragraphs 4 and 8.
poses.sort(key=lambda v:v[0])
coil['wind']=0.;coil['slide']=0.
for sec,(wind,slide) in poses:
 coil['wind']=float(wind);coil['slide']=float(slide);coil.keyframe_insert('["wind"]',frame=frame(sec));coil.keyframe_insert('["slide"]',frame=frame(sec))
key(coil,'location',xkeys);key(spin,'rotation_euler',spinkeys)
cm=core.data.materials[0].copy();cm.name='X-ray rubber core';core.data.materials[0]=cm;cm.surface_render_method='BLENDED'
alpha=cm.node_tree.nodes.get('Principled BSDF').inputs['Alpha'];aa=cue(2,'축 방향으로');bb=cue(3,'베어링 쪽으로');cc=cue(3,'길이가 긴')
scalar_key(alpha,[(0,1),(aa-.05,1),(aa,.18),(offsets[3]-.05,.18),(offsets[3],1),(bb-.05,1),(bb,.18),(cc-.05,.18),(cc,1),(total,1)])
for ob in list(ACTIVE.objects):
 if ob.name.startswith('Spiral rubber vane'):
  ob.data.materials[0]=cm
# Short hairs move around the outside of the roller into the intake, never through it.
fur=[]
for i in range(20):
 x=-.55+i*.055;y=-1.2-(i%5)*.14
 o=tube('Short hair - floor to intake',[[(-.045+j*.006,.012*math.sin(j*.7+i),0) for j in range(16)]],.0013,furmat);fur.append(o)
 vals=[]
 for p,start in [(2,cue(2,'흡입력이')),(3,cue(3,'짧은 털은')),(5,cue(5,'흡입력은'))]:
  for j in range(15):
   u=j/14;sec=start+i*.035+u*2.1
   if u<.35:yy=y*(1-u/.35);zz=.012
   elif u<.90:ph=-math.pi/2+(u-.35)/.55*math.pi*.80;yy=.345*math.cos(ph);zz=.34+.345*math.sin(ph)
   else:yy=.22+(u-.90)*3;zz=.62
   vals.append((sec,(x,yy,max(.012,zz))))
  vals.append((start+2.9,(x,.80,.62)))
 key(o,'location',vals)
 vis=[(0,True)]
 for p,start in [(2,cue(2,'흡입력이')),(3,cue(3,'짧은 털은')),(5,cue(5,'흡입력은'))]:vis.extend([(start-.05,False),(start+3.0,True)])
 key(o,'hide_render',vis)
 for fc in o.animation_data.action.fcurves:
  if fc.data_path=='hide_render':
   for kp in fc.keyframe_points:kp.interpolation='CONSTANT'
 # Enter the opaque intake rather than dissolving outside it.

# SET 3: real cap opening, exposed compact tangles, cutting and reassembly.
collection('BENCH');studio();box('Felt maintenance mat',(0,0,-.04),(9,8,.07),felt,w=.07)
benchRobot,_=product('Stopped robot on maintenance mat',False);benchRobot.location=(0,1.5,.545);benchRobot.rotation_euler.y=math.pi
cleanRoot,cleanSpin,cleanCaps,cleanCore=roller('Removable maintenance brush');cleanRoot.location=(0,-.35,.38)
contact_shadow('Maintenance soft contact shadow',(0,-.35,.006),(4.3,1.0));contact_shadow('Robot on bench contact shadow',(0,1.5,.004),(4.8,3.1))
for side,cap in zip([-1,1],cleanCaps):
 x=side*1.6
 ring('Flexible cap dust seal',side*.050,.138,.060,.010,rubber,cap)
 key(cap,'rotation_euler',[(0,(0,0,0)),(cue(4,'양끝 캡을'),(0,0,0)),(cue(4,'열어 보면',True),(side*.7,0,0)),(offsets[5]-.05,(side*.7,0,0)),(offsets[8],(0,0,0)),(cue(8,'캡을 열어'),(0,0,0)),(cue(8,'열어 보세요',True),(side*.7,0,0)),(cue(8,'모터를 지키는'),(side*.7,0,0)),(total-.3,(0,0,0))])
 key(cap,'location',[(0,(x,0,0)),(cue(4,'양끝 캡을'),(x,0,0)),(cue(4,'열어 보면',True),(x+side*.65,0,0)),(offsets[5]-.05,(x+side*.65,0,0)),(offsets[8],(x,0,0)),(cue(8,'캡을 열어'),(x,0,0)),(cue(8,'열어 보세요',True),(x+side*.65,0,0)),(cue(8,'모터를 지키는'),(x+side*.65,0,0)),(total-.4,(x,0,0))])
key(cleanRoot,'location',[(0,(0,-.35,.38)),(offsets[8]-.02,(0,-.35,.38)),(offsets[8],(0,.80,.805)),(cue(8,'브러시를 꺼내서'),(0,.80,.805)),(cue(8,'브러시를 꺼내서')+.5,(0,.80,1.3)),(cue(8,'양끝 캡을'),(0,-.35,1.10)),(cue(8,'열어 보세요',True),(0,-.35,.38)),(cue(8,'모터를 지키는'),(0,-.35,.38)),(total-.15,(0,.80,.805))])
clumps=[]
for side in [-1,1]:
 paths=[]
 for k in range(48):
  r=.081+(k%8)*.003;x=side*(1.55+.027*math.sin(k*2.399));turns=1.1+1.3*(.5+.5*math.sin(k*1.7))
  paths.append([(x+.009*math.sin(j*.4+k),(r+.003*math.sin(j*.5+k))*math.cos(j/95*math.tau*turns+k*.31),(r+.003*math.sin(j*.5+k))*math.sin(j/95*math.tau*turns+k*.31)) for j in range(96)])
 ob=tube('48 individually fine compressed end hairs',paths,.00072,hairmat,cleanRoot);clumps.append(ob)
 # Open a visible cut gap in each individual curve before removal.
 cutPaths=[]
 for path in paths:
  cutPaths.append([(x,y+(0.028 if 9<=j<17 else 0),z+(0.018 if 9<=j<17 else 0)) for j,(x,y,z) in enumerate(path)])
 shape_animation(ob,[(0,paths),(cue(8,'가위나 도구로'),paths),(cue(8,'잘라',True),cutPaths),(total,cutPaths)])
 key(ob,'location',[(0,(0,0,0)),(cue(8,'잘라 빼는'),(0,0,0)),(cue(8,'모터를 지키는'),(side*.8,-.4,1.0)),(total,(side*.8,-.4,1.0))])
 # At the shear instant topology changes into two genuinely separate curves.
 cuttime=cue(8,'잘라',True)
 key(ob,'hide_render',[(0,False),(cuttime,True),(total,True)])
 for fc in ob.animation_data.action.fcurves:
  if fc.data_path=='hide_render':
   for kp in fc.keyframe_points:kp.interpolation='CONSTANT'
 for part,slices in enumerate([(0,13),(15,96)]):
  frag=tube('Physically separated cut hair fragment',[path[slices[0]:slices[1]] for path in paths],.00072,hairmat,cleanRoot)
  key(frag,'hide_render',[(0,True),(cuttime,False),(total,False)])
  for fc in frag.animation_data.action.fcurves:
   if fc.data_path=='hide_render':
    for kp in fc.keyframe_points:kp.interpolation='CONSTANT'
  key(frag,'location',[(0,(0,0,0)),(cuttime,(0,0,0)),(cue(8,'모터를 지키는'),(side*(.8+part*.12),-.4,1.0+part*.12)),(total,(side*(.8+part*.12),-.4,1.0+part*.12))])
hand=glove('Hand lifts roller and removes hair');key(hand,'location',[(0,(2.1,-.8,.2)),(cue(4,'양끝 캡을'),(1.85,-.4,.42)),(offsets[5]-.02,(1.85,-.4,.42)),(offsets[8],(2.3,-.6,.8)),(cue(8,'브러시를 꺼내서'),(1.4,.5,1.0)),(cue(8,'열어 보세요',True),(2,-.4,.48)),(cue(8,'잘라 빼는'),(1.5,-.4,.45)),(cue(8,'모터를 지키는'),(2.3,-.7,1.2)),(total,(2.3,-.7,.7))]);hand.rotation_euler=(math.pi/2,0,-math.pi/2)
hand.rotation_euler=(0,0,math.pi/2)
key(hand,'location',[(offsets[4],(.7,-.35,.9)),(offsets[4]+1.4,(.0,-.35,.82)),(cue(4,'양끝 캡을'),(1.9,-.35,.82)),(cue(4,'로보락'),(2.0,-.35,.82)),(cue(4,'끝단과'),(1.5,-.35,.82)),(cue(4,'베어링을'),(2.1,-.35,.82)),(cue(4,'안내합니다'),(-1.4,-.35,.9)),(offsets[5]-.02,(-1.9,-.35,.82)),(cue(8,'일주일에'),(1.9,-.35,.85)),(cue(8,'머리카락이 많거나'),(.0,-.35,.95)),(cue(8,'반려동물이'),(-1.5,-.35,.85)),(cue(8,'두 번이면'),(-1.9,-.35,.85)),(cue(8,'충분합니다',True),(1.9,-.35,.9))])
key(cleanSpin,'rotation_euler',[(offsets[4]+14.65+j*.15,(.07*math.sin(j*1.7),0,0)) for j in range(38)]+[(offsets[5],(0,0,0)),(total,(0,0,0))])
scissors=empty('Working scissors')
for side in [-1,1]:
 blade=empty('Scissor blade with handle',scissors)
 pts=[(-.30,side*.035,0),(.0,side*.06,0),(.83,side*.005,0),(.72,side*-.05,0)]
 me=bpy.data.meshes.new('Tapered sharpened steel blade');me.from_pydata(pts,[],[(0,1,2,3)]);o=bpy.data.objects.new('Sharpened scissor blade',me);ACTIVE.objects.link(o);o.parent=blade;me.materials.append(metal);sol=o.modifiers.new('Blade thickness','SOLIDIFY');sol.thickness=.014;edge(o,.004)
 tube('Moulded finger loop',[ [(-.43+.17*math.cos(j/64*math.tau),side*.16+.11*math.sin(j/64*math.tau),0) for j in range(65)] ],.035,graphite,blade)
 key(blade,'rotation_euler',[(0,(0,0,side*.33)),(cue(8,'가위나 도구로'),(0,0,side*.33)),(cue(8,'잘라',True),(0,0,side*.015)),(total,(0,0,side*.015))])
key(scissors,'location',[(0,(4,-1,1)),(cue(8,'끝단에 감겨'),(3,-1,.8)),(cue(8,'가위나 도구로'),(1.15,-.35,.48)),(cue(8,'잘라',True),(1.15,-.35,.48)),(total,(3,-1,1.0))]);scissors.rotation_euler=(math.pi/2,0,0)

# Required additional structural assets. Kept as an inspectable library because
# the user explicitly held paragraph 6; no unverified brand claim is voiced.
collection('ASSET_LIBRARY_HELD_6');dual=empty('Two short rollers with opposite helical pitch')
for side in [-1,1]:
 rr,ss,cc,core2=roller('Short roller',dual,1.30);rr.location=(side*.80,0,.34)
 key(ss,'rotation_euler',[(0,(0,0,0)),(total,(side*math.tau*8,0,0))])
comb=empty('Cutting comb asset');box('Cutting comb plastic holder',(0,0,.8),(2.9,.20,.15),graphite,comb,w=.04)
for j in range(25):
 x=-1.35+j*.112;me=bpy.data.meshes.new('Cutting comb tooth');me.from_pydata([(x-.035,0,.78),(x+.035,0,.78),(x+.015,0,.42),(x-.015,0,.42)],[],[(0,1,2,3)]);o=bpy.data.objects.new('Individual sharpened steel comb tooth',me);ACTIVE.objects.link(o);o.parent=comb;me.materials.append(metal);so=o.modifiers.new('Steel thickness','SOLIDIFY');so.thickness=.018;edge(o,.005)

# Cameras and action table, anchored to the measured narration's local words.
with (OLD/'storyboard-aligned.csv').open() as f:semantic=list(csv.DictReader(f))
marks={1:[4.975,6.713],2:[5.025,9.750],3:[4.213,7.775,10.0,14.425,17.2],4:[2.9,7.925,14.65],5:[cue(5,'흡입력은')-offsets[5],cue(5,'머리카락이 롤러에')-offsets[5]],7:[cue(7,'여전히 끝단에')-offsets[7],cue(7,'회전하는 롤러')-offsets[7]],8:[7.688,10.075,12.537,19.025,22.475]}
cutrows=[]
for p in paragraphs:
 times=[0]+marks[p]+[durations[f'{p:02}']];safe=[times[0]]
 for t in times[1:-1]:
  if t-safe[-1]>=1.5:safe.append(t)
 if times[-1]-safe[-1]<1.5:safe.pop()
 safe.append(times[-1]);count=0
 for aa,bb in zip(safe,safe[1:]):
  n=math.ceil((bb-aa)/3)
  for k in range(n):
   count+=1;aa1=aa+(bb-aa)*k/n;bb1=aa+(bb-aa)*(k+1)/n
   relevant=[r for r in semantic if int(r['paragraph'])==p and aa1-.02<=float(r['speech_start_sec'] or 0)<bb1]
   if not relevant:relevant=[min([r for r in semantic if int(r['paragraph'])==p],key=lambda r:abs(float(r['speech_start_sec'])-aa1))]
   cutrows.append({'cut_id':f'P{p}-C{count:02}','paragraph':p,'start_sec':aa1,'end_sec':bb1,'speech_cues':'; '.join(r['speech_cue'] for r in relevant),'linked_actions':'; '.join(r['subject_start']+' → '+r['actual_action']+' → '+r['result'] for r in relevant)})
angles=[(.35,-2.8,1.65),(1.9,-1.5,1.1),(.1,-.35,3.6),(-1.7,-1.8,.75)]
plan=[];last_angle=None
for idx,row in enumerate(cutrows):
 p=int(row['paragraph']);a=offsets[p]+float(row['start_sec']);b=min(offsets[p]+float(row['end_sec']),offsets[p]+durations[f'{p:02}']);mid=(a+b)/2
 setname='ROOM' if p==1 else ('BENCH' if p==4 or (p==8 and a>=cue(8,'청소가')-.02) else 'MECHANISM')
 focus=(0,0,.38);angle=idx%4;lens=56
 if setname=='ROOM':
  focus=(0,-.2,1.0);locs=[(4,-7.5,5),(0,-8,4),(4,-5,5.5),(-4,-5,3)]
  if a>=6.35:focus=(-1.40,-.70,1.03);loc=Vector(focus)+Vector([(1.1,-2.8,2.2),(-1.5,-2.3,1.5),(.1,-.3,3.2),(1.8,-1.8,.8)][angle]);lens=64
  else:loc=locs[angle]
 elif setname=='BENCH':
  target=1.55 if ('캡' in row['speech_cues'] or '끝단' in row['speech_cues'] or '잘라' in row['speech_cues'] or '도구' in row['speech_cues']) else 0
  if p==8 and mid<cue(8,'브러시를 꺼내서'):focus=(0,.8,1);loc=(3.6,-6,5);lens=53
  elif p==8 and mid>=cue(8,'모터를 지키는'):
   focus=(0,.4,.8);loc=[(3.8,-5,4),(-3.8,-5,3),(0,-4,6),(3,-3,2.5)][angle];lens=48
  else:
   focus=(target,-.35,.43);loc=Vector(focus)+Vector(angles[angle]);lens=60 if target else 42
 else:
  target=0
  if p==3:
   target=1.68*smooth((mid-cue(3,'가운데에 머물지'))/(cue(3,'모입니다',True)-cue(3,'가운데에 머물지')))
   if mid>=cue(3,'짧은 털은'):target=.1
  elif p==2:target=1.68*smooth((mid-cue(2,'머리카락을 축 방향으로'))/max(1,offsets[3]-cue(2,'머리카락을 축 방향으로')))
  elif p==7:target=1.60
  elif p==5:target=.75
  elif p==8:target=1.68*smooth((mid-cue(8,'끝단으로'))/max(.1,cue(8,'미끄러지게 하는',True)-cue(8,'끝단으로')))
  focus=(target,0,.34);loc=Vector(focus)+Vector(angles[angle]);lens=58
  if p==3 and mid>=cue(3,'짧은 털은') and mid<cue(3,'길이가 긴'):loc=Vector(focus)+Vector((.65,-2.7,1.9));lens=50
 bpy.ops.object.camera_add(location=loc);cam=add(bpy.context.object,f'CAM_{idx:03}_{setname}');cam.rotation_euler=(Vector(focus)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.dof.use_dof=True;cam.data.dof.focus_distance=(Vector(focus)-cam.location).length;cam.data.dof.aperture_fstop=8
 # Set cameras live in the scene root so collection visibility cannot remove them.
 ACTIVE.objects.unlink(cam);S.collection.objects.link(cam)
 marker=S.timeline_markers.new(row['cut_id'],frame=frame(a));marker.camera=cam
 plan.append({'id':row['cut_id'],'paragraph':p,'start':a,'end':b,'start_frame':frame(a),'end_frame_exclusive':frame(b),'set':setname,'camera':cam.name,'spoken_words':row['speech_cues'],'object_and_action':row['linked_actions'],'status':'KEYFRAMED_3D'})
S.camera=bpy.data.objects[plan[0]['camera']];S.frame_start=1;S.frame_end=math.ceil(total*FPS)
for name,c in COLS.items():c.hide_render=name!='ROOM'
(BASE/'scene-plan.json').write_text(json.dumps({'fps':24,'duration_audio':total,'held_paragraph':6,'cuts':plan},ensure_ascii=False,indent=2))
with (BASE/'scene-table.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=plan[0].keys(),lineterminator='\n');w.writeheader();w.writerows(plan)
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'hair-animation.blend'),compress=True)
print('BUILD COMPLETE',total,'seconds',len(plan),'camera cuts')
