from pathlib import Path
import numpy as np,json,wave,subprocess,os
P=Path('/workspace/work/hair-v3');A=json.loads((P/'timeline.json').read_text());D=json.loads((P/'metrics.json').read_text())['duration'];R=48000;N=round(D*R);rng=np.random.default_rng(103);x=np.zeros(N,np.float32);t=np.arange(N,dtype=np.float32)/R
for hz in [110,164.81,220]:x+=.0008*np.sin(2*np.pi*hz*t)*(.7+.3*np.sin(2*np.pi*.08*t))
def add(start,duration,kind,amp=.03):
 st=max(0,round(start*R));n=min(round(duration*R),N-st)
 if n<10:return
 q=np.arange(n)/R;z=rng.standard_normal(n);env=np.sin(np.pi*np.arange(n)/n)**2
 if kind=='click':v=(z*.15+np.sin(2*np.pi*1100*q)+.5*np.sin(2*np.pi*2300*q))*np.exp(-q*110)
 elif kind=='snip':v=(z*.5+np.sin(2*np.pi*1700*q)*.25)*np.exp(-q*42)
 elif kind=='motor':v=(np.sin(2*np.pi*110*q)+.25*np.sin(2*np.pi*440*q)+.12*z)*env*(.8+.2*np.sin(2*np.pi*13*q))
 elif kind=='air':v=np.convolve(z,np.ones(5)/5,mode='same')*env
 else:v=np.convolve(z,np.ones(18)/18,mode='same')*env
 x[st:st+n]+=amp*v.astype(np.float32)
for s in A:
 mode=s['mode'];start=s['start'];dur=s['end']-start
 add(start,.10,'click',.013)
 if mode in ['cap','assemble']:add(start+.06,.10,'click',.035)
 if mode in ['home','wrap','slide','duo','duoflow','path','motor','overview','accumulate']:add(start,min(.65,dur),'motor',.006)
 if mode in ['short','suction','pinned']:add(start+.05,min(1.0,dur-.1),'air',.022)
 if mode in ['flip','remove']:add(start+.1,min(.6,dur-.1),'cloth',.028)
 if mode in ['snip','cut'] and s['start']<=s['action_start']+(s['action_end']-s['action_start'])*.5<s['end']:add(s['action_start']+(s['action_end']-s['action_start'])*.5,.13,'snip',.06)
with wave.open(str(P/'foley_designed.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(R);w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'narration.wav'),'-i',str(P/'foley_designed.wav'),'-filter_complex','[0:a]loudnorm=I=-16:TP=-1.5:LRA=9[v];[v][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9[a]','-map','[a]','-ar','48000',str(P/'mix_new.wav')],check=True)
os.replace(P/'mix_new.wav',P/'mix.wav');print('mode-specific foley complete')
