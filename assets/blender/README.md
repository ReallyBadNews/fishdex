# Blender source archive

Every historical scene is retained. Open a `.blend` normally, or use Blender **File → Append → Scene** to bring selected scenes into another project. Images are packed; no texture downloads are needed.

- `../models/fishdex-source.blend`: all 57 scenes present before the realism pass, including early studies, alternate renders, the app emblem, and the original default scene. `archive-manifest.json` records scene names and the file checksum.
- `v3/<asset>.blend`: version 3 editable scenes, previous version 3 iterations, and export copies for that fish or lure. Objects remain separate in editable scenes; runtime copies are joined for mobile rendering.
- `v3/manifest.json`: exact saved scene inventory, file checksums, and asset identifiers, verified by reopening each library's scene list.

The source files are excluded from EAS uploads. Only the generated GLBs and specimen thumbnails ship in the app. No source scenes are deleted when rebuilding. `scripts/modeling/build_realistic.py` documents the deterministic modeling pipeline; load it after the four earlier modeling scripts, then call `build_realistic('bass')`, for example. The builder loads existing revisions before a fresh-session rebuild. Call `archive_realism()` after a batch to refresh and verify the complete inventory.

These are original illustrative studies with improved materials and anatomy, not measured anatomical reconstructions or independently validated photorealistic models.
