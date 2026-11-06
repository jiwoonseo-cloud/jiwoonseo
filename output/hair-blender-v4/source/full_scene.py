import bpy,math,random,ast,json,sys,os,time,shutil,struct
from math import sin,cos,pi
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'hair-full-assets.blend'));s=bpy.context.scene
B=json.loads((P/'blocks.json').read_text());SH=json.loads((P/'full-shots.json').read_text());EV=json.loads((P/'full-events.json').read_text());N=3128
source=(P/'blender_pilot.py').read_text()
for node in ast.parse(source).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['ease','pose']:exec(ast.get_source_segment(source,node))
pilot_pose=pose
ROOT=bpy.data.objects['ROBOT_ROOT'];roller=bpy.data.objects['main brush rotating group'];hair=bpy.data.objects['80 distinct long hair curves'];cam=s.camera;focus=bpy.data.objects['physical focus target'];Y=-.065;Z=.02305;NP=144
rng=random.Random(3403)
for _ in range(3840*4):rng.random()
strand_specs=[(rng.uniform(.34,.48),rng.uniform(-.0045,.0045),rng.uniform(-.0012,.0012),rng.uniform(-.00014,.00014)) for _ in range(80)]
start=21.455;wrap_start=23.102708;slide_start=27.693625;finish=31.375458
# Continuous wrists and forearms extend out of frame instead of floating gloves.
skin=bpy.data.materials.new('warm skin forearm');skin.use_nodes=True;bs=skin.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.34,.19,.12,1);bs.inputs['Roughness'].default_value=.52;bs.inputs['Subsurface Weight'].default_value=.07
sleeve=bpy.data.materials.new('charcoal cotton sleeve');sleeve.use_nodes=True;sleeve.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.028,.033,.038,1);sleeve.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.82
for handname in ['HAND_R','HAND_L']:
 for name,pos,scale,matl in [('anatomical wrist',(.105,0,.006),(.065,.020,.016),skin),('soft cotton forearm',(.270,0,.006),(.170,.030,.025),sleeve)]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=pos);ob=bpy.context.object;ob.name=handname+' '+name;ob.scale=scale;ob.parent=bpy.data.objects[handname];ob.data.materials.append(matl)
  for face in ob.data.polygons:face.use_smooth=True
  ob['base_location']=list(ob.location);ob['base_rotation']=list(ob.rotation_euler);ob['base_scale']=list(ob.scale)
# Irregular dust aggregates are distinct from pet fur in the suction explanation.
dust_root=bpy.data.objects.new('DUST_STREAM',None);s.collection.objects.link(dust_root);dust_root.parent=ROOT;dustparts=[];drng=random.Random(714)
dustmat=bpy.data.materials.new('matte beige dust aggregate');dustmat.use_nodes=True;db=dustmat.node_tree.nodes.get('Principled BSDF');db.inputs['Base Color'].default_value=(.40,.31,.22,1);db.inputs['Roughness'].default_value=.86
for i in range(48):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=drng.uniform(.00015,.00040),location=(0,0,-2));ob=bpy.context.object;ob.name='individual airborne dust aggregate';ob.parent=dust_root;ob.scale=(drng.uniform(.8,1.3),drng.uniform(.7,1.1),drng.uniform(.6,1.2));ob.data.materials.append(dustmat)
 for vtx in ob.data.vertices:vtx.co*=drng.uniform(.83,1.17)
 ob['base_location']=list(ob.location);ob['base_rotation']=list(ob.rotation_euler);ob['base_scale']=list(ob.scale);dustparts.append(ob)
allobj=list(s.objects)
for o in allobj:
 if o.animation_data:o.animation_data_clear()
 if o.type in ['CURVE','CAMERA'] and o.data.animation_data:o.data.animation_data_clear()
