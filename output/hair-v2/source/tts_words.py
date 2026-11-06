import asyncio,ssl,json,pathlib
import edge_tts,edge_tts.communicate as comm
comm._SSL_CTX=ssl.create_default_context()
P=pathlib.Path('/workspace/work/hair-v2');S=json.loads((P/'script.json').read_text())
async def main():
 for i,txt in enumerate(S):
  out=P/f'edgewb_{i:02}.mp3';meta=[]
  if out.exists() and out.stat().st_size>1000:continue
  with out.open('wb') as f:
   async for c in edge_tts.Communicate(txt,voice='ko-KR-SunHiNeural',rate='+10%',boundary='WordBoundary',proxy='http://proxy:8080').stream():
    if c['type']=='audio':f.write(c['data'])
    elif c['type'] in ['SentenceBoundary','WordBoundary']:meta.append(c)
  (P/f'edgewb_{i:02}.json').write_text(json.dumps(meta,ensure_ascii=False))
  print(i,out.stat().st_size,flush=True)
asyncio.run(main())
