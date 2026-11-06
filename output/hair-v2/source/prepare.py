import pathlib,json,re,subprocess,csv,shutil,math
import numpy as np,soundfile as sf
from PIL import Image,ImageFilter,ImageDraw
P=pathlib.Path('/workspace/work/hair-v2');O=pathlib.Path('/workspace/jiwoonseo/output/hair-v2');O.mkdir(parents=True,exist_ok=True);(O/'assets').mkdir(exist_ok=True)
S=json.loads((P/'script.json').read_text());sections=[];samples=[];cues=[];offset=0
def ts(t,ass=False):
 if ass:
  m=round(t*100);return f'{m//360000}:{m//6000%60:02}:{m//100%60:02}.{m%100:02}'
 m=round(t*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'
for i,txt in enumerate(S):
 wav=P/f'voice_{i:02}.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/f'edgewb_{i:02}.mp3'),'-ar','48000','-ac','1',str(wav)],check=True)
 a,sr=sf.read(wav);dur=len(a)/sr;samples.append(a);sections.append(dict(section=i+1,start=offset,end=offset+dur,duration=dur,text=txt))
 words=txt.split();meta=json.loads((P/f'edgewb_{i:02}.json').read_text());assert len(words)==len(meta),(i,len(words),len(meta))
 for w,m in zip(words,meta):assert re.sub(r'[^가-힣A-Za-z0-9]','',w)==re.sub(r'[^가-힣A-Za-z0-9]','',m['text']),(w,m)
 j=0
 while j<len(words):
  n=2
  if j+2<len(words) and len(' '.join(words[j:j+3]))<=12:n=3
  if len(words)-(j+n)==1:n+=1
  n=min(n,len(words)-j);start=offset+meta[j]['offset']/1e7;end=min(offset+dur,offset+(meta[j+n-1]['offset']+meta[j+n-1]['duration'])/1e7)
  cues.append(dict(start=start,end=end,text=' '.join(words[j:j+n])));j+=n
 offset+=dur
duration=math.ceil((offset+.4)*24)/24
plans=[['overview','explode','bearing','overview'],['wrap','overview','wrap','slide','wrap','slide'],['wrap','wrap','slide','slide','bearing','separate','separate','slide','bearing'],['caps','bearing','caps','explode','bearing','caps','clean','caps'],['separate','wrap','separate','slide','wrap','separate','slide','bearing'],['duo','duo','duo','duo','separate','duo','slide','duo','duo'],['bearing','caps','slide','separate','bearing','slide','caps','overview'],['slide','wrap','caps','clean','explode','caps','bearing','clean','overview','clean']]
cuts=[]
for sec,plan in zip(sections,plans):
 st=sec['start'];en=sec['end'];n=round((en-st)/2.4);n=max(n,1)
 for j in range(n):
  a=round((st+(en-st)*j/n)*24)/24;b=round((st+(en-st)*(j+1)/n)*24)/24
  mode=plan[j%len(plan)];cuts.append(dict(cut=len(cuts)+1,section=sec['section'],start=a,end=b,duration=b-a,mode=mode,variant=j%3,motion='부품 레이어: '+mode))
cuts[-1]['end']=duration;cuts[-1]['duration']=duration-cuts[-1]['start']
assert all(1.5<=c['duration']<=3 for c in cuts)
# Exact original words, only cue boundaries differ.
assert re.sub(r'\s','', ''.join(c['text'] for c in cues))==re.sub(r'\s','', ''.join(S))
for j in range(1,len(cues)):cues[j]['start']=max(cues[j]['start'],cues[j-1]['end'])
(O/'subtitles.srt').write_text('\n'.join(f"{i+1}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues)))
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Noto Sans CJK KR,62,&H00FFFFFF,&H00FFFFFF,&H00202020,&H90000000,-1,0,0,0,100,100,0,0,1,3,3,5,55,55,0,1
Style: Label,Noto Sans CJK KR,44,&H003A3AE7,&H003A3AE7,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,5,40,40,0,1
Style: Notice,Noto Sans CJK KR,29,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,5,40,40,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
events=[]
for c in cues:events.append(f"Dialogue: 2,{ts(c['start'],True)},{ts(c['end'],True)},Sub,,0,0,0,,{{\\pos(540,1267)\\fad(45,45)}}{c['text']}")
labels={'wrap':'모에 걸림 → 감김','slide':'끝단 · 베어링','separate':'짧은 털 ↑  긴 머리카락 ↻','duo':'짧은 롤러 2개 · 중앙 흡입','caps':'양끝 캡','bearing':'베어링','clean':'끝단 확인','explode':'브러시 분리','overview':'왜 끝단에 감길까'}
for c in cuts:
 events.append(f"Dialogue: 1,{ts(c['start'],True)},{ts(c['end'],True)},Label,,0,0,0,,{{\\pos(540,310)\\fad(100,100)}}{labels[c['mode']]}")
 if c['section'] in [4,6]:events.append(f"Dialogue: 1,{ts(c['start'],True)},{ts(c['end'],True)},Notice,,0,0,0,,{{\\pos(540,1590)}}원리 연출, 특정 제품 아님")
 if c['section']==6:events.append(f"Dialogue: 1,{ts(c['start'],True)},{ts(c['end'],True)},Notice,,0,0,0,,{{\\pos(540,1640)}}기종별 구조 다름 · 브랜드별 적용 상이")
meta=json.loads((P/'edgewb_07.json').read_text());off=sections[7]['start']
week1=next(off+x['offset']/1e7 for x in meta if x['text']=='일주일에');week2=next(off+x['offset']/1e7 for x in meta if x['text']=='두');week_end=min(week2+2.8,duration)
events.append(f'Dialogue: 3,{ts(week1,True)},{ts(week2,True)},Label,,0,0,0,,{{\\pos(540,410)}}주 1회')
events.append(f'Dialogue: 3,{ts(week2,True)},{ts(week_end,True)},Label,,0,0,0,,{{\\pos(540,410)}}머리카락·반려동물 가정 주 2회')
events.append(f'Dialogue: 3,{ts(week1,True)},{ts(week_end,True)},Notice,,0,0,0,,{{\\pos(540,475)}}기종별 사용설명서 · 오염 상태에 따라 조정')
(O/'subtitles.ass').write_text(header+'\n'.join(events)+'\n')
(O/'timeline.json').write_text(json.dumps(cuts,ensure_ascii=False,indent=2));(O/'voice_timing.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2))
with (O/'timeline.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(cuts[0]),lineterminator='\n');w.writeheader();w.writerows(cuts)
(O/'narration.txt').write_text('\n\n'.join(S));shutil.copy(P/'script.json',O/'script.json')
voice=np.concatenate(samples);voice=np.pad(voice,(0,round(duration*48000)-len(voice)));sr=48000;t=np.arange(len(voice))/sr
bed=.005*(np.sin(2*np.pi*98*t)+.4*np.sin(2*np.pi*146.83*t));mix=voice*.90+bed
for c in cuts:
 a=round(c['start']*sr);l=min(int(.16*sr),len(mix)-a);u=np.arange(l)/sr;mix[a:a+l]+=.035*np.sin(2*np.pi*(350*u+1600*u*u))*np.exp(-u*27)
sf.write(P/'mix.wav',np.tanh(mix),sr);sf.write(P/'narration.wav',voice,sr)
shutil.copy('/workspace/generated_images/exec-84c793a3-89e6-490c-9d83-e9399f3d38e6.png',O/'assets/reference.png')
shutil.copy('/workspace/generated_images/exec-d6989cc9-11d5-4927-8339-dde6d2ad036e.png',O/'assets/layers.png')
im=Image.open(O/'assets/layers.png').convert('RGBA')
for n,box in [('housing',(0,0,620,660)),('roller',(620,220,1260,420)),('endcaps',(0,760,610,1160)),('hair',(630,690,1110,1260)),('fur',(980,760,1260,1020))]:im.crop(box).save(O/'assets'/f'{n}.png')
print('DURATION',duration,'CUTS',len(cuts),'CUES',len(cues),'maxchars',max(len(c['text']) for c in cues),flush=True)
