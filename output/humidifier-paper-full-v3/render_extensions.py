#!/usr/bin/env python3
"""Two new original scenes matching paper_sensor_v2. Existing Pillow/NumPy/FFmpeg only."""
import math,time,json,subprocess,argparse,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import paper_base as p
R=Path(__file__).resolve().parent
W,H,FPS=1080,1920,24
INK,TEAL,CYAN,PAPER=p.INK,p.TEAL,p.CYAN,p.PAPER
DURATIONS={'atomization':16,'minerals':18}
CAPTIONS={
'atomization':[(0,3.5,['먼저 저 하얀 분무를','확대해보죠.']),(3.5,9.8,['초음파 가습기는 물을 진동시켜','아주 작은 물방울로 쪼개','날려 보냅니다.']),(9.8,16,['눈앞에 떠 있는 건','기체인 수증기가 아니라,','작은 액체 방울들이에요.'])],
'minerals':[(0,4.2,['물방울에 실린 미네랄도','함께 공기 중으로 나갈 수 있죠.']),(4.2,11.5,['이때 물이 증발하면,','미네랄은 작은 고체 입자로','남을 수 있습니다.']),(11.5,18,['젖어 있을 땐 안 보이던 물자국이,','마르고 나면 하얗게 남는 것처럼요.'])]}

def chapter(im,s):p.text(im,s,75,233,25,(86,111,112),True,'lm')
def finish(im,t,which):
    # All typography remains stationary while artwork reveals and moves.
    clean=p.base(); im.paste(clean.crop((0,0,W,185)),(0,0));im.paste(clean.crop((0,1450,W,H)),(0,1450))
    for a,b,lines in CAPTIONS[which]:
        if a<=t<b:
            for k,line in enumerate(lines):p.text(im,line,540,1510+k*61,40,INK,True)
    d=ImageDraw.Draw(im);d.line((74,1717,1006,1717),fill=(202,206,187),width=2)
    d.line((74,1717,74+932*t/DURATIONS[which],1717),fill=TEAL,width=3)
    return im

def aperture(a,b,q,cx=540,cy=780):
    q=p.ease(q);mask=Image.new('L',(W,H));d=ImageDraw.Draw(mask);r=12+1450*q
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=255)
    im=Image.composite(b,a,mask)
    if q<.38:ImageDraw.Draw(im).ellipse((cx-r,cy-r,cx+r,cy+r),outline=(83,146,143),width=4)
    return im

# Same vessel as the selected sensor scene, at a larger product scale.
def whole(t):
    im=p.base();chapter(im,'01  물이 잘게 나뉘는 순간');d=ImageDraw.Draw(im)
    d.ellipse((-60,360,1120,1480),outline=(216,215,195),width=2)
    d.line((90,1375,990,1375),fill=(190,195,179),width=2)
    p.humidifier(im,540,880,1.55)
    # A plume of particles, not a gas cloud. Continuous trajectories start at nozzle.
    for k in range(35):
        age=((t*.43+k*.067)%1);x=540+math.sin(k*1.31)*age*200;y=794-age*430
        r=3+(k%4)*2;alpha=int(190*min(1,age*9,(1-age)*5));p.droplet(im,x,y,r,alpha)
    p.curve(im,[(695,758),(850,700),(943,700)],(82,126,126),2)
    p.text(im,'액체 물방울',947,667,28,INK,True,'rm')
    p.text(im,'초음파 가습기',540,1399,26,(69,101,106))
    return im

