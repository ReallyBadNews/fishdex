import Storage from "expo-sqlite/kv-store";
import * as FS from "expo-file-system/legacy";
import * as ImageManipulator from "expo-image-manipulator";
import { initialJournal, validateJournal, uid, type Journal } from "./state";
const KEY = "fishdex-journal-v1";
const photoDir = `${FS.documentDirectory}catches/`;
export function loadJournal(): Journal {
  const raw = Storage.getItemSync(KEY);
  return raw ? validateJournal(JSON.parse(raw)) : initialJournal();
}
export function persistJournal(j: Journal) {
  Storage.setItemSync(KEY, JSON.stringify(validateJournal(j)));
}
export function photoUri(name?: string) {
  return name ? photoDir + name : undefined;
}
export async function savePhoto(uri: string) {
  await FS.makeDirectoryAsync(photoDir, { intermediates: true });
  const clean = await ImageManipulator.manipulateAsync(
    uri,
    [{ resize: { width: 1600 } }],
    { compress: 0.85, format: ImageManipulator.SaveFormat.JPEG },
  );
  const name = `${uid()}.jpg`;
  await FS.copyAsync({ from: clean.uri, to: photoDir + name });
  return name;
}
export async function exportBackup(journal: Journal) {
  const photos: Record<string, string> = {};
  for (const c of journal.catches)
    if (c.photo && !photos[c.photo])
      photos[c.photo] = await FS.readAsStringAsync(photoDir + c.photo, {
        encoding: FS.EncodingType.Base64,
      });
  const uri = `${FS.cacheDirectory}Fishdex-backup-${new Date().toISOString().slice(0, 10)}.json`;
  await FS.writeAsStringAsync(
    uri,
    JSON.stringify({
      format: "fishdex-backup",
      version: 1,
      exportedAt: new Date().toISOString(),
      journal,
      photos,
    }),
  );
  return uri;
}
export async function readBackup(uri: string) {
  const info = await FS.getInfoAsync(uri);
  if (!info.exists || (info.size ?? 0) > 250 * 1024 * 1024)
    throw new Error("Choose a Fishdex backup smaller than 250 MB.");
  const value = JSON.parse(await FS.readAsStringAsync(uri));
  if (
    value?.format !== "fishdex-backup" ||
    value.version !== 1 ||
    !value.photos ||
    typeof value.photos !== "object" ||
    Array.isArray(value.photos)
  )
    throw new Error("Choose a valid Fishdex backup.");
  const journal = validateJournal(value.journal);
  for (const c of journal.catches)
    if (
      c.photo &&
      (typeof value.photos[c.photo] !== "string" ||
        !/^[A-Za-z0-9+/]+={0,2}$/.test(value.photos[c.photo]) ||
        !value.photos[c.photo].startsWith("/9j/"))
    )
      throw new Error("The backup is missing a valid catch photo.");
  return { journal, photos: value.photos as Record<string, string> };
}
export async function restoreBackup(
  backup: Awaited<ReturnType<typeof readBackup>>,
) {
  await FS.makeDirectoryAsync(photoDir, { intermediates: true });
  const names = new Map<string, string>();
  // New names keep the existing journal's photos intact if restoration fails.
  for (const c of backup.journal.catches)
    if (c.photo && !names.has(c.photo)) {
      const name = `${uid()}.jpg`;
      await FS.writeAsStringAsync(photoDir + name, backup.photos[c.photo], {
        encoding: FS.EncodingType.Base64,
      });
      names.set(c.photo, name);
    }
  const j = {
    ...backup.journal,
    catches: backup.journal.catches.map((c) => ({
      ...c,
      photo: c.photo ? names.get(c.photo) : undefined,
    })),
  };
  persistJournal(j);
  return j;
}
