from pathlib import Path
import json,math,time,subprocess,bisect,concurrent.futures,argparse
import numpy as np
from PIL import Image,ImageDraw
import paper_base as p
import render_extensions as e
R=Path(__file__).resolve().parent
T=json.loads((R/'timing.json').read_text()); END=T[-1]['end']+.65
START=[x['start'] for x in T]
FPS=24

def cap(im,line,t):
 clean=p.base();im.paste(clean.crop((0,1450,1080,1920)),(0,1450))
 words=line.split();lines=[];current=''
 for w in words:
  candidate=(current+' '+w).strip()
  if p.font(42,True).getlength(candidate)>920:
   lines.append(current);current=w
  else:current=candidate
 if current:lines.append(current)
 for j,s in enumerate(lines):p.text(im,s,540,1518+j*65,42,p.INK,True)
 d=ImageDraw.Draw(im);d.line((74,1730,1006,1730),fill=(202,206,187),width=2);d.line((74,1730,74+932*t/END,1730),fill=p.TEAL,width=4)
 return im

def redroom(t,light=1):
 im=p.scene_room(t);d=ImageDraw.Draw(im)
 # Small red lamp on the same purifier front; illustrative, not an invented PM reading.
 d.rounded_rectangle((735,1060,830,1077),radius=8,fill=(201,65,46) if light else (53,142,132))
 return im

def sensor(t,kind=None,q=0,hold=False):
 im=p.CHAMBER.copy();p.beam(im,t)
 if kind:
  # Particle trajectory stays central x=540; receiver is x=733: no material contact.
  q=max(0,min(1,q)); y=430+760*q;x=540+8*math.sin(q*math.pi*2)
  activation=max(0,1-abs(y-810)/(31 if kind=='water' else 25))
  if activation>0:p.scattering(im,x,810,.5*activation)
  if kind=='water':p.droplet(im,x,y,31)
  else:p.dust(im,x,y,25)
  p.feedback(im,max(activation,.7 if hold and q>.48 else 0),t)
 p.text(im,'빛이 입자에서 흩어져 검출기에 도달',540,1400,25,(74,107,111))
 return im

def mineral_intro(t,q):
 im=e.suspended(min(4,q*4));
 return im

