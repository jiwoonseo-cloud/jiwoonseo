from pathlib import Path
import json,re,difflib,shutil,numpy as np
r=Path(__file__).resolve().parent
asr=json.loads((r/'asr.json').read_text());words=[w for s in asr for w in s['words']]
norm=lambda s:''.join(c for c in s if c.isalnum())
def ts(s):
 h,m,x=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(x)
blocks=re.split(r'\n\s*\n',(r/'supertonic/paragraph_timings.srt').read_text().strip())
rows=[];caps=[];summary=[]
for block in blocks:
 lines=block.splitlines();a,b=map(ts,lines[1].split(' --> '));sentences=lines[2:];target=''.join(norm(s) for s in sentences)
 wds=[w for w in words if w['end']>a and w['start']<b]
 observed='';starts=[];ends=[]
 for w in wds:
  z=norm(w['word']);n=len(z)
  for j,c in enumerate(z):observed+=c;starts.append(w['start']+(w['end']-w['start'])*j/max(1,n));ends.append(w['start']+(w['end']-w['start'])*(j+1)/max(1,n))
 sm=difflib.SequenceMatcher(None,target,observed,autojunk=False);mapping={}
 for match in sm.get_matching_blocks():
  for j in range(match.size):mapping[match.a+j]=match.b+j
 keys=sorted(mapping)
 def moment(k,end=False):
  values=ends if end else starts
  if k in mapping:return values[mapping[k]]
  return float(np.interp(k,keys,[values[mapping[x]] for x in keys]))
 cursor=0
 for s in sentences:
  n=len(norm(s));start=max(a,moment(cursor));end=min(b,moment(cursor+n-1,True));row=dict(index=len(rows),text=s,start=round(start,3),end=round(end,3),duration=round(end-start,3));rows.append(row)
  groups=[];cur=[]
  for word in s.split():
   if cur and (len(' '.join(cur+[word]))>18 or len(cur)>=3):groups.append(' '.join(cur));cur=[]
   cur.append(word)
  if cur:groups.append(' '.join(cur))
  offset=cursor
  for g in groups:
   gn=len(norm(g));caps.append(dict(text=g,start=round(max(a,moment(offset)),3),end=round(min(b,moment(offset+gn-1,True)),3)));offset+=gn
  cursor+=n
 summary.append(dict(paragraph=int(lines[0]),character_match_ratio=sm.ratio(),source='provided paragraph boundaries + local ASR word timing',reference=target,asr=observed))
assert len(rows)==26
for i in range(1,len(rows)):assert rows[i]['start']>=rows[i-1]['end']-.05
shutil.copyfile(r/'narration.wav',r/'melo_fast_narration.wav');shutil.copyfile(r/'timing.json',r/'melo_fast_timing.json')
shutil.copyfile(r/'supertonic/narration_master.wav',r/'narration.wav')
(r/'timing.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));(r/'aligned_captions.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2));(r/'alignment_review.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print('match ratios',[(x['paragraph'],round(x['character_match_ratio'],3)) for x in summary]);print('rows',len(rows),'captions',len(caps));print(rows[:2]);print(rows[-1])
