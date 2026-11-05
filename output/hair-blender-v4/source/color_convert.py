import bpy,sys,pathlib,time,os
P=pathlib.Path(__file__).resolve().parent;stage=os.environ.get('STAGE','pilot');s=bpy.context.scene;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8'
args=sys.argv[sys.argv.index('--')+1:]
watch=args==['watch'];args=range(0,int(os.environ.get('TOTAL_FRAMES','3128'))) if watch and stage!='pilot' else range(1,241) if watch else args
if watch and os.environ.get('FRAME_LIST'):args=[int(q) for q in os.environ['FRAME_LIST'].split(',')]
for n in args:
 if (P/f'{stage}-frames/{int(n):04}.cached').exists():continue
 if watch:
  while not (P/f'{stage}-denoised/{int(n):04}.filtered').exists() and not (P/f'{stage}-frames/{int(n):04}.cached').exists():time.sleep(.2)
  if (P/f'{stage}-frames/{int(n):04}.cached').exists() or ((P/f'{stage}-denoised/{int(n):04}.png').exists() and not (P/f'{stage}-denoised/{int(n):04}.exr').exists()):continue
 im=bpy.data.images.load(str(P/f'{stage}-denoised/{int(n):04}.exr'),check_existing=False);im.save_render(str(P/f'{stage}-denoised/{int(n):04}.png'),scene=s);bpy.data.images.remove(im);print('COLOR_FRAME',n,flush=True)
 if watch:
  for f in [P/f'{stage}-frames/{int(n):04}.exr',P/f'{stage}-denoised/{int(n):04}.exr']:f.unlink(missing_ok=True)
