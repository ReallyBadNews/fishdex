# Blender source archive

Every historical scene is retained. Open a `.blend` normally, or use Blender **File → Append → Scene** to bring selected scenes into another project. Images are packed; no texture downloads are needed.

- `../models/fishdex-source.blend`: all 57 scenes present before the realism pass, including early studies, alternate renders, the app emblem, and the original default scene. `archive-manifest.json` records scene names and the file checksum.
- `v3/<asset>.blend`: version 3 editable scenes, previous version 3 iterations, and export copies for that fish or lure. Objects remain separate in editable scenes; runtime copies are joined for mobile rendering.
- `v3/manifest.json`: exact saved scene inventory, file checksums, and asset identifiers, verified by reopening each library's scene list.
- `v4/<asset>.blend`: the current refinement, with separate editable meshes, packed color/normal/roughness textures, and a studio camera. The 31 per-asset JSON records and `v4/manifest.json` inventory the source scenes and runtime exports. All earlier archives remain intact.

The source files are excluded from EAS uploads. Only the generated GLBs and specimen thumbnails ship in the app. No source scenes are deleted when rebuilding. `scripts/modeling/build_realistic.py` documents the deterministic modeling pipeline; load it after the four earlier modeling scripts, then call `build_realistic('bass')`, for example. The builder loads existing revisions before a fresh-session rebuild. Call `archive_realism()` after a batch to refresh and verify the complete inventory.

These are original illustrative studies with improved materials and anatomy, not measured anatomical reconstructions or independently validated photorealistic models.

For the current revision, run `blender -b --factory-startup --python-exit-code 1 --python scripts/modeling/build_refined.py -- bass` from the repository root. Replace `bass` with any catalog model ID. Use a fresh Blender process for each asset to bound memory. The builder resolves the checkout path itself and only writes revision 4 sources, runtime GLBs, specimen PNGs, and angled review renders. Run `npm run models:bundle` afterward. [Revision 4 review](../../docs/model-review/v4/index.html) includes every model.
