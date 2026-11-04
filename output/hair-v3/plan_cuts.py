"""Plan 1.5–3s continuous-state cuts from measured speech boundaries.
These are a production plan, never a claim that the shots have been rendered.
"""
from pathlib import Path
import csv,json,subprocess,math
BASE=Path(__file__).resolve().parent
voice=BASE/'narration/ko-KR-HyunsuMultilingualNeural'
with (BASE/'storyboard-aligned.csv').open() as f:actions=list(csv.DictReader(f))
out=[]
for p in [1,2,3,4,5,7,8]:
 ev=json.loads((voice/f'{p:02}.json').read_text());duration=float(json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-of','json',str(voice/f'{p:02}.mp3')]))['format']['duration'])
 # Frame-accurate visual end covers the audio, without shortening or stretching it.
 end_frame=math.ceil(duration*24);anchors=sorted(set([0,end_frame]+[round(e['offset']/1e7*24) for e in ev]))
 pa=[r for r in actions if int(r['paragraph'])==p];semantic=set(round(float(r['speech_start_sec'])*24) for r in pa)
 cost=[float('inf')]*len(anchors);prev=[None]*len(anchors);cost[0]=0
 for j in range(1,len(anchors)):
  for i in range(j):
   d=(anchors[j]-anchors[i])/24
   if not 1.5<=d<=3:continue
   c=cost[i]+(d-2.4)**2+.12-(.06 if anchors[j] in semantic else 0)
   if c<cost[j]:cost[j]=c;prev[j]=i
 assert prev[-1] is not None,(p,'No valid cut plan')
 steps=[];j=len(anchors)-1
 while j:steps.append((anchors[prev[j]],anchors[j]));j=prev[j]
 for k,(a,b) in enumerate(reversed(steps),1):
  relevant=[r for r in pa if a/24<=float(r['speech_start_sec'])<b/24]
  inherited=next((r for r in reversed(pa) if float(r['speech_start_sec'])<=a/24),pa[0])
  if not relevant or relevant[0]!=inherited:relevant=[inherited]+relevant
  out.append({'cut_id':f'P{p}-C{k:02}','paragraph':p,'paragraph_start_frame':a,'paragraph_end_frame_exclusive':b,'start_sec':f'{a/24:.3f}','end_sec':f'{b/24:.3f}','duration_sec':f'{(b-a)/24:.3f}','linked_actions':'; '.join(r['shot_id'] for r in relevant),'speech_cues':'; '.join(r['speech_cue'] for r in relevant),'continuity_rule':'Continue the current physical state; never restart the action at this cut','status':'PLANNED_NOT_RENDERED'})
with (BASE/'cut-plan-excluding-held-6.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator='\n');w.writeheader();w.writerows(out)
print(len(out),'planned cuts; all durations within 1.5–3 seconds; none represented as finished video.')
