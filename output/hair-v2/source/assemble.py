import pathlib,json,subprocess,time
P=pathlib.Path('/workspace/work/hair-v2');O=pathlib.Path('/workspace/jiwoonseo/output/hair-v2');(P/'masters').mkdir(exist_ok=True);(P/'clips').mkdir(exist_ok=True)
counts={'overview':12,'wrap':24,'slide':18,'separate':18,'duo':18,'caps':12,'bearing':12,'clean':12,'explode':24}
def run(cmd):subprocess.run(cmd,check=True)
while not (P/'DENOISE_DONE').exists():time.sleep(2)
for mode,n in counts.items():
 while not (P/'denoised'/f'{mode}_{n-1:03}.png').exists():time.sleep(2)
 out=P/'masters'/f'{mode}.mp4'
 if out.exists() and out.stat().st_size>1000:continue
 print('MASTER',mode,flush=True)
 run(['ffmpeg','-v','error','-y','-framerate',str((n-1)/2.5),'-i',str(P/'denoised'/f'{mode}_%03d.png'),'-vf','hqdn3d=2:1.5:3:2.5,tpad=stop_mode=clone:stop_duration=0.6,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:me=hexbs:mb_size=16,format=yuv420p','-frames:v','60','-c:v','libx264','-crf','18','-preset','fast','-threads','4',str(out)])
cuts=json.loads((O/'timeline.json').read_text());concat=[]
i=0
while i<len(cuts):
 j=i+1
 while j<len(cuts) and cuts[j]['mode']==cuts[i]['mode'] and cuts[j]['section']==cuts[i]['section']:j+=1
 for k in range(i,j):cuts[k]['phase_start']=(k-i)/(j-i);cuts[k]['phase_end']=(k-i+1)/(j-i)
 i=j
for c in cuts:
 mode=c['mode'];dur=c['duration'];nf=round(dur*24);v=c['variant'];out=P/'clips'/f"{c['cut']:03}.mp4"
 # The primary motion is in component geometry; these tiny reframings distinguish macro inserts.
 if v==0:crop='scale=1080:1920'
 elif v==1:crop='crop=iw*0.96:ih*0.96:iw*0.02:ih*0.02,scale=1080:1920'
 else:crop='crop=iw*0.92:ih*0.92:iw*0.05:ih*0.03,scale=1080:1920'
 segstart=c['phase_start']*2.5;segdur=(c['phase_end']-c['phase_start'])*2.5
 vf=f'setpts=PTS-STARTPTS,setpts={dur/segdur:.9f}*PTS,{crop},tpad=stop_mode=clone:stop_duration=0.4,minterpolate=fps=24:mi_mode=blend,tpad=stop_mode=clone:stop_duration=1,format=yuv420p'
 run(['ffmpeg','-v','error','-y','-ss',str(segstart),'-t',str(segdur),'-i',str(P/'masters'/f'{mode}.mp4'),'-vf',vf,'-frames:v',str(nf),'-an','-c:v','libx264','-crf','22','-preset','veryfast','-threads','4',str(out)])
 concat.append(f"file '{out}'\n")
 print('CUT',c['cut'],mode,flush=True)
(P/'concat.txt').write_text(''.join(concat))
(O/'timeline.json').write_text(json.dumps(cuts,ensure_ascii=False,indent=2))
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(P/'concat.txt'),'-c','copy',str(P/'picture.mp4')])
print('FINAL subtitles and audio',flush=True)
run(['ffmpeg','-v','error','-y','-i',str(P/'picture.mp4'),'-i',str(P/'mix.wav'),'-vf',f"ass={O/'subtitles.ass'}",'-c:v','libx264','-crf','24','-preset','fast','-threads','4','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(O/'robot_brush_hair_v2.mp4')])
print('DONE',flush=True)