get=lambda n:bpy.data.objects[n]
body=get('closed round ABS upper shell');partial=get('circular white robot cover rear cutaway');under=get('dark underside service plate');duo=get('DUO');inlet=get('INLET');fur=get('SHORT_FUR');halfA=get('CUT_HALF_A');halfB=get('CUT_HALF_B');comb=get('CUTTER_COMB');motor=get('MOTOR');rotor=get('MOTOR_ROTOR');spool=get('SPOOL');thread=get('SPOOL_THREAD');scissors=get('SCISSORS');room=get('ROOM');handR=get('HAND_R');handL=get('HAND_L');window=get('broad living room window')
furmat=bpy.data.materials.new('pale fine pet undercoat');furmat.use_nodes=True;furmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.46,.34,.20,1);furmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.45;fur.data.materials.clear();fur.data.materials.append(furmat);fur.data.bevel_depth=.00008
caps=[get('CAP_L'),get('CAP_R')];bearings=[get('BEARING_L'),get('BEARING_R')];halves=[get('DUO_HALF_-1'),get('DUO_HALF_1')];leaves=[get('SCISSOR_LEAF_-1'),get('SCISSOR_LEAF_1')]
under.location.z=-.0012;under['base_location']=list(under.location)
for plate in [body,under]:
 for face in plate.data.polygons:
  if abs(face.normal.x)>.95:face.use_smooth=False
port=get('central short roller intake throat');port.rotation_euler=(0,0,pi/2);port.location=(0,-.065,.043);port['base_rotation']=list(port.rotation_euler);port['base_location']=list(port.location)
axle=get('stainless axle and keyed ends');core=get('tapered rubber roller with end shoulders');fins=[o for o in roller.children if 'helical molded lip' in o.name]
black=bpy.data.materials['carbon rubber micrograin'];teal=bpy.data.materials['molded flexible teal elastomer']
ghost=black.copy();ghost.name='scientific xray rubber';g=ghost.node_tree.nodes.get('Principled BSDF');g.inputs['Alpha'].default_value=.12;g.inputs['Transmission Weight'].default_value=.7
ghostfin=teal.copy();ghostfin.name='scientific xray vane';ghostfin.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.22

def vis(o,yes):
 o.hide_render=not yes
 for c in o.children_recursive:c.hide_render=not yes

def reset():
 for o in allobj:
  if 'base_location' in o:o.location=o['base_location'];o.rotation_euler=o['base_rotation'];o.scale=o['base_scale']
  o.hide_render=False
 for o in [duo,inlet,fur,halfA,halfB,comb,motor,spool,thread,scissors,handR,handL,dust_root]:vis(o,False)
 core.data.materials[0]=black
 for ob in fins:ob.data.materials[0]=teal
 vis(body,False);vis(under,False)
 for o in ROOT.children:
  if any(k in o.name for k in ['lidar','button','bumper']):vis(o,False)
 window.data.energy=0


CAM_LIFT=0
def camera_at(target,off,lens=55,fstop=20,surface=0,variant=0):
 bpy.context.view_layer.update();target=ROOT.matrix_world@(Vector(target)+Vector((0,0,CAM_LIFT)));off=Vector(off)
 if variant:
  a=.19 if variant==1 else -.23;off=Vector((off.x*cos(a)-off.y*sin(a),off.x*sin(a)+off.y*cos(a),off.z*(1.08 if variant==1 else .88)))
 cam.location=target+off;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.dof.aperture_fstop=fstop;focus.location=target+off.normalized()*surface


def closed():
 vis(body,True);vis(under,True);vis(partial,False)
 for o in ROOT.children:
  if any(k in o.name for k in ['lidar','button','bumper']):vis(o,True)

def packed(t,center=.130,r=.0065,care=False,turns=5,spread=1):
 for i,(sp,(_,dx,dy,dz)) in enumerate(zip(hair.data.splines,strand_specs)):
  sign=1 if i%2 else -1;compression=.4+.9*max(0,min(1,(r-.0065)/.0165));x=center+dx*compression*spread;rr=r+dz+.0008*(i%7)/7+(i%5==0)*.0010;phase=.9*sin(i*3.1)
  for j,p in enumerate(sp.points):
   q=j/(NP-1)
   if care and q>.78:
    v=(q-.78)/.22;a=-pi/2-turns*2*pi*.78-t*14+phase
    xx=x+.0006*sin(i+v*3)+.012*v*sin(i*.7);yy=Y+rr*cos(a)-.035*v;zz=Z+rr*sin(a)+.012*v*v
   else:
    a=-pi/2-turns*2*pi*q-t*14+phase;xx=x+.002*q+(.0005+.001*r/.023)*sin(q*7*pi+i)*sin(q*pi);yy=Y+rr*cos(a);zz=Z+rr*sin(a)
   p.co=(xx,yy,zz,1)

