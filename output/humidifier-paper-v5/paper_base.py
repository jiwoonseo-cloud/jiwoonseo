#!/usr/bin/env python3
"""Original editorial paper-cut animation. No downloaded assets or executable code.
Render: python render_paper.py --render
Preview: python render_paper.py --stills
Dependencies: existing Pillow, NumPy, ffmpeg. Native 1080 x 1920, 24 fps.
"""
import math, os, time, subprocess, argparse, json, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parent
W,H,FPS,DURATION=1080,1920,24,20
PAPER=(240,234,220); INK=(31,51,62); TEAL=(26,121,131); CYAN=(102,201,208); LIGHT=(247,162,82); ORANGE=(214,94,52)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fonts={}
def font(n,b=False):
    key=n,b
    if key not in fonts: fonts[key]=ImageFont.truetype(BOLD if b else FONT,n)
    return fonts[key]
def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,t):return a+(b-a)*t
def pt(x,y):return int(round(x)),int(round(y))
def text(im,s,x,y,size=28,color=INK,bold=False,anchor='mm'):
    ImageDraw.Draw(im).text((x,y),s,fill=color,font=font(size,bold),anchor=anchor)
def bezier(p0,p1,p2,p3,steps=90):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0],(1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]) for t in np.linspace(0,1,steps)]
def curve(im,points,color,width=2):ImageDraw.Draw(im).line(points,fill=color,width=width,joint='curve')
# Deterministic paper, no film-noise flicker.
rng=np.random.default_rng(721)
noise=rng.normal(0,1.8,(H,W,1))
y,x=np.ogrid[:H,:W]
light=(-9*((x-W*.38)/W)**2-7*((y-H*.4)/H)**2)[:,:,None]
arr=np.clip(np.array(PAPER)+noise+light,0,255).astype('uint8')
BG=Image.fromarray(arr)
def base():
    im=BG.copy();d=ImageDraw.Draw(im)
    d.line((72,151,1008,151),fill=(176,182,173),width=1)
    text(im,'물과 빛 사이',74,105,24,INK,True,'lm')
    text(im,'가습기 × 공기청정기',1006,105,22,(86,104,107),False,'rm')
    text(im,'원리 시각화 · 축척과 시간은 이해를 위해 조정',540,1790,20,(91,108,110))
    return im

def shadow(im,bbox,radius=22,offset=(10,15),strength=45):
    lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    b=[bbox[0]+offset[0],bbox[1]+offset[1],bbox[2]+offset[0],bbox[3]+offset[1]]
    d.rounded_rectangle(b,radius=radius,fill=(27,47,50,strength))
    im.paste(Image.alpha_composite(im.convert('RGBA'),lay.filter(ImageFilter.GaussianBlur(18))).convert('RGB'))

def droplet(im,x,y,r,alpha=255,tilt=0):
    # Rounded airborne aerosol droplet, not teardrop. Scalloped paper edge + glass-like fine contour.
    r=max(2,r); sz=int(r*2+12);lay=Image.new('RGBA',(sz,sz));d=ImageDraw.Draw(lay);c=sz/2
    d.ellipse((c-r+2,c-r+4,c+r+2,c+r+4),fill=(12,67,79,int(alpha*.13)))
    d.ellipse((c-r,c-r,c+r,c+r),fill=(*CYAN,int(alpha*.94)),outline=(*TEAL,alpha),width=max(1,int(r*.045)))
    d.ellipse((c-r*.71,c-r*.74,c+r*.68,c+r*.73),outline=(185,233,230,int(alpha*.8)),width=max(1,int(r*.025)))
    d.arc((c-r*.59,c-r*.59,c+r*.55,c+r*.55),180,283,fill=(238,250,239,alpha),width=max(2,int(r*.095)))
    d.arc((c-r*.79,c-r*.77,c+r*.77,c+r*.79),15,95,fill=(25,134,146,int(alpha*.65)),width=max(1,int(r*.04)))
    d.ellipse((c-r*.50,c-r*.52,c-r*.27,c-r*.28),fill=(245,250,236,int(alpha*.94)))
    im.paste(lay,(int(x-c),int(y-c)),lay)

