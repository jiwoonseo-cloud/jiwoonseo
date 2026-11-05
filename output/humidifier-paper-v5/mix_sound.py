import numpy as np,wave,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;sr=48000;duration=109.375;x=np.zeros(round(duration*sr));rng=np.random.default_rng(521)
rows=json.loads((r/'timing.json').read_text())
for row in rows[1:]:
 i=int(row['start']*sr);n=int(.14*sr);u=np.arange(n)/sr;env=np.sin(np.pi*u/.14)**2;x[i:i+n]+=rng.normal(0,.0025,n)*env
for t in [2.94,33.7,40.7,74.4,79.6,107.5]:
 i=int(t*sr);n=int(.18*sr);u=np.arange(n)/sr;x[i:i+n]+=np.sin(2*np.pi*560*u)*np.exp(-u*25)*.007
with wave.open(str(r/'sfx.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((x*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'narration.wav'),'-i',str(r/'sfx.wav'),'-filter_complex','[0:a]loudnorm=I=-16:TP=-1.5:LRA=9[v];[v][1:a]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.88:level=false[a]','-map','[a]','-ar','48000',str(r/'mix.wav')],check=True)
