export type SpeciesId = "bluegill" | "bass" | "pike" | "unknown";
export const species = [
  {
    id: "bluegill",
    name: "Bluegill",
    scientific: "Lepomis macrochirus",
    title: "The little lake explorer",
    color: "#A8B98B",
    clues: "Round, deep body • small mouth • black ear flap",
    facts: [
      "Look for a dark flap behind the eye and a dark spot near the back of the top fin.",
      "Weed beds and submerged logs make good bluegill hiding places.",
      "Its long, pointed side fins help you tell it from other sunfish.",
    ],
    habitat: "Warm lakes, ponds, and sheltered shallows",
    source: "bluegill",
  },
  {
    id: "bass",
    name: "Largemouth bass",
    scientific: "Micropterus nigricans",
    title: "The ambush artist",
    color: "#92A982",
    clues: "Big mouth • dark side stripe • notched top fin",
    facts: [
      "Its upper jaw reaches beyond the back of its eye.",
      "Look for a dark stripe running along its green sides.",
      "Weeds, fallen trees, and docks offer places to hide and ambush prey.",
    ],
    habitat: "Weedy lakes and quiet, sheltered water",
    source: "largemouth",
  },
  {
    id: "pike",
    name: "Northern pike",
    scientific: "Esox lucius",
    title: "The reed-bed hunter",
    color: "#8AAEAB",
    clues: "Long body • pale spots • top fin near tail",
    facts: [
      "Pale spots stand out against its darker body.",
      "Its single top fin sits far back, close to the tail.",
      "Weedy shallows and fallen timber are favorite hiding places.",
    ],
    habitat: "Weedy shallows, lakes, and slow rivers",
    source: "pike",
  },
] as const;
export const baits = [
  "Not recorded",
  "Worm",
  "Minnow",
  "Jig",
  "Spinner",
  "Crankbait",
  "Soft plastic",
  "Topwater frog",
  "Other",
] as const;
export const baitModel: Record<string, string> = {
  Worm: "worm",
  Minnow: "minnow",
  Jig: "jig",
  Spinner: "spinner",
  Crankbait: "crankbait",
  "Soft plastic": "soft-plastic",
  "Topwater frog": "frog",
};
export function fishName(id: string) {
  return species.find((s) => s.id === id)?.name ?? "Unidentified fish";
}
