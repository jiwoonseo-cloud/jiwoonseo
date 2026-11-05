from pathlib import Path
import torch, soundfile as sf, json, numpy as np, time
from melo.api import TTS
R=Path(__file__).resolve().parent
torch.set_num_threads(4); torch.manual_seed(2026)
m=TTS(language='KR',device='cpu',config_path=str(R/'models/config.json'),ckpt_path=str(R/'models/checkpoint.pth'))
lines=[s for s in (R/'script.txt').read_text().splitlines() if s.strip()]
(R/'audio').mkdir(exist_ok=True)
sr=m.hps.data.sampling_rate
all_audio=[np.zeros(int(sr*.35))];cursor=.35; timing=[]
for i,line in enumerate(lines):
 path=R/'audio'/f'{i:02}.wav'
 if path.exists(): a,_=sf.read(path)
 else:
  a=m.tts_to_file(line,0,speed=1.0,quiet=True);sf.write(path,a,sr)
 dur=len(a)/sr;timing.append(dict(index=i,text=line,start=cursor,end=cursor+dur,duration=dur))
 all_audio.extend([a,np.zeros(int(sr*.28))]);cursor+=dur+.28
 print(i,round(dur,2),line,flush=True)
sf.write(R/'narration.wav',np.concatenate(all_audio),sr)
(R/'timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2))
print('TOTAL',cursor,flush=True)
