"""Document rendered actions and actual TTS word overlaps, without changing media."""
from pathlib import Path
import json,csv
B=Path(__file__).resolve().parents[1];P=json.loads((B/'scene-plan.json').read_text());D=json.loads((B/'source/voice-measurements.json').read_text())['ko-KR-HyunsuMultilingualNeural']['paragraph_seconds'];offsets={};t=0;events=[]
for p in [1,2,3,4,5,7,8]:
 offsets[p]=t
 for e in json.loads((B/'audio'/f'{p:02}.json').read_text()):events.append((p,t+e['offset']/1e7,t+(e['offset']+e['duration'])/1e7,e['text']))
 t+=D[f'{p:02}']
fix={
 'P2-C01':'브러시와 긴 모발 → 롤러 회전과 모발의 위치를 보여 줌 → 감김 원인 부품 소개',
 'P2-C02':'흡입구 앞 브러시와 긴 모발 → 롤러가 회전함 → 기계적인 감김 원인으로 연결',
 'P2-C03':'나선 모와 아래로 뻗은 긴 모발 → 모가 회전하며 모발 경로에 접근 → 접촉 방향 제시',
 'P2-C04':'회전하는 모와 긴 가닥들 → 계속 회전하며 접촉 위치를 보여 줌 → 감김 준비',
 'P3-C09':'끝단에 도착한 긴 모발 → 롤러 회전 중 다발이 축에 남고 미세하게 흔들림 → 긴 가닥 잔류',
 'P3-C10':'축에 남은 긴 모발 → 회전과 분리된 잔류 상태를 확인 → 끝단의 다발 유지',
 'P5-C01':'흡입구 앞 감긴 긴 모발 → 롤러 회전 중 다발이 남은 상태를 보임 → 더 센 흡입에 대한 질문 연결',
 'P5-C02':'감긴 다발과 흡입구 → 롤러가 회전함 → 긴 가닥 잔류 유지',
 'P5-C05':'이미 감긴 가닥들 → 회전하며 추가 감김이 증가 → 기계적인 걸림 유지',
 'P5-C07':'회전 중 감긴 모발 → 축 방향으로 이동함 → 끝단 부근으로 접근',
 'P5-C08':'끝단으로 이동하는 다발 → 축에 모이고 잔류함 → 감김이 남음',
 'P8-C03':'회전하는 브러시와 모발 → 다발이 끝단 이동을 마침 → 축에 남는 결과',
 'P8-C09':'캡이 열린 축의 감김 → 벌어진 가위가 접근하고 날이 모발 바깥에 위치함 → 절단 준비',
 'P8-C10':'모발 바깥의 가위 → 날이 닫히고 가닥이 두 조각으로 분리되어 위·바깥으로 이동함 → 감김 제거',
}
for c in P['cuts']:
 c['spoken_words']=' '.join(e[3] for e in events if e[0]==c['paragraph'] and e[1]<c['end']-1e-7 and e[2]>c['start']+1e-7)
 if c['id'] in fix:c['object_and_action']=fix[c['id']]
 if c['paragraph']==7:c['object_and_action']='끝단 부근의 감긴 다발 → 브러시 회전 중 조금씩 축 끝으로 압축·이동함 → 나선 구조와 긴 모발의 잔류 관계를 보임'
 c['object_and_action']=c['object_and_action'].replace('한 가닥','가는 가닥들').replace('집게로 가닥을','가닥을')
(B/'scene-plan.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
def write(name,rows):
 with (B/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)
write('scene-table.csv',P['cuts']);shots=[]
for c in P['cuts']:
 if c['id']=='P5-C04':
  s=shots[-1];s.update(id='P5-C03+C04',end=c['end'],end_frame_exclusive=c['end_frame_exclusive']);s['spoken_words']+='; '+c['spoken_words'];s['object_and_action']+='; '+c['object_and_action'];s['camera']+=' / CAM_032_MECHANISM (continuous view)'
 else:shots.append(dict(c))
assert len(shots)==57;write('shot-table.csv',shots)
r=B/'report.md';s=r.read_text();mark='|시간(초)|내레이션 단어|화면 대상 · 움직임|';s=s[:s.index(mark)].rstrip().removesuffix('## 최종 장면 표').rstrip()+'\n\n';s+='## 최종 장면 표\n\n'+mark+'\n|---|---|---|\n'
for c in shots:s+=f"|{c['start']:.3f}–{c['end']:.3f}|{c['spoken_words']}|{c['object_and_action']}|\n"
r.write_text(s)
print('Documented 57 actual shots / 58 native render segments; media unchanged')
