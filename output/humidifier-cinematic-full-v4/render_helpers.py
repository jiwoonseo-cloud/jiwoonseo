from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
import numpy as np, math,json,subprocess,sys,os,time
from pathlib import Path
P=Path(__file__).resolve().parent; W,H=1080,1920;FPS=24
art=Image.open(P/'assets/cinematic-storyboard.png').convert('RGB')
room=art.crop((0,0,543,965)).resize((W,H),Image.Resampling.LANCZOS)
sensor=art.crop((543,0,1086,965)).resize((W,H),Image.Resampling.LANCZOS)
# Photographic surfaces, matching the source's warm window and cool metal lighting.
table=room.crop((0,1520,1080,1920)).resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(3))
macro=ImageEnhance.Brightness(room).enhance(.35).filter(ImageFilter.GaussianBlur(34))
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fonts={n:ImageFont.truetype(font,n) for n in [24,28,34,42,48,54,64,86]}
def txt(im,s,xy,size=34,fill=(241,238,226),anchor='mm'):
 ImageDraw.Draw(im).text(xy,s,font=fonts[size],fill=fill,anchor=anchor,stroke_width=2 if size<50 else 4,stroke_fill=(16,20,23))
def glow(im,xy,r,color=(245,203,132),strength=.7):
 r=max(2,int(r));yy,xx=np.mgrid[-r:r+1,-r:r+1];alpha=np.exp(-(xx*xx+yy*yy)/(r*r*.18))*strength*220
 a=np.zeros((r*2+1,r*2+1,4),dtype=np.uint8);a[:,:,:3]=color;a[:,:,3]=alpha.astype('uint8');im.paste(Image.fromarray(a), (int(xy[0])-r,int(xy[1])-r),Image.fromarray(a[:,:,3]))
def light(im,a,b,p=1,width=3):
 if p<.005:return
 pad=25;x0=max(0,int(min(a[0],b[0]))-pad);y0=max(0,int(min(a[1],b[1]))-pad);x1=min(W,int(max(a[0],b[0]))+pad);y1=min(H,int(max(a[1],b[1]))+pad)
 layer=Image.new('RGBA',(x1-x0,y1-y0));d=ImageDraw.Draw(layer);aa=(a[0]-x0,a[1]-y0);bb=(b[0]-x0,b[1]-y0)
 d.line([aa,bb],fill=(245,210,149,int(95*p)),width=width*4);layer=layer.filter(ImageFilter.GaussianBlur(5));ImageDraw.Draw(layer).line([aa,bb],fill=(255,227,179,int(150*p)),width=width);im.paste(layer,(x0,y0),layer)
def drop(im,x,y,r,opacity=1,solute=False):
 r=max(3,int(r));x=int(x);y=int(y)
 if x-r<0 or y-r<0 or x+r>=W or y+r>=H:return
 yy,xx=np.mgrid[-r:r+1,-r:r+1];u=xx/r;v=yy/r;q=u*u+v*v;z=np.sqrt(np.maximum(0,1-q));mask=np.clip((1-q)*r/1.5,0,1)
 # Refract the real local background; warm Fresnel rim and soft window reflection.
 src=np.array(im.crop((x-r,y-r,x+r+1,y+r+1)))
 ix=np.clip((r+xx*(.64+.28*q)).astype(int),0,2*r);iy=np.clip((r+yy*(.64+.28*q)).astype(int),0,2*r)
 c=src[iy,ix].astype(float)*(0.88+.14*z[:,:,None]);fres=np.maximum(0,1-z)**4
 shine=np.exp(-((u+.36)**2/.025+(v+.43)**2/.065))
 caust=np.exp(-((u-.37)**2/.035+(v-.55)**2/.045))
 c+=fres[:,:,None]*np.array([50,48,39])+shine[:,:,None]*np.array([170,165,146])+caust[:,:,None]*np.array([90,73,45])
 out=Image.fromarray(np.uint8(np.clip(c,0,255)));alpha=Image.fromarray(np.uint8(mask*opacity*255));im.paste(out,(x-r,y-r),alpha)
 if solute:
  d=ImageDraw.Draw(im)
  for k in range(13):
   a=k*2.4;rr=r*(.18+.54*((k*7%13)/13));px=x+math.cos(a+y*.0004)*rr;py=y+math.sin(a)*rr
   d.ellipse((px-2,py-2,px+2,py+2),fill=(194,184,147))
def mineral(im,x,y,r=18):
 d=ImageDraw.Draw(im);pts=[(x+math.cos(k*.897)*r*(.8+.2*math.sin(k*4)),y+math.sin(k*.897)*r) for k in range(7)];d.polygon(pts,fill=(167,153,127));d.polygon([pts[0],pts[1],(x-2,y+1),pts[-1]],fill=(224,214,189));d.line([pts[2],(x,y),pts[5]],fill=(121,110,91),width=2)
