import bpy,math,time,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=str(__import__('pathlib').Path(__file__).resolve().parent);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=720;s.render.resolution_y=1280;s.render.resolution_percentage=100;s.render.threads=3
for o in list(bpy.data.objects):
 if o.name.startswith('Ejected') or o.name in ['Outlet neck','Outlet dark opening']:bpy.data.objects.remove(o,do_unlink=True)
# Make the water depth a transparent section, not an opaque slab.
m=bpy.data.materials.new('Clear water cross section');m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.09;tr=n.new('ShaderNodeBsdfTransparent');bs=n.new('ShaderNodeBsdfDiffuse');bs.inputs[0].default_value=(.12,.35,.4,1);m.node_tree.links.new(tr.outputs[0],mix.inputs[1]);m.node_tree.links.new(bs.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs[0]);o=bpy.data.objects['Water depth cross-section'];o.data.materials.clear();o.data.materials.append(m)
# Open-front discharge chimney, aligned above atomization zone.
vs=[];fs=[]
for j in range(33):
 a=j*math.pi/32
 for z in [1.85,3.3]:vs.append((.48*math.cos(a),.48*math.sin(a),z))
for j in range(32):fs.append((2*j,2*j+1,2*j+3,2*j+2))
me=bpy.data.meshes.new('chimney mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Open mist discharge chimney',me);bpy.context.collection.objects.link(o);o.data.materials.append(bpy.data.materials['Warm ceramic housing']);mo=o.modifiers.new('Wall','SOLIDIFY');mo.thickness=.055
# Small screws and actual electrode lead remain visible in close-ups.
cam=s.camera
views=[('device',(2.4,-7,4.2),(0,0,1.5),4.7),('disc',(1.3,-3,1.7),(0,-.18,.52),2.25),('surface',(1.2,-3.6,3.1),(0,0,1.7),2.8)]
allmeta={}
for name,pos,aim,scale in views:
 cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;bpy.context.view_layer.update()
 pts={}
 for tag,p in [('disc',(0,0,.64)),('surface',(0,0,1.65)),('outlet',(0,0,3.3)),('board',(0,-.55,.16)),('gasket',(.5,0,.51))]:
  v=world_to_camera_view(s,cam,Vector(p));pts[tag]=[v.x*1080,(1-v.y)*1920]
 # General affine projection is exact for this orthographic camera.
 for tag,p in [('origin',(0,0,0)),('unitx',(1,0,0)),('unity',(0,1,0)),('unitz',(0,0,1))]:
  v=world_to_camera_view(s,cam,Vector(p));pts[tag]=[v.x*1080,(1-v.y)*1920]
 allmeta[name]=pts;s.render.filepath=P+'/review/'+name+'_plate.png';t=time.time();bpy.ops.render.render(write_still=True);print('PLATE',name,time.time()-t,flush=True)
json.dump(allmeta,open(P+'/projection.json','w'));bpy.ops.wm.save_as_mainfile(filepath=P+'/device_detail.blend')
