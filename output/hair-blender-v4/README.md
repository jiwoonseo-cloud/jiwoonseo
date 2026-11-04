# Blender robot brush animation

- hair-animation.blend: native keyed geometry, cameras and component motion.
- test-10s.mp4 / test-contact-sheet.jpg: first hard-action gate.
- robot-hair-blender.mp4 / contact-sheet.jpg: completed 133.25-second film.
- report.md / scene-table.csv: scope, corrections and narration/action timing.
- source/: reproducible Blender scene, native baking, rendering and final edit.

Blender 4.3.2, FFmpeg, Python NumPy/Pillow, Noto CJK fonts. Run source/render.py with Blender, then source/finish.py with Python. Production used 16 native frame ranges and assembled them without frame interpolation. Paragraph 6 remains held by user decision.

Rebuild native scene in this order (each Blender invocation uses --python-exit-code 1):

1. source/build.py
2. source/bake_native.py
3. source/polish_native.py
4. source/finalize_scene.py
5. source/polish_hands.py
6. source/bench_layout.py
7. source/clarify_dust.py
8. source/render.py -- --mode full --chunk N --chunks 16
9. python source/finish.py --mode audio, then --mode full --chunks 16

Scripts resolve the output folder relative to their location. Render intermediates live in repository work/hair-blender-v4. The .blend itself contains native shape keys and does not require a custom deformation callback to play.

After rendering, source/document_actual_scenes.py writes the as-built word/action tables.
