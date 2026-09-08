"""Verify revision 4 source libraries and refresh their manifest in Blender.

blender -b --factory-startup --python-exit-code 1 --python scripts/modeling/verify_refined.py
Only reads .blend/GLB assets. Writes the aggregate manifest after all checks pass.
"""
import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/blender/v4"
records = []
names = sorted(p.stem for p in (ROOT / "assets/models").glob("*.glb"))
assert len(names) == 31, "Unexpected runtime catalog inventory"
for name in names:
    record = json.loads((SOURCE / f"{name}.json").read_text())
    source = SOURCE / f"{name}.blend"
    runtime = ROOT / "assets/models" / f"{name}.glb"
    assert record["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest(), name
    assert record["glb_sha256"] == hashlib.sha256(runtime.read_bytes()).hexdigest(), name
    with bpy.data.libraries.load(str(source), link=False) as (library, loaded):
        assert library.scenes == [record["scene"]], (name, library.scenes)
        loaded.images = library.images
    assert all(image.packed_file for image in loaded.images), f"{name}: unpacked texture"
    record["packed_images"] = len(loaded.images)
    for image in loaded.images:
        bpy.data.images.remove(image)
    assert record["primitives"] <= 16, name
    assert record["triangles"] < 100_000, name
    assert record["glb_bytes"] < 3 * 1024 * 1024, name
    records.append(record)
total = sum(r["glb_bytes"] for r in records)
assert total < 64 * 1024 * 1024
manifest = {
    "revision": 4,
    "blender": bpy.app.version_string,
    "asset_count": len(records),
    "scene_count": len(records),
    "runtime_bytes": total,
    "generator_sha256": hashlib.sha256((ROOT / "scripts/modeling/build_refined.py").read_bytes()).hexdigest(),
    "files": records,
}
(SOURCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"VERIFIED {len(records)} editable scenes, packed images, runtime exports; {total} GLB bytes.")
