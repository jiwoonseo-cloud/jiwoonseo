from pathlib import Path
import json,subprocess
P=Path(__file__).resolve().parent;O=P.parent;S=json.loads((P/'script.json').read_text());raw=json.loads((P/'voice_02.json').read_text());original=S[2].split();assert len(raw)==len(original)
start=21.455;end=31.375458;events=[]
for w,e in zip(original,raw):
 t=20.28+e['offset']/1e7
 if start-.0001<=t<end-.001:events.append(dict(text=w,start=t-start,end=min(10,20.28+(e['offset']+e['duration'])/1e7-start)))
c=[]
for e in events:
 if c and len(c[-1]['words'])<3 and len(' '.join(c[-1]['words']+[e['text']]))<=14:c[-1]['words'].append(e['text']);c[-1]['end']=e['end']
 else:c.append(dict(start=e['start'],end=e['end'],words=[e['text']]))
def ts(t):
 q=round(t*100);return f'{q//360000}:{q//6000%60:02}:{q//100%60:02}.{q%100:02}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK KR,58,&H00FFFFFF,&H00FFFFFF,&H00202020,&H85000000,-1,0,0,0,100,100,0,0,1,4,3,5,40,40,0,1
Style: Note,Noto Sans CJK KR,27,&H00FFFFFF,&H00FFFFFF,&H00202020,&H85000000,0,0,0,0,100,100,0,0,1,2,1,5,30,30,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
a=[header]
for x in c:a.append(f'Dialogue: 0,{ts(x["start"])},{ts(x["end"])},Main,,0,0,0,,{{\\pos(540,1267)}}'+ ' '.join(x['words'])+'\n')
a.append('Dialogue: 0,0:00:00.00,0:00:10.00,Note,,0,0,0,,{\\pos(540,1600)}원리 설명용 동작 · 특정 제품 아님\n');(O/'pilot.ass').write_text(''.join(a))
subprocess.run(['ffmpeg','-v','error','-y','-ss','1.175','-i',str(P/'voice_02.mp3'),'-t','9.920458','-ar','48000',str(P/'pilot-voice.wav')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-start_number','1','-i',str(P/'pilot-denoised/%04d.png'),'-i',str(P/'pilot-voice.wav'),'-vf','ass='+str(O/'pilot.ass'),'-af','apad=pad_dur=0.079542','-t','10','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(O/'pilot-10s.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(O/'pilot-10s.mp4'),'-vf',"select='not(mod(n,24))+eq(n,239)',scale=270:480,tile=4x3",'-frames:v','1',str(O/'pilot-contact-sheet.jpg')],check=True)
print('pilot built')
