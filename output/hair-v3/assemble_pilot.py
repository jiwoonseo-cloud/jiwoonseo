"""Assemble three directly rendered 24fps motion tests and unchanged voice excerpts.
This is a 270x480 diagnostic preview, not the requested final 1080x1920 film.
"""
import subprocess,json,wave,math
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent;WORK=BASE.parent.parent/'work/hair-v3';R=WORK/'render'
def run(args):subprocess.run(args,check=True)
for shot in ['flip','catch','suction']:
 frames=list(R.glob(f'preview-{shot}[0-9]*.png'));assert len(frames)==72,(shot,len(frames))
 run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(R/f'preview-{shot}%04d.png'),'-frames:v','72','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(WORK/f'{shot}.mp4')])
(WORK/'clips.txt').write_text(''.join(f"file '{WORK/shot}.mp4'\n" for shot in ['flip','catch','suction']))
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(WORK/'clips.txt'),'-c','copy',str(WORK/'silent-test.mp4')])
sr=24000;n=9*sr;audio=np.zeros(n,dtype=np.float32)
voice=BASE/'narration/ko-KR-HyunsuMultilingualNeural'
excerpts=[(1,4.975,6.350,1.075,'브러시 뒤집었더니'),(3,2.500,3.875,3.500,'모에 걸립니다'),(3,14.425,16.938,6.100,'짧은 털은 흡입으로 빨려 올라가지만')]
for p,start,end,dest,text in excerpts:
 b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-t',str(end-start),'-i',str(voice/f'{p:02}.mp3'),'-f','f32le','-ar',str(sr),'-ac','1','-'])
 a=np.frombuffer(b,dtype=np.float32);i=round(dest*sr);audio[i:i+len(a)]+=a
rng=np.random.default_rng(33)
for when,length,gain,kind in [(0.5,.45,.025,'cloth'),(3.65,.16,.02,'pluck'),(6.5,1.9,.022,'suction')]:
 tt=np.arange(round(length*sr))/sr;env=np.sin(np.pi*np.arange(len(tt))/max(1,len(tt)-1))**2
 noise=rng.normal(size=len(tt));noise=np.convolve(noise,np.ones(8)/8,mode='same')
 signal=noise if kind!='pluck' else np.sin(math.tau*420*tt)*np.exp(-tt*22)
 i=round(when*sr);audio[i:i+len(tt)]+=gain*env*signal
# Quiet original tonal bed. No third-party music or stock effects.
t=np.arange(n)/sr
for hz in [110,164.81,220]:audio+=.0025*np.sin(math.tau*hz*t)*(.7+.3*np.sin(math.tau*.5*t))
assert np.max(np.abs(audio))<1,'Audio clipping'
with wave.open(str(WORK/'pilot-audio.wav'),'wb') as f:
 f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes((audio*32767).astype('<i2').tobytes())
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 270
PlayResY: 480
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Noto Sans CJK KR,16,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,1,0.5,5,10,10,0,1
Style: Small,Noto Sans CJK KR,9,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,0.6,0,5,8,8,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.07,0:00:02.45,Caption,,0,0,0,,{\\pos(135,317)}브러시 뒤집었더니
Dialogue: 0,0:00:03.50,0:00:04.88,Caption,,0,0,0,,{\\pos(135,317)}모에 걸립니다
Dialogue: 0,0:00:06.10,0:00:07.43,Caption,,0,0,0,,{\\pos(135,317)}짧은 털은 흡입으로
Dialogue: 0,0:00:07.43,0:00:08.62,Caption,,0,0,0,,{\\pos(135,317)}빨려 올라가지만
Dialogue: 1,0:00:00.00,0:00:09.00,Small,,0,0,0,,{\\pos(135,455)}저해상도 동작 시험 · 완성본 아님
Dialogue: 1,0:00:03.00,0:00:06.00,Small,,0,0,0,,{\\pos(135,425)}원리 설명용 저속 재현
Dialogue: 1,0:00:06.00,0:00:09.00,Small,,0,0,0,,{\\pos(135,425)}설명용 단면 · 저속 재현
'''
(BASE/'motion-test.ass').write_text(ass)
run(['ffmpeg','-v','error','-y','-i',str(WORK/'silent-test.mp4'),'-i',str(WORK/'pilot-audio.wav'),'-vf',f'ass={BASE}/motion-test.ass','-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-c:a','aac','-b:a','128k','-pix_fmt','yuv420p','-movflags','+faststart',str(BASE/'motion-test_270x480.mp4')])
(BASE/'pilot-excerpts.json').write_text(json.dumps({'status':'DIAGNOSTIC TEST - NOT FINAL VIDEO','shots':{'flip':[0,3],'catch':[3,6],'suction':[6,9]},'voice_excerpts':excerpts,'post_audio_speed_adjustment':False,'frame_interpolation':False,'repeated_motion_clips':False},ensure_ascii=False,indent=2))
print('9-second diagnostic preview assembled; no final-quality approval implied.')