def flowing_fur(u,wide=False):
 vis(fur,True)
 path=[Vector((0,-.145,.0001)),Vector((0,-.105,.005)),Vector((0,-.092,.023)),Vector((0,-.085,.045)),Vector((0,-.050,.058)),Vector((0,-.005,.065))]
 def curveat(q):
  q=max(0,min(.99999,q));a=q*(len(path)-1);k=int(a);v=a-k;return path[k].lerp(path[k+1],v)
 for i,sp in enumerate(fur.data.splines):
  q=max(0,min(1,(u*2.4-i*.045)/.38));q=q*q;offset=(i%9-4)*.008*(1-q)
  for j,p in enumerate(sp.points):
   a=curveat(min(1,q+j*.004));a.x+=offset+.0007*sin(i+j*.9);p.co=(*a,1)
  if q>.985:
   for p in sp.points:p.co=(0,0,-2,1)

def flowing_dust(seconds):
 vis(dust_root,True)
 path=[Vector((0,-.14,.012)),Vector((0,-.11,.018)),Vector((0,-.085,.041)),Vector((0,-.047,.058)),Vector((0,-.005,.065))]
 for i,ob in enumerate(dustparts):
  q=((seconds/.48+i/48)%1)**1.7;a=min(.99999,q)*(len(path)-1);k=int(a);co=path[k].lerp(path[k+1],a-k);co.x+=(i%9-4)*.007*(1-q);co.z+=.002*sin(i*2.7)*(1-q);ob.location=co;ob.rotation_euler=(seconds*5+i,seconds*7+i*.3,seconds*3);ob.hide_render=q>.98

def twin_flow(t,u,show_hair=True):
 vis(roller,False);vis(duo,True);vis(inlet,True);axle.hide_render=True
 for i,h in enumerate(halves):h.rotation_euler.x=(-1 if i==0 else 1)*t*12
 hair.hide_render=not show_hair
 for i,sp in enumerate(hair.data.splines):
  sg=-1 if i<40 else 1;pp=ease(min(1,u/.68));cx=sg*(.096*(1-pp)+.003);rr=.023*(1-.90*ease((u-.68)/.23));rise=.055*ease((u-.77)/.23)
  for j,p in enumerate(sp.points):
   q=j/(NP-1);a=-pi/2+sg*(t*12+q*pi*3)+.55*sin(i*3.1);ri=rr+.0005*(i%7)/7*(1-u);xx=cx+strand_specs[i][1]*.6+.0008*sin(q*7*pi+i)*sin(q*pi)*(1-u);yy=Y+ri*cos(a)+rise;zz=Z+ri*sin(a)+rise
   p.co=(xx,yy,zz,1) if u<.99 else (0,0,-2,1)

def split_hair(u,pull=False):
 vis(hair,False);vis(halfA,True);vis(halfB,True)
 halfA.location.z=hair.location.z;halfB.location.z=hair.location.z
 for i,original in enumerate(hair.data.splines):
  for group,k in [(halfA,0),(halfB,72)]:
   for j,p in enumerate(group.data.splines[i].points):
    q=original.points[j+k].co.xyz.copy();q.x+=u*.035;q.y-=u*.022;q.z+=(-.025 if pull else .040)*u+(0 if group==halfA else .008*u);p.co=(*q,1)
 if u>.95:vis(halfA,False);vis(halfB,False)


