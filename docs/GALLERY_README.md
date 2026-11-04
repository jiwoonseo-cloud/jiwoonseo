# 영상 갤러리 운영 방법

## 처음 공개하기
1. 갤러리 구축 PR을 확인하고 **main에 병합**합니다.
2. 저장소 **Settings → Pages**를 엽니다.
3. **Build and deployment → Source → Deploy from a branch**를 선택합니다.
4. **Branch → main**, 폴더는 **/docs**를 선택하고 **Save**를 누릅니다.
5. Actions의 `pages build and deployment`가 성공하면 아래 주소를 엽니다.

https://jiwoonseo-cloud.github.io/jiwoonseo/

공개 전까지 주소가 404로 표시될 수 있습니다. 저장소는 현재 공개 저장소이며 갤러리와 포함된 보고서도 공개됩니다.

## 자동 갱신
- main / codex/* push, 같은 저장소 PR 생성·변경·종료, 수동 실행 때 갱신합니다.
- 원격 main 및 codex/* **브랜치 끝 커밋**의 모든 mp4를 수집합니다. 과거에 삭제된 파일이나 다른 접두사의 브랜치, 미커밋 로컬 파일은 대상이 아닙니다.
- 제작 브랜치에는 쓰지 않습니다. 변경사항은 `gallery/automated-update`에서 main 대상 PR로 올라오며, **병합해야 사이트에 반영됩니다.** 자동 병합은 설정하지 않습니다.
- Settings → Actions → General → Workflow permissions에서 **Allow GitHub Actions to create and approve pull requests**를 켜야 자동 PR 생성이 가능합니다. 조직 정책으로 차단되면 아래 수동 방법을 사용합니다.
- workflow는 PR 코드를 실행하지 않고 main의 스크립트만 실행합니다. 외부 fork PR은 건너뜁니다.
- 자동 PR의 변경은 GITHUB_TOKEN으로 생성되므로 다른 Actions를 자동 실행시키지 않을 수 있습니다. 병합 후 Pages 배포 상태를 확인하세요.

## 수동 갱신
Git, Python 3, ffmpeg/ffprobe가 필요합니다. 원본 제작 폴더와 분리한 복제본에서 실행하세요.

```bash
git clone https://github.com/jiwoonseo-cloud/jiwoonseo.git video-gallery
cd video-gallery
git switch -c gallery/manual-update origin/main
bash scripts/update_gallery.sh
git add docs
git commit -m 'chore: refresh video gallery'
git push -u origin gallery/manual-update
# GitHub에서 main 대상 PR을 생성하고 병합
```

이미 fetch를 완료했다면 `bash scripts/update_gallery.sh --no-fetch`를 사용합니다.

## 파일과 표시 규칙
- `docs/videos/브랜치명_원래파일명.mp4`: 브랜치의 `/`는 `%2F`로 인코딩합니다. 동일 브랜치의 서로 다른 폴더에 같은 이름이 있으면 경로 해시를 덧붙여 충돌을 방지합니다.
- 생성된 docs 영상은 재수집하지 않습니다. 원본은 이동·변경·삭제하지 않습니다.
- 최신순은 원본 파일의 마지막 Git 커밋 시간 기준입니다. 복사본에 원본 폴더명을 표시합니다.
- 같은 폴더의 report.md(대소문자 무관)는 안전하게 이스케이프한 HTML로 복사해 연결합니다.
- 99 MB 이상은 720p급(세로 최대 720×1280, 가로 최대 1280×720) H.264/AAC로 압축하고 99 MB 미만을 검증합니다. 이는 GitHub의 일반 Git 파일 크기 제한(100 MiB)도 피하도록 한 보수적 기준입니다. 원본은 보존합니다.
- Git LFS 포인터는 영상이 아니므로 명확한 오류로 중단합니다. 현재 저장소의 실제 Git blob 영상을 대상으로 합니다.
- 자동 생성 목록은 `docs/gallery.json`, 플레이어는 `docs/index.html`입니다. 페이지를 직접 수정하면 다음 갱신 때 덮어써집니다.
