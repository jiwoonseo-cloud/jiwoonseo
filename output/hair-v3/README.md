# hair-v3 — 제작 초안

**완성본이 아닙니다.** 6번 문단은 사용자 지시로 제작 보류 중입니다. 최종 영상의 사실·음성·시각 품질 합격 판정도 하지 않았습니다.

- 먼저 `report.md`와 `fact-check.md`를 읽어 주세요.
- `motion-test_270x480.mp4`: 9초 저해상도 동작 시험.
- `voice-comparison/`: 동일 문장의 목소리 3종, 모두 1.0배.
- `narration/`: 허가된 1~5·7~8번의 세 목소리 합성 원본과 발화 경계.
- `script-original.txt`: 8문단 원문 전부.
- `storyboard-aligned.csv`: 문단 내부의 실제 발화 시점과 의미·행동 연결.
- `cut-plan-excluding-held-6.csv`: 1.5~3초 계획 컷. 완성 영상 목록이 아닙니다.
- 자막 파일 이름의 `excluding-held-6`은 6번이 빠진 잠정 자료임을 표시합니다.

## 재현

Blender 4.3.2와 FFmpeg, Python 3.12+ 및 NumPy가 필요합니다. 음성 재합성에는 edge-tts 7.3.1과 네트워크 접근이 필요하며, 외부 전송 허가 범위는 1~5·7~8번입니다. 6번은 코드에서도 건너뜁니다.

```sh
python storyboard.py
python synthesize.py
python align.py
python plan_cuts.py
blender -b -t 5 --python build_pilot.py -- --shot flip --motion-preview --size 270 --samples 4
blender -b -t 5 --python build_pilot.py -- --shot catch --motion-preview --size 270 --samples 4
blender -b -t 5 --python build_pilot.py -- --shot suction --motion-preview --size 270 --samples 8
python assemble_pilot.py
```

스크립트는 저장소 `output/hair-v3`에서의 배치를 기준으로 상대 경로를 계산합니다. 중간 렌더 프레임은 `work/hair-v3/render`에 저장합니다. 시험용 단면은 실제 특정 제품의 반쪽 롤러 형태를 뜻하지 않습니다.
