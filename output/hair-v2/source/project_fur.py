import pathlib,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/work/hair-v2')
exec((P/'scene.py').read_text().split('args=sys.argv')[0])
frames=[]
for i in range(18):
 t=i/17;state('separate',t);bpy.context.view_layer.update();pts=[]
 for k in range(8):
  u=(t+k*.125)%1;x=(-1.4+(k%5)*.7)*(1-u)**1.6
  if u<.45:y=-1.95+.09*u/.45;z=.05+1.10*u/.45
  elif u<.8:y=-1.86+1.21*(u-.45)/.35;z=1.15+.35*(u-.45)/.35
  else:y=-.65;z=1.5+.35*(u-.8)/.2
  co=world_to_camera_view(sc,cam,Vector((x,y,z)));pts.append([co.x*720,(1-co.y)*1280,u])
 frames.append(pts)
(pathlib.Path(P)/'fur_projection.json').write_text(json.dumps(frames))