def dust(im,x,y,r):
    d=ImageDraw.Draw(im)
    pts=[(x+math.cos(i*math.pi/8)*r*(.8+.2*math.sin(i*8.1)),y+math.sin(i*math.pi/8)*r*(.8+.2*math.sin(i*7.1))) for i in range(16)]
    d.polygon(pts,fill=(149,127,103),outline=(92,89,80))
    d.line([(x-r*.4,y-r*.2),(x+r*.18,y-r*.5),(x+r*.4,y+r*.25),(x-r*.25,y+r*.4)],fill=(204,184,149),width=3)

def humidifier(im,x,y,s=1):
    d=ImageDraw.Draw(im)
    def b(a):return (x+a[0]*s,y+a[1]*s,x+a[2]*s,y+a[3]*s)
    # paper sculptural object, elliptical water vessel, fine ribs
    d.ellipse(b((-160,270,170,315)),fill=(205,206,187))
    d.rounded_rectangle(b((-126,-55,126,260)),radius=int(45*s),fill=(168,202,198),outline=(47,115,124),width=2)
    d.polygon([(x+90*s,y-40*s),(x+126*s,y-23*s),(x+126*s,y+211*s),(x+90*s,y+240*s)],fill=(116,177,176))
    d.ellipse(b((-126,-84,126,-18)),fill=(218,232,217),outline=(57,125,131),width=2)
    d.ellipse(b((-110,-69,110,-31)),fill=(154,198,191),outline=(93,155,157),width=1)
    d.ellipse(b((-36,-67,36,-38)),fill=INK)
    # water fill line and depth
    d.line((x-107*s,y+64*s,x+105*s,y+64*s),fill=(227,241,226),width=2)
    for i in range(9):
        yy=y+(87+i*16)*s
        curve(im,bezier((x-101*s,yy),(x-20*s,yy+15*s),(x+10*s,yy-12*s),(x+105*s,yy+4*s),30),(126,185,185),1)
    d.rounded_rectangle(b((-66,204,66,230)),radius=12,fill=(226,235,215),outline=(91,150,148),width=1)
    d.ellipse(b((-6,211,6,223)),fill=(59,130,132))
    # lid ribs
    for i in range(15):
        xx=x-100*s+i*14*s
        d.line((xx,y-12*s,xx,y+25*s),fill=(201,222,209),width=2)

def purifier(im,x,y,s=1):
    d=ImageDraw.Draw(im)
    def b(a):return(x+a[0]*s,y+a[1]*s,x+a[2]*s,y+a[3]*s)
    d.ellipse(b((-167,325,186,374)),fill=(205,206,187))
    d.polygon([(x-138*s,y-92*s),(x+112*s,y-112*s),(x+160*s,y-80*s),(x-84*s,y-51*s)],fill=(240,235,219),outline=(118,136,128))
    d.polygon([(x+112*s,y-112*s),(x+160*s,y-80*s),(x+160*s,y+308*s),(x+112*s,y+340*s)],fill=(192,200,184),outline=(118,136,128))
    d.polygon([(x-138*s,y-92*s),(x+112*s,y-112*s),(x+112*s,y+340*s),(x-138*s,y+357*s)],fill=(227,228,208),outline=(118,136,128))
    for ix in range(20):
        xx=x+(-117+ix*11)*s
        d.line((xx,y+111*s,xx,y+292*s),fill=(174,190,176),width=2)
    for i in range(7):
        yy=y+(118+i*25)*s
        d.line((x-124*s,yy,x+101*s,yy-14*s),fill=(197,210,190),width=2)
    # physical sensor in appliance same ring that drives transition
    d.ellipse(b((-63,-21,43,85)),fill=INK,outline=(78,112,111),width=6)
    d.ellipse(b((-49,-7,29,71)),fill=(70,146,148),outline=(172,206,190),width=3)
    d.ellipse(b((-41,1,21,63)),fill=(38,84,91))
    # v5: the status readout is drawn once by the scene, avoiding a second green bar.