def mist(im,t,travel=False):
 for k in range(42):
  u=(t*.18+k*.024)%1
  if travel:x=275+u*540;y=875+u*330-math.sin(u*math.pi)*440
  else:x=275+math.sin(k*6+t*.3)*u*90;y=875-u*410
  drop(im,x,y,2+(k%4),min(1,u*7,(1-u)*5)*.65)
 # softly blurred aerosol plume, kept below the photo's contrast
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 for k in range(22):
  u=(t*.14+k/22)%1;x=275+(math.sin(k*3)*u*70 if not travel else u*540);y=875-u*400 if not travel else 875+u*330-math.sin(u*math.pi)*440;r=5+u*20;d.ellipse((x-r,y-r,x+r,y+r),fill=(233,233,219,int(15*(1-u))))
 layer=layer.filter(ImageFilter.GaussianBlur(10));im.paste(layer,(0,0),layer)
def red(im,p=1):
 glow(im,(810,800),70,(235,49,26),p*.7);d=ImageDraw.Draw(im);d.rounded_rectangle((769,787,851,807),radius=9,fill=(int(70+170*p),35,22))
def field(im,t,solute=False):
 for k in range(15):
  x=145+(k*177%790)+20*math.sin(t*.5+k);y=340+(k*271%790)-t*10%90
  drop(im,x,y,10+(k%4)*5,.75,solute)
def optical(im,t,mode='water',progress=1):
 E=(240,885);V=(690,1080);cross=(585,885)
 light(im,E,(1018,885),.45*progress,2);glow(im,E,38,strength=.55*progress)
 # One pass every 3.8 s; the particle stays left of the detector and passes the beam.
 u=(t/3.8)%1;y=660+u*455;x=585+22*math.sin(u*math.pi*2)
 pulse=math.exp(-((y-885)/21)**2)
 if mode!='empty':
  if mode=='dust':mineral(im,x,y,13)
  else:drop(im,x,y,27,1)
  for k,a in enumerate([-.7,-1.5,-2.7,2.5,.2]):
   light(im,(x,885),(x+math.cos(a)*110,885+math.sin(a)*110),pulse*.3,2)
  light(im,(x,885),V,pulse*.85,3);glow(im,(x,885),42,strength=pulse*.35);glow(im,V,48,strength=pulse*.8)
 txt(im,'발광부',(235,981),24);txt(im,'수광부',(738,1160),24)
 if mode!='empty':
  txt(im,'빛 산란',(550,547),28) if pulse>.1 else None
  # Modest readout trace responds only when the particle crosses the light.
  d=ImageDraw.Draw(im);pts=[]
  for j in range(250):
   v=t-(249-j)/90;ph=(v/3.8)%1;val=math.exp(-((660+ph*455-885)/21)**2)
   pts.append((760+j,620-val*48))
  d.line(pts,fill=(220,198,155),width=2)
def water_surface(im,t,emit=True,solute=False):
 # Reflect the source room in a shaded, elliptical water surface.
 x0,y0,rw,rh=100,910,440,120
 patch=room.crop((0,250,1080,850)).resize((rw*2+1,rh*2+1)).filter(ImageFilter.GaussianBlur(5))
 arr=np.asarray(patch).astype(float);yy,xx=np.mgrid[-rh:rh+1,-rw:rw+1];rho=(xx/rw)**2+(yy/rh)**2
 shift=(np.sin(xx*.022-t*5+yy*.03)*3).astype(int)
 iy=np.clip(np.arange(rh*2+1)[:,None]+shift,0,rh*2)
 arr=arr[iy,np.arange(rw*2+1)[None,:]]*.50+np.array([7,15,19])
 mask=Image.fromarray(np.uint8(np.clip((1-rho)*20,0,1)*255))
 im.paste(Image.fromarray(np.uint8(np.clip(arr,0,255))),(x0,y0),mask)
 d=ImageDraw.Draw(im)
 d.arc((100,910,980,1150),0,180,fill=(105,113,108),width=3)
 for k in range(4):
  u=(t*.7+k/4)%1;r=35+u*380
  d.arc((540-r,1030-r*.24,540+r,1030+r*.24),185,335,fill=(int(70+55*(1-u)),int(77+52*(1-u)),int(75+48*(1-u))),width=2)
 for k in range(18):
  u=(t*.22+k/18)%1;x=300+k*28+math.sin(k*2)*u*90;y=1020-u*580
  if emit:drop(im,x,y,7+(k%3)*4,min(1,u*8,(1-u)*4),solute)
 txt(im,'설명용 확대 · 시간과 크기 단순화',(540,1800),24)