# Static layered, curved, cut-paper reservoir; not a block diagram.
def vessel():
    im=p.base();chapter(im,'01  물이 잘게 나뉘는 순간');d=ImageDraw.Draw(im)
    p.shadow(im,(189,610,888,1270),70,(15,22),45)
    d.rounded_rectangle((191,596,889,1245),radius=85,fill=(110,164,162),outline=(49,108,117),width=3)
    d.rounded_rectangle((212,611,868,1212),radius=71,fill=(205,220,203),outline=(78,132,135),width=2)
    d.rounded_rectangle((247,644,833,1168),radius=55,fill=(235,233,211),outline=(119,167,155),width=2)
    # Continuous open cross-section: the back half-rim is an explicit annulus.
    # No central rounded rectangle is pasted over the ellipse, so no straight
    # rectangular notch or floating strip interrupts the top opening.
    d.rounded_rectangle((236,606,846,1168),radius=55,fill=(230,232,210))
    d.rectangle((236,606,846,720),fill=(230,232,210))
    outer=[(540+349*math.cos(a),606+44*math.sin(a)) for a in np.linspace(math.pi,2*math.pi,100)]
    inner=[(540+304*math.cos(a),606+28*math.sin(a)) for a in np.linspace(math.pi,2*math.pi,100)]
    d.polygon(outer+inner[::-1],fill=(215,231,213))
    d.line(outer,fill=(60,123,128),width=3)
    d.line(inner,fill=(92,153,150),width=2)
    # cut edge fibers along base; reference paper construction
    for x in range(229,855,12):d.line((x,1213,x+19,1238),fill=(149,186,174),width=1)
    # top rim ends leave central cross-sectional face exposed
    d.polygon([(191,601),(236,610),(236,1156),(264,1200),(217,1199),(191,1161)],fill=(176,206,189),outline=(72,133,132))
    d.polygon([(846,609),(889,601),(889,1160),(859,1200),(815,1200),(846,1157)],fill=(109,169,166),outline=(55,119,124))
    # base circuitry/wires are attached to the transducer
    d.line([(540,1189),(540,1260),(710,1260),(710,1317)],fill=(102,153,142),width=5)
    d.rounded_rectangle((645,1301,779,1360),radius=13,fill=(213,219,195),outline=(86,139,129),width=2)
    for x in [664,685,706,727,748]:d.line((x,1317,x,1345),fill=(121,165,145),width=2)
    return im
VESSEL=vessel()

def atom(t):
    im=VESSEL.copy();d=ImageDraw.Draw(im)
    # Water level and animated surface waves. Emission originates at surface, not piezo disc.
    surface=[]
    for x in range(257,825,3):
        dx=x-540;crest=61*math.exp(-(dx/37)**2)*(0.82+.18*math.sin(t*6))
        y=833+5*math.sin(dx*.045-t*7)-crest
        surface.append((x,y))
    d.polygon(surface+[(821,1126),(259,1126)],fill=(132,190,188))
    d.line(surface,fill=(42,129,139),width=4)
    d.line([(x,y+11) for x,y in surface],fill=(194,227,213),width=2)
    # Layering through water: curved wavefronts travelling toward the surface.
    for k in range(7):
        q=((t*.7+k/7)%1);y=1126-q*275;half=38+q*220
        pts=p.bezier((540-half,y),(450,y-20),(630,y-20),(540+half,y),55)
        p.curve(im,pts,(171,216,201),2)
    # piezo ceramic disc attached under water, mechanical displacement exaggerated & disclosed.
    dy=2*math.sin(t*17)
    d.ellipse((410,1110+dy,670,1177+dy),fill=(173,103,66),outline=(117,82,61),width=2)
    d.ellipse((410,1095+dy,670,1154+dy),fill=(242,172,102),outline=(145,105,71),width=2)
    d.ellipse((434,1104+dy,646,1143+dy),fill=(246,211,151),outline=(169,128,83),width=2)
    for r in [17,29,41]:d.ellipse((540-r,1124-r*.24+dy,540+r,1124+r*.24+dy),outline=(184,145,95),width=1)
    # droplets pinch off the crest and travel upward into the plume.
    for k in range(23):
        q=((t*.52+k*.113)%1);x=540+math.sin(k*2.17)*q*208;y=771-q*425
        alpha=int(215*min(1,q*12,(1-q)*6));p.droplet(im,x,y,4+(k%4)*2.7,alpha)
    # Hero drop guides camera into the next shot.
    q=(t*.37)%1;p.droplet(im,547+q*48,767-q*360,13+q*9,int(245*min(1,q*9)))
    p.curve(im,[(660,1136),(808,1280),(953,1280)],(79,125,124),2)
    p.text(im,'초음파 진동판',955,1244,26,INK,True,'rm')
    p.text(im,'진동을 받은 물의 표면',540,1410,25,(77,111,113))
    return im

