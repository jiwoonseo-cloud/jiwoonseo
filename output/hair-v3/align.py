"""Align storyboard cues to measured TTS word boundaries (not estimated timings).
The timeline explicitly excludes the user-held paragraph 6. It is not final.
"""
from pathlib import Path
import csv,json,re,subprocess,html
BASE=Path(__file__).resolve().parent
def norm(s):return re.sub('[^가-힣a-zA-Z0-9]','',html.unescape(s))
def duration(f):return float(json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-of','json',str(f)]))['format']['duration'])
def stamp(t,ass=False):
 if ass:
  cs=round(t*100);hh,cs=divmod(cs,360000);mm,cs=divmod(cs,6000);ss,cs=divmod(cs,100)
  return f'{hh}:{mm:02}:{ss:02}.{cs:02}'
 h=int(t//3600);m=int(t//60)%60;s=int(t)%60
 return f'{h:02}:{m:02}:{s:02},{int(t%1*1000):03}'
paras=(BASE/'script-original.txt').read_text().split('\n\n')
voice='ko-KR-HyunsuMultilingualNeural';folder=BASE/'narration'/voice
summary={};candidates={}
for d in (BASE/'narration').iterdir():
 vals={f.stem:round(duration(f),3) for f in sorted(d.glob('*.mp3'))}
 candidates[d.name]={'paragraph_seconds':vals,'total_excluding_6_seconds':round(sum(vals.values()),3),'rate':'+0%','post_speed_adjustment':False}
(BASE/'voice-measurements.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2))
offset=0;caps=[];alignment={};paragraph_offsets={}
for p,text in enumerate(paras,1):
 if p==6:continue
 ev=json.loads((folder/f'{p:02d}.json').read_text());words=re.findall(r'\S+',text)
 # Neither the script nor TTS event stream may lose normalized characters.
 assert norm(''.join(e['text'] for e in ev))==norm(text),(p,'TTS text mismatch')
 spans=[];start=0
 for e in ev:
  tok=norm(e['text']);spans.append((start,start+len(tok),e['offset']/1e7,(e['offset']+e['duration'])/1e7));start+=len(tok)
 alignment[p]=(norm(text),spans);paragraph_offsets[p]=offset
 # Match each original written word to its spoken span, retaining punctuation.
 ww=[];pos=0
 for w in words:
  end=pos+len(norm(w));matches=[s for s in spans if s[1]>pos and s[0]<end]
  assert matches,(p,w)
  ww.append((w,offset+matches[0][2],offset+matches[-1][3]));pos=end
 i=0
 while i<len(ww):
  count=min(2,len(ww)-i)
  if len(ww)-i>=3 and len(' '.join(w[0] for w in ww[i:i+3]))<=13:count=3
  group=ww[i:i+count];caps.append((group[0][1],group[-1][2],' '.join(w[0] for w in group)));i+=count
 offset+=duration(folder/f'{p:02d}.mp3')
with (BASE/'storyboard.csv').open() as f:rows=list(csv.DictReader(f))
for row in rows:
 p=int(row['paragraph'])
 if p==6:continue
 text,spans=alignment[p];cue=norm(row['speech_cue']);idx=text.find(cue)
 if idx<0:
  row['status']='CUE_REQUIRES_MANUAL_ALIGNMENT';continue
 matches=[s for s in spans if s[1]>idx and s[0]<idx+len(cue)]
 row['speech_start_sec']=f'{matches[0][2]:.3f}';row['speech_end_sec']=f'{matches[-1][3]:.3f}'
 row['status']='MEASURED_PARAGRAPH_LOCAL_TIME__NOT_FINAL_CUT_DURATION'
with (BASE/'storyboard-aligned.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
srt='\n\n'.join(f'{i}\n{stamp(a)} --> {stamp(b)}\n{txt}' for i,(a,b,txt) in enumerate(caps,1))+'\n'
(BASE/'narration-excluding-held-6.srt').write_text(srt)
ass='''[Script Info]
Title: PROVISIONAL - paragraph 6 held, not final delivery
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK KR,64,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,2,5,50,50,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
ass+='\n'.join(f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Default,,0,0,0,,{{\\pos(540,1267)}}{txt}' for a,b,txt in caps)+'\n'
(BASE/'narration-excluding-held-6.ass').write_text(ass)
(BASE/'paragraph-offsets-excluding-held-6.json').write_text(json.dumps({'voice':voice,'timeline':'PROVISIONAL CONCATENATION EXCLUDING USER-HELD PARAGRAPH 6','offsets':paragraph_offsets,'duration_seconds':round(offset,3)},ensure_ascii=False,indent=2))
print('Measured',round(offset,3),'seconds,',len(caps),'caption cues. Unmatched storyboard cues:',[r['shot_id'] for r in rows if r['status']=='CUE_REQUIRES_MANUAL_ALIGNMENT'])