def scene_room(t):
    im=base();d=ImageDraw.Draw(im)
    # environmental concentric diagrams are real atmosphere lines, not a frame template
    d.ellipse((-260,250,1240,1550),outline=(214,213,194),width=1)
    d.ellipse((-90,395,1100,1450),outline=(217,215,196),width=1)
    d.line((74,1340,1006,1340),fill=(188,194,177),width=2)
    humidifier(im,267,990,.95);purifier(im,800,765,1.0)
    # three distinct airflow paths, continuously emitted droplets
    paths=[bezier((267,940),(225,555),(620,450),(790,797),120),bezier((263,942),(330,610),(660,585),(790,797),120),bezier((270,940),(415,695),(662,672),(790,797),120)]
    for path in paths:curve(im,path,(168,197,185),1)
    for k in range(16):
        p=((t*.24+k*.079)%1)
        path=paths[k%3];i=min(119,int(p*119));xx,yy=path[i]
        fade=min(1,p*6,(1-p)*8)
        droplet(im,xx,yy,5+(k%4)*2,int(170*fade))
    # hero parcel travels path and is not scene-wide camera-only motion
    p=ease((t-.2)/4.0);path=paths[0];xx,yy=path[min(119,int(p*119))]
    droplet(im,xx,yy,18+4*math.sin(t*.8))
    # tiny physical component annotation
    curve(im,[(852,798),(930,722),(966,722)],(73,112,113),2)
    text(im,'먼지 센서',970,690,25,INK,True,'rm')
    text(im,'초음파 가습기',261,1390,26,(69,101,106))
    text(im,'공기청정기',808,1193,26,(69,101,106))
    return im