def macro(t):
    im=p.base();chapter(im,'01  물이 잘게 나뉘는 순간');d=ImageDraw.Draw(im)
    # Continuous orbital arrangement through a shallow illustrative plane, gentle parallax.
    d.ellipse((80,335,1000,1320),outline=(210,213,192),width=2)
    p.droplet(im,540+18*math.sin(t*.65),786-13*math.cos(t*.6),222)
    for k in range(9):
        a=k*2.399+t*.11;rad=326+35*math.sin(k);x=540+rad*math.cos(a);y=814+rad*1.18*math.sin(a)
        p.droplet(im,x,y,10+(k%4)*8,165+(k%2)*50)
    p.curve(im,[(700,669),(869,570),(956,570)],(81,128,127),2)
    p.text(im,'작은 액체 방울',957,529,29,INK,True,'rm')
    p.text(im,'보이는 흰 분무는 물방울의 모임',540,1360,27,(73,109,113))
    return im

def atom_frame(t):
    if t<2.7:im=whole(t)
    elif t<3.6:im=aperture(whole(t),atom(t-3.6),(t-2.7)/.9,540,810)
    elif t<9.25:im=atom(t-3.6)
    elif t<10.05:im=aperture(atom(t-3.6),macro(t-10.05),(t-9.25)/.8,550,610)
    else:im=macro(t-10.05)
    return finish(im,t,'atomization')

# Two marker constellations: same matter before/after; markers are explicitly conceptual.
PTS=[(-.57,-.28),(-.25,-.58),(.15,-.53),(.52,-.19),(.51,.31),(.17,.54),(-.23,.38),(-.51,.12),(.07,-.09)]
def mineral(im,x,y,r,rot=0):
    d=ImageDraw.Draw(im);pnts=[(x+math.cos(rot+k*math.tau/6)*r*(.78+.18*math.sin(k*3.5)),y+math.sin(rot+k*math.tau/6)*r*(.78+.18*math.cos(k*2.1))) for k in range(6)]
    d.polygon(pnts,fill=(243,240,216),outline=(126,145,130))
    d.polygon([pnts[0],pnts[1],(x,y),pnts[5]],fill=(255,252,234))
    d.line([pnts[2],(x,y),pnts[5]],fill=(192,199,172),width=2)

