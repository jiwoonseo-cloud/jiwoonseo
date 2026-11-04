import json,subprocess,pathlib,re,math,wave
import numpy as np
P=pathlib.Path('/workspace/work/hair-v3'); O=pathlib.Path('/workspace/jiwoonseo/output/hair-v3');O.mkdir(parents=True,exist_ok=True)
S=json.loads((P/'script.json').read_text()); events=[]; durations=[];offsets=[];off=0
for i,txt in enumerate(S):
 d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(P/f'voice_{i:02}.mp3')]))
 offsets.append(off);durations.append(d)
 words=txt.split();raw=json.loads((P/f'voice_{i:02}.json').read_text())
 assert len(words)==len(raw),(i,len(words),len(raw))
 for w,e in zip(words,raw):
  assert re.sub(r'[^가-힣A-Za-z0-9]','',w)==re.sub(r'[^가-힣A-Za-z0-9]','',e['text']),(w,e)
  events.append(dict(text=w,start=off+e['offset']/1e7,end=off+(e['offset']+e['duration'])/1e7,para=i))
 off+=d

def at(p,word,n=0):
 a=[e['start'] for e in events if e['para']==p and e['text'].startswith(word)]
 return a[n]
# Meaning/action boundaries explicitly tied to spoken words, never paragraph round-robin.
blocks=[(0,'home'),(at(0,'청소'),'flip'),(at(0,'머리카락이'),'reveal'),
(at(1,'고장'),'reveal'),(at(1,'원인은'),'contact'),(at(1,'이'),'wrap'),
(at(2,'롤러가'),'contact'),(at(2,'한'),'wrap'),(at(2,'저항이'),'slide'),(at(2,'짧은'),'short'),(at(2,'길이가'),'remain'),
(at(3,'그래서'),'center'),(at(3,'양끝'),'cap'),(at(3,'로보락'),'bearing'),(at(3,'너무'),'motor'),
(at(4,'그럼'),'suction'),(at(4,'머리카락이'),'wrap'),(at(4,'회전이'),'slide'),(at(4,'그래서'),'remain'),
(at(5,'그래서'),'remove'),(at(5,'로보락은'),'duo'),(at(5,'머리카락을'),'duoflow'),(at(5,'드리미나'),'cut'),(at(5,'공통점은'),'path'),
(at(6,'그런데'),'center'),(at(6,'긴'),'accumulate'),(at(6,'구조가'),'bearing'),(at(6,'회전하는'),'slide'),
(at(7,'결국'),'wrap'),(at(7,'머리카락을'),'slide'),(at(7,'청소가'),'remove'),(at(7,'양끝'),'cap'),(at(7,'일주일에'),'bearing'),(at(7,'끝단에'),'snip'),(at(7,'모터를'),'assemble')]
blocks.sort();timeline=[]
for j,(start,mode) in enumerate(blocks):
 end=blocks[j+1][0] if j+1<len(blocks) else off
 n=max(1,math.ceil((end-start)/3))
 for k in range(n):
  timeline.append(dict(start=start+(end-start)*k/n,end=start+(end-start)*(k+1)/n,action_start=start,action_end=end,mode=mode,angle=k%3,para=next((e['para'] for e in reversed(events) if e['start']<=start),0)))
(P/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2));(P/'words.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
# Complete verbatim captions, preserve original punctuation; word boundaries supplied by TTS.
cues=[];i=0
while i<len(events):
 group=[events[i]];i+=1
 while i<len(events) and events[i]['para']==group[0]['para'] and len(group)<3 and len(' '.join(x['text'] for x in group+[events[i]]))<=14:
  group.append(events[i]);i+=1
 cues.append(dict(start=group[0]['start'],end=events[i]['start'] if i<len(events) else off,text=' '.join(x['text'] for x in group)))
assert ' '.join(c['text'] for c in cues)==' '.join(' '.join(S).split())
def ts(t,ass=False):
 if ass:
  cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(O/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{ts(c["start"])} --> {ts(c["end"])}\n{c["text"]}' for i,c in enumerate(cues))+'\n')
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK KR,60,&H00FFFFFF,&H00FFFFFF,&H00202020,&H85000000,-1,0,0,0,100,100,0,0,1,4,3,5,50,50,0,1
Style: Notice,Noto Sans CJK KR,24,&H00DDDDDD,&H00FFFFFF,&H00202020,&H85000000,0,0,0,0,100,100,0,0,1,1,1,5,30,30,0,1
Style: Label,Noto Sans CJK KR,58,&H005C5CFF,&H00FFFFFF,&H00202020,&H85000000,-1,0,0,0,100,100,0,0,1,2,2,5,30,30,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
a=[header]
for c in cues:a.append(f'Dialogue: 1,{ts(c["start"],True)},{ts(c["end"],True)},Main,,0,0,0,,{{\\pos(540,1267)}}'+c['text']+'\n')
a.append(f'Dialogue: 0,0:00:00.00,{ts(off,True)},Notice,,0,0,0,,{{\\pos(540,1790)}}원리 시각화 연출 · 특정 제품 아님\n')
# Explicit screen flags: locked narration contains unverified brand-specific assertions.
a.append(f'Dialogue: 0,{ts(at(5,"로보락은"),True)},{ts(at(5,"공통점은"),True)},Notice,,0,0,0,,{{\\pos(540,1650)}}브랜드별 회전 방향·절단 방식은 추가 확인 필요\n')
for text,start,end in [('주 한 번',at(7,'일주일에'),at(7,'머리카락이')),('반려동물 집 주 두 번',at(7,'머리카락이'),at(7,'끝단에'))]:a.append(f'Dialogue: 2,{ts(start,True)},{ts(end,True)},Label,,0,0,0,,{{\\pos(540,370)}}'+text+'\n')
(P/'captions.ass').write_text(''.join(a));(O/'script.txt').write_text('\n\n'.join(S)+'\n');(O/'shot-list.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
(P/'voice_concat.txt').write_text('\n'.join(f"file '{P}/voice_{i:02}.mp3'" for i in range(8)))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(P/'voice_concat.txt'),'-ar','48000','-ac','1',str(P/'narration.wav')],check=True)
# Original quiet tonal bed + short custom foley at each edit; no third-party music.
rate=48000;n=round(off*rate);rng=np.random.default_rng(31);bed=np.zeros(n,dtype=np.float32)
t=np.arange(n,dtype=np.float32)/rate
for hz in [110,164.81,220]:bed+=.0008*np.sin(2*np.pi*hz*t)*(.7+.3*np.sin(2*np.pi*.08*t))
for shot in timeline:
 st=round(shot['start']*rate);nn=min(round(.12*rate),n-st);q=np.arange(nn)/rate
 noise=rng.standard_normal(nn);noise=np.convolve(noise,np.ones(9)/9,mode='same');sound=.013*noise*np.exp(-q*33)+.008*np.sin(2*np.pi*(260-600*q)*q)*np.exp(-q*45);bed[st:st+nn]+=sound
with wave.open(str(P/'foley.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes((np.clip(bed,-1,1)*32767).astype('<i2').tobytes())
(P/'metrics.json').write_text(json.dumps(dict(duration=off,cuts=len(timeline),cues=len(cues),durations=durations),indent=2));print('duration',off,'shots',len(timeline),'captions',len(cues))
