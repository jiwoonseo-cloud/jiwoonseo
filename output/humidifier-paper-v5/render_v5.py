from pathlib import Path
import math,json,subprocess,time,bisect,concurrent.futures,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import paper_base as p
R=Path(__file__).resolve().parent
W,H,FPS=1080,1920,24
# Remove every inherited slide header and source annotation before rebuilding cached art.
p.base=lambda:p.BG.copy()
p.text=lambda *a,**kw:None
p.CHAMBER=p.chamber()
import render_extensions as e
e.VESSEL=e.vessel()
T=json.loads((R/'timing.json').read_text()) if (R/'timing.json').exists() else []
START=[x['start'] for x in T];END=max(109.37,T[-1]['end']+.25) if T else 115
INK,TEAL=p.INK,p.TEAL
BG=p.BG
TEXT_BOXES=[]
def txt(im,s,x,y,size=34,fill=INK,bold=True,anchor='mm',stroke=0):
 d=ImageDraw.Draw(im);d.text((x,y),s,font=p.font(size,bold),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=INK)

def arrow(im,pts,col=TEAL,width=5):
 d=ImageDraw.Draw(im);d.line(pts,fill=col,width=width,joint='curve');a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-17*math.cos(ang-.42),b[1]-17*math.sin(ang-.42)),(b[0]-17*math.cos(ang+.42),b[1]-17*math.sin(ang+.42))],fill=col)

def dots(im,cx,cy,r,alpha=1):
 d=ImageDraw.Draw(im)
 for k,(dx,dy) in enumerate(e.PTS):
  x,y=cx+dx*r,cy+dy*r;d.ellipse((x-5,y-5,x+5,y+5),fill=(203,137,68))

def paperdrop(im,x,y,r,minerals=False,alpha=255):
 p.droplet(im,x,y,r,alpha)
 if minerals:dots(im,x,y,r*.8)

def clean_stage(im):
 # Reserve a permanent caption safe zone. Artwork never extends into it.
 im.paste(BG.crop((0,1430,W,H)),(0,1430));return im

def lamp(im,x,y,w,q):
 d=ImageDraw.Draw(im);q=p.ease(q)
 d.rounded_rectangle((x-w/2-9,y-37,x+w/2+9,y+37),radius=30,fill=(31,56,61))
 color=tuple(round(a+(b-a)*q) for a,b in zip((63,164,132),(232,52,43)))
 d.rounded_rectangle((x-w/2,y-25,x+w/2,y+25),radius=21,fill=color)
 d.line((x-w*.37,y-11,x+w*.37,y-11),fill=(255,200,159) if q>.5 else (181,233,202),width=6)
 if q>.85:
  for ang in [-2.5,-1.57,-.64]:
   x0=x+math.cos(ang)*w*.7;y0=y+math.sin(ang)*70
   x1=x+math.cos(ang)*w*.83;y1=y+math.sin(ang)*93
   d.line((x0,y0,x1,y1),fill=(210,77,48),width=4)

def intro(t,returning=False):
 im=p.base();d=ImageDraw.Draw(im)
 # Clear large readout on the purifier, no second green lamp underneath.
 p.purifier(im,635,610,1.7);p.humidifier(im,236,1010,.87)
 lamp(im,615,1109,235,1 if returning else (t-2.94)/.4)
 d.line([(744,1115),(903,1220),(968,1220)],fill=INK,width=4,joint='curve')
 d.ellipse((735,1106,753,1124),fill=(229,65,44))
 txt(im,'상태 표시등',968,1270,32,anchor='rm')
 for k in range(17):
  q=(t*.25+k*.061)%1;x=236+q*390;y=945+(664-945)*q-150*math.sin(q*math.pi)
  paperdrop(im,x,y,6+k%3*3,alpha=int(200*min(q*8,(1-q)*5,1)))
 return clean_stage(im)

