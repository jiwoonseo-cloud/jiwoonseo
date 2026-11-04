# Blender robot brush animation

- hair-animation.blend: native keyed geometry, cameras and component motion.
- test-10s.mp4 / test-contact-sheet.jpg: first hard-action gate.
- robot-hair-blender.mp4 / contact-sheet.jpg: completed film (added after full rendering).
- report.md / scene-table.csv: scope, corrections and narration/action timing.
- source/: reproducible Blender scene, native baking, rendering and final edit.

Blender 4.3.2, FFmpeg, Python NumPy/Pillow, Noto CJK fonts. Run source/render.py with Blender, then source/finish.py with Python. The one-off workflow renders native full frames in 16 chunks and assembles them without frame interpolation. Paragraph 6 remains held by user decision.