def suspended(t):
    im=p.base();chapter(im,'02  물이 사라진 뒤');d=ImageDraw.Draw(im)
    # A large floating drop carried in air; source identity retained by vignette below.
    phase=p.ease((t-4.3)/5.0);radius=230*(1-phase)+48*phase
    z=1+2.8*p.ease((t-8.65)/1.25)
    xx=540+11*math.sin(t*.7)*z;yy=810-14*math.sin(t*.45)*z
    d.ellipse((540+(168-540)*z,810+(410-810)*z,540+(912-540)*z,810+(1230-810)*z),outline=(211,213,193),width=2)
    # A faint calm airflow tracing is visually separate from material inside the drop.
    for k in [0,1,2]:
        p.curve(im,p.bezier((130,1125+k*32),(260,1140+k*32),(810,1000+k*22),(935,1050+k*22),90),(203,210,190),1)
    # Liquid boundary contracts rather than changing to white. Vapor is not drawn as a visible gas.
    alpha=int(255*(1-p.ease((t-8.2)/1.5)))
    if alpha>0:p.droplet(im,xx,yy,radius*z,alpha)
    for k,(dx,dy) in enumerate(PTS):
        rad=radius*(.9-.32*phase)*z;x=xx+dx*rad+3*math.sin(t+k)*z;y=yy+dy*rad+3*math.cos(t*.7+k)*z
        if phase<.9:
            rr=5.5*z;col=(210,150,81)
            d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col,outline=(153,120,72),width=1)
        else:mineral(im,x,y,(8+9*p.ease((phase-.9)/.1))*z,k*.6)
    if t>8.65:
        # Geometry is redrawn at the camera scale, keeping paper edges sharp.
        p.text(im,'남은 입자 확대',540,580,25,(80,114,110))
    if t<4.5:
        p.curve(im,[(600,760),(840,558),(961,558)],(88,127,120),2)
        p.text(im,'녹아 있는 미네랄',960,521,28,INK,True,'rm')
        p.text(im,'물속의 점은 성분을 설명하기 위한 표시',540,1295,24,(91,116,111))
    else:
        # restrained paired directional arcs; never depict boiling, visible vapor, or particles vanishing
        if t<9.5:
            for k in range(5):
                ang=-2.65+k*.53;start=radius*z+30;reach=start+55+25*math.sin(t*1.3+k)
                x0=xx+math.cos(ang)*start;y0=yy+math.sin(ang)*start
                x1=xx+math.cos(ang)*reach;y1=yy+math.sin(ang)*reach
                d.line((x0,y0,x1,y1),fill=(125,179,170),width=2)
                d.ellipse((x1-2,y1-2,x1+2,y1+2),fill=(125,179,170))
        p.text(im,'물은 증발',540,466,28,TEAL,True)
        if t>7.3:
            p.text(im,'미네랄은 남을 수 있습니다',540,1175,29,INK,True)
            p.text(im,'입자 크기·시간을 확대한 개념 표현',540,1295,24,(91,116,111))
    return im

# Familiar mineral water mark analogy, rendered as an oblique cut-paper tabletop.
def watermark(t):
    im=p.base();chapter(im,'02  물이 사라진 뒤');d=ImageDraw.Draw(im)
    # thick dark paper tile: oblique perspective and warm edge highlight
    d.polygon([(135,608),(812,473),(974,1117),(294,1282)],fill=(27,68,74),outline=(22,53,60))
    d.polygon([(135,608),(294,1282),(294,1300),(135,626)],fill=(59,97,96))
    d.polygon([(294,1282),(974,1117),(974,1135),(294,1300)],fill=(42,85,86))
    for i in range(12):
        x=185+i*59;d.line((x,650-i*8,x+125,1180-i*9),fill=(39,81,84),width=1)
    q=p.ease((t-.5)/4);cx,cy=547,873
    # Airborne crystals are NOT shown landing; this is an explicit household analogy.
    p.text(im,'물자국에 비유하면',540,373,27,(77,109,111),True)
    # broad elliptical mineral ring stays, the wet patch retreats inside it.
    pts=[]
    for k in range(150):
        a=k*math.tau/149;rr=1+.023*math.sin(k*1.7)
        x=cx+230*math.cos(a)*rr;y=cy+145*math.sin(a)*rr-40*math.cos(a)
        pts.append((x,y))
    # mineral trace becomes visible as water is gone; it's not a claim to exact deposition simulation
    ringcol=tuple(int(p.lerp(a,b,q)) for a,b in zip((52,103,108),(236,235,209)))
    d.line(pts,fill=ringcol,width=6,joint='curve')
    if q<.99:
        sx=220*(1-q)**.55;sy=135*(1-q)**.55
        # glossy puddle includes the faint ring while wet
        d.ellipse((cx-sx,cy-sy,cx+sx,cy+sy),fill=(72,143,148),outline=(116,182,178),width=2)
        d.arc((cx-sx*.78,cy-sy*.76,cx+sx*.78,cy+sy*.7),196,296,fill=(164,208,191),width=4)
    if q>.6:
        for k in range(39):
            a=k*2.399;xx=cx+math.cos(a)*(216+12*math.sin(k));yy=cy+math.sin(a)*(137+7*math.cos(k))-40*math.cos(a)
            mineral(im,xx,yy,3+3*q,k)
    p.text(im,'마른 뒤 드러나는 하얀 흔적' if q>.8 else '젖어 있을 때는 눈에 잘 띄지 않던 성분',540,1392,26,(74,107,111))
    return im