# Cached hand-built layered sensor cross section. Main camera stays here so cause is readable.
def chamber():
    im=base();d=ImageDraw.Draw(im)
    # oversized organic slab with die-cut optical chamber
    shadow(im,(91,403,987,1261),38,(14,22),50)
    d.rounded_rectangle((91,403,987,1261),radius=48,fill=(160,185,174),outline=(81,119,120),width=2)
    d.rounded_rectangle((91,403,987,1226),radius=48,fill=(199,211,187),outline=(81,119,120),width=2)
    # fine diagonal fibers on cut edges
    for xx in range(120,960,14):d.line((xx,1227,xx+21,1257),fill=(131,163,153),width=1)
    # screws
    for xx,yy in [(126,442),(950,442),(126,1188),(950,1188)]:
        d.ellipse((xx-9,yy-9,xx+9,yy+9),fill=(227,230,205),outline=(103,137,131),width=1)
        d.line((xx-4,yy+3,xx+4,yy-3),fill=(107,137,128),width=2)
    # main chamber and air path -- gap extends from inlet to outlet
    d.rounded_rectangle((268,453,811,1158),radius=60,fill=(51,87,91),outline=(16,54,63),width=2)
    d.rounded_rectangle((283,465,795,1136),radius=54,fill=(232,228,207),outline=(126,165,158),width=2)
    d.rectangle((429,403,652,485),fill=(78,126,126))
    d.rectangle((447,403,634,492),fill=(232,228,207))
    d.rectangle((429,1114,652,1226),fill=(78,126,126))
    d.rectangle((447,1113,634,1226),fill=(232,228,207))
    # thin breath-like streamlines in duct
    for xx in [472,500,580,609]:
        curve(im,bezier((xx,426),(xx-18,679),(xx+21,936),(xx,1192),80),(199,211,191),1)
    # left emitter chassis with real paper facets, lens and brass rails
    d.polygon([(108,750),(276,750),(295,773),(295,871),(108,871)],fill=(197,112,68),outline=(117,85,61))
    d.polygon([(108,750),(276,750),(295,773),(126,773)],fill=(242,174,103),outline=(147,105,69))
    for xx in range(126,253,15):d.line((xx,785,xx,852),fill=(160,88,60),width=2)
    d.rounded_rectangle((256,775,293,852),radius=8,fill=(105,100,78),outline=(62,74,67),width=2)
    d.ellipse((276,785,306,842),fill=(250,196,117),outline=(117,105,68),width=3)
    d.ellipse((284,793,300,834),fill=(251,222,152))
    # right beam stop, not detector. Distinguish scattering receiver below.
    d.polygon([(787,758),(936,758),(957,780),(957,859),(787,859)],fill=(55,79,77),outline=(31,55,59),width=2)
    for xx in range(803,950,12):d.line((xx,777,xx,842),fill=(82,104,92),width=2)
    # angled detector optical collection cone at bottom-right
    d.polygon([(702,1000),(751,950),(874,1040),(812,1107)],fill=(65,124,131),outline=(27,70,82),width=2)
    d.polygon([(702,1000),(751,950),(764,963),(714,1013)],fill=(155,204,198),outline=(52,112,117))
    d.line((718,998,749,967),fill=(237,246,218),width=8)
    # circuitry is ornamental but follows detector to lower feedback display
    d.line([(842,1082),(913,1138),(913,1313),(793,1313)],fill=(107,153,143),width=6,joint='curve')
    for yy in [1144,1190,1242]:d.ellipse((906,yy-7,920,yy+7),fill=(122,164,151),outline=(60,114,113))
    # below lower edge, screen is a self-contained conceptual readout, no fabricated number
    d.rounded_rectangle((665,1269,807,1352),radius=17,fill=INK,outline=(91,128,122),width=2)
    d.rounded_rectangle((677,1280,795,1340),radius=9,fill=(55,83,82))
    # component labels, deliberately small
    text(im,'광원',184,718,24,INK,True)
    text(im,'빛 검출 센서',825,1170,23,INK,True)
    text(im,'공기 통로',540,353,27,INK,True)
    # arrow breath leading into cutaway
    d.line((540,382,540,416),fill=(56,117,121),width=3)
    d.polygon([(532,406),(540,420),(548,406)],fill=(56,117,121))
    return im
CHAMBER=chamber()

def beam(im,t):
    lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    # narrow light path, not a flash; constant physical beam
    for k in range(15,0,-1):
        d.polygon([(299,810-k*.35),(787,810-k*.8),(787,810+k*.8),(299,810+k*.35)],fill=(246,163,70,int(2+30/k)))
    d.line((300,810,786,810),fill=(248,178,75,170),width=4)
    # moving wave packets make beam travel readable; conceptual visualization
    for i in range(6):
        xx=300+((t*135+i*83)%486)
        d.line((xx,807,xx+15,807),fill=(255,229,157,220),width=3)
    im.paste(lay,(0,0),lay)

def scattering(im,x,y,phase):
    # rays are diagrammatic paths, not physically proportional intensity distributions
    s=math.sin(math.pi*max(0,min(1,phase)))
    if s<=0:return
    lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    rays=[(-170,-110),(-81,-196),(145,-160),(229,-67),(182,84),(-118,124),(-227,45),(183,177)]
    p=ease(min(1,phase*4))
    for i,(dx,dy) in enumerate(rays):
        ex=x+dx*p;ey=y+dy*p
        d.line((x,y,ex,ey),fill=(237,155,62,int(210*s)),width=2+(i%3==0))
        if phase<.8:d.ellipse((ex-3,ey-3,ex+3,ey+3),fill=(250,185,78,int(240*s)))
    # a selected ray reaches the off-axis optical receiver (not main beam stop)
    d.line((x,y,733,983),fill=(247,162,66,int(240*s)),width=4)
    d.ellipse((725,976,741,992),fill=(254,201,95,int(225*s)))
    im.paste(lay,(0,0),lay)

