"""Check the evaluated Blender mesh, rather than only scripted control values."""
import bpy,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];S=bpy.context.scene;o=bpy.data.objects['36 separate animated human hairs'];rows=[]
for f in [685,709,757,805,877,924]:
 S.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);mesh=ev.to_mesh();positive=max(v.co.y for v in mesh.vertices)
 rows.append({'frame':f,'time':(f-1)/24,'shape_eval_time':o.data.shape_keys.eval_time,'wind':float(o['wind']),'slide':float(o['slide']),'center_x':o.location.x,'evaluated_max_y':positive,'mesh_vertices':len(mesh.vertices),'hidden':o.hide_render});ev.to_mesh_clear()
assert rows[-1]['evaluated_max_y']<rows[0]['evaluated_max_y']*.65,'The final mesh did not tighten onto the end shaft'
assert rows[-1]['center_x']>rows[0]['center_x']+1,'The evaluated bundle did not migrate to the end'
(B/'native-mesh-check.json').write_text(json.dumps({'native_shape_key_animation':True,'states':rows},indent=2));print('NATIVE MESH CHECK PASSED',rows,flush=True)
