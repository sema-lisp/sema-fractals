# comet-ballet

A Sema-generated, non-fractal animation. Output: comet-ballet-1920-60fps.mp4 (1920 square, 60 fps, six seconds). The matching preview GIF loops forever at 20 fps.

Run from this directory: sema --no-llm animate.sema. Generate only the still: sema --no-llm render.sema. Source geometry is in comet-ballet.sema. Native rsvg-convert and FFmpeg provide rasterization and codecs. Rendering is at 3840 square before downsampling, with three-scale linear-RGB bloom.

verification.json is produced after frame count, frame rate, colour metadata, strict video decoding, and GIF loop checks pass.
