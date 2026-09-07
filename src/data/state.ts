import { baits, type SpeciesId } from "./catalog.ts";
export type Profile = { id: string; name: string; color: string; bait: string };
export type Coordinates = {
  latitude: number;
  longitude: number;
  accuracy?: number;
  timestamp?: number;
};
export type Spot = { id: string; name: string; coordinate?: Coordinates };
export type Catch = {
  id: string;
  profileId: string;
  speciesId: SpeciesId;
  date: string;
  photo?: string;
  bait: string;
  coordinate?: Coordinates;
  spotId?: string;
  nickname?: string;
  notes?: string;
  length?: number;
  weight?: number;
  sex?: "male" | "female";
  disposition?: "released" | "kept";
  source: "camera" | "library" | "manual";
};
export type Journal = {
  version: 1;
  activeProfileId: string;
  profiles: Profile[];
  catches: Catch[];
  spots: Spot[];
};
export const colors = ["#527D8A", "#647E42", "#9D7537", "#7B6890", "#986959"];
export const uid = () =>
  `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
export function initialJournal(): Journal {
  return {
    version: 1,
    activeProfileId: "dad",
    profiles: ["Dad", "Mason", "Nolan"].map((name, i) => ({
      id: name.toLowerCase(),
      name,
      color: colors[i],
      bait: "Not recorded",
    })),
    catches: [],
    spots: [],
  };
}
export function removeProfile(
  j: Journal,
  id: string,
  transferTo?: string,
): Journal {
  if (j.profiles.length < 2 || !j.profiles.some((p) => p.id === id))
    throw new Error("Keep at least one angler.");
  if (
    transferTo &&
    (transferTo === id || !j.profiles.some((p) => p.id === transferTo))
  )
    throw new Error("Choose another angler.");
  const profiles = j.profiles.filter((p) => p.id !== id);
  return {
    ...j,
    profiles,
    activeProfileId:
      j.activeProfileId === id ? profiles[0].id : j.activeProfileId,
    catches: transferTo
      ? j.catches.map((c) =>
          c.profileId === id ? { ...c, profileId: transferTo } : c,
        )
      : j.catches.filter((c) => c.profileId !== id),
  };
}
export function badges(j: Journal, profileId: string) {
  const catches = j.catches.filter((c) => c.profileId === profileId);
  const discovered = new Set(
    catches.map((c) => c.speciesId).filter((id) => id !== "unknown"),
  );
  const record = catches.some(
    (c) =>
      c.speciesId !== "unknown" &&
      c.length &&
      catches.some(
        (older) =>
          older.speciesId === c.speciesId &&
          older.length &&
          Date.parse(older.date) < Date.parse(c.date) &&
          older.length < c.length!,
      ),
  );
  return [
    { name: "First catch", earned: catches.length > 0, icon: "☀" },
    { name: "Lake explorer", earned: discovered.size === 3, icon: "✦" },
    { name: "Personal best", earned: record, icon: "⚑" },
  ];
}
export function mergeCatchEdit(
  current: Catch,
  edited: Catch,
  locationEdited: boolean,
): Catch {
  return {
    ...edited,
    coordinate: locationEdited ? edited.coordinate : current.coordinate,
    spotId: locationEdited ? edited.spotId : current.spotId,
  };
}
function fail(): never {
  throw new Error(
    "This is not a valid Fishdex backup. Your current journal has not been changed.",
  );
}
const object = (x: unknown): x is Record<string, any> =>
  !!x && typeof x === "object" && !Array.isArray(x);
const str = (x: unknown, max = 5000): x is string =>
  typeof x === "string" && x.length <= max;
const id = (x: unknown) => str(x, 100) && /^[a-zA-Z0-9_-]+$/.test(x);
const coord = (c: unknown) =>
  c === undefined ||
  (object(c) &&
    Number.isFinite(c.latitude) &&
    Math.abs(c.latitude) <= 90 &&
    Number.isFinite(c.longitude) &&
    Math.abs(c.longitude) <= 180 &&
    (c.accuracy === undefined ||
      (Number.isFinite(c.accuracy) && c.accuracy >= 0)));
export function validateJournal(value: unknown): Journal {
  if (
    !object(value) ||
    value.version !== 1 ||
    !Array.isArray(value.profiles) ||
    !value.profiles.length ||
    value.profiles.length > 50 ||
    !Array.isArray(value.catches) ||
    value.catches.length > 50000 ||
    !Array.isArray(value.spots)
  )
    fail();
  const v = value as Journal;
  for (const p of v.profiles)
    if (
      !object(p) ||
      !id(p.id) ||
      !str(p.name, 40) ||
      !p.name.trim() ||
      !/^#[0-9a-f]{6}$/i.test(p.color) ||
      !baits.includes(p.bait as any)
    )
      fail();
  const profiles = new Set(v.profiles.map((p) => p.id));
  if (profiles.size !== v.profiles.length || !profiles.has(v.activeProfileId))
    fail();
  for (const s of v.spots)
    if (
      !object(s) ||
      !id(s.id) ||
      !str(s.name, 80) ||
      !s.name.trim() ||
      !coord(s.coordinate)
    )
      fail();
  const spots = new Set(v.spots.map((s) => s.id));
  if (spots.size !== v.spots.length) fail();
  for (const c of v.catches) {
    if (
      !object(c) ||
      !id(c.id) ||
      !profiles.has(c.profileId) ||
      !["bluegill", "bass", "pike", "unknown"].includes(c.speciesId) ||
      !str(c.date, 60) ||
      !Number.isFinite(Date.parse(c.date)) ||
      !baits.includes(c.bait as any) ||
      !coord(c.coordinate) ||
      (c.spotId !== undefined && !spots.has(c.spotId)) ||
      !["camera", "library", "manual"].includes(c.source)
    )
      fail();
    if (
      c.photo !== undefined &&
      (!str(c.photo, 300) || !/^[a-zA-Z0-9_-]+\.jpg$/.test(c.photo))
    )
      fail();
    for (const n of ["length", "weight"] as const)
      if (
        c[n] !== undefined &&
        (!Number.isFinite(c[n]) ||
          c[n]! <= 0 ||
          c[n]! > (n === "length" ? 100 : 200))
      )
        fail();
    for (const n of ["notes", "nickname"] as const)
      if (c[n] !== undefined && !str(c[n], n === "notes" ? 5000 : 80)) fail();
    if (c.sex !== undefined && !["male", "female"].includes(c.sex)) fail();
    if (
      c.disposition !== undefined &&
      !["released", "kept"].includes(c.disposition)
    )
      fail();
  }
  if (new Set(v.catches.map((c) => c.id)).size !== v.catches.length) fail();
  return v;
}