def comparison(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 # Two independently animated pathways, with equal paper materials.
 d.line((540,460,540,1300),fill=(189,196,176),width=2)
 p.text(im,'방울이 빛을 산란',288,410,30,p.INK,True)
 p.text(im,'증발 뒤 남는 입자',795,410,30,p.INK,True)
 p.droplet(im,284,760,106)
 d.line((84,760,178,760),fill=(236,159,65),width=4)
 for k in range(6):
  a=-1.2+k*.5;d.line((284,760,284+205*math.cos(a),760+205*math.sin(a)),fill=(224,152,65),width=3)
 radius=100*(1-p.ease(q))
 if radius>2:p.droplet(im,790,760,radius,int(255*(1-q)))
 for k,(dx,dy) in enumerate(e.PTS):
  x,y=790+dx*(80-45*q),760+dy*(80-45*q)
  if q>.8:e.mineral(im,x,y,8+q*8,k)
  else:d.ellipse((x-4,y-4,x+4,y+4),fill=(210,150,81))
 p.text(im,'광학 신호',284,1130,29,p.TEAL,True);p.text(im,'남은 고체 성분',790,1130,29,p.TEAL,True)
 return im

def reading(t):
 im=p.base();d=ImageDraw.Draw(im)
 p.purifier(im,540,620,1.25)
 d.rounded_rectangle((410,1000,661,1105),radius=18,fill=p.INK)
 p.text(im,'미세먼지 표시',535,1052,32,(238,211,165),True)
 p.text(im,'성분  ·  위험성',540,1270,38,p.INK,True)
 p.text(im,'표시 숫자만으로는 판단할 수 없음',540,1350,27,(83,109,110))
 return im

def scene(t):
 i=max(0,min(len(T)-1,bisect.bisect_right(START,t)-1));row=T[i];local=max(0,t-row['start']);q=min(1,local/row['duration'])
 if i<=1:im=redroom(t,t>2)
 elif i==2:im=e.whole(t)
 elif i==3:im=e.atom(local)
 elif i==4:im=e.macro(local)
 elif i==5:im=redroom(local)
 elif i==6:im=sensor(t)
 elif i==7:im=sensor(t,'dust',.12+.5*q)
 elif i==8:im=sensor(t,'dust',.62+.38*q,True)
 elif i==9:im=sensor(t,'water',.12+.5*q)
 elif i==10:im=sensor(t,'water',.62+.38*q,True)
 elif i==11:
  im=sensor(t,'water',(.2+local*.12)%1,True);p.feedback(im,.6+.4*q,t)
 elif i in (12,13,14):im=e.suspended(min(4,4*(t-T[12]['start'])/(T[14]['end']-T[12]['start'])))
 elif i in (15,16):
  im=e.whole(t-T[15]['start']);p.droplet(im,727,570,107)
  for k,(dx,dy) in enumerate(e.PTS):
   x,y=727+dx*70,570+dy*70;ImageDraw.Draw(im).ellipse((x-4,y-4,x+4,y+4),fill=(210,150,81))
  p.text(im,'점은 녹아 있는 성분의 개념 표시',540,1407,23,(83,109,110))
 elif i==17:im=e.suspended(4.3+q*6.3)
 elif i==18:im=e.watermark(q*5.5)
 elif i==19:im=redroom(t)
 elif i in (20,21):im=comparison(t,0 if i==20 else q)
 elif i==22:im=reading(t)
 elif i==23:im=redroom(t)
 elif i==24:im=e.atom(local)
 else:im=sensor(t,'water',.3+.4*q,True)
 # Preserve restrained paper header; remove old section numbering from reused assets.
 clean=p.base();im.paste(clean.crop((0,185,1080,290)),(0,185))
 return im,i

def frame(t):
 im,i=scene(t)
 # Only narrative viewpoint changes dissolve for 0.25 s; the sensor camera stays fixed.
 cuts={2,3,4,5,6,12,15,17,18,19,20,22,23,24,25}
 elapsed=t-T[i]['start']
 if i in cuts and 0<=elapsed<.25:
  prior,_=scene(T[i]['start']-.001);im=Image.blend(prior,im,p.ease(elapsed/.25))
 return cap(im,T[i]['text'],t)

def render(part):
 a,b=part;out=R/f'part_{a:05}.mp4';start=time.time()
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-threads','2','-crf','21','-pix_fmt','yuv420p',str(out)]
 ff=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for n in range(a,b):ff.stdin.write(frame(n/24).tobytes())
 ff.stdin.close();assert ff.wait()==0
 print(a,b,round(time.time()-start,1),flush=True);return str(out)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--test',action='store_true');args=ap.parse_args()
 if args.stills:
  sheet=Image.new('RGB',(6*216,5*384),p.PAPER)
  for i,row in enumerate(T):
   im=frame(row['start']+row['duration']*.55);im.resize((216,384)).save(R/f'review_{i:02}.jpg');sheet.paste(im.resize((216,384)),((i%6)*216,(i//6)*384))
  sheet.save(R/'contact_sheet.jpg',quality=95)
 elif args.test:
  a=int(T[9]['start']*24);render((a,a+72))
 else:
  total=math.ceil(END*24);parts=[(a,min(total,a+240)) for a in range(0,total,240)]
  with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:files=list(pool.map(render,parts))
  (R/'concat.txt').write_text(''.join("file '"+x+"'\n" for x in files))
  subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(R/'concat.txt'),'-i',str(R/'narration.wav'),'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=9,apad','-c:a','aac','-b:a','160k','-t',str(total/24),'-movflags','+faststart',str(R/'paper_full_v3.mp4')],check=True)
  print('DONE',total/24,flush=True)
