import pathlib,json,re,subprocess,datetime,time
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=pathlib.Path('/workspace/work/hair-v2');O=pathlib.Path('/workspace/jiwoonseo/output/hair-v2');F=O/'robot_brush_hair_v2.mp4'
while not (P/'assemble.log').exists() or 'DONE' not in (P/'assemble.log').read_text():time.sleep(2)
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate','-of','json',str(F)]));v=next(s for s in info['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'])==(1080,1920,'24/1');assert abs(float(info['format']['duration'])-141.125)<.05
subprocess.run(['ffmpeg','-v','error','-i',str(F),'-f','null','-'],check=True)
C=json.loads((O/'timeline.json').read_text());S=json.loads((O/'script.json').read_text());txt=(O/'subtitles.srt').read_text();blocks=txt.strip().split('\n\n');caption=[];prev=0
for b in blocks:
 lines=b.splitlines();a=list(map(int,re.findall(r'\d+',lines[1])));st=a[0]*3600+a[1]*60+a[2]+a[3]/1000;en=a[4]*3600+a[5]*60+a[6]+a[7]/1000
 assert prev<=st<en<=141.125,(prev,st,en);prev=en;caption.append(lines[2]);assert 2<=len(lines[2].split())<=3
assert re.sub(r'\s','', ''.join(caption))==re.sub(r'\s','', ''.join(S));assert len(blocks)==99
assert len(C)==57 and all(1.5<=c['duration']<=3 for c in C)
# Verify that every encoded shot contains changing picture content, then inspect a contact sheet.
motions=[]
for c in C:
 f=P/'clips'/f"{c['cut']:03}.mp4"
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-vf','select=eq(n\\,8)+eq(n\\,32),scale=90:160,format=gray','-frames:v','2','-fps_mode','vfr','-f','rawvideo','-'])
 a=np.frombuffer(raw,dtype=np.uint8).reshape(2,160,90);delta=float(np.mean(np.abs(a[0].astype(float)-a[1].astype(float))));assert delta>.05,(c,delta);motions.append(dict(cut=c['cut'],mean_frame_change=delta))
shots=[]
for mode in ['overview','explode','wrap','slide','separate','duo','caps','bearing','clean']:
 c=next(c for c in C if c['mode']==mode);t=(c['start']+c['end'])/2;p=P/f'check_{mode}.jpg'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(F),'-frames:v','1','-vf','scale=216:384',str(p)],check=True);shots.append((mode,p))
sheet=Image.new('RGB',(216*5,418*2),(20,24,28));d=ImageDraw.Draw(sheet)
for i,(mode,p) in enumerate(shots):x=i%5*216;y=i//5*418;sheet.paste(Image.open(p),(x,y));d.text((x+8,y+389),mode,fill='white')
sheet.save(O/'contact_sheet.jpg',quality=90)
c=next(c for c in C if c['mode']=='overview');subprocess.run(['ffmpeg','-v','error','-y','-ss',str((c['start']+c['end'])/2),'-i',str(F),'-frames:v','1',str(O/'poster.jpg')],check=True)
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)));start=datetime.datetime.fromtimestamp((P/'script.json').stat().st_mtime,datetime.timezone(datetime.timedelta(hours=9)))
result=dict(video=info,subtitles=dict(cues=99,full_script_match=True,words_per_cue='2–3',position_y=1267,background_box=False),cuts=dict(total=57,moving=57,still=0,min_seconds=min(c['duration'] for c in C),max_seconds=max(c['duration'] for c in C)),audio=dict(tts='ko-KR-SunHiNeural',rate='+10%',post_time_stretch=False),full_decode='passed',motion_frame_checks=motions,finished_kst=now.isoformat(timespec='seconds'),measured_start_kst=start.isoformat(timespec='seconds'),measured_elapsed_seconds=round((now-start).total_seconds()))
(O/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
with (O/'report.md').open('a') as f:f.write(f'\n## 최종 파일 검수\n\nffprobe 1080×1920 / 24fps / {info["format"]["duration"]}초 확인. 전체 FFmpeg 디코딩 통과. 99개 자막의 순서·비중첩·범위·2–3어절 및 원문 전체 일치 확인. 57개 컷 각각의 중간 프레임 차이를 검사해 고정 프레임이 아님을 확인했다. 프레임 차이 검사는 물리적 정확성을 증명하지 않으며, 9개 대표 구도 콘택트시트를 함께 보존했다.\n\n검수 완료: {now.isoformat(timespec="seconds")} KST. 대본 JSON 저장({start.isoformat(timespec="seconds")})부터 검수까지 실측 {(now-start).total_seconds()/60:.1f}분. 최초 지침 탐색·기준 이미지 요청 준비 등 대본 파일 저장 이전 시간은 제외되므로 전체 청구용 계측이 아니다. 토큰 사용량은 확인 불가.\n')
print('VALIDATED',info['format']['duration'],'seconds',flush=True)