def full_pose(t):
 global CAM_LIFT
 CAM_LIFT=0
 reset();b=next((b for b in B if b['start']<=t<b['end']),B[-1]);shot=next((x for x in SH if x['start']<=t<x['end']),SH[-1]);m=b['mode'];u=max(0,min(1,(t-b['start'])/(b['end']-b['start'])));v=shot['angle'];tau=t-b['start']
 roller.rotation_euler.x=t*18;packed(t)
 if m=='core':
  for o in allobj:
   if o.type in ['MESH','CURVE'] and not o.get('core_original',False):o.hide_render=True
  vis(room,False)
  pilot_pose(t-start)
  if t<start:
   p=ease((t-b['start'])/(start-b['start']));roller.rotation_euler.x=-2*pi*p
   for sp in hair.data.splines:
    for point in sp.points:point.co.y+=.008*(1-p)
  return m
 if m in ['home','flip','inspect','center','caps','check','check_again','remove','caps_final','routine','snip','assemble']:
  closed();vis(partial,False);roller.rotation_euler.x=0;packed(0,care=True)
  lift=(-.055 if m in ['caps_final','routine','snip'] else -.006 if m in ['caps','check','check_again'] else 0);CAM_LIFT=lift
  roller.location.z+=lift;hair.location.z=lift;axle.location.z+=lift
  for ob in caps+bearings:ob.location.z+=lift
  handR.location.z+=lift;handL.location.z+=lift
  if m in ['caps_final','routine','snip']:handR.location.x=.160;handL.location.x=-.160
 if m=='home':
  window.data.energy=350;RootY=.22*(1-ease(min(1,u/.85)));ROOT.location.y=RootY
  for wheel in [get('DRIVE_WHEEL_-1'),get('DRIVE_WHEEL_1')]:wheel.rotation_euler.x=-(.22-RootY)/.024
  get('SIDE_BRUSH').rotation_euler.z=t*10 if u<.85 else 0
  if v==0:camera_at((0,0,.035),(.45,-.70,.40),40,11,.035,0)
  else:camera_at((0,-.07,.035),(.28,-.40,.23),50,18,.025,0)
 elif m=='flip':
  ROOT.location.z=.098*ease(u)+.16*sin(pi*u);ROOT.rotation_euler.x=pi*ease(u);vis(handR,True);vis(handL,True)
  camera_at((0,0,.035),(.20,-.35,.80),35,16,.03,v)
 elif m in ['inspect','center','caps','check','check_again','caps_final','routine']:
  ROOT.rotation_euler.x=pi;ROOT.location.z=.098;vis(handR,True);vis(handL,True)
  if m=='inspect':
   ROOT.rotation_euler.z=.09*sin(pi*u);roller.rotation_euler.x=.9*ease((t-EV['inspect_turn'])/.5)-.2*ease((t-EV['inspect_turn']-1)/.4);packed(-roller.rotation_euler.x/14,care=True)
   if v==2:camera_at((0,0,.03),(.18,-.35,.50),40,22,.015,0)
   else:camera_at((.09,Y,.024),(.12,-.20,.15),65,24,.008,v)
  elif m=='center':
   packed(0,.130,care=True);lift=-.006*ease(u);CAM_LIFT=lift;roller.location.z+=lift;hair.location.z=lift;axle.location.z+=lift
   for ob in caps+bearings:ob.location.z+=lift
   handR.location.z+=lift;handL.location.z+=lift
   camera_at((-.028,Y,.023),(.07,-.13,.11),55,24,.015,v)
  else:
   open_time=EV['caps_open'] if m=='caps' else EV['caps_final_open'];pull=.026*ease((t-open_time)/.5) if m in ['caps','caps_final'] else .026
   for i,c in enumerate(caps):c.location.x+=(1 if i else -1)*pull
   handR.location.x+=pull;handL.location.x-=pull
   if m in ['caps','caps_final']:
    twist=(.35*ease((t-open_time-.65)/.5) if v==0 else .35+.15*ease((t-shot['start'])/.45));handR.rotation_euler.x=twist;handL.rotation_euler.x=-twist;caps[1].rotation_euler.x=twist;caps[0].rotation_euler.x=-twist;bearings[1].rotation_euler.x=twist
   if m in ['routine','check','check_again']:
    handR.rotation_euler.x=.25*sin(pi*u);handL.rotation_euler.x=-.2*sin(pi*u);caps[1].rotation_euler.x=.25*sin(pi*u);caps[0].rotation_euler.x=-.2*sin(pi*u);bearings[1].rotation_euler.x=.25*sin(pi*u);bearings[0].rotation_euler.x=-.2*sin(pi*u)
   if m=='check_again':vis(roller,False);vis(duo,True);duo.location.z+=CAM_LIFT;axle.hide_render=True
   if m in ['routine','check_again'] and v==0:camera_at((0,Y,.025),(.22,.34,.30),40,22,.015,0)
   elif v==0 and m in ['caps','caps_final']:camera_at((0,Y,.024),(.26,-.36,.30),40,18,.018,v)
   else:camera_at((.133,Y,.025),(.055,.11,.085),55,32,.005,v)
 elif m=='floor_intro':
  roller.rotation_euler.x=t*10;packed(t,.03,.023,turns=1.5)
  camera_at((0,Y,.019),(.12,-.23,.07),55,24,.018,v)
 elif m=='spool':
  vis(spool,True);vis(thread,True);hair.hide_render=True;spool.rotation_euler.x=-tau*10
  for i,sp in enumerate(thread.data.splines):
   for j,p in enumerate(sp.points):
    q=j/99;a=-pi/2+q*(.2+u*4)*2*pi;x=-.012+.025*u+q*.0007+i*.00004;p.co=(x,-.13+.0125*cos(a),.035+.0125*sin(a),1)
  camera_at((0,-.13,.035),(.065,-.14,.085),60,24,.012,v)
 elif m in ['short','remain','air_compare','pinned','migrate_strong','retain']:
  vis(inlet,True);packed(t,.130,.0065)
  if m=='short':flowing_fur(u)
  elif m in ['air_compare','pinned','migrate_strong']:flowing_dust(tau)
  if m=='migrate_strong':packed(t,-.025+.155*ease(u),.023-.0165*ease((u-.87)/.13))
  if m=='remain':camera_at((.132,Y,.024),(.06,-.12,.075),55,32,.006,v)
  elif m=='short':camera_at((0,-.075,.033),(.10,-.16,.13),55,32,.012,v)
  elif m=='air_compare':
   if v==0:camera_at((0,-.12,.018),(.035,-.13,.035),45,28,.003,0)
   elif v==1:camera_at((0,-.025,.055),(.07,-.095,.085),50,28,.012,0)
   else:camera_at((0,-.035,.045),(.35,-.44,.40),35,20,.02,0)
  elif m=='pinned':
   if v==0:camera_at((.045,Y-.02,.027),(.18,-.27,.20),35,24,.015,0)
   else:camera_at((.13,Y-.005,.022),(.02,-.08,.06),55,32,.005,0)
  elif m=='migrate_strong':
   if v==0:camera_at((-.025+.155*ease(u),Y,.022),(-.09,-.10,.045),45,30,.01,0)
   else:camera_at((0,Y-.065,.020),(0,-.10,.55),35,24,.01,0)
  elif m=='retain':
   if v==0:camera_at((.132,Y,.022),(.075,-.10,.045),50,32,.005,0)
   else:vis(motor,True);rotor.rotation_euler.x=t*18;camera_at((.125,-.03,.035),(.08,-.16,.16),50,28,.01,0)
  else:camera_at((.035,Y,.028),(.18,-.27,.20),55,24,.015,v)
 elif m=='motor':
  vis(partial,False);vis(motor,True);rotor.rotation_euler.x=12*(tau-.22*tau*tau/(b['end']-b['start']));roller.rotation_euler.x=rotor.rotation_euler.x
  camera_at((.123,.003,.045),(.06,.11,.11),65,30,.008,v)
 elif m in ['module','duo_spin','duo_flow','paths']:
  if m=='module':
   roller.location.z+=.10*ease(min(1,u*2));vis(duo,True);vis(inlet,True);hair.hide_render=True
   for i,h in enumerate(halves):h.location.x+=(-1 if i==0 else 1)*.12*(1-ease((u-.4)/.6))
   camera_at((0,Y,.050),(.20,-.30,.32),45,20,.02,v)
  elif m=='paths':
   vis(comb,True);vis(inlet,True);comb.location.x=.0015*sin(t*2*pi*6);packed(t,.025,.023,turns=1.2);split_hair(u);flowing_fur(u);camera_at((0,-.035,.040),(.20,-.28,.30),45,24,.018,v)
  else:
   suction=EV['duo_suction'];moveEnd=b['end']
   q=u if m=='paths' else (0 if m=='duo_spin' else min(1,(t-b['start'])/(moveEnd-b['start'])))
   twin_flow(t,q,m!='duo_spin')
   if v==0:camera_at((0,Y,.027),(.08,-.29,.28),35,24,.014,0)
   else:camera_at((0,Y,.027),(.08,-.24,.23),55,24,.014,v)
   cam.rotation_euler.rotate_axis('Z',.65)
 elif m=='cut':
  vis(comb,True);vis(inlet,True);comb.location.x=.0015*sin(t*2*pi*6);packed(t,.025,.023,turns=1.4)
  cut_time=EV['brand_cut']+.35
  if t>cut_time:split_hair(ease((t-cut_time)/max(.2,b['end']-cut_time)))
  camera_at((.025,Y-.017,.025),(-.08,-.14,.09),65,32,.018,v)
 elif m in ['residual','hairy_floor']:
  twin_flow(t,0,False);vis(hair,True);packed(t,.132,.0065,care=True)
  caps[1].location.x+=.022*ease(u)
  if v==0:camera_at((0,Y,.03),(.19,-.28,.27),45,26,.015,0)
  else:camera_at((.132,Y,.024),(.07,-.13,.09),60,32,.007,v)
 elif m in ['xray_migrate','xray_continue','overview']:
  core.data.materials[0]=ghost
  for fin in fins:fin.data.materials[0]=ghostfin
  vis(motor,True);rotor.rotation_euler.x=t*12
  if m in ['overview','xray_continue']:
   begin=next(q['start'] for q in B if q['mode']=='overview');ending=next(q['start'] for q in B if q['mode']=='remove');u=max(0,min(1,(t-begin)/(ending-begin)))
  cx=-.04+.17*ease(u);packed(t,cx,.023-.0165*ease((u-.85)/.15))
  if m=='overview':camera_at((.03,-.035,.035),(.23,-.30,.33),45,22,.018,v)
  else:camera_at((cx,Y,.025),(.07,-.16,.14),50,28,.01,v)
 elif m=='remove':
  ROOT.rotation_euler.x=pi;ROOT.location.z=.098;vis(handR,True);vis(handL,True);extract=ease((t-EV['remove_start'])/.65);lift=-.055*extract;CAM_LIFT=lift;roller.location.z+=lift;hair.location.z=lift;axle.location.z+=lift
  for i,ob in enumerate(caps+bearings):ob.location.z+=lift
  handR.location.z+=lift;handL.location.z+=lift;handR.location.x=.182-.022*extract;handL.location.x=-.182+.022*extract
  camera_at((0,Y,.020),(.24,-.35,.31),40,18,.015,v)
 elif m=='snip':
  ROOT.rotation_euler.x=pi;ROOT.location.z=.098;caps[1].location.x+=.026;caps[0].location.x-=.026;vis(handR,True);vis(handL,True);vis(scissors,True)
  approach=ease((t-b['start'])/.8);approach_y=-.035*(1-approach);scissors.location=(.132,Y-.074+approach_y,.02305+CAM_LIFT);scissors.rotation_euler.z=pi
  close=ease((t-(EV['snip_close']-.5))/.5);pull=ease((t-EV['snip_pull'])/max(.2,b['end']-EV['snip_pull']))
  for i,l in enumerate(leaves):l.rotation_euler.z=(-1 if i==0 else 1)*(.35*(1-close)+.015)
  handR.location=(.132,-.176+approach_y,.032+CAM_LIFT);handR.rotation_euler.z=-pi/2;handR.location.x+=pull*.035;scissors.location.x+=pull*.035;scissors.location.y-=pull*.022;scissors.location.z-=pull*.025;handR.location.y-=pull*.022;handR.location.z-=pull*.025
  if t>EV['snip_close']:split_hair(pull,True)
  camera_at((.132,Y-.004,.023),(.06,.13,.10),60,32,.005,v)
 elif m=='assemble':
  vis(hair,False);vis(handR,True);vis(handL,True);ROOT.rotation_euler.x=pi*(1-ease((u-.55)/.45));ROOT.location.z=.098*(1-ease((u-.55)/.45));lift=-.055*(1-ease(min(1,u/.5)));CAM_LIFT=lift;roller.location.z+=lift;axle.location.z+=lift
  for ob in caps+bearings:ob.location.z+=lift
  for i,ob in enumerate(caps):ob.location.x+=(1 if i else -1)*.025*(1-ease(min(1,u/.5)))
  handR.location.z+=lift;handL.location.z+=lift;window.data.energy=250
  camera_at((0,Y,.025),(.31,-.48,.43),45,18,.02,v)
 else:camera_at((0,Y,.025),(.22,-.30,.24),50,22,.02,v)
 if m in ['short','remain','air_compare','pinned','migrate_strong','retain','cut','paths']:port.hide_render=True
 return m