def pour(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 # Tilted clear vessel and continuous stream ending inside the open reservoir.
 vessel=Image.new('RGBA',(480,500));vd=ImageDraw.Draw(vessel)
 vd.polygon([(95,50),(365,50),(330,410),(130,410)],fill=(192,220,210,255),outline=(48,120,127),width=5)
 vd.polygon([(117,195),(342,195),(323,390),(136,390)],fill=(112,187,187),outline=(43,132,140))
 vd.line((115,75,142,355),fill=(236,247,229),width=9)
 vessel=vessel.rotate(-28,expand=True,resample=Image.Resampling.BICUBIC);im.paste(vessel,(5,250),vessel)
 p.humidifier(im,646,983,1.6)
 for k in range(25):
  u=(t*1.3+k/25)%1;x=427+(646-427)*u+6*math.sin(u*8);y=600+290*u
  paperdrop(im,x,y,8+2*math.sin(k),alpha=210)
 # Lens looks through apparently clear water, without showing dust suddenly appearing.
 d.ellipse((634,352,934,652),fill=(218,232,216),outline=TEAL,width=5)
 d.ellipse((664,382,904,622),fill=(138,196,190),outline=(190,225,210),width=3)
 d.line((886,620,975,704),fill=INK,width=16)
 return clean_stage(im)

def mist(t):
 im=p.base();d=ImageDraw.Draw(im)
 d.ellipse((210,1110,870,1250),fill=(155,201,190),outline=TEAL,width=4)
 d.ellipse((300,1135,780,1210),fill=(28,66,76))
 # Many droplets stream out; lens has a physically separate sampling footprint.
 for k in range(30):
  q=(t*.35+k*.043)%1;paperdrop(im,540+math.sin(k*2.3)*q*260,1150-q*800,6+k%4*5,alpha=int(235*min(1,q*10,(1-q)*5)))
 cx,cy=540,640;d.ellipse((cx-220,cy-220,cx+220,cy+220),outline=TEAL,width=6)
 paperdrop(im,cx-65,cy+44,82);paperdrop(im,cx+90,cy-70,47)
 d.line((708,809,842,943),fill=INK,width=17)
 return clean_stage(im)

def atom(t):return clean_stage(e.atom(t))

def macro(t):
 im=p.base();paperdrop(im,540+12*math.sin(t),745,245)
 for k in range(8):
  ang=k*2.399+t*.2;paperdrop(im,540+370*math.cos(ang),760+460*math.sin(ang),18+k%3*14,alpha=190)
 # Moving specular crescent and isolated round drops distinguish liquid from gas.
 return clean_stage(im)

def entry(t,q):
 im=p.base();p.purifier(im,590,625,1.6)
 # Actual circular intake center from the reused purifier geometry.
 cx,cy=582,676
 d=ImageDraw.Draw(im);d.ellipse((cx-88,cy-88,cx+88,cy+88),outline=(235,156,69),width=7)
 d.line([(cx+75,cy-45),(855,440),(950,440)],fill=INK,width=5,joint='curve')
 d.ellipse((cx+66,cy-54,cx+84,cy-36),fill=(235,156,69))
 txt(im,'먼지 센서 입구',950,390,36,anchor='rm')
 for k in range(7):
  u=(t*.28+k*.14)%1;paperdrop(im,120+u*(cx-120),830-154*u,9+k%3*8,alpha=int(230*min(1,(1-u)*6)))
 # Omit the unrelated grille arrow: only the leader ending at the sensor intake remains.
 return clean_stage(im)

def sensor(t,kind=None,q=0,labels=False,signal=False):
 im=p.CHAMBER.copy();p.beam(im,t);d=ImageDraw.Draw(im)
 if labels:
  txt(im,'광원',184,698,31)
  txt(im,'빛 검출기',870,1365,31)
  d.line([(870,1328),(963,1264),(963,1140),(820,1060)],fill=INK,width=5,joint='curve')
  d.ellipse((810,1050,830,1070),fill=(234,154,68))
 if kind:
  # Slower crossing and faster entry/exit, generated at target timing rather than retimed clips.
  q=max(0,min(1,q))
  if q<.3:y=p.lerp(450,780,p.ease(q/.3))
  elif q<.75:y=p.lerp(780,840,(q-.3)/.45)
  else:y=p.lerp(840,1190,p.ease((q-.75)/.25))
  x=535;radius=32 if kind=='water' else 25;activation=max(0,1-abs(y-810)/radius)
  if activation:p.scattering(im,x,810,.5*activation)
  if kind=='water':paperdrop(im,x,y,radius)
  else:p.dust(im,x,y,radius)
  p.feedback(im,max(activation,.7 if signal and q>.55 else 0),t)
 return clean_stage(im)

def detector(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 # Macro photodetector, orange light becomes a circuit pulse.
 d.polygon([(500,470),(720,500),(850,800),(620,770)],fill=(70,137,143),outline=(30,75,84),width=5)
 d.polygon([(500,470),(530,405),(750,437),(720,500)],fill=(175,217,202),outline=TEAL,width=4)
 for k in range(6):
  x=510+k*35;d.line((x,460,x+24,416),fill=(235,241,211),width=8)
 for k in range(4):
  u=(t*.7+k*.25)%1;x=120+u*435;y=250+u*210
  d.line((x-22,y-12,x+22,y+12),fill=(235,160,62),width=7)
 d.line([(740,745),(850,850),(850,1050),(530,1050)],fill=(81,147,136),width=9,joint='curve')
 d.rounded_rectangle((180,940,550,1180),radius=28,fill=INK)
 points=[]
 for i in range(170):
  x=204+i*1.9;y=1060-58*math.exp(-((i-75-24*math.sin(t*2))/11)**2)
  points.append((x,y))
 d.line(points,fill=(242,175,80),width=5)
 txt(im,'빛 신호 → 전기 신호',540,1320,32)
 return clean_stage(im)

def both_scatter(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 p.dust(im,275,620,65);paperdrop(im,275,1000,76)
 for y in [620,1000]:
  d.line((60,y,210,y),fill=(237,167,70),width=6)
  d.line((275,y,720,810),fill=(237,167,70),width=5)
 d.rounded_rectangle((720,710,930,910),radius=26,fill=(74,136,139),outline=INK,width=4)
 d.line((735,755,735,865),fill=(240,235,193),width=13)
 txt(im,'흩어진 빛을 읽음',820,1020,31)
 return clean_stage(im)

def readout(t,q):
 im=p.base();d=ImageDraw.Draw(im);p.purifier(im,540,600,1.8);lamp(im,520,1136,245,1)
 # Symbolic bars, not a fabricated concentration or a health grade.
 for k in range(5):
  h=40+k*21;d.rounded_rectangle((367+k*66,974-h,410+k*66,974),radius=9,fill=(234,167,75) if q>k*.15 else (162,183,165))
 txt(im,'표시 상승의 개념 표현',540,1370,27,(79,108,109),False)
 return clean_stage(im)

def inspect_drop(t,q,show=False):
 im=p.base();paperdrop(im,540,745,245)
 if show:dots(im,540,745,190)
 d=ImageDraw.Draw(im)
 # Narrow moving light scan reveals the conceptual mineral markers.
 scan=350+380*q;d.line((scan,505,scan,985),fill=(237,175,85),width=3)
 if show:txt(im,'점은 녹아 있는 성분의 개념 표시',540,1275,28,(79,108,109),False)
 return clean_stage(im)

def dissolved(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 d.rounded_rectangle((225,380,855,1200),radius=76,fill=(194,219,205),outline=TEAL,width=4)
 d.rounded_rectangle((250,500,830,1175),radius=51,fill=(122,190,184))
 for k in range(30):
  x=295+(k*97%475)+8*math.sin(t+k);y=560+(k*149%530)+8*math.cos(t*.8+k)
  d.ellipse((x-6,y-6,x+6,y+6),fill=(215,153,79))
 txt(im,'녹아 있는 미네랄',540,1300,32)
 return clean_stage(im)

def emission_with_minerals(t,q):
 im=atom(t);d=ImageDraw.Draw(im)
 for k in range(15):
  x=300+k*34;y=960+58*math.sin(k*1.7+t*.4);d.ellipse((x-4,y-4,x+4,y+4),fill=(203,137,68))
 for k in range(5):
  u=(t*.32+k*.2)%1;x=540+math.sin(k*2.1)*u*165;y=760-u*390
  paperdrop(im,x,y,17,minerals=True)
 return clean_stage(im)

def airborne(t,q):
 im=p.base()
 for k in range(4):
  x=160+k*260+45*math.sin(t*.65+k);y=680+200*math.sin(k*1.5+t*.35)
  paperdrop(im,x,y,100-k*12,minerals=True)
 arrow(im,[(230,1140),(850,1140)],(100,160,149),4)
 return clean_stage(im)

def evaporate(t,q):
 im=p.base();d=ImageDraw.Draw(im);q=p.ease(max(0,min(1,(q-.1)/.75)))
 rad=250*(1-q)+35*q
 if q<.99:paperdrop(im,540,750,rad,alpha=int(255*(1-q*.8)))
 for k,(dx,dy) in enumerate(e.PTS):
  x=540+dx*(rad*.8);y=750+dy*(rad*.8)
  if q<.8:d.ellipse((x-5,y-5,x+5,y+5),fill=(205,143,72))
  else:e.mineral(im,x,y,12+q*14,k)
 if q<.9:
  for a in [-2.5,-1.8,-1.1,-.4]:
   x=540+math.cos(a)*(rad+35);y=750+math.sin(a)*(rad+35)
   arrow(im,[(x,y),(x+math.cos(a)*65,y+math.sin(a)*65)],(107,167,158),3)
 else:txt(im,'고체 입자가 남을 수 있음',540,1170,34)
 return clean_stage(im)

# One exact fixed outline is used by the wet film, its highlight, and the dry deposit.
MARK=[(540+(1+.035*math.sin(a*7))*285*math.cos(a),800+(1+.035*math.sin(a*7))*175*math.sin(a)-44*math.cos(a)) for a in np.linspace(0,math.tau,180)]
def watermark(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 d.polygon([(100,500),(860,370),(992,1110),(230,1240)],fill=(27,68,74),outline=(18,50,58))
 d.polygon([(230,1240),(992,1110),(992,1134),(230,1264)],fill=(55,100,98))
 for k in range(13):d.line((160+k*52,550-k*6,280+k*52,1170-k*8),fill=(34,77,81),width=2)
 q=p.ease(max(0,min(1,(q-.45)/.45)))
 # Uniform thinning of the film keeps the contact line pinned. No mismatched shrinking ellipse.
 film=Image.new('RGBA',(W,H));fd=ImageDraw.Draw(film)
 fd.polygon(MARK,fill=(99,184,185,int(220*(1-q))))
 fd.line(MARK+[MARK[0]],fill=(170,222,204,int(150*(1-q))),width=5)
 im.paste(film,(0,0),film);d=ImageDraw.Draw(im)
 col=tuple(int(p.lerp(a,b,q)) for a,b in zip((63,123,125),(247,239,208)))
 d.line(MARK+[MARK[0]],fill=col,width=7)
 for k in range(0,180,4):
  x,y=MARK[k]
  if q>.25:e.mineral(im,x,y,2+4*q,k)
 txt(im,'물자국에 비유하면',540,1350,28,(79,108,109),False)
 return clean_stage(im)

def compare(t,q,solid=False):
 im=p.base();d=ImageDraw.Draw(im)
 d.line((540,390,540,1180),fill=(178,192,174),width=3)
 paperdrop(im,270,755,120);d.line((60,755,150,755),fill=(237,160,70),width=6)
 for a in [-1.0,-.4,.25,.8]:d.line((270,755,270+205*math.cos(a),755+205*math.sin(a)),fill=(237,160,70),width=4)
 if solid:
  for k,(dx,dy) in enumerate(e.PTS):e.mineral(im,800+dx*80,755+dy*80,24,k)
 else:paperdrop(im,800,755,120,minerals=True)
 txt(im,'물방울의 빛 산란',270,1120,31);txt(im,'증발 후 잔류',800,1120,31)
 return clean_stage(im)

def limits(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 d.rounded_rectangle((260,410,820,900),radius=65,fill=(37,74,81),outline=(21,52,61),width=5)
 for k in range(5):d.rounded_rectangle((330+k*82,800-50-k*40,380+k*82,800),radius=11,fill=(235,165,75))
 txt(im,'측정 신호',540,1000,36)
 txt(im,'성분?    위험성?',540,1160,40)
 txt(im,'표시만으로는 알 수 없음',540,1280,31,(79,108,109),False)
 return clean_stage(im)

def bridge(t,q):
 im=p.base();p.humidifier(im,240,785,1.1);p.purifier(im,810,660,1.1)
 for k in range(6):
  u=(t*.22+k/6)%1;paperdrop(im,250+u*510,680-150*math.sin(u*math.pi),17,alpha=220)
 # Mechanisms linked by the same moving parcel, without a title slide.
 arrow(im,[(350,1200),(700,1200)],(82,149,141),5)
 return clean_stage(im)

def surface(t,q):
 im=p.base();d=ImageDraw.Draw(im)
 d.ellipse((140,680,940,1100),fill=(114,185,181),outline=TEAL,width=5)
 for k in range(6):
  u=(t*.5+k/6)%1;rx=40+u*330;ry=rx*.45;d.ellipse((540-rx,890-ry,540+rx,890+ry),outline=(183,222,205),width=3)
 for k in range(14):
  u=(t*.48+k*.09)%1;paperdrop(im,540+math.sin(k*2.2)*u*180,840-u*520,9+k%3*6)
 return clean_stage(im)

FUNS=[lambda t,q:intro(t),pour,lambda t,q:mist(t),lambda t,q:atom(t),lambda t,q:macro(t),entry,lambda t,q:sensor(t,labels=True),lambda t,q:sensor(t,'dust',(.3*p.ease(t/1.64) if t<1.64 else .3+.45*min(1,(t-1.64)/2.78))),detector,lambda t,q:sensor(t,'water',q),both_scatter,readout,lambda t,q:inspect_drop(t,q),lambda t,q:inspect_drop(t,q,True),dissolved,emission_with_minerals,airborne,evaporate,watermark,lambda t,q:intro(t,True),lambda t,q:compare(t,q),lambda t,q:compare(t,q,True),limits,bridge,surface,lambda t,q:sensor(t,'water',q,signal=True)]

def scene(t):
 i=max(0,min(len(T)-1,bisect.bisect_right(START,t)-1));row=T[i];local=max(0,t-row['start']);q=min(1,local/row['duration']);return FUNS[i](local,q),i

def caption_parts(s):
 # Compact phrase chunks, never overlapping diagrams. Preserve text order verbatim.
 words=s.split();groups=[];cur=[]
 for w in words:
  if cur and (len(' '.join(cur+[w]))>18 or len(cur)>=3):groups.append(' '.join(cur));cur=[]
  cur.append(w)
 if cur:groups.append(' '.join(cur))
 return groups
CAPS=[]
for row in T:
 parts=caption_parts(row['text']);weights=[len(x.replace(' ','')) for x in parts];total=sum(weights);cur=row['start']
 for text,weight in zip(parts,weights):
  end=cur+row['duration']*weight/total;CAPS.append(dict(text=text,start=cur,end=end));cur=end
if (R/'aligned_captions.json').exists():CAPS=json.loads((R/'aligned_captions.json').read_text())
CSTART=[c['start'] for c in CAPS]

def frame(t):
 im,i=scene(t);elapsed=t-T[i]['start']
 # Keep dust/drop sensor chamber cuts steady. Brief dissolves bridge different physical scales.
 if i>0 and i not in (7,13,21) and elapsed<.16:
  old,_=scene(T[i]['start']-.001);im=Image.blend(old,im,p.ease(elapsed/.16))
 d=ImageDraw.Draw(im)
 c=CAPS[max(0,min(len(CAPS)-1,bisect.bisect_right(CSTART,t)-1))]
 txt(im,c['text'],540,1535,58,(255,253,242),True,stroke=4)
 # Small footer is a methodological disclosure, not a slide title.
 txt(im,'원리 시각화 · 축척과 시간 조정',540,1785,22,(101,119,111),False)
 return im

def render(part):
 a,b=part;out=R/f'part_{a:05}.mp4';start=time.time();ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-threads','2','-crf','20','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
 for n in range(a,b):ff.stdin.write(frame(n/24).tobytes())
 ff.stdin.close();assert ff.wait()==0;print(a,b,round(time.time()-start,2),flush=True);return str(out)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--test',action='store_true');args=ap.parse_args()
 if args.stills:
  sheet=Image.new('RGB',(1296,1920),p.PAPER)
  for i,x in enumerate(T):
   im=frame(x['start']+x['duration']*.65);im.save(R/f'review_{i:02}.jpg',quality=94);sheet.paste(im.resize((216,384)),((i%6)*216,(i//6)*384))
  sheet.save(R/'contact_sheet.jpg',quality=95)
 elif args.test:render((0,120))
 else:
  total=math.ceil(END*FPS);parts=[(a,min(total,a+240)) for a in range(0,total,240)]
  with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:files=list(pool.map(render,parts))
  (R/'concat.txt').write_text(''.join("file '"+x+"'\n" for x in files))
  subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(R/'concat.txt'),'-i',str(R/('mix.wav' if (R/'mix.wav').exists() else 'narration.wav')),'-map','0:v','-map','1:a','-c:v','copy','-af','apad','-c:a','aac','-b:a','160k','-t',str(total/24),'-movflags','+faststart',str(R/'paper_full_v5.mp4')],check=True)
  (R/'caption_timing.json').write_text(json.dumps(CAPS,ensure_ascii=False,indent=2));print('DONE',total/24,flush=True)
