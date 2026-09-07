import test from "node:test";
import assert from "node:assert/strict";
import { models } from "../src/generated/models.ts";
const names = [
  "bluegill",
  "bass",
  "pike",
  "worm",
  "minnow",
  "jig",
  "spinner",
  "crankbait",
  "soft-plastic",
  "frog",
];
test("all ten 3D specimens are valid self-contained GLB assets with no remote buffers or textures", () => {
  for (const name of names) {
    const buffer = Buffer.from(models[name], "base64");
    assert.equal(buffer.readUInt32LE(0), 0x46546c67, name);
    assert.equal(buffer.readUInt32LE(4), 2, name);
    assert.equal(buffer.readUInt32LE(8), buffer.length, name);
    const size = buffer.readUInt32LE(12);
    const gltf = JSON.parse(buffer.subarray(20, 20 + size).toString());
    assert.ok(gltf.meshes.length > 0, name);
    assert.equal(gltf.scenes.length, 1, `${name} must contain only its own scene`);
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