s.render.engine='CYCLES';s.cycles.samples=int(os.environ.get('SAMPLES','2'));s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=1;s.cycles.adaptive_threshold=.12;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=1;s.cycles.glossy_bounces=2;s.render.use_persistent_data=True;s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.resolution_percentage=int(os.environ.get('RENDER_PERCENT','100'));s.render.fps=24;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='16';s.view_layers[0].cycles.denoising_store_passes=True
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];mode=args[0] if args else 'full'
if mode=='full' and not (P/'PILOT_PASSED.json').exists():raise RuntimeError('Pilot visual gate has not passed; full-scene rendering is blocked.')
if mode=='preview':frames=sorted(set([int(round((q['start']+q['end'])*12)) for q in SH]+[0,N-1,int(EV['snip_close']*24),int(EV['snip_pull']*24)]));stage='full-preview'
elif mode=='still':frames=[int(x) for x in args[1:]];stage='full-preview'
else:frames=list(range(int(os.environ.get('START_FRAME','0')),int(os.environ.get('END_FRAME',str(N)))));stage='full'
if mode=='full' and os.environ.get('FRAME_LIST'):frames=[int(q) for q in os.environ['FRAME_LIST'].split(',')]
(P/f'{stage}-frames').mkdir(exist_ok=True);(P/f'{stage}-denoised').mkdir(exist_ok=True)
for f in frames:
 if mode=='full' and os.environ.get('PRIORITY_GATE')=='1' and f==0:
  print('WAITING_CRITICAL_REVIEW',flush=True)
  while not (P/'CRITICAL_PASSED.json').exists():time.sleep(.2)
 if mode=='full':
  while len(list((P/f'{stage}-frames').glob('*.exr')))>=6:time.sleep(.2)
 out=P/f'{stage}-frames/{f:04}.exr';rgb=P/f'{stage}-denoised/{f:04}.png'
 cache=None
 if mode=='full' and out.exists() and (P/f'{stage}-frames/{f:04}.ready').exists():
  print('PENDING_POSTPROCESS',f,flush=True);continue
 if mode=='full' and rgb.exists():
  (P/f'{stage}-frames/{f:04}.cached').touch();print('RESUMED',f,flush=True);continue
 if 515<=f<=752:cache=P/f'pilot-denoised/{f-514:04}.png'
 elif mode=='full':
  pre=P/f'full-preview-denoised/{f:04}.png'
  if pre.exists() and struct.unpack('>II',pre.read_bytes()[16:24])==(1080,1920):cache=pre
 if cache and cache.exists():
  shutil.copy2(cache,rgb);(P/f'{stage}-frames/{f:04}.cached').touch();print('CACHED',f,flush=True);continue
 s.frame_set(f+1);m=full_pose(f/24);
 for ob in [hair,fur,halfA,halfB,thread]:ob.data.update_tag()
 bpy.context.view_layer.update();s.render.filepath=str(out);clock=time.time();bpy.ops.render.render(write_still=True);(P/f'{stage}-frames/{f:04}.ready').touch();print('FULL_FRAME',f,m,'SECONDS',round(time.time()-clock,3),flush=True)
(P/f'{stage.upper()}_RENDER_DONE').write_text(str(len(frames)))
