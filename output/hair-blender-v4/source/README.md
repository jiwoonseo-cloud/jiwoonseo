# Blender 재현 소스

Blender 4.3.2와 ffmpeg, Python/Pillow/NumPy/OpenEXR, OpenImageDenoise 1.4.3을 포함한 `oidn==0.2.1` Python 바인딩이 필요하다. `python -m pip install numpy pillow OpenEXR oidn==0.2.1`로 Python 패키지를 설치한다. `master-scene.blend`는 카메라에서 바로 볼 수 있는 기준 제품 장면이고, `hair-full-assets.blend`는 전체 부품 라이브러리다. 두 파일 모두 팩된 재질을 포함한다. `full_scene.py`가 통일 자산을 불러와 단어 시각에 맞춰 가닥·부품·카메라를 프레임마다 평가한다. 편집용 pilot blend의 소수 키포즈를 보간한 결과와 최종 렌더는 다르다.

최종 렌더: `blender -b -t 4 -P full_scene.py -- full`.

별도 터미널에서 `STAGE=full python denoise_frames.py watch`, `STAGE=full blender -b -t 1 -P color_convert.py -- watch`로 후처리한 뒤 `python assemble_full.py`로 합성한다. denoise_frames.py는 설치된 oidn 패키지의 동봉 라이브러리를 사용한다. Linux x86_64 기준이며 다른 OS에서는 라이브러리 파일 이름을 맞춰야 한다. 별도의 인터넷 음성 요청 없이 포함된 MP3/WAV를 쓴다. 전체 프레임의 재렌더는 CPU에서 오래 걸린다.

`PILOT_PASSED.json`은 실제 검수 기록이며 새 경로·재질로 바꿀 때는 삭제하고 시험 영상을 다시 검수해야 한다. 원본 레퍼런스 파일과 타사 영상은 포함하지 않는다.
