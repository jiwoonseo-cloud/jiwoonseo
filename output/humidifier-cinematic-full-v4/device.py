import bpy,math,os,time
from mathutils import Vector
P=str(__import__('pathlib').Path(__file__).resolve().parent);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,col,metal=0,rough=.3,trans=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;n.inputs['Transmission Weight'].default_value=trans;n.inputs['IOR'].default_value=1.333 if trans else 1.45;return m
white=mat('Warm ceramic housing',(.7,.69,.64),.1,.27);metal=mat('Brushed stainless electrode',(.38,.43,.46),.85,.24);rubber=mat('Gasket',(.025,.035,.036),.05,.55);ceramic=mat('Piezo ceramic',(.7,.59,.34),.12,.4);water=mat('Water',(.2,.48,.56),.05,.1,.8);pcb=mat('Driver PCB',(.025,.13,.09),.15,.35);copper=mat('Copper',(.45,.16,.055),.8,.25);floor=mat('Charcoal tabletop',(.035,.047,.05),.2,.38)
def cyl(name,r,depth,loc,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(m);b=o.modifiers.new('Machined bevel','BEVEL');b.width=.025;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o
def cube(name,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('Edge radius','BEVEL');b.width=.04;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o
def tube(name,pts,r,m):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for q,p in zip(s.points,pts):q.co=(*p,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
# Cut-away reservoir: rear shell, open front, clearly layered transducer at the floor.
verts=[];faces=[]
for j in range(65):
 a=j*math.pi/64
 for z in [.4,2.5]:verts.append((1.25*math.cos(a),1.25*math.sin(a),z))
for j in range(64):faces.append((2*j,2*j+1,2*j+3,2*j+2))
mesh=bpy.data.meshes.new('section_shell');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('Reservoir cutaway wall',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(white);sol=o.modifiers.new('Shell thickness','SOLIDIFY');sol.thickness=.09;bev=o.modifiers.new('Rounded rim','BEVEL');bev.width=.025;bev.segments=3
cyl('Reservoir floor',1.29,.13,(0,0,.4),white)
cyl('Seal',.53,.08,(0,0,.49),rubber)
cyl('Metal mount',.46,.06,(0,0,.55),metal)
disc=cyl('Piezoelectric disc',.39,.05,(0,0,.6),ceramic)
electrode=cyl('Electrode surface',.34,.016,(0,0,.634),metal)
for x in [-.65,.65]:
 cyl('Assembly fastener',.055,.03,(x,.3,.49),metal)
board=cube('Drive board',(0,-.55,.16),(1.6,.8,.08),pcb)
for x in [-.5,-.15,.25]:cube('Driver component',(x,-.55,.25),(.22,.25,.14),rubber)
tube('Power lead',[(.28,-.2,.6),(.42,-.5,.45),(.45,-.75,.28)],.024,copper)
tube('Return lead',[(-.28,-.2,.58),(-.5,-.5,.42),(-.5,-.75,.28)],.024,rubber)
# Water section plane with radial capillary ripples, exaggerated slow visualization.
verts=[];faces=[];N=80
for j in range(N+1):
 for k in range(N+1):
  x=(j/N-.5)*2.4;y=(k/N-.5)*2.4;r=(x*x+y*y)**.5;z=1.65+.025*math.cos(r*35)*math.exp(-r*r*2)
  verts.append((x,y,z))
for j in range(N):
 for k in range(N):
  if ((j/N-.5)*2.4)**2+((k/N-.5)*2.4)**2<1.15**2:
   a=j*(N+1)+k;faces.append((a,a+1,a+N+2,a+N+1))
me=bpy.data.meshes.new('water waves');me.from_pydata(verts,[],faces);me.update();surface=bpy.data.objects.new('Vibrating water surface',me);bpy.context.collection.objects.link(surface);surface.data.materials.append(water)
for p in me.polygons:p.use_smooth=True
# water's cut face shows the depth between transducer and surface.
cube('Water depth cross-section',(0,0,1.12),(2.2,.025,1.03),water)
drops=[]
for k in range(35):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.018+(k%4)*.006,location=(.16*math.sin(k*2.4),.1+.16*math.cos(k*2.4),1.7+(k/35)*1.2));o=bpy.context.object;o.name='Ejected liquid droplet';o.data.materials.append(water);drops.append(o)
# Side cut upper cap and open outlet, visibly separate from the submerged emitter.
cube('Outlet neck',(.0,.6,2.8),(.7,.55,.7),white)
cube('Outlet dark opening',(0,.6,3.17),(.42,.3,.025),rubber)
cube('Table',(0,0,-.16),(200,200,.15),floor)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.09,.12,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,energy,color,size in [('Warm window',(-3,-4,7),950,(1,.77,.48),5),('Cool fill',(4,-1,4),700,(.5,.72,1),4),('Rim',(-1,4,5),1200,(1,.9,.7),3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-7,4.4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.1;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=540;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=4
s.view_settings.view_transform='AgX';s.render.filepath=P+'/review/device_test.png';start=time.time();bpy.ops.wm.save_as_mainfile(filepath=P+'/device.blend');bpy.ops.render.render(write_still=True);print('FRAME_SECONDS',time.time()-start)
