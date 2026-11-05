from faster_whisper import WhisperModel
from pathlib import Path
import json,time,subprocess,numpy as np
r=Path(__file__).resolve().parent;m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4,download_root=str(r/'whisper_models'))
audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(r/'supertonic/narration_master.wav'),'-ar','16000','-ac','1','-f','f32le','-']),dtype=np.float32)
segments,info=m.transcribe(audio,language='ko',word_timestamps=True,beam_size=5,vad_filter=False)
result=[]
for s in segments:
 row=dict(start=s.start,end=s.end,text=s.text,words=[dict(word=w.word,start=w.start,end=w.end,probability=w.probability) for w in s.words]);result.append(row);print(s.start,s.end,s.text,flush=True)
(r/'asr.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
