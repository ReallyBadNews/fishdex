import test from "node:test";
import assert from "node:assert/strict";
import {
  initialJournal,
  validateJournal,
  removeProfile,
  badges,
  mergeCatchEdit,
  type Catch,
} from "../src/data/state.ts";
import { weightGuide } from "../src/data/weight.ts";
const catchOne: Catch = {
  id: "catch-1",
  profileId: "mason",
  speciesId: "bluegill",
  date: "2026-09-07T14:00:00.000Z",
  bait: "Worm",
  source: "camera",
  photo: "photo-1.jpg",
  length: 6,
};
test("journal round-trip preserves family profiles, catches and private coordinates", () => {
  const j = initialJournal();
  j.catches.push({
    ...catchOne,
    coordinate: { latitude: 44.1, longitude: -85.2, accuracy: 12 },
  });
  assert.deepEqual(validateJournal(JSON.parse(JSON.stringify(j))), j);
});
test("editing details preserves a GPS fix that arrived after opening the form, unless location was explicitly changed", () => {
  const current = { ...catchOne, coordinate: { latitude: 44, longitude: -85 } };
  const edited = { ...catchOne, nickname: "First bluegill" };
  assert.deepEqual(
    mergeCatchEdit(current, edited, false).coordinate,
    current.coordinate,
  );
  assert.equal(mergeCatchEdit(current, edited, true).coordinate, undefined);
});
test("removing an angler transfers catches and switches active profile without losing spots", () => {
  const j = initialJournal();
  j.activeProfileId = "mason";
  j.catches = [catchOne];
  j.spots = [{ id: "lake", name: "Family lake" }];
  const next = removeProfile(j, "mason", "dad");
  assert.equal(next.catches[0].profileId, "dad");
  assert.equal(next.activeProfileId, "dad");
  assert.deepEqual(next.spots, j.spots);
  assert.equal(j.catches[0].profileId, "mason");
});
test("profile deletion only removes the selected angler’s catches", () => {
  const j = initialJournal();
  j.catches = [catchOne, { ...catchOne, id: "catch-2", profileId: "nolan" }];
  const next = removeProfile(j, "mason");
  assert.equal(next.catches.length, 1);
  assert.equal(next.catches[0].profileId, "nolan");
  assert.throws(() =>
    removeProfile({ ...j, profiles: [j.profiles[0]] }, "dad"),
  );
  assert.throws(() => removeProfile(j, "mason", "mason"));
});
test("backups reject broken relations, duplicate IDs, unsafe photo names and invalid measurements", () => {
  for (const patch of [
    { profileId: "missing" },
    { spotId: "missing" },
    { photo: "../../elsewhere.jpg" },
    { coordinate: { latitude: 120, longitude: 0 } },
    { weight: -2 },
    { length: Infinity },
    { sex: "unknown" },
    { date: "not a date" },
    { speciesId: "fake" },
  ]) {
    const j = initialJournal();
    j.catches = [{ ...catchOne, ...patch } as Catch];
    assert.throws(() => validateJournal(j));
  }
  const duplicate = initialJournal();
  duplicate.catches = [catchOne, catchOne];
  assert.throws(() => validateJournal(duplicate));
});
test("badges are profile-specific and an unidentified catch does not unlock a species", () => {
  const j = initialJournal();
  j.catches = [{ ...catchOne, speciesId: "unknown" }];
  assert.equal(badges(j, "mason")[0].earned, true);
  assert.equal(badges(j, "mason")[1].earned, false);
  assert.ok(badges(j, "nolan").every((b) => !b.earned));
});
test("personal-best badge requires a prior smaller measurement for the same species", () => {
  const j = initialJournal();
  j.catches = [
    catchOne,
    { ...catchOne, id: "catch-2", length: 8, date: "2026-09-08T14:00:00Z" },
  ];
  assert.equal(badges(j, "mason")[2].earned, true);
  j.catches[1].speciesId = "bass";
  assert.equal(badges(j, "mason")[2].earned, false);
});
test("length-based guides use documented units and reject unsupported lengths", () => {
  assert.equal(weightGuide("pike", 35), 12.25);
  assert.equal(weightGuide("bluegill", 6), 0.18);
  assert.ok(Math.abs(weightGuide("bass", 12)! - 0.917) < 0.02);
  assert.equal(weightGuide("unknown", 12), undefined);
  assert.equal(weightGuide("bass", 3), undefined);
  assert.equal(weightGuide("bluegill", NaN), undefined);
});

test("expanded catalog catches survive persistence and keep the three-species explorer badge", async () => {
  const { species, baits } = await import("../src/data/catalog.ts");
  const j = initialJournal();
  j.catches = species.map((fish, i) => ({
    ...catchOne,
    id: `expanded-${i}`,
    speciesId: fish.id,
    bait: baits[i % baits.length],
  }));
  assert.deepEqual(validateJournal(JSON.parse(JSON.stringify(j))), j);
  assert.equal(
    badges(j, catchOne.profileId).find((b) => b.name === "Lake explorer")
      ?.earned,
    true,
  );
  j.catches[0].speciesId =
    "nonexistent-species" as (typeof j.catches)[0]["speciesId"];
  assert.throws(() => validateJournal(j));
});
