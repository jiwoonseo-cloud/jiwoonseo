from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
import numpy as np,math,json,sys,subprocess,time,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent;W,H,FPS=1080,1920,24
spec=importlib.util.spec_from_file_location('legacy',str(P/'render_helpers.py'));L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';fonts={n:ImageFont.truetype(font,n) for n in [24,28,34,42,48,54,64,86,120]}
rows=json.load(open(P/'timeline.json'));meta=json.load(open(P/'projection.json'))
plates={k:Image.open(P/'review'/f'{k}_plate.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.4)) for k in ['device','disc','surface']}
room=L.room;sensor=L.sensor;table=L.table;bg=ImageEnhance.Brightness(room).enhance(.4).filter(ImageFilter.GaussianBlur(22))
def text(im,s,xy,size=34,color=(245,243,235),anchor='mm'):
 ImageDraw.Draw(im).text(xy,s,font=fonts[size],fill=color,anchor=anchor,stroke_width=2 if size<50 else 4,stroke_fill=(12,18,20))
def proj(view,x,y,z):
 m=meta[view];o=np.array(m['origin']);return o+x*(np.array(m['unitx'])-o)+y*(np.array(m['unity'])-o)+z*(np.array(m['unitz'])-o)
def label(im,s,p,q,size=28):
 d=ImageDraw.Draw(im);d.line([tuple(p),tuple(q)],fill=(205,220,219),width=2);d.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=(236,223,188));text(im,s,q,size)
def plume(im,t,travel=False,solute=False):
 low=Image.new('RGBA',(540,960));d=ImageDraw.Draw(low)
 for k in range(135):
  u=(t*.42+k*.00741)%1
  x=275+(math.sin(k*1.7+t*.6)*65*u if not travel else 530*u+math.sin(k*1.7)*18)
  y=875-560*u if not travel else 875-440*math.sin(math.pi*u)+270*u
  r=2+13*u;alpha=int(35*(1-u)**.7*min(1,u*12));d.ellipse(((x-r)/2,(y-r*1.7)/2,(x+r)/2,(y+r*1.7)/2),fill=(236,238,235,alpha))
 low=low.filter(ImageFilter.GaussianBlur(2.5));layer=low.resize((W,H));im.paste(layer,(0,0),layer)
 for k in range(18):
  u=(t*.35+k/18)%1;x=275+(math.sin(k*1.7)*65*u if not travel else 530*u);y=875-560*u if not travel else 875-440*math.sin(math.pi*u)+270*u
  L.drop(im,x,y,3+k%3,.6)
def emission(im,view,t,solute=False):
 # Liquid detaches from surface above submerged transducer, travels through the chimney, exits above it.
 for k in range(52):
  u=(t*.32+k/52)%1;z=1.66+u*2.1;x=.07*math.sin(k*2.4)+max(0,z-3.2)*.22*math.sin(k);y=-.08+.09*math.cos(k*2.4)
  p=proj(view,x,y,z);r=4+(k%4)*2
  if 40<p[0]<1040 and 180<p[1]<1750:
   L.drop(im,*p,r,min(1,u*8,(1-u)*8))
   if solute and r>=8:
    d=ImageDraw.Draw(im);d.ellipse((p[0]-1,p[1]-1,p[0]+1,p[1]+1),fill=(225,197,119))
 # Broad soft mist at the outlet avoids large isolated bubble-only emission.
 if view=='device':
  p=proj(view,0,0,3.35);fog=Image.new('RGBA',(W,H));d=ImageDraw.Draw(fog)
  for k in range(25):
   u=(t*.38+k/25)%1;x=p[0]+math.sin(k*3)*u*70;y=p[1]-u*220;r=8+u*18;d.ellipse((x-r,y-r,x+r,y+r),fill=(238,242,244,int(20*(1-u))))
  fog=fog.filter(ImageFilter.GaussianBlur(9));im.paste(fog,(0,0),fog)
def waves(im,view,t):
 d=ImageDraw.Draw(im)
 for k in range(4):
  u=(t*.8+k/4)%1;r=.05+u*.9;pts=[tuple(proj(view,r*math.cos(a),r*math.sin(a),1.65+.012*math.sin(t*10+a*3))) for a in np.linspace(math.pi,2*math.pi,45)]
  d.line(pts,fill=(int(140+70*(1-u)),int(168+65*(1-u)),int(173+60*(1-u))),width=2)
def device(view,t,phase='emit',solute=False):
 im=plates[view].copy();m=meta[view]
 if phase in ['drive','all']:
  mask=Image.new('L',(W,H)); points=[tuple(proj(view,.42*math.cos(a),.42*math.sin(a),.63)) for a in np.linspace(0,math.pi*2,70)];ImageDraw.Draw(mask).polygon(points,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(1));offset=int((7 if view=='disc' else 3)*math.sin(t*16));im.paste(plates[view],(0,offset),mask)
  L.glow(im,m['board'],90,(111,185,171),.2+.15*math.sin(t*8)**2)
  for k in range(3):
   z=.66+((t*.55+k/3)%1)*.87;p=proj(view,0,0,z);d=ImageDraw.Draw(im);d.arc((p[0]-42,p[1]-13,p[0]+42,p[1]+13),180,360,fill=(188,218,212),width=2)
  L.glow(im,m['disc'],100,(220,191,122),.15+.25*math.sin(t*12)**2)
 if phase in ['water','emit','all']:waves(im,view,t)
 if phase in ['emit','all']:emission(im,view,t,solute)
 if view=='device':
  label(im,'압전 진동판',m['disc'],(805,1460));label(im,'수면',m['surface'],(210,785));label(im,'분무 통로',m['outlet'],(800,490));label(im,'구동 회로',m['board'],(290,1620))
 elif view=='disc':
  label(im,'금속 전극',m['disc'],(810,630));label(im,'압전 진동판',proj(view,.36,0,.6),(805,1080));text(im,'전기 신호 → 빠른 진동',(540,1540),34)
 else:text(im,'수면의 교란 → 물방울 분리',(540,1540),34)
 text(im,'진동·입자 크기 확대 표현',(540,1790),24)
 return im

def optic(t,kind='water',close=False,step='scatter'):
 im=sensor.copy();E=(240,885);V=(690,1080);L.light(im,E,(1018,885),.45,2);L.glow(im,E,40,strength=.45)
 u=max(0,min(1,(t-.35)/2.8));x=580+30*math.sin(u*math.pi*2);y=660+u*440;p=math.exp(-((y-885)/27)**2)
 if step!='empty':
  if kind=='dust':L.mineral(im,x,y,20)
  else:L.drop(im,x,y,34)
  for a in [-2.5,-1.1,-.25,.6,2.5]:L.light(im,(x,885),(x+math.cos(a)*110,885+math.sin(a)*110),p*.28,2)
  L.light(im,(x,885),V,p*.9,3);L.glow(im,V,55,strength=p*.9)
 if close:im=im.crop((340,650,880,1610)).resize((W,H),Image.Resampling.LANCZOS)
 else:
  text(im,'발광부',(230,990),28);text(im,'수광부',(760,1165),28)
 return im

def display(t,q,uncertain=False):
 im=room.copy();L.red(im,1);im=im.crop((470,440,1050,1471)).resize((W,H),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(im);d.rounded_rectangle((190,430,890,900),radius=35,fill=(19,28,28),outline=(92,111,109),width=3)
 text(im,'표시 예시',(540,490),28);num=12+int(76*min(1,max(0,q)))
 text(im,str(num),(540,650),120,color=(244,126,97));text(im,'미세먼지',(540,810),34)
 if uncertain:
  text(im,'성분  ?', (335,1030),42);text(im,'위험성  ?', (750,1030),42)
 return im

def liquid_macro(t,phase='liquid',q=0):
 im=bg.copy();cx=540;cy=800
 if phase=='liquid':
  # Distinct traveling droplets, not a single motionless orb.
  for k in range(7):
   x=160+k*125+25*math.sin(t*.9+k);y=510+((k*133-t*80)%530);L.drop(im,x,y,22+k%3*12,.8)
  L.drop(im,cx+60*math.sin(t*.45),cy-35*t,110)
  text(im,'액체 물방울',(540,1110),42)
 elif phase=='dissolved':
  # Close sectional volume: dispersed solute markers stay within the liquid, never free-floating solids.
  d=ImageDraw.Draw(im);d.rounded_rectangle((150,430,930,1110),radius=50,fill=(38,66,72),outline=(139,177,180),width=3)
  for k in range(40):
   x=205+(k*173%660)+12*math.sin(t+k);y=485+(k*227%540)+12*math.cos(t*.8+k);d.ellipse((x-3,y-3,x+3,y+3),fill=(207,190,136))
  text(im,'물속에 녹아 있는 성분',(540,360),42);text(im,'미네랄 위치를 표시한 확대 모식도',(540,1540),24)
 elif phase=='dry':
  radius=max(8,155*(1-q));L.drop(im,cx,cy,radius,max(0,1-q*1.05));
  if q>.22:
   d=ImageDraw.Draw(im)
   for k in range(16):
    x=cx+math.cos(k*2.4)*radius*.7;y=cy+math.sin(k*2.4)*radius*.7;d.ellipse((x-2,y-2,x+2,y+2),fill=(213,197,153))
  if q>.78:
   L.mineral(im,cx,cy,25);text(im,'남을 수 있는 고체 입자',(540,1070),34)
  elif q>.25:text(im,'물은 증발',(540,1070),34)
 return im

def residue(t,q):
 im=table.copy();layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 # Flattened wet deposit contracts; fine chalky residue appears at original boundary.
 a=max(0,1-q*1.7);d.ellipse((215,630,865,970),fill=(41,55,55,int(a*130)));layer=layer.filter(ImageFilter.GaussianBlur(14));im.paste(layer,(0,0),layer)
 d=ImageDraw.Draw(im)
 for k in range(1100):
  angle=k*2.399963;r=.94+.06*math.sin(k*3.2);x=540+math.cos(angle)*319*r;y=800+math.sin(angle)*165*r;alpha=min(1,max(0,(q-.2)*1.5));c=int(100+120*alpha);d.ellipse((x-1,y-1,x+1,y+1),fill=(c,c-4,c-13))
 text(im,'젖은 자국' if q<.5 else '마른 뒤 남은 자국',(540,1090),42)
 return im

def split_compare(t,q,final=False):
 left=device('device',t,'all',False) if final else optic(t,'water',True)
 right=optic(t+1,'water',True) if final else liquid_macro(t,'dry',q)
 out=Image.new('RGB',(W,H),(16,24,28));out.paste(left.resize((540,960)),(0,400));out.paste(right.resize((540,960)),(540,400));ImageDraw.Draw(out).line((540,400,540,1360),fill=(112,129,128),width=2)
 text(out,'물방울 배출' if final else '물방울의 산란',(270,325),34);text(out,'흩어진 빛 검출' if final else '증발 후 잔류',(810,325),34)
 return out

def frame(i,t,q,now):
 if i==0:
  im=room.copy();plume(im,t);L.red(im,max(0,min(1,(t-2.4)*2)))
 elif i==1:im=display(t,.2)
 elif i==2:
  im=room.copy();plume(im,t+2);im=im.crop((70,390,610,1350)).resize((W,H),Image.Resampling.LANCZOS)
 elif i==3:
  if t<2.15:im=device('disc',t,'drive')
  elif t<3.65:im=device('device',t,'all')
  else:im=device('surface',t,'emit')
 elif i==4:im=liquid_macro(t,'liquid')
 elif i==5:
  im=room.copy();plume(im,t,True);label(im,'흡입구',(820,1100),(820,1450))
 elif i==6:im=optic(t,step='empty')
 elif i==7:im=optic(t,'dust')
 elif i==8:
  im=optic(2,'dust',True);d=ImageDraw.Draw(im);d.rounded_rectangle((140,650,940,1020),radius=24,fill=(16,26,29));pts=[]
  for k in range(int(650*min(1,t/2))):pts.append((210+k,920-170*math.exp(-((k-230)/40)**2)))
  if len(pts)>1:d.line(pts,fill=(235,209,157),width=4)
  text(im,'산란광 신호 → 농도 추정',(540,1100),34)
 elif i==9:im=optic(t+.25,'water',True)
 elif i==10:
  im=Image.new('RGB',(W,H),(17,24,27));a=optic(.8+t*.5,'dust',True);b=optic(.8+t*.5,'water',True);im.paste(a.resize((540,960)),(0,280));im.paste(b.resize((540,960)),(540,280));text(im,'고체 입자',(270,220),34);text(im,'물방울',(810,220),34);text(im,'둘 다 빛을 산란',(540,1430),42)
 elif i==11:im=display(t,max(0,(q-.4)/.6))
 elif i==12:im=liquid_macro(t,'dry',q*.6)
 elif i==13:im=liquid_macro(t,'dissolved',q)
 elif i==14:
  im=plates['surface'].copy();waves(im,'surface',t)
  for k in range(24):
   x=.75*math.sin(k*3.1);y=.7*math.cos(k*3.1);p=proj('surface',x,y,1.55);d=ImageDraw.Draw(im);d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=(205,187,131))
  text(im,'미네랄이 녹아 있는 물',(540,1540),34);text(im,'성분 위치 확대 표시',(540,1790),24)
 elif i==15:im=device('device',t,'all',True)
 elif i==16:
  im=device('surface',t+(rows[15]['end']-rows[15]['start']),'emit',True);text(im,'물방울과 함께 이동',(540,380),42)
 elif i==17:im=liquid_macro(t,'dry',min(1,q*1.2))
 elif i==18:im=residue(t,q)
 elif i==19:
  im=room.copy();L.red(im,1)
 elif i==20:im=split_compare(t,.05)
 elif i==21:im=split_compare(t,q)
 elif i==22:im=display(t,1,True)
 elif i==23:im=split_compare(t,.8,True)
 elif i==24:im=device('surface',t,'emit')
 else:im=optic(t,'water',True)
 caption=next((c['text'] for c in rows[i]['captions'] if c['start']<=now<c['end']+.03),'')
 if caption:text(im,caption,(540,1280),54)
 return im

def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'full'
 if mode=='stills':
  for i in [0,2,3,4,7,8,9,10,13,14,15,16,17,18,21,25]:
   r=rows[i];t=min(1.7,(r['end']-r['start'])*.6);frame(i,t,.5,r['start']+t).save(P/f'review/new_{i:02}.jpg',quality=92)
  return
 chosen=[rows[3]] if mode=='test' else rows;out=P/('device_motion_test.mp4' if mode=='test' else 'v4_silent.mp4')
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-c:v','libx264','-threads','3','-preset','fast','-crf','20','-profile:v','high','-level:v','4.1','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);st=time.time()
 for r in chosen:
  for n in range(round(r['start']*FPS),round(r['end']*FPS)):
   now=n/FPS;t=now-r['start'];im=frame(r['index'],t,t/(r['end']-r['start']),now);proc.stdin.write(im.tobytes())
  print(r['index'],round(time.time()-st,1),flush=True)
 proc.stdin.close();assert proc.wait()==0
if __name__=='__main__':main()
