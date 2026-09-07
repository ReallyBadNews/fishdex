import test from "node:test";
import assert from "node:assert/strict";
import { models } from "../src/generated/models.ts";
import { species, baitModel } from "../src/data/catalog.ts";
const names = [...species.map((f) => f.id), ...Object.values(baitModel)];
test("every catalog fish and bait has a valid self-contained GLB with no remote resources", () => {
  assert.deepEqual(Object.keys(models).sort(), [...names].sort());
  for (const name of names) {
    const buffer = Buffer.from(models[name], "base64");
    assert.equal(buffer.readUInt32LE(0), 0x46546c67, name);
    assert.equal(buffer.readUInt32LE(4), 2, name);
    assert.equal(buffer.readUInt32LE(8), buffer.length, name);
    const size = buffer.readUInt32LE(12);
    const gltf = JSON.parse(buffer.subarray(20, 20 + size).toString());
    if (species.some((fish) => fish.id === name)) {
      assert.ok(
        gltf.materials.some((material: { normalTexture?: { index: number } }) =>
          material.normalTexture !== undefined,
        ),
        `${name} preserves its skin relief in the runtime export`,
      );
    }
    assert.ok(gltf.meshes.length > 0, name);
    assert.ok(
      gltf.meshes.flatMap((m: { primitives: unknown[] }) => m.primitives)
        .length <= 16,
      `${name} stays within the mobile draw-call budget`,
    );
    assert.equal(
      gltf.scenes.length,
      1,
      `${name} must contain only its own scene`,
    );
    assert.ok(
      gltf.buffers.every((b: { uri?: string }) => !b.uri),
      name,
    );
    assert.ok(
      (gltf.images ?? []).every(
        (i: { uri?: string; bufferView?: number }) =>
          !i.uri && i.bufferView !== undefined,
      ),
      name,
    );
    assert.ok(
      !(gltf.extensionsRequired ?? []).some(
        (e: string) => e.includes("draco") || e.includes("meshopt"),
      ),
      name,
    );
  }
});
