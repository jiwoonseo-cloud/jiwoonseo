from PIL import Image,ImageFilter
import pathlib,math,numpy as np
P=pathlib.Path('/workspace/work/hair-v2');A=pathlib.Path('/workspace/jiwoonseo/output/hair-v2/assets')
body=Image.open(A/'housing.png').convert('RGBA');roller=Image.open(A/'roller.png').convert('RGBA');caps=Image.open(A/'endcaps.png').convert('RGBA')
def paste(im,asset,xy,size,shadow=True):
 o=asset.resize(size,Image.Resampling.LANCZOS);x,y=map(round,xy)
 if shadow:
  sh=Image.new('RGBA',o.size,(0,0,0,0));sh.putalpha(o.getchannel('A').point(lambda a:int(a*.6)));sh=sh.filter(ImageFilter.GaussianBlur(13));im.alpha_composite(sh,(x+10,y+22))
 im.alpha_composite(o,(x,y))
yy,xx=np.mgrid[0:1280,0:720];g=np.clip(43-17*((xx-360)/650)**2-13*((yy-620)/900)**2,15,50);bg=np.stack([g*.82,g*.92,g,np.full_like(g,255)],axis=2).astype('uint8')
for i in range(24):
 t=i/23;s=t*t*(3-2*t);im=Image.fromarray(bg,'RGBA')
 paste(im,body,(80,120-45*s),(560,596))
 paste(im,roller,(175,496+205*s),(370,116))
 left=caps.crop((0,0,300,400));right=caps.crop((300,0,610,400))
 paste(im,left,(110-52*s,528+198*s),(95,125));paste(im,right,(510+52*s,528+198*s),(95,125))
 im.convert('RGB').save(P/'renders'/f'explode_{i:03}.png')
print('24 transparent-layer disassembly frames')
