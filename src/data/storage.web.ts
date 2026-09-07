import { initialJournal, validateJournal, type Journal } from "./state";
const KEY = "fishdex-web-preview";
export function loadJournal(): Journal {
  const raw = localStorage.getItem(KEY);
  return raw ? validateJournal(JSON.parse(raw)) : initialJournal();
}
export function persistJournal(j: Journal) {
  localStorage.setItem(KEY, JSON.stringify(validateJournal(j)));
}
export function photoUri(name?: string) {
  return name;
}
export async function savePhoto(_uri: string): Promise<string> {
  throw new Error("Photo capture is available in the iPhone app.");
}
export async function exportBackup(_j: Journal): Promise<string> {
  throw new Error("Use the iPhone app to export a complete backup.");
}
export async function readBackup(
  _uri: string,
): Promise<{ journal: Journal; photos: Record<string, string> }> {
  throw new Error("Restore a backup in the iPhone app.");
}
export async function restoreBackup(
  _b: Awaited<ReturnType<typeof readBackup>>,
): Promise<Journal> {
  throw new Error("Restore a backup in the iPhone app.");
}