def feedback(im,activation,t):
    d=ImageDraw.Draw(im)
    for i in range(5):
        h=11+i*6
        col=(224,150,70) if i<math.ceil(activation*5) else (85,114,105)
        d.rounded_rectangle((689+i*20,1327-h,700+i*20,1327),radius=3,fill=col)
    if activation>.02:
        route=[(842,1082),(913,1138),(913,1313),(793,1313)]
        path=[]
        for a,b in zip(route,route[1:]):
            for f in np.linspace(0,1,40):path.append((lerp(a[0],b[0],f),lerp(a[1],b[1],f)))
        q=((t*1.5)%1);xx,yy=path[int(q*(len(path)-1))]
        d.ellipse((xx-6,yy-6,xx+6,yy+6),fill=(238,170,79))

def scene_sensor(t):
    im=CHAMBER.copy();beam(im,t)
    # 0–3s empty chamber lets a viewer map the light source and the off-axis receiver.
    # 3–7s dust travels fully through, 9–14.5s water follows the same path.
    dust_y=(lerp(445,790,ease((t-2.4)/2.0)) if t<4.4 else lerp(790,830,ease((t-4.4)/1.1)) if t<5.5 else lerp(830,1175,ease((t-5.5)/1.7)))
    dust_x=535+13*math.sin(t*1.4)
    dust_phase=(t-4.4)/1.1
    water_y=(lerp(436,787,ease((t-8.45)/2.05)) if t<10.5 else lerp(787,833,ease((t-10.5)/1.5)) if t<12.0 else lerp(833,1160,ease((t-12.0)/2.35)))
    water_x=537-9*math.sin(t*.95)
    water_phase=(t-10.5)/1.5
    if 2.4<t<7.2:
        scattering(im,dust_x,810,dust_phase)
        dust(im,dust_x,dust_y,25)
    if 8.45<t<14.35:
        scattering(im,water_x,810,water_phase)
        droplet(im,water_x,water_y,34)
    activate=max(math.sin(math.pi*max(0,min(1,dust_phase))),math.sin(math.pi*max(0,min(1,water_phase))))
    held=max(activate,.66*(1-ease((t-5.5)/1.4)) if 5.5<t<6.9 else 0,.66*(1-ease((t-12)/1.1)) if 12<t<13.1 else 0)
    feedback(im,held,t)
    # permanent little particles, physically moving through rather than changing crops
    for i in range(5):
        yy=430+((t*70+i*137)%778)
        xx=477+(i%3)*58
        ImageDraw.Draw(im).ellipse((xx-1,yy-1,xx+1,yy+1),fill=(169,192,177))
    return im

CAPTIONS=[
 (0,4.8,['이 물방울이 공기청정기의','먼지 센서로 들어갑니다.']),
 (4.8,8.0,['광학식 센서 안에는','빛이 지나가는 통로가 있습니다.']),
 (8.0,11.8,['먼지 같은 입자가 그 빛을 지나면','빛이 사방으로 흩어지고,']),
 (11.8,14.1,['센서는 그 신호를 이용해','먼지 농도를 계산하죠.']),
 (14.1,17.8,['그런데 물방울도','빛을 흩뜨립니다.']),
 (17.8,20.0,['센서가 그 성분까지','검사하는 건 아니거든요.'])]

def captions(im,t):
    for a,b,lines in CAPTIONS:
        if a<=t<b:
            for j,line in enumerate(lines):text(im,line,540,1514+j*67,44,INK,True)
            break
    # fine progress marker: designed as movement not title cards
    d=ImageDraw.Draw(im);d.line((74,1695,1006,1695),fill=(202,206,187),width=2)
    d.line((74,1695,74+932*t/DURATION,1695),fill=TEAL,width=3)


