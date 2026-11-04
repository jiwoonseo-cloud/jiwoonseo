"""Round articulated glove fingertips and expose the actual scissor contact."""
import bpy,math,json,itertools
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1];S=bpy.context.scene;P=json.loads((B/'scene-plan.json').read_text())
for o in bpy.data.objects:
 if not o.name.startswith('Articulated glove finger'):continue
 old=o.data;vs0=old.vertices;x=sum(v.co.x for v in vs0[:10])/10
 # Preserve each finger's length but use a perpendicular rounded cross section.
 L=vs0[30].co.y-.30;L=L/.72
 path=[Vector((x,.14,.01)),Vector((x,.30,.015)),Vector((x,.30+L*.4,-.025)),Vector((x,.30+L*.72,-.12)),Vector((x,.30+L*.83,-.18))]
 tang=(path[-1]-path[-2]).normalized();path.extend([path[-1]+tang*.025,path[-1]+tang*.045,path[-1]+tang*.053]);rads=[.064,.065,.061,.055,.048,.043,.027,.006];vs=[];fs=[];N=16
 for k,pt in enumerate(path):
  t=(path[min(k+1,len(path)-1)]-path[max(0,k-1)]).normalized();u=Vector((1,0,0));v=t.cross(u).normalized()
  for j in range(N):q=pt+rads[k]*(u*math.cos(math.tau*j/N)+v*math.sin(math.tau*j/N));vs.append(q)
 for k in range(len(path)-1):
  for j in range(N):a=k*N+j;b=k*N+(j+1)%N;fs.append((a,b,b+N,a+N))
 fs.extend([tuple(reversed(range(N))),tuple(range((len(path)-1)*N,len(path)*N))]);me=bpy.data.meshes.new('Rounded articulated glove anatomy');me.from_pydata(vs,[],fs)
 for mat in old.materials:me.materials.append(mat)
 o.data=me
 for poly in me.polygons:poly.use_smooth=True
# Keep the bearing and blade contact together, with two genuinely different views.
for c in P['cuts']:
 if c['id'] not in ['P8-C09','P8-C10']:continue
 cam=bpy.data.objects[c['camera']];target=Vector((1.5,-.20,.62));off=Vector((.45,-3.3,1.5) if c['id']=='P8-C09' else (-.8,-3.1,2.1));cam.location=target+off;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;cam.data.dof.focus_distance=off.length
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(B/'hair-animation.blend'),compress=True)
