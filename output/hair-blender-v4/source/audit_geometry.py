"""Supplement visual inspection with a conservative solid-core/floor check."""
import bpy,sys,json,math
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'source'));from kinematics import evaluate
sc=bpy.context.scene;ob=bpy.data.objects['36 separate animated human hairs'];rows=[]
for t in np.linspace(24.288+2.5,24.288+14.10,100):
 sc.frame_set(round(t*24)+1);evaluate(sc)
 co=[]
 for sp in ob.data.splines:
  a=np.empty(len(sp.points)*4,dtype=np.float32);sp.points.foreach_get('co',a);co.append(a.reshape(-1,4)[:,:3])
 xyz=np.concatenate(co);xx=xyz[:,0]+ob.location.x;rr=np.hypot(xyz[:,1],xyz[:,2]);inside=((np.abs(xx)<1.498)&(rr<.218-.001))
 rows.append({'time':round(t,3),'wind':float(ob['wind']),'slide':float(ob['slide']),'center_x':round(ob.location.x,4),'inside_solid_core_points':int(inside.sum()),'lowest_world_z':round(float(xyz[:,2].min())+.34,5)})
assert not any(r['inside_solid_core_points'] for r in rows),'Hair penetrates the solid roller core'
assert min(r['lowest_world_z'] for r in rows)>=.0059,'Hair penetrates contact plane'
(B/'geometry-audit.json').write_text(json.dumps({'tested_points_per_frame':36*96,'sampled_states':len(rows),'core_intersections':0,'floor_intersections':0,'note':'Supplement only; not a substitute for watching the rendered test. Soft nylon contact is intentional.','states':rows},ensure_ascii=False,indent=2))
print('GEOMETRY AUDIT PASSED',len(rows),'states')
