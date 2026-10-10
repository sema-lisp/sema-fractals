# Evolving scenes

Kinetic Loom is a non-fractal, periodic 3D ribbon field. Eighty-four strands twist around a changing ring, with seventy-two orbiting lights. Both the shape and camera orientation evolve through smooth periodic functions.

All custom geometry, bloom definitions, timing, orchestration, and verification are Sema. Native rsvg-convert and FFmpeg provide rasterization and codecs.

Outputs: kinetic-loom-1920-60fps.mp4 (1920 square, 60 fps, six seconds), kinetic-loom-preview.gif (640 square, 20 fps, infinite loop), and kinetic-loom-still.png. Rasterization occurs at 3840 square before downsampling. The MP4 uses BT.709 colour primaries/matrix and the sRGB transfer function. Set repeat in your player to loop the MP4.

Run from this directory: sema --no-llm animate.sema. To regenerate only the still: sema --no-llm render.sema.

verification.json is written after output frame-count, frame-rate, colour metadata, strict decode, and GIF loop checks pass.

## Three additional designs

- Wave Atlas: rolling wave interference across a luminous perspective landscape.
- Comet Ballet: independently moving lights with short curved trails.
- Prism Engine: nested octahedral cages with different rotations and changing scales.

Run all three from this directory: sema --no-llm prepare-three.sema, then sema --no-llm animate-three.sema. The directories wave-atlas/, comet-ballet/, and prism-engine/ contain the sources and outputs.

The optional raster-bloom.sema file is a multiresolution bloom experiment. Current exports retain full-resolution bloom.
