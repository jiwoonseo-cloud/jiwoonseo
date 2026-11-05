from pathlib import Path
import json,math,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;O=P.parent;B=json.loads((P/'blocks.json').read_text());A=(O/'captions.ass').read_text();header=A[:A.index('Dialogue:')];R=P/'critical-review';R.mkdir(exist_ok=True)
def parse(t):h,m,s=t.split(':');return int(h)*3600+int(m)*60+float(s)
def fmt(t):
 n=round(max(0,t)*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
for b in B:
 if b['mode'] not in (sys.argv[1:] or ['short','duo_flow','snip']):continue
 mode=b['mode'];first=math.ceil(b['start']*24);end=math.ceil(b['end']*24);n=end-first;t0=first/24;dur=n/24
 assert all((P/f'full-denoised/{i:04}.png').exists() for i in range(first,end)),mode+' incomplete'
 lines=[header]
 for line in A.splitlines():
  if not line.startswith('Dialogue:'):continue
  v=line.split(',',9);lo=parse(v[1]);hi=parse(v[2]);
  if hi<t0 or lo>t0+dur:continue
  v[1]=fmt(max(0,lo-t0));v[2]=fmt(min(dur,hi-t0));lines.append(','.join(v)+'\n')
 ass=R/f'{mode}.ass';ass.write_text(''.join(lines))
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-start_number',str(first),'-i',str(P/'full-denoised/%04d.png'),'-ss',str(t0),'-i',str(P/'narration-full.wav'),'-vf','ass='+str(ass),'-frames:v',str(n),'-t',str(dur),'-c:v','libx264','-threads','2','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac',str(R/f'{mode}.mp4')],check=True)
 samples=sorted(set(list(range(first,end,6))+[end-1]));cols=6;rows=math.ceil(len(samples)/cols);im=Image.new('RGB',(cols*270,rows*505),(22,22,22));d=ImageDraw.Draw(im)
 for j,i in enumerate(samples):
  a=Image.open(P/f'full-denoised/{i:04}.png');a.thumbnail((270,480));x=j%cols*270;y=j//cols*505;im.paste(a,(x,y+25));d.text((x+5,y+3),f'{i/24:.3f}s f{i}',font=font,fill='white')
 im.save(R/f'{mode}-contact.jpg',quality=94)
 print('CRITICAL_REVIEW',mode,first,end-1,n,flush=True)
