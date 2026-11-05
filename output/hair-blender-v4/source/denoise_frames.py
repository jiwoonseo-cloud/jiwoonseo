import sys,ctypes,pathlib,time,os
import OpenEXR,Imath,numpy as np,oidn
P=pathlib.Path(__file__).resolve().parent;stage=os.environ.get('STAGE','pilot');D=P/f'{stage}-denoised';D.mkdir(exist_ok=True)
dev=oidn.NewDevice();lib=ctypes.CDLL(str(pathlib.Path(oidn.__file__).parent/'lib.linux.x64/libOpenImageDenoise.so.1.4.3'));lib.oidnSetDevice1i.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int];lib.oidnSetDevice1i(dev,b'numThreads',int(os.environ.get('OIDN_THREADS','2')));oidn.CommitDevice(dev)
lib.oidnSetFilter1b.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_bool]
pt=Imath.PixelType(Imath.PixelType.FLOAT)
watch=sys.argv[1:]==['watch'];args=range(0,int(os.environ.get('TOTAL_FRAMES','3128'))) if watch and stage!='pilot' else range(1,241) if watch else sys.argv[1:]
if watch and os.environ.get('FRAME_LIST'):args=[int(q) for q in os.environ['FRAME_LIST'].split(',')]
for arg in args:
 if (P/f'{stage}-frames/{int(arg):04}.cached').exists():continue
 if watch:
  while not (P/f'{stage}-frames/{int(arg):04}.ready').exists() and not (P/f'{stage}-frames/{int(arg):04}.cached').exists():time.sleep(.2)
  if (P/f'{stage}-frames/{int(arg):04}.cached').exists() or ((D/f'{int(arg):04}.png').exists() and not (P/f'{stage}-frames/{int(arg):04}.exr').exists()):continue
 f=P/f'{stage}-frames'/f'{int(arg):04}.exr';ex=OpenEXR.InputFile(str(f));window=ex.header()['dataWindow'];w=window.max.x+1;h=window.max.y+1
 def read(name,parts):return np.ascontiguousarray(np.stack([np.frombuffer(ex.channel('ViewLayer.'+name+'.'+c,pt),np.float32).reshape(h,w) for c in parts],axis=-1))
 color=read('Combined','RGB');albedo=read('Denoising Albedo','RGB');normal=read('Denoising Normal','XYZ');ex.close();out=np.zeros_like(color)
 filt=oidn.NewFilter(dev,'RT')
 for name,arr in [('color',color),('albedo',albedo),('normal',normal),('output',out)]:oidn.SetSharedFilterImage(filt,name,arr,oidn.FORMAT_FLOAT3,w,h)
 lib.oidnSetFilter1b(filt,b'hdr',True);oidn.CommitFilter(filt);t=time.time();oidn.ExecuteFilter(filt);assert oidn.GetDeviceError(dev)==0
 header=OpenEXR.Header(w,h);header['channels']={c:Imath.Channel(pt) for c in 'RGB'};output=OpenEXR.OutputFile(str(D/f'{int(arg):04}.exr'),header);output.writePixels({c:out[:,:,i].copy().tobytes() for i,c in enumerate('RGB')});output.close();oidn.ReleaseFilter(filt);(D/f'{int(arg):04}.filtered').touch();print('DENOISED',arg,round(time.time()-t,3),flush=True)
oidn.ReleaseDevice(dev)