def frame(t):
    if t<4.35:im=scene_room(t)
    elif t<5.2:
        # A physical match move into the sensor opening. It begins at the existing aperture,
        # then paper layers peel outward into the interior view; no unrelated dissolve.
        p=ease((t-4.35)/.85)
        room=scene_room(t)
        sensor=scene_sensor(max(0,t-5.2))
        radius=int(45+1800*p)
        mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask)
        cx=lerp(790,540,p);cy=lerp(797,810,p)
        md.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=255)
        # visible die cut rim follows aperture for material continuity
        im=Image.composite(sensor,room,mask)
        if p<.29:ImageDraw.Draw(im).ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=(72,128,129),width=9)
    else:
        st=t-5.2
        im=scene_sensor(st)
        # v2: hold the explanatory sensor geometry steady while particles and
        # light move. The prior alternating 17% zooms distracted from the path.
        z=1.0
        if z>1.001:
            # crop fixed UI away before camera so typography does not drift
            im=im.transform((W,H),Image.Transform.AFFINE,(1/z,0,540*(1-1/z),0,1/z,810*(1-1/z)),resample=Image.Resampling.BICUBIC)
            clean=base();im.paste(clean.crop((0,0,W,190)),(0,0));im.paste(clean.crop((0,1448,W,H)),(0,1448))
    captions(im,t)
    return im

def make_sound():
    sr=48000;n=int(DURATION*sr);a=np.zeros(n,dtype=np.float64);rng=np.random.default_rng(45)
    # Quiet designed tactile airy ambience. No speech; synthesis is original and local.
    for start,dur,hz,gain in [(0,5.2,90,.018),(4.35,.85,260,.032),(9.3,1.6,700,.027),(15.65,1.6,880,.027)]:
        k=int(start*sr);nn=min(int(dur*sr),n-k);u=np.arange(nn)/sr
        env=np.sin(np.pi*np.minimum(1,u/dur))**2
        a[k:k+nn]+=np.sin(2*np.pi*hz*u)*env*gain
        if start<5:a[k:k+nn]+=rng.normal(0,.018,nn)*env
    a=np.clip(a,-.8,.8)
    with wave.open(str(ROOT/'sound_design.wav'),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes((a*32767).astype('<i2').tobytes())

def render():
    start=time.time();out=ROOT/'paper_sensor_clean_no_voice.mp4'
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(DURATION*FPS):
        im=frame(i/FPS);p.stdin.write(im.tobytes())
        if i%48==0:print(f'{i}/{DURATION*FPS} frames, {time.time()-start:.1f}s',flush=True)
    p.stdin.close();code=p.wait()
    if code:raise RuntimeError(f'ffmpeg exited {code}')
    make_sound()
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(out),'-i',str(ROOT/'sound_design.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(ROOT/'paper_sensor_v2.mp4')],check=True)
    (ROOT/'render_metadata.json').write_text(json.dumps({'width':W,'height':H,'fps':FPS,'duration_seconds':DURATION,'render_wall_seconds':round(time.time()-start,2),'narration':False,'audio':'Original locally synthesized quiet SFX only','style':'Original layered paper cutaway, Pillow/NumPy/FFmpeg'},ensure_ascii=False,indent=2))
    print(f'DONE: {time.time()-start:.1f}s',flush=True)

def stills():
    times=[1.5,4.7,7,9.8,12,16.5]
    sheet=Image.new('RGB',(360*3,640*2),(240,234,220))
    for i,t in enumerate(times):
        im=frame(t);im.save(ROOT/f'frame_{t:04.1f}.png');sheet.paste(im.resize((360,640),Image.Resampling.LANCZOS),((i%3)*360,(i//3)*640))
    sheet.save(ROOT/'contact_sheet.jpg',quality=94)
    print('Stills ready')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--stills',action='store_true');args=ap.parse_args()
    if args.stills:stills()
    if args.render:render()
