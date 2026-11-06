"""Word-timed full captions, never carrying the next sentence onto this action."""
from pathlib import Path
import re,json,csv
B=Path(__file__).resolve().parents[1]
norm=lambda s:re.sub('[^가-힣a-zA-Z0-9]','',s)
paras=(B/'script-original.txt').read_text().split('\n\n');d=json.loads((B/'source/voice-measurements.json').read_text())['ko-KR-HyunsuMultilingualNeural']['paragraph_seconds'];offset=0;caps=[]
for p,text in enumerate(paras,1):
 if p==6:continue
 ev=json.loads((B/'audio'/f'{p:02}.json').read_text());assert norm(''.join(e['text'] for e in ev))==norm(text)
 spans=[];pos=0
 for e in ev:
  n=len(norm(e['text']));spans.append((pos,pos+n,e['offset']/1e7,(e['offset']+e['duration'])/1e7));pos+=n
 words=[];pos=0
 for word in text.split():
  end=pos+len(norm(word));ss=[s for s in spans if s[1]>pos and s[0]<end];words.append((word,ss[0][2]+offset,ss[-1][3]+offset));pos=end
 i=0
 while i<len(words):
  group=[]
  while i<len(words) and len(group)<3:
   if len(group)>=2 and len(' '.join(g[0] for g in group+[words[i]]))>13:break
   w=words[i];group.append(w);i+=1
   if re.search('[,.!?]$',w[0]):break
  caps.append((group[0][1],group[-1][2],' '.join(g[0] for g in group)))
 offset+=d[f'{p:02}']
def ass_stamp(t):
 c=round(t*100);h,c=divmod(c,360000);m,c=divmod(c,6000);s,c=divmod(c,100);return f'{h}:{m:02}:{s:02}.{c:02}'
def srt_stamp(t):
 c=round(t*1000);h,c=divmod(c,3600000);m,c=divmod(c,60000);s,c=divmod(c,1000);return f'{h:02}:{m:02}:{s:02},{c:03}'
header='''[Script Info]
Title: Robot brush hair mechanism - paragraph 6 held
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
ass=header+'\n'.join(f'Dialogue: 0,{ass_stamp(a)},{ass_stamp(b)},Default,,0,0,0,,{{\\pos(540,1267)}}{t}' for a,b,t in caps)+'\n'
for name in ['subtitles.ass','subtitles.base.ass']:(B/name).write_text(ass)
(B/'subtitles.srt').write_text('\n\n'.join(f'{i}\n{srt_stamp(a)} --> {srt_stamp(b)}\n{t}' for i,(a,b,t) in enumerate(caps,1))+'\n')
assert norm(''.join(t for _,_,t in caps))==norm(''.join(t for i,t in enumerate(paras,1) if i!=6))
print(len(caps),'captions; no sentence-crossing captions; full text preserved excluding held paragraph 6')