def frame(i,t,q,caption=''):
 if i in [0,1,5,11,19,22,23]:
  im=room.copy();mist(im,t,i in [5,23]);red(im, max(0,min(1,(t-3)/1)) if i==0 else 1)
  if i in [11,22]:
   d=ImageDraw.Draw(im);d.rounded_rectangle((649,580,955,725),radius=22,fill=(25,31,28));txt(im,str(12+int(76*max(0,min(1,(q-.5)*2)))) if i==11 else '88',(803,641),64,fill=(244,150,115));txt(im,'표시 예시',(803,704),24)
   if i==22:txt(im,'수치 ≠ 성분·위험성',(540,1070),42)
 elif i in [6,7,8,9,10,20,25]:
  im=sensor.copy();optical(im,t+(5.275510204081634 if i==8 else (3.638503401360545 if i==10 else 0)),'empty' if i==6 else ('dust' if i in [7,8] else 'water'),min(1,t/1.5))
  if i==10:txt(im,'성분 검사 기능이 아닙니다',(540,555),34)
  txt(im,'광학 원리 시각화 · 실제 제품 단면 아님',(540,1775),24)
 elif i in [3,15,24]:
  im=macro.copy();water_surface(im,t,True,i==15)
 elif i in [2,4]:
  im=macro.copy();field(im,t)
  drop(im,540,780,140+10*math.sin(t*.4));txt(im,'액체 물방울',(540,1060),42)
 elif i in [12,13,14,16,17,21]:
  im=macro.copy()
  if i in [12,17,21]:
   r=150*(1-.88*min(1,q*1.4));drop(im,540,780,r,max(0,1-q*1.3),True)
   if i!=12 and q>.5:mineral(im,540,780,24)
   if q>.55:txt(im,'물은 증발',(360,560),34)
   if i!=12 and q>.65:txt(im,'남을 수 있는 고체 입자',(540,1020),34)
  else:
   drop(im,540+12*math.sin(t*.2),780,160,1,True)
   txt(im,'녹아 있는 미네랄',(540,1050),34)
   txt(im,'성분 위치를 보여 주는 개념 표현',(540,1775),24)
 elif i==18:
  im=table.copy();d=ImageDraw.Draw(im);a=max(0,1-q*1.7);r=180
  # Wet footprint disappears, solid mineral ring remains on the same surface.
  wet=Image.new('RGBA',(W,H));wd=ImageDraw.Draw(wet);wd.ellipse((250,660,830,920),fill=(63,73,72,int(150*a)));wet=wet.filter(ImageFilter.GaussianBlur(9));im.paste(wet,(0,0),wet)
  for k in range(350):
   angle=k*2.39996;rr=1+.025*math.sin(k*4);x=540+math.cos(angle)*285*rr;y=790+math.sin(angle)*126*rr
   col=int(100+100*min(1,q*1.8));d.ellipse((x-2,y-2,x+2,y+2),fill=(col,col-5,col-16))
  txt(im,'젖은 자국 → 마른 잔류물',(540,1060),34)
 else:im=room.copy()
 txt(im,'원리 시각화 연출 · 특정 제품 아님',(540,110),24)
 if caption:txt(im,caption,(540,1280),54)
 return im

def main():
 timeline=json.load(open(P/'timeline.json'));mode=sys.argv[1] if len(sys.argv)>1 else 'full'
 if mode=='stills':
  for i in [0,3,4,7,9,14,17,18,22,25]:
   row=timeline[i];frame(i,1.9,.55,row['captions'][0]['text']).save(P/f'review/scene_{i:02}.jpg',quality=92)
  return
 if mode.startswith('scene:'):
  chosen=[timeline[int(mode.split(':')[1])]];output=P/f'scene_{chosen[0]["index"]:02d}.mp4'
 elif mode=='test':chosen=[timeline[9]];output=P/'sensor_test.mp4'
 else:chosen=timeline;output=P/'video_silent.mp4'
 cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time()
 for row in chosen:
  i=row['index'];first=round(row['start']*FPS);last=round(row['end']*FPS)
  for n in range(first,last):
   now=n/FPS;local=now-row['start'];q=local/(row['end']-row['start']);cap=next((c['text'] for c in row['captions'] if c['start']<=now<c['end']+.04),'')
   im=frame(i,local,q,cap);proc.stdin.write(im.tobytes())
  print(i,'rendered',round(time.time()-start),flush=True)
 proc.stdin.close();assert proc.wait()==0
if __name__=='__main__':main()