def mineral_frame(t):
    if t<11:im=suspended(t)
    elif t<11.9:
        # Match the remaining mineral cluster to the dry white trace analogy.
        im=aperture(suspended(11),watermark(t-11.9),(t-11)/.9,540,810)
    else:im=watermark(t-11.9)
    return finish(im,t,'minerals')

def make_sound(which):
    dur=DURATIONS[which];sr=48000;n=dur*sr;a=np.zeros(n);rng=np.random.default_rng(122)
    events=[(.15,.3,180,.025),(2.7,.9,220,.022),(3.7,5.3,84,.012),(9.25,.8,350,.025)] if which=='atomization' else [(0,.3,240,.018),(4.3,5,160,.01),(11,.9,230,.02),(16,.4,520,.018)]
    for start,length,hz,gain in events:
        i=int(start*sr);nn=min(int(length*sr),n-i);u=np.arange(nn)/sr;env=np.sin(np.pi*u/length)**2
        a[i:i+nn]+=(np.sin(math.tau*hz*u)*.6+rng.normal(0,.28,nn))*env*gain
    path=R/f'{which}_sfx.wav'
    with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
    return path

def render(which):
    fun=atom_frame if which=='atomization' else mineral_frame;duration=DURATIONS[which];start=time.time();frames=R/f'frames_{which}';frames.mkdir(exist_ok=True)
    for i in range(duration*FPS):
        fun(i/FPS).save(frames/f'{i:05}.jpg',quality=96,subsampling=0)
        if i%96==0:print(f'{which}: {i}/{duration*FPS} frames; {time.time()-start:.1f}s',flush=True)
    sfx=make_sound(which);out=R/f'paper_{which}_v1.mp4'
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate',str(FPS),'-i',str(frames/'%05d.jpg'),'-i',str(sfx),'-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(out)],check=True)
    print(f'{which} done in {time.time()-start:.1f}s',flush=True)
    return {'file':out.name,'seconds':duration,'width':W,'height':H,'fps':FPS,'frames':duration*FPS,'render_wall_seconds':round(time.time()-start,1),'audio':'Original quiet SFX, no narration'}

def stills():
    samples=[('atomization',1.4),('atomization',5),('atomization',8),('atomization',12),('minerals',2),('minerals',6.5),('minerals',10.5),('minerals',17)]
    sheet=Image.new('RGB',(1080,1920),PAPER)
    for i,(which,t) in enumerate(samples):
        im=(atom_frame if which=='atomization' else mineral_frame)(t);im.save(R/f'{which}_{t:04.1f}.jpg',quality=96)
        thumb=im.resize((270,480),Image.Resampling.LANCZOS);sheet.paste(thumb,((i%4)*270,(i//4)*960))
    # Two rows of four portrait frames without empty space.
    out=Image.new('RGB',(1080,960),PAPER)
    out.paste(sheet.crop((0,0,1080,480)),(0,0));out.paste(sheet.crop((0,960,1080,1440)),(0,480));out.save(R/'contact_sheet.jpg',quality=96)
    print('Stills ready',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--render',choices=['all','atomization','minerals']);args=ap.parse_args()
    if args.stills:stills()
    if args.render:
        names=['atomization','minerals'] if args.render=='all' else [args.render]
        result=[render(n) for n in names];(R/'render_metadata.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
