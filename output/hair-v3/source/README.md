# 제작 소스

Node.js, Chromium, ffmpeg, 한국어 Noto Sans CJK 글꼴이 필요합니다. npm install 후 node capture.mjs 실행 후 python postprocess.py를 실행하면 timeline.json에 맞춰 매 프레임을 직접 렌더링합니다. 기본 Chromium 경로는 /usr/bin/chromium입니다. 영상 생성 AI나 보간은 사용하지 않습니다.

```sh
npm install
node capture.mjs
python postprocess.py
ffmpeg -framerate 24 -i frames/%05d.jpg -i mix.wav -vf 'ass=captions.ass' -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart ../hair-v3-review.mp4
```

목소리는 무료로 접근 가능한 Edge 온라인 TTS의 ko-KR-HyunsuMultilingualNeural입니다. 배속 설정은 +0%입니다. 이 비공식 연동의 장기 가용성 및 상업적 이용 조건은 별도 확인이 필요합니다. 재생산에 필요한 실제 음원을 포함했습니다. 사용자 대본의 단어는 보존했고 음성 입력의 쉼표·마침표만 정규화했습니다. 자막에는 원문 구두점을 보존했습니다.

prepare_v3.py와 tts_full.py는 이번 환경의 절대경로를 포함하는 작업 기록입니다. 재실행 시 P/O 경로를 소스 폴더와 출력 폴더로 바꾸세요. 최종 편집 시간표 timeline.json과 자막 파일은 이미 생성되어 있습니다. prepare 스크립트 재실행 시 semantic_fix.py의 후속 수정도 반영해야 합니다.

실사 제품 사진이나 타사 동영상 자산은 포함하지 않았습니다. assets/master.jpg는 AI 생성 기준 이미지이고, 나머지 이미지도 AI 생성 또는 그 레이어·재질 추출물입니다. 3D 메시·동작은 scene.js에 있습니다.
