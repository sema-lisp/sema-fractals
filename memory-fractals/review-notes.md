# Native Sema animation tool review

Reviewed new Sema drawing and animation files from no-index diffs, without creating a Git repository.

Corrected repeated list copying by changing path buffers to mutable arrays. Confirmed finite coordinate checks, fixed viewport bounds, shared-buffer separation, source endpoint equality, motion, subprocess exit handling, safe argument quoting, binary stdout separation from progress, frame validation, resolution, and frame-rate verification. Added early rejection for invalid names, modes, and frame counts.

A four-frame 60-fps end-to-end pipeline passed before the full render. The deeper geometry stress suite passed all five cases. Full video verification records are written only after each encoder and probe complete.

Sema limitations encountered: regular-file stream APIs reject FIFO handles, and proc/write-stdin is text-oriented. The tool uses CLI binary stdout with a standard process pipeline instead. Native SVG rasterization and FFmpeg supply antialiasing, filters, and codecs; all custom source and orchestration are Sema.

Verdict: Approve. All three 240-frame, 1920-square, 60-fps outputs passed frame-count and frame-rate checks, strict full-video decoding, and infinite GIF loop-extension checks.
