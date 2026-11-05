from pathlib import Path
import json,subprocess,math,wave,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;O=P.parent;D=P/'full-denoised';O.mkdir(exist_ok=True)
W=json.loads((P/'words-original.json').read_text());S=json.loads((P/'script.json').read_text());SH=json.loads((P/'full-shots.json').read_text());B=json.loads((P/'blocks.json').read_text());E=json.loads((P/'full-events.json').read_text());T=130.32;FPS=24;N=3128
assert ' '.join(x['text'] for x in W)==' '.join(' '.join(S).split())
chunks=[]
for w in W:
 if chunks and chunks[-1]['para']==w['para'] and len(chunks[-1]['words'])<3 and len(' '.join(chunks[-1]['words']+[w['text']]))<=13 and not chunks[-1]['words'][-1].endswith(('.', '?', '!')):chunks[-1]['words'].append(w['text']);chunks[-1]['end']=w['end']
 else:chunks.append(dict(start=w['start'],end=w['end'],words=[w['text']],para=w['para']))
def ass_t(t):
 q=round(t*100);return f'{q//360000}:{q//6000%60:02}:{q//100%60:02}.{q%100:02}'
def srt_t(t):
 q=round(t*1000);return f'{q//3600000:02}:{q//60000%60:02}:{q//1000%60:02},{q%1000:03}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK KR,58,&H00FFFFFF,&H00FFFFFF,&H00202020,&H85000000,-1,0,0,0,100,100,0,0,1,4,3,5,40,40,0,1
Style: Note,Noto Sans CJK KR,26,&H00FFFFFF,&H00FFFFFF,&H00202020,&H85000000,0,0,0,0,100,100,0,0,1,2,1,5,30,30,0,1
Style: Label,Noto Sans CJK KR,65,&H004C4CFF,&H004C4CFF,&H00202020,&H85000000,-1,0,0,0,100,100,0,0,1,3,2,5,30,30,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
a=[header];sr=[]
for i,x in enumerate(chunks):
 end=min(chunks[i+1]['start']-.005,x['end']+.07) if i+1<len(chunks) else min(T,x['end']+.08)
 end=max(x['end'],end);txt=' '.join(x['words']);sr.append(f'{i+1}\n{srt_t(x["start"])} --> {srt_t(end)}\n{txt}\n')
 a.append(f'Dialogue: 1,{ass_t(x["start"])},{ass_t(end)},Main,,0,0,0,,{{\\pos(540,1267)}}{txt}\n')
# Brand passages and general visualization notice are post-production text.
for lo,hi in [(0,T)]:a.append(f'Dialogue: 0,{ass_t(lo)},{ass_t(hi)},Note,,0,0,0,,{{\\pos(540,1510)}}원리 시각화 연출, 특정 제품 아님\n')
for lo,hi,txt in [(E['weekly'],E.get('weekly_end',E['twice']),'주 1회'),(E['twice'],E['routine_end'],'주 2회')]:a.append(f'Dialogue: 1,{ass_t(lo)},{ass_t(hi)},Label,,0,0,0,,{{\\pos(540,345)}}{txt}\n')
(O/'captions.ass').write_text(''.join(a));(O/'captions.srt').write_text('\n'.join(sr));(O/'script.json').write_text(json.dumps(S,ensure_ascii=False,indent=2));(O/'word-timings.json').write_text(json.dumps(W,ensure_ascii=False,indent=2));(O/'shots.json').write_text(json.dumps(SH,ensure_ascii=False,indent=2))
# Original low-volume sound bed and event-specific Foley; no copyrighted samples.
sr=48000;rng=np.random.default_rng(807);audio=np.zeros((math.ceil(T*sr),2),np.float32)
def add(t,dur,kind,gain):
 n=min(int(dur*sr),len(audio)-int(t*sr));
 if n<=0:return
 x=np.arange(n)/sr;noise=rng.normal(0,1,n);env=np.minimum(1,x/.025)*np.minimum(1,(dur-x)/.08);env=np.maximum(0,env)
 if kind=='whoosh':v=np.convolve(noise,np.ones(31)/31,'same')*np.sin(np.pi*x/dur)**2
 elif kind=='click':v=noise*np.exp(-x*85)+.35*np.sin(2*np.pi*1600*x)*np.exp(-x*65)
 elif kind=='snip':v=noise*np.exp(-x*35)+.2*np.sin(2*np.pi*3400*x)*np.exp(-x*50)
 elif kind=='suction':v=np.convolve(noise,np.ones(8)/8,'same')*.5+.04*np.sin(2*np.pi*210*x)
 else:v=.4*np.sin(2*np.pi*95*x)+.18*np.sin(2*np.pi*190*x)+.1*noise
 v=np.asarray(v*env*gain,np.float32);p=int(t*sr);audio[p:p+n,0]+=v;audio[p:p+n,1]+=v
