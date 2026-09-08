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
        gltf.materials.some(
          (material: { normalTexture?: { index: number } }) =>
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

test("refined models preserve mapped textures after joining and fit the mobile asset budget", () => {
  let totalBytes = 0;
  for (const name of names) {
    const buffer = Buffer.from(models[name], "base64");
    totalBytes += buffer.length;
    assert.ok(
      buffer.length < 3 * 1024 * 1024,
      `${name}: compact offline asset`,
    );
    const jsonSize = buffer.readUInt32LE(12);
    const gltf = JSON.parse(buffer.subarray(20, 20 + jsonSize).toString());
    const binaryStart = 28 + jsonSize;
    let triangles = 0;
    for (const mesh of gltf.meshes) {
      for (const primitive of mesh.primitives) {
        const indices = gltf.accessors[primitive.indices];
        triangles += indices.count / 3;
        const material = gltf.materials[primitive.material];
        const texture = material.pbrMetallicRoughness?.baseColorTexture;
        if (!texture) continue;
        const uvIndex =
          primitive.attributes[`TEXCOORD_${texture.texCoord ?? 0}`];
        assert.notEqual(
          uvIndex,
          undefined,
          `${name}: ${material.name} has UVs`,
        );
        const uv = gltf.accessors[uvIndex];
        assert.equal(uv.type, "VEC2");
        assert.equal(uv.componentType, 5126);
        const view = gltf.bufferViews[uv.bufferView];
        const start =
          binaryStart + (view.byteOffset ?? 0) + (uv.byteOffset ?? 0);
        let minU = Infinity,
          maxU = -Infinity,
          minV = Infinity,
          maxV = -Infinity;
        for (let i = 0; i < uv.count; i++) {
          const offset = start + i * (view.byteStride ?? 8);
          const u = buffer.readFloatLE(offset);
          const v = buffer.readFloatLE(offset + 4);
          assert.ok(Number.isFinite(u) && Number.isFinite(v), name);
          minU = Math.min(minU, u);
          maxU = Math.max(maxU, u);
          minV = Math.min(minV, v);
          maxV = Math.max(maxV, v);
        }
        assert.ok(
          maxU - minU > 0.25 && maxV - minV > 0.25,
          `${name}: ${material.name} must not collapse to a single texel during mesh joining`,
        );
      }
    }
    assert.ok(triangles < 100_000, `${name}: ${triangles} triangles`);
  }
  assert.ok(
    totalBytes < 64 * 1024 * 1024,
    "the complete catalog fits its offline budget",
  );
});
