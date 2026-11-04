#!/usr/bin/env python3
"""Read immutable remote snapshots; write only generated gallery assets."""
import hashlib
import html
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
LIMIT = 99_000_000  # Below both 100 MB and GitHub's 100 MiB Git object limit.

def git(*args):
    return subprocess.check_output(['git', *args])

def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))

def esc(value):
    return html.escape(str(value), quote=True)

def url(value):
    return quote(str(value), safe='/')

refs = git('for-each-ref', '--format=%(refname)', 'refs/remotes/origin').decode().splitlines()
snapshots = [(ref.removeprefix('refs/remotes/origin/'), git('rev-parse', ref).decode().strip())
             for ref in refs if ref == 'refs/remotes/origin/main' or ref.startswith('refs/remotes/origin/codex/')]
if not any(branch == 'main' for branch, _ in snapshots):
    raise SystemExit('origin/main is required')
output = ROOT / 'docs'
output.mkdir(exist_ok=True)
previous = {}
manifest = output / 'gallery.json'
if manifest.exists():
    previous = {item['file']: item for item in json.loads(manifest.read_text())}
items = []
with tempfile.TemporaryDirectory(prefix='video-gallery-') as temp:
    stage = Path(temp)
    (stage / 'videos').mkdir()
    (stage / 'reports').mkdir()
    used = set()
    for branch, commit in sorted(snapshots):
        entries = git('ls-tree', '-r', '-z', commit).split(b'\0')
        blobs = {}
        for entry in filter(None, entries):
            metadata, path = entry.split(b'\t', 1)
            mode, kind, oid = metadata.decode().split()
            if kind == 'blob' and mode in ('100644', '100755'):
                blobs[path.decode()] = oid
        for path, oid in sorted(blobs.items()):
            if not path.lower().endswith('.mp4') or path.startswith('docs/'):
                continue
            source = Path(path)
            name = quote(branch, safe='') + '_' + source.name
            if name in used:
                name = quote(branch, safe='') + '_' + source.stem + '_' + hashlib.sha256(path.encode()).hexdigest()[:12] + source.suffix
            if name in used:
                raise RuntimeError('Filename collision: ' + name)
            used.add(name)
            target = stage / 'videos' / name
            old = previous.get(name, {})
            cached = output / 'videos' / name
            if old.get('blob') == oid and old.get('encoding_version') == 1 and cached.exists() and cached.stat().st_size < LIMIT:
                import shutil
                shutil.copyfile(cached, target)
            else:
                with target.open('wb') as stream:
                    subprocess.run(['git', 'cat-file', 'blob', oid], stdout=stream, check=True)
                with target.open('rb') as header:
                    is_lfs = header.read(128).startswith(b'version https://git-lfs.github.com/spec/v1')
                if is_lfs:
                    raise RuntimeError('Git LFS pointer requires materialization: ' + branch + ':' + path)
                if target.stat().st_size >= LIMIT:
                    info = probe(target)
                    duration = float(info['format']['duration'])
                    bitrate = math.floor(LIMIT * 8 * .90 / duration) - 96000
                    if bitrate < 64000:
                        raise RuntimeError('Video too long for one <100 MB file: ' + path)
                    original = stage / 'original.mp4'
                    target.rename(original)
                    # Portrait <=720x1280; landscape <=1280x720. Never upscale.
                    scale = "scale=w='if(gte(iw,ih),min(1280,iw),min(720,iw))':h='if(gte(iw,ih),min(720,ih),min(1280,ih))':force_original_aspect_ratio=decrease:force_divisible_by=2"
                    for attempt in range(3):
                        run('ffmpeg', '-v', 'error', '-y', '-i', str(original), '-map', '0:v:0', '-map', '0:a:0?', '-vf', scale,
                            '-c:v', 'libx264', '-preset', 'medium', '-b:v', str(int(bitrate * .8 ** attempt)),
                            '-maxrate', str(int(bitrate * .8 ** attempt)), '-bufsize', str(bitrate * 2),
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(target))
                        if target.stat().st_size < LIMIT:
                            break
                    else:
                        raise RuntimeError('Compressed file still exceeds limit: ' + path)
            info = probe(target)
            duration = float(info['format']['duration'])
            timestamp = int(git('log', '-1', '--format=%ct', commit, '--', path).decode().strip())
            report = next((p for p in blobs if str(Path(p).parent) == str(source.parent) and Path(p).name.lower() == 'report.md'), None)
            report_url = None
            if report:
                report_name = name + '.html'
                content = git('cat-file', 'blob', blobs[report]).decode('utf-8', errors='replace')
                (stage / 'reports' / report_name).write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>제작 보고서</title><style>body{max-width:850px;margin:32px auto;padding:20px;font:16px/1.7 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><a href="../index.html">← 갤러리</a><pre>' + esc(content).replace(' \n', '&#32;\n') + '</pre></html>')
                report_url = 'reports/' + report_name
            items.append(dict(file=name, branch=branch, source=path, blob=oid, encoding_version=1,
                              duration=duration, timestamp=timestamp, report=report_url, title=source.stem))
    items.sort(key=lambda item: (-item['timestamp'], item['branch'], item['source']))
    cards = []
    for item in items:
        duration = round(item['duration'])
        report_link = '<a href="' + url(item['report']) + '">제작 보고서 ↗</a>' if item['report'] else '<span>보고서 없음</span>'
        cards.append(f'''<article><video controls playsinline preload="none" aria-label="{esc(item['title'])}"><source src="videos/{url(item['file'])}" type="video/mp4">브라우저가 동영상을 지원하지 않습니다.</video><div class="details"><p class="branch">{esc(item['branch'])}</p><h2>{esc(item['title'])}</h2><p class="meta">{duration // 60}:{duration % 60:02d} · {esc(item['source'])}</p>{report_link}</div></article>''')
    page = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>영상 라이브러리</title><meta name="description" content="브랜치별 제작 영상을 한곳에서 재생하고 보고서를 확인하세요."><style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,sans-serif;background:#101115;color:#f4f4f5}*{box-sizing:border-box}body{margin:0}header,main,footer{max-width:1320px;margin:auto;padding:32px 24px}header{padding-top:64px}small,.branch{color:#a9b8ff;letter-spacing:.06em}h1{font-size:clamp(32px,6vw,56px);margin:14px 0}header p,footer,.meta{color:#a8abb7}main{display:grid;grid-template-columns:1fr;gap:28px}article{min-width:0;background:#1a1c23;border:1px solid #30323b;border-radius:18px;overflow:hidden}video{display:block;width:100%;aspect-ratio:9/16;object-fit:contain;background:#050505}.details{padding:22px}h2{font-size:20px;overflow-wrap:anywhere;margin:12px 0}.branch,.meta{font-size:13px;overflow-wrap:anywhere}a{color:#b5c3ff;text-underline-offset:4px}a:focus-visible,video:focus-visible{outline:3px solid #b5c3ff;outline-offset:3px}@media(min-width:700px){main{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(min-width:1100px){main{grid-template-columns:repeat(3,minmax(0,1fr))}}</style></head><body><header><small>JIWOONSEO / VIDEO LIBRARY</small><h1>영상 라이브러리</h1><p>브랜치별 영상을 한곳에서. 최신 영상부터 확인하세요.</p><p>COUNT_PLACEHOLDER개 영상 · main / codex/* · 영상 파일의 마지막 커밋 기준</p></header><main>CARDS_PLACEHOLDER</main><footer>원본 제작 파일은 각 브랜치에 보존됩니다.</footer></body></html>'''
    page = page.replace('COUNT_PLACEHOLDER', str(len(items))).replace('CARDS_PLACEHOLDER', '\n'.join(cards) or '<p>등록된 영상이 없습니다.</p>')
    # Do not remove unrelated docs files. Remove only assets listed by our old manifest.
    keep = {item['file'] for item in items}
    for name, old in previous.items():
        if name not in keep and Path(name).name == name:
            (output / 'videos' / name).unlink(missing_ok=True)
            if old.get('report') == 'reports/' + name + '.html':
                (output / old['report']).unlink(missing_ok=True)
    import shutil
    for folder in ('videos', 'reports'):
        (output / folder).mkdir(exist_ok=True)
        for file in (stage / folder).iterdir():
            shutil.copyfile(file, output / folder / file.name)
    (output / 'index.html').write_text(page)
    (output / '.nojekyll').touch()
    manifest.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n')
print(f'Gallery updated: {len(items)} videos across {len(snapshots)} branches')
