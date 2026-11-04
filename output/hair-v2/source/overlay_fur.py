import pathlib,json,numpy as np
from PIL import Image
P=pathlib.Path('/workspace/work/hair-v2');A=pathlib.Path('/workspace/jiwoonseo/output/hair-v2/assets')
src=Image.open(A/'fur.png').convert('RGBA');a=np.array(src);a[(a[:,:,0]>a[:,:,1].astype(float)*1.6)&(a[:,:,0]>100),3]=0;src=Image.fromarray(a);src=src.crop(src.getbbox()).resize((28,15),Image.Resampling.LANCZOS)
src.save(A/'short_fur_sprite.png')
for i,pts in enumerate(json.loads((P/'fur_projection.json').read_text())):
 p=P/'denoised'/f'separate_{i:03}.png';im=Image.open(p).convert('RGBA')
 for x,y,u in pts:
  o=src.rotate(-30+70*u,expand=True, resample=Image.Resampling.BICUBIC)
  if u>.88:o.putalpha(o.getchannel('A').point(lambda v:int(v*(1-u)/.12)))
  im.alpha_composite(o,(round(x-o.width/2),round(y-o.height/2)))
 im.convert('RGB').save(p)
print('short fur image layer composited on 18 motion frames')
