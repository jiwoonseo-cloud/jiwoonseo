"""Unchanged natural-speed narration + directly rendered 3D frames + subtitles.
Also writes contact sheets at exact one-second intervals from the delivered MP4.
"""
import json,subprocess,wave,math,re,csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1];W=BASE.parents[1]/'work/hair-blender-v4';P=json.loads((BASE/'scene-plan.json').read_text());SR=24000
def run(a):subprocess.run(a,check=True)
def stamp(t):
 cs=round(t*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100);return f'{h}:{m:02}:{s:02}.{cs:02}'
def join_video(mode,chunks=4):
 files=[W/f'{mode}-silent-{i}.mp4' for i in range(chunks)]
 for f in files:assert f.exists(),f
 listing=W/f'{mode}-list.txt';listing.write_text(''.join(f"file '{f}'\n" for f in files))
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(W/f'{mode}-joined.mp4')])
def full_audio():
 arrays=[]
 for p in [1,2,3,4,5,7,8]:
  b=subprocess.check_output(['ffmpeg','-v','error','-i',str(BASE/'audio'/f'{p:02}.mp3'),'-f','f32le','-ar',str(SR),'-ac','1','-']);arrays.append(np.frombuffer(b,dtype='<f4').copy())
 voice=np.concatenate(arrays);mix=voice.copy();rng=np.random.default_rng(15)
 # Quiet original ambient bed and individually timed mechanical effects.
 t=np.arange(len(mix))/SR
 for h in [98,146.83,196]:mix+=.0012*np.sin(math.tau*h*t)*(.65+.35*np.sin(math.tau*.12*t))
 for i,c in enumerate(P['cuts']):
  length=.13;tt=np.arange(round(length*SR))/SR;noise=rng.normal(size=len(tt));noise=np.convolve(noise,np.ones(5)/5,mode='same');fx=.010*noise*np.sin(np.pi*np.arange(len(tt))/len(tt))**2
  j=round((c['start']+.06)*SR);count=min(len(fx),len(mix)-j)
  if count>0:mix[j:j+count]+=fx[:count]
 assert abs(mix).max()<1,'Audio clipping'
 with wave.open(str(W/'narration-mix.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((mix*32767).astype('<i2').tobytes())
 return len(mix)/SR
def labels():
 s=(BASE/'subtitles.base.ass').read_text()
 header,events=s.split('[Events]',1)
 header+='Style: Small,Noto Sans CJK KR,29,&H00EEEEEE,&H00EEEEEE,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,1.4,1,5,35,35,0,1\n'
 s=header+'[Events]'+events
 def line(a,b,text,y=1730):return f'Dialogue: 1,{stamp(a)},{stamp(b)},Small,,0,0,0,,{{\\pos(540,{y})}}{text}\n'
 for c in P['cuts']:
  if c['set']=='MECHANISM':s+=line(c['start'],c['end'],'원리 재현 · 설명용 저속')
 s+=line(14.937,18.0,'나선형 브러시의 감김 원리 예시',1650)
 s+=line(36.075,41.488,'반투명 단면',1650)
 s+=line(54.509,61.234,'원리 시각화 연출, 특정 제품 아님',1650)
 s+=line(119.889,126.377,'관리 주기는 기종 설명서와 오염 상태에 따라 달라집니다',1670)
 (BASE/'subtitles.ass').write_text(s)
def contact(video,out,seconds=None):
 tmp=W/(out.stem+'-frames');tmp.mkdir(exist_ok=True)
 run(['ffmpeg','-v','error','-y','-i',str(video),'-vf','select=not(mod(n\\,24)),scale=270:480','-fps_mode','vfr','-q:v','3',str(tmp/'%04d.jpg')])
 fs=sorted(tmp.glob('*.jpg'));cols=5 if len(fs)<=10 else 6;ww=270 if len(fs)<=10 else 180;hh=round(ww*16/9)+26;rows=math.ceil(len(fs)/cols)
 im=Image.new('RGB',(cols*ww,rows*hh),'#151a20');d=ImageDraw.Draw(im)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15 if ww==180 else 20)
 for i,f in enumerate(fs):
  x=(i%cols)*ww;y=(i//cols)*hh;pic=Image.open(f).resize((ww,hh-26));im.paste(pic,(x,y+26));d.text((x+6,y+3),f'{i//60:02}:{i%60:02}',font=font,fill='white')
 im.save(out,quality=92)
def make_test():
 join_video('test');start=json.loads((BASE/'render-log-test-0.json').read_text())['test_start_seconds']
 def seconds(t):h,m,s=t.split(':');return int(h)*3600+int(m)*60+float(s)
 lines=[]
 for line in (BASE/'subtitles.ass').read_text().splitlines():
  if not line.startswith('Dialogue:'):lines.append(line);continue
  fields=line.split(',',9);aa=seconds(fields[1])-start;bb=seconds(fields[2])-start
  if bb<=0 or aa>=10:continue
  fields[1]=stamp(max(0,aa));fields[2]=stamp(min(10,bb));lines.append(','.join(fields))
 (BASE/'test-subtitles.ass').write_text('\n'.join(lines)+'\n')
 run(['ffmpeg','-v','error','-y','-i',str(W/'test-joined.mp4'),'-ss',str(start),'-i',str(W/'narration-mix.wav'),'-vf',f'ass={BASE}/test-subtitles.ass','-map','0:v','-map','1:a','-t','10','-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','128k','-movflags','+faststart',str(BASE/'test-10s.mp4')])
 contact(BASE/'test-10s.mp4',BASE/'test-contact-sheet.jpg')
def make_full(chunks=5):
 join_video('full',chunks);labels()
 run(['ffmpeg','-v','error','-y','-i',str(W/'full-joined.mp4'),'-i',str(W/'narration-mix.wav'),'-vf',f'ass={BASE}/subtitles.ass','-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','20','-maxrate','5M','-bufsize','10M','-g','48','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(BASE/'robot-hair-blender.mp4')])
 contact(BASE/'robot-hair-blender.mp4',BASE/'contact-sheet.jpg')
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--mode',choices=['audio','test','full'],default='audio');a.add_argument('--chunks',type=int,default=5);args=a.parse_args()
 if args.mode=='audio':print('Audio duration',full_audio())
 if args.mode=='test':make_test()
 if args.mode=='full':make_full(args.chunks)