for sh in SH:
 mode=sh['mode'];dur=sh['end']-sh['start'];kind='click' if mode in ['caps','caps_final','remove','assemble','check','check_again'] else 'suction' if mode in ['short','air_compare','duo_flow','paths'] else 'whoosh';add(sh['start'],min(.28,dur),kind,.075 if kind=='click' else .070)
 if mode in ['core','floor_intro','duo_spin','duo_flow','motor','pinned','migrate_strong','retain']:add(sh['start'],dur,'motor',.018)
 if mode in ['short','duo_flow','paths']:add(sh['start'],dur,'suction',.055)
add(E['snip_close'],.24,'snip',.07)
x=np.arange(len(audio))/sr;bed=(np.sin(2*np.pi*98*x)+.5*np.sin(2*np.pi*146.83*x)+.3*np.sin(2*np.pi*196*x))*.0018;bed*=np.minimum(1,x)*np.minimum(1,T-x);audio+=bed[:,None];audio=np.clip(audio,-1,1)
with wave.open(str(P/'sound-design.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((audio*32767).astype('<i2').tobytes())
if '--prepare' not in __import__('sys').argv:
 missing=[n for n in range(N) if not (D/f'{n:04}.png').exists()];assert not missing,f'Missing {len(missing)} native frames'
 for n in range(N):
  with (D/f'{n:04}.png').open('rb') as f:header=f.read(24)
  assert struct.unpack('>II',header[16:24])==(1080,1920),f'Non-native frame {n}'
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-start_number','0','-i',str(D/'%04d.png'),'-i',str(P/'narration-full.wav'),'-i',str(P/'sound-design.wav'),'-filter_complex',f'[0:v]ass={O}/captions.ass[v];[1:a]volume=1[a];[a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[out]','-map','[v]','-map','[out]','-t',str(T),'-c:v','libx264','-threads','3','-preset','fast','-crf','19','-maxrate','5500k','-bufsize','11000k','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(O/'hair-blender-v4.mp4')],check=True)
 # Every actual second from final encoded movie, with timestamp outside frame.
 C=P/'final-one-second';C.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(O/'hair-blender-v4.mp4'),'-vf',"select='not(mod(n,24))',scale=216:384",'-vsync','vfr',str(C/'%03d.jpg')],check=True)
 frames=sorted(C.glob('*.jpg'));assert len(frames)==131,len(frames);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
 pages=[]
 for page in range(math.ceil(len(frames)/40)):
  batch=frames[page*40:(page+1)*40];canvas=Image.new('RGB',(216*8,410*math.ceil(len(batch)/8)),(24,26,29));draw=ImageDraw.Draw(canvas)
  for j,f in enumerate(batch):
   x=(j%8)*216;y=(j//8)*410;canvas.paste(Image.open(f),(x,y+26));draw.text((x+7,y+3),f'{page*40+j:03d}s',font=font,fill='white')
  name=O/f'contact-sheet-{page+1:02d}.jpg';canvas.save(name,quality=91);pages.append(name)
 # Also deliver a single complete 1-second sheet.
 large=Image.new('RGB',(1728,sum(Image.open(p).height for p in pages)),(24,26,29));cursor=0
 for p in pages:
  page=Image.open(p);large.paste(page,(0,cursor));cursor+=page.height
 large.save(O/'contact-sheet-all.jpg',quality=90)
 print('ASSEMBLED',T,'seconds',len(frames),'one-second samples')
