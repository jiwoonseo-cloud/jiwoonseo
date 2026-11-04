from pathlib import Path
from PIL import Image,ImageOps
P=Path(__file__).resolve().parent
im=ImageOps.fit(Image.open(P/'assets/master.jpg'),(1080,1920),method=Image.Resampling.LANCZOS)
# One intentional static discovery shot. No action is represented by a pan/zoom.
for f in range(151,193):im.save(P/f'frames/{f:05}.jpg',quality=94)
