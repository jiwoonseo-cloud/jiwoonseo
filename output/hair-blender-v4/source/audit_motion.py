"""Count visible object-motion cuts; this supplements rendered visual review."""
import bpy,json,numpy as np
from pathlib import Path
B=Path(__file__).resolve().parents[1];S=bpy.context.scene;P=json.loads((B/'scene-plan.json').read_text());rows=[]
for cut in P['cuts']:
 obs=[o for o in bpy.data.collections[cut['set']].objects if o.type in {'MESH','CURVE'}];states=[]
 for f in np.linspace(cut['start_frame'],cut['end_frame_exclusive']-1,7).astype(int):
  S.frame_set(int(f));a={}
  for o in obs:
   if not o.hide_render:a[o.name]=np.array(o.matrix_world).reshape(-1)
  coil=bpy.data.objects['36 separate animated human hairs']
  if cut['set']=='MECHANISM':a['hair wind and slide']=np.array([float(coil['wind']),float(coil['slide'])])
  states.append(a)
 changed=set()
 for a,b in zip(states,states[1:]):
  for name in a.keys()&b.keys():
   if np.max(np.abs(a[name]-b[name]))>1e-5:changed.add(name)
 rows.append({'cut':cut['id'],'start':cut['start'],'end':cut['end'],'visible_object_motion':bool(changed),'moving_objects':sorted(changed)})
result={'note':'Object/world transform and hair-control sampling supplements, never replaces actual frame inspection. Static discovery shots may be intentional.','cuts':len(rows),'object_motion_cuts':sum(x['visible_object_motion'] for x in rows),'static_cuts':sum(not x['visible_object_motion'] for x in rows),'rows':rows};(B/'motion-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print({k:v for k,v in result.items() if k!='rows'},flush=True)
