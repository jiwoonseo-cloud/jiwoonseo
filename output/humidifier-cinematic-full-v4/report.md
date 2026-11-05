# Cinematic v4 — revised action edit

The rejected v3 remains unchanged. This separate 109.37-second version replaces the flat ultrasonic diagram with a newly modeled reservoir cutaway: driver board and wiring, ceramic piezoelectric disc and electrode, seal and screws, water surface and open discharge chimney. Disc motion, upward disturbance, surface ripples, droplet separation and outlet mist follow the explanation. Sensor particles scatter a beam toward the detector; they do not physically strike the detector.

The former 69–73/77-second repetition is replaced by distinct actions in the new timeline: dissolved components at 55.63–62.79 seconds; water and solute emission at 62.79–70.93; evaporation and solid residue at 70.93–76.13; a drying water mark at 76.13–81.44. The opening mist, sensor entry, detector signal, dust/water comparison and final two-process comparison are also revised. The unnecessary generic-product disclaimer is removed. Diagram labels still disclose enlarged motion/particles.

## Speech and synchronization

All 26 sentences of the approved Korean script are preserved verbatim, including 72 short caption groups. This uses the supplied Supertonic M1 male narration, 109.37 seconds, preferred relatively by the user among previous samples. No post-synthesis speed change was applied. An independently synthesized 92-second Melo experiment was retained privately but not used. The final edit is about 20 seconds shorter than v3 because the supplied narration differs, not because v3 was sped up.

Paragraph timing was supplied with the voice. Whisper-small word timestamps were matched back to the exact approved text for caption timing; unmatched characters were interpolated. This is estimated alignment, not human-certified forced alignment. Actual auditory listening was unavailable in this execution interface. Pronunciation, prosody and subjective naturalness therefore remain UNVERIFIED; this must not be described as an approved natural voice. The archive's exact model-weight version/license was not independently established. No voice cloning or paid TTS API was used here.

## Visual references and scope

Direct pixel inspection: supplied cinematic storyboard and old v3 frames at 69 and 77 seconds; TDK/Humidifirst ultrasonic installation drawings at https://tdktransducers.com/ (tdk.jpg and tdk2.jpg). Those drawings informed submerged transducer, water-column and discharge relationships, not dimensions or a replica product.

The parent reviewed Know_n_eat https://www.youtube.com/watch?v=zMSHpXRUNX0 and TechNote and described continuous causal changes rather than camera-only motion. That direction informed this edit. This environment's YouTube download returned proxy 403; Instagram was throttled. Their actual videos were NOT independently watched here.

The device uses three newly rendered Blender Cycles plates at 720×1280, composited at 1080×1920 with procedural motion, droplets and lighting. This is a hybrid illustration, NOT a physical fluid simulation or continuous full-3D animation. Surface and particle scale are explanatory. Some render grain and photographic/CG texture differences remain. New plate pixels, a 5.72-second motion test decoded into frames, and the contact sheet were inspected; not every final frame was manually watched.

## Validation and delivery

- MP4 1080×1920, 24 fps, H.264 High level 4.1, yuv420p; AAC-LC 48 kHz; faststart.
- 2,621 video frames, 109.208333-second video stream; 109.370-second audio/container. The final audio extends about 0.162 seconds past the last video timestamp.
- Full final MP4 decode completed with exit 0 and no errors.
- Exact script and concatenated caption text equality passed (whitespace ignored only for caption segmentation).
- No actual iPhone or browser playback check was available. Compatible codec metadata does not establish device playback.
- No paid API, Veo, model training or fine-tuning was used. External API expenditure for this edit: zero. Hosted CPU resource cost is not exposed.
- Rendering took about 170 seconds for the final silent video. Three detailed CPU plates took roughly 110 seconds each; tests, speech alignment, assembly and review added time.

Run `python3 render_v4.py full` with Pillow/numpy, Noto Sans CJK fonts and ffmpeg to reproduce the silent composite. Supplied plates are included. `device.py` and `plates.py` are the Blender source scripts; run device then plates from this directory to rebuild the plates. Narration is embedded in the MP4; the source WAV is not duplicated in the public repository. `captions.srt`, `timeline.json`, `script.txt` and review/contact.jpg accompany the edit.

This is a revised review candidate, not a claim of user acceptance. Keep PR #23 draft and do not merge main without authorization.
