#!/usr/bin/env python3
"""Map each video blob to the commit and PR that actually introduced its bytes.

Reads remote refs only. Does not check out or modify any production branch.
Requires GitHub CLI authentication (GH_TOKEN in Actions).
"""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])

def api(path):
    data=subprocess.check_output(['gh','api','--paginate',path],cwd=ROOT).decode()
    decoder=json.JSONDecoder()
    items=[]
    while data.strip():
        page,end=decoder.raw_decode(data.lstrip())
        items.extend(page)
        data=data.lstrip()[end:]
    return items

remote=git('remote','get-url','origin').decode().strip().removesuffix('.git')
if remote.startswith('git@github.com:'):
    repository=remote.split(':',1)[1]
elif remote.startswith('https://github.com/'):
    repository=remote.removeprefix('https://github.com/')
else:
    raise SystemExit('Expected a github.com origin')
refs=git('for-each-ref','--format=%(refname)','refs/remotes/origin').decode().splitlines()
videos={}
for ref in sorted(refs):
    branch=ref.removeprefix('refs/remotes/origin/')
    if branch=='HEAD' or branch.startswith('gallery/'):
        continue
    snapshot=git('rev-parse',ref).decode().strip()
    for entry in filter(None,git('ls-tree','-rz',snapshot).split(b'\0')):
        meta,raw_path=entry.split(b'\t',1)
        mode,kind,blob=meta.decode().split()
        path=raw_path.decode()
        if kind!='blob' or mode not in ('100644','100755') or not path.lower().endswith('.mp4') or path.startswith('docs/'):
            continue
        # Full-history traversal follows the actual file commit through merges.
        changed=git('log','-1','--format=%H%x00%ct',snapshot,'--',path).decode().strip().split('\0')
        if len(changed)!=2:
            raise RuntimeError(f'Cannot resolve video origin: {branch}:{path}')
        commit,timestamp=changed[0],int(changed[1])
        # Refuse to attach a commit if its path does not hold these exact video bytes.
        actual=git('rev-parse',commit+':'+path).decode().strip()
        if actual!=blob:
            raise RuntimeError(f'Origin hash mismatch: {branch}:{path}')
        v=videos.setdefault(blob,{'sources':[],'candidates':{}})
        v['sources'].append({'branch':branch,'path':path,'fileCommit':commit})
        old=v['candidates'].get(commit)
        if not old or path<old['path']:
            v['candidates'][commit]={'commit':commit,'timestamp':timestamp,'path':path}

cache={}
result={}
for blob,v in sorted(videos.items()):
    candidates=sorted(v.pop('candidates').values(),key=lambda c:(c['timestamp'],c['commit'],c['path']))
    # Earliest byte-identical file is the origin; later copies must not claim authorship.
    origin=candidates[0]
    commit=origin['commit']
    if commit not in cache:
        cache[commit]=api(f'repos/{repository}/commits/{commit}/pulls?per_page=100')
    prs=[]
    for pr in cache[commit]:
        head=pr.get('head',{}).get('ref','')
        if head.startswith('gallery/'):
            continue
        prs.append({'number':pr['number'],'title':pr['title'],'url':pr['html_url'],'branch':head,'state':pr['state'],'createdAt':pr['created_at']})
    prs.sort(key=lambda pr:(pr['createdAt'],pr['number']))
    result[blob]={**origin,'prs':prs,'sources':sorted(v['sources'],key=lambda x:(x['branch'],x['path'])),'method':'file-commit-pr' if prs else 'file-commit-no-pr'}
output=ROOT/'docs'/'provenance.json'
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps({'repository':repository,'videos':result},ensure_ascii=False,indent=2,sort_keys=True)+'\n')
print(f'Provenance: {len(result)} unique videos, {sum(bool(v["prs"]) for v in result.values())} linked to production PRs')
