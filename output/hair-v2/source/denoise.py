import pathlib,time,shutil
import numpy as np,oidn
from PIL import Image
P=pathlib.Path('/workspace/work/hair-v2');D=P/'denoised';D.mkdir(exist_ok=True)
while not (P/'RENDERS_DONE').exists():time.sleep(2)
d=oidn.NewDevice();oidn.CommitDevice(d);f=oidn.NewFilter(d,'RT');a=np.zeros((1280,720,3),dtype='float32');out=np.zeros_like(a)
oidn.SetSharedFilterImage(f,'color',a,oidn.FORMAT_FLOAT3,720,1280);oidn.SetSharedFilterImage(f,'output',out,oidn.FORMAT_FLOAT3,720,1280);oidn.CommitFilter(f)
files=list(sorted((P/'renders').glob('*.png')))
for i,p in enumerate(files):
 if p.name.startswith('explode_'):shutil.copy(p,D/p.name);continue
 a[:]=np.asarray(Image.open(p).convert('RGB'),dtype='float32')/255;oidn.ExecuteFilter(f);assert oidn.GetDeviceError(d)==0
 Image.fromarray((np.clip(out,0,1)*255).astype('uint8')).save(D/p.name)
 if i%10==0:print(i,'/',len(files),flush=True)
oidn.ReleaseFilter(f);oidn.ReleaseDevice(d);(P/'DENOISE_DONE').write_text('complete');print('DONE',flush=True)
