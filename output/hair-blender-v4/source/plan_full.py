import json,math,pathlib,subprocess
P=pathlib.Path(__file__).resolve().parent;S=json.loads((P/'script.json').read_text());E=json.loads((P/'words.json').read_text())
for i,txt in enumerate(S):
 a=[e for e in E if e['para']==i];assert len(a)==len(txt.split())
 for e,w in zip(a,txt.split()):e['text']=w
(P/'words-original.json').write_text(json.dumps(E,ensure_ascii=False,indent=2))
def at(p,w,n=0):return [e['start'] for e in E if e['para']==p and e['text'].startswith(w)][n]
D=130.320
blocks=[(0,'home'),(at(0,'청소'),'flip'),(at(0,'머리카락이'),'inspect'),(at(1,'원인은'),'floor_intro'),(at(1,'이'),'spool'),(at(2,'롤러가'),'core'),(at(2,'짧은'),'short'),(at(2,'길이가'),'remain'),(at(3,'그래서'),'center'),(at(3,'양끝'),'caps'),(at(3,'로보락'),'check'),(at(3,'너무'),'motor'),(at(4,'그럼'),'air_compare'),(at(4,'머리카락이'),'pinned'),(at(4,'회전이'),'migrate_strong'),(at(4,'그래서'),'retain'),(at(5,'그래서'),'module'),(at(5,'로보락은'),'duo_spin'),(at(5,'머리카락을'),'duo_flow'),(at(5,'드리미나'),'cut'),(at(5,'공통점은'),'paths'),(at(6,'그런데'),'residual'),(at(6,'긴'),'hairy_floor'),(at(6,'구조가'),'check_again'),(at(6,'회전하는'),'xray_migrate'),(at(7,'결국'),'overview'),(at(7,'머리카락을'),'xray_continue'),(at(7,'청소가'),'remove'),(at(7,'양끝'),'caps_final'),(at(7,'일주일에'),'routine'),(at(7,'끝단에'),'snip'),(at(7,'모터를'),'assemble')]
B=[];shots=[]
for j,(begin,mode) in enumerate(blocks):
 end=blocks[j+1][0] if j+1<len(blocks) else D
 b={'start':begin,'end':end,'mode':mode};B.append(b)
 if mode=='core':bounds=[begin,23.102708,25.555,27.555,29.555,end]
 else:
  n=max(1,math.ceil((end-begin)/3));bounds=[begin+(end-begin)*k/n for k in range(n+1)]
 for k in range(len(bounds)-1):shots.append({'start':bounds[k],'end':bounds[k+1],'action_start':begin,'action_end':end,'mode':mode,'angle':k%3,'index':len(shots)})
# Short semantic blocks retain the preceding camera where their view is compatible.
(P/'blocks.json').write_text(json.dumps(B,ensure_ascii=False,indent=2));(P/'full-shots.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2))
(P/'full-events.json').write_text(json.dumps({'inspect_turn':at(1,'고장'),'caps_open':at(3,'캡을'),'caps_final_open':at(7,'캡을'),'remove_start':at(7,'브러시를'),'snip_close':at(7,'잘라'),'snip_pull':at(7,'빼는'),'brand_cut':at(5,'절단'),'duo_suction':at(5,'바로'),'weekly':at(7,'일주일에'),'weekly_end':at(7,'머리카락이'),'twice':at(7,'두'),'routine_end':at(7,'끝단에')},ensure_ascii=False,indent=2))
(P/'concat-voice.txt').write_text('\n'.join(f"file '{P}/voice_{i:02}.mp3'" for i in range(8)))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(P/'concat-voice.txt'),'-ar','48000','-ac','1',str(P/'narration-full.wav')],check=True)
print('duration',D,'frames',math.ceil(D*24),'shots',len(shots),'minimum_cut',min(x['end']-x['start'] for x in shots))
