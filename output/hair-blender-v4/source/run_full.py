from pathlib import Path
import os,time,datetime,json,subprocess
P=Path(__file__).resolve().parent
if (P/'full-run.json').exists():
 previous=json.loads((P/'full-run.json').read_text())
 if 'started_epoch' in previous:
  attempts=json.loads((P/'full-run-attempts.json').read_text()) if (P/'full-run-attempts.json').exists() else [];attempts.append(previous);(P/'full-run-attempts.json').write_text(json.dumps(attempts,indent=2))
(P/'full-run.json').write_text(json.dumps({'state':'waiting_for_pilot_review'},indent=2))
while not (P/'PILOT_PASSED.json').exists():time.sleep(.2)
env=dict(os.environ,FRAME_LIST=(P/'full-frame-order.txt').read_text(),PRIORITY_GATE='1');begin=time.time();record={'state':'rendering','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'started_epoch':begin,'frames':3128,'fps':24,'resolution':[1080,1920],'samples':2,'render_threads':4,'denoise_threads':2}
(P/'full-run.json').write_text(json.dumps(record,indent=2));r=subprocess.run(['blender','-b','-t','4','-P',str(P/'full_scene.py'),'--','full'],env=env)
record.update(state='finished' if r.returncode==0 else 'failed',exit_code=r.returncode,elapsed_seconds=time.time()-begin,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(P/'full-run.json').write_text(json.dumps(record,indent=2));raise SystemExit(r.returncode)
