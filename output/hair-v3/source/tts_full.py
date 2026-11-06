import asyncio,ssl,pathlib,json,re
import edge_tts,edge_tts.communicate as comm
comm._SSL_CTX=ssl.create_default_context();P=pathlib.Path('/workspace/work/hair-v3');S=json.loads((P/'script.json').read_text())
async def main():
 for i,txt in enumerate(S):
  # Pronunciation words are unchanged. Punctuation normalization avoids long synthetic pauses.
  spoken=re.sub(r'[,\.]','',txt);meta=[]
  with (P/f'voice_{i:02}.mp3').open('wb') as f:
   async for c in edge_tts.Communicate(spoken,voice='ko-KR-HyunsuMultilingualNeural',rate='+0%',boundary='WordBoundary',proxy='http://proxy:8080').stream():
    if c['type']=='audio':f.write(c['data'])
    elif c['type']=='WordBoundary':meta.append(c)
  (P/f'voice_{i:02}.json').write_text(json.dumps(meta,ensure_ascii=False));print(i,'done',flush=True)
asyncio.run(main())
