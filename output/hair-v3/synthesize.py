"""Natural speed Korean narration. Requires edge-tts; explicit user consent obtained.
Paragraph 6 is deliberately not synthesized: user requested production hold.
TLS verification stays enabled with the environment CA bundle.
"""
import asyncio,importlib,json,os
from pathlib import Path
import edge_tts
for name in ['edge_tts.communicate','edge_tts.voices']:
 importlib.import_module(name)._SSL_CTX.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
BASE=Path(__file__).resolve().parent
paragraphs=[p.strip() for p in (BASE/'script-original.txt').read_text().split('\n\n')]
async def main():
 for voice in ['ko-KR-HyunsuMultilingualNeural','ko-KR-InJoonNeural','ko-KR-SunHiNeural']:
  out=BASE/'narration'/voice;out.mkdir(parents=True,exist_ok=True)
  for i,text in enumerate(paragraphs,1):
   if i==6:continue
   if (out/f'{i:02d}.json').exists():continue
   talk=edge_tts.Communicate(text,voice,rate='+0%',proxy=os.environ.get('HTTPS_PROXY'),boundary='WordBoundary')
   events=[];sub=edge_tts.SubMaker()
   with (out/f'{i:02d}.mp3').open('wb') as f:
    async for e in talk.stream():
     if e['type']=='audio':f.write(e['data'])
     elif e['type']=='WordBoundary':
      events.append(e);sub.feed(e)
   (out/f'{i:02d}.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
   (out/f'{i:02d}.srt').write_text(sub.get_srt())
   print(voice,i,'complete',flush=True)
asyncio.run(main())
