// Field marks: linked state wildlife-agency references. Original wording and art.
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
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/bluegill",
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
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/largemouth",
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
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/pike",
  },
  {
    id: "smallmouth",
    name: "Smallmouth bass",
    scientific: "Micropterus dolomieu",
    title: "The rocky-river hunter",
    color: "#9BAF91",
    clues: "Bronze sides • vertical bars • shorter jaw",
    facts: [
      "Its jaw ends beneath the eye, rather than behind it.",
      "Bronze cheek streaks and dark vertical bars help separate it from largemouth bass.",
    ],
    habitat: "Rocky lakes and flowing rivers",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/smallmouth",
  },
  {
    id: "yellow-perch",
    name: "Yellow perch",
    scientific: "Perca flavescens",
    title: "The golden schoolmate",
    color: "#9BAF91",
    clues: "Yellow sides • dark upright bars • two top fins",
    facts: [
      "Look for a row of dark vertical bands on golden sides.",
      "Its spiny front dorsal fin is separate from the softer rear one.",
    ],
    habitat: "Lakes and slower rivers, often near vegetation",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/yellow-perch",
  },
  {
    id: "walleye",
    name: "Walleye",
    scientific: "Sander vitreus",
    title: "The low-light hunter",
    color: "#9BAF91",
    clues: "Reflective eyes • separate top fins • white lower tail tip",
    facts: [
      "A pale tip on the bottom of the tail is a useful clue.",
      "Look for a dark patch at the back of the spiny dorsal fin.",
    ],
    habitat: "Lakes and rivers, often close to deeper water",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/walleye",
  },
  {
    id: "pumpkinseed",
    name: "Pumpkinseed",
    scientific: "Lepomis gibbosus",
    title: "The painted sunfish",
    color: "#9BAF91",
    clues: "Red ear tip • blue cheek lines • orange belly",
    facts: [
      "A red accent marks the edge of its dark ear flap.",
      "Blue lines radiate across the cheek; its body is deep and rounded.",
    ],
    habitat: "Vegetated shallows around docks and fallen wood",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/pumpkinseed",
  },
  {
    id: "green-sunfish",
    name: "Green sunfish",
    scientific: "Lepomis cyanellus",
    title: "The creek explorer",
    color: "#9BAF91",
    clues: "Large mouth • blue cheek streaks • pale fin edges",
    facts: [
      "Its mouth is larger than a bluegill’s, with the jaw reaching under the eye.",
      "Look for blue-green cheek markings and light edges on the fins.",
    ],
    habitat: "Quiet creek pools and sheltered shallow water",
    source: "https://mdc.mo.gov/discover-nature/field-guide/green-sunfish",
  },
  {
    id: "rock-bass",
    name: "Rock bass",
    scientific: "Ambloplites rupestris",
    title: "The red-eyed ambusher",
    color: "#9BAF91",
    clues: "Red eyes • big mouth • rows of dark side marks",
    facts: [
      "The reddish eye is a helpful field mark.",
      "It has six anal-fin spines, more than most other familiar sunfish.",
    ],
    habitat: "Rocky shallows and streams with places to hide",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/rock-bass",
  },
  {
    id: "black-crappie",
    name: "Black crappie",
    scientific: "Pomoxis nigromaculatus",
    title: "The speckled schooler",
    color: "#9BAF91",
    clues: "Irregular dark flecks • deep body • tall top fin",
    facts: [
      "Dark markings scatter across its sides instead of forming clear bars.",
      "Counting seven or eight dorsal spines helps separate it from white crappie.",
    ],
    habitat: "Lakes and sheltered water with plants and woody cover",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/crappie",
  },
  {
    id: "white-crappie",
    name: "White crappie",
    scientific: "Pomoxis annularis",
    title: "The silver-barred schooler",
    color: "#9BAF91",
    clues: "Dark vertical bars • silvery sides • large mouth",
    facts: [
      "Its side markings often line up as vertical bars.",
      "It usually has five or six dorsal spines; black crappie have more.",
    ],
    habitat: "Lakes, backwaters, and slow rivers",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/crappie",
  },
  {
    id: "channel-catfish",
    name: "Channel catfish",
    scientific: "Ictalurus punctatus",
    title: "The whiskered river rover",
    color: "#9BAF91",
    clues: "Deeply forked tail • barbels • spotted sides",
    facts: [
      "Young fish often show dark spots on the sides; larger adults may lose them.",
      "The deeply forked tail separates it from bullheads and flathead catfish.",
    ],
    habitat: "Lakes and rivers with deeper pools and cover",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/catfish",
  },
  {
    id: "flathead-catfish",
    name: "Flathead catfish",
    scientific: "Pylodictis olivaris",
    title: "The logjam giant",
    color: "#9BAF91",
    clues: "Broad flat head • projecting lower jaw • square tail",
    facts: [
      "The broad, flattened head gives this fish its name.",
      "Its lower jaw projects forward and its tail lacks the channel catfish’s deep fork.",
    ],
    habitat: "Deep river pools and lakes with submerged wood",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/flathead-catfish",
  },
  {
    id: "brown-bullhead",
    name: "Brown bullhead",
    scientific: "Ameiurus nebulosus",
    title: "The mottled bottom explorer",
    color: "#9BAF91",
    clues: "Brown mottling • dark chin barbels • slightly notched tail",
    facts: [
      "Dark chin barbels help distinguish it from yellow bullhead.",
      "Its body has no scales; a soft adipose fin sits behind the main dorsal fin.",
    ],
    habitat: "Quiet, vegetated ponds, lakes, and river backwaters",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/bullheads",
  },
  {
    id: "yellow-bullhead",
    name: "Yellow bullhead",
    scientific: "Ameiurus natalis",
    title: "The golden-whiskered explorer",
    color: "#9BAF91",
    clues: "Pale chin barbels • yellow-brown body • nearly square tail",
    facts: [
      "Its pale chin barbels are a useful clue beside darker-barbelled bullheads.",
      "Check the nearly straight tail edge and the long anal fin.",
    ],
    habitat: "Sheltered pools and vegetated backwaters",
    source: "https://mdc.mo.gov/discover-nature/field-guide/yellow-bullhead",
  },
  {
    id: "black-bullhead",
    name: "Black bullhead",
    scientific: "Ameiurus melas",
    title: "The muddy-water explorer",
    color: "#9BAF91",
    clues: "Dark chin barbels • olive-black body • notched tail",
    facts: [
      "The chin barbels are dark, and the tail has a shallow notch.",
      "Similar bullheads can be hard to separate; keep the catch unidentified if the clues are unclear.",
    ],
    habitat: "Muddy pools, ponds, and slow backwaters",
    source: "https://mdc.mo.gov/discover-nature/field-guide/black-bullhead",
  },
  {
    id: "muskie",
    name: "Muskellunge",
    scientific: "Esox masquinongy",
    title: "The patient ambush hunter",
    color: "#9BAF91",
    clues: "Dark marks on light sides • long snout • rear top fin",
    facts: [
      "Look for dark markings on a lighter body, unlike a northern pike’s pale spots.",
      "The dorsal fin sits near the tail; patterns vary between individuals.",
    ],
    habitat: "Lakes and rivers with cover beside deeper water",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/muskie",
  },
  {
    id: "brook-trout",
    name: "Brook trout",
    scientific: "Salvelinus fontinalis",
    title: "The cold-stream jewel",
    color: "#9BAF91",
    clues: "Wormlike back marks • red side spots • white fin edges",
    facts: [
      "Red side spots may have blue halos; pale winding marks cover the back.",
      "Its lower fins have pale leading edges. Brook trout are Michigan’s state fish.",
    ],
    habitat: "Cold, clean streams and spring-fed lakes",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/brook-trout",
  },
  {
    id: "lake-trout",
    name: "Lake trout",
    scientific: "Salvelinus namaycush",
    title: "The deep-water wanderer",
    color: "#9BAF91",
    clues: "Light spots • deeply forked tail • small adipose fin",
    facts: [
      "Pale spots cover a darker body, and the tail is deeply forked.",
      "Unlike stream trout, lake trout often spend summer in deep, cold lake water.",
    ],
    habitat: "Deep, cold inland lakes",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/lake-trout",
  },
  {
    id: "white-bass",
    name: "White bass",
    scientific: "Morone chrysops",
    title: "The silver-striped schooler",
    color: "#9BAF91",
    clues: "Horizontal stripes • silver body • two separate top fins",
    facts: [
      "Several dark lengthwise stripes run along the silvery sides.",
      "It belongs to the temperate bass family, a different family from largemouth and smallmouth bass.",
    ],
    habitat: "Larger lakes and their connecting rivers",
    source:
      "https://www.michigan.gov/dnr/education/michigan-species/fish-species/white-bass",
  },
] as const;
export type SpeciesId = (typeof species)[number]["id"] | "unknown";
export const speciesIds: ReadonlySet<string> = new Set([
  ...species.map((f) => f.id),
  "unknown",
]);
export const baits = [
  "Not recorded",
  "Worm",
  "Minnow",
  "Jig",
  "Spinner",
  "Crankbait",
  "Soft plastic",
  "Topwater frog",
  "Spoon",
  "Spinnerbait",
  "Jerkbait",
  "Topwater popper",
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
  Spoon: "spoon",
  Spinnerbait: "spinnerbait",
  Jerkbait: "jerkbait",
  "Topwater popper": "popper",
};
export function fishName(id: string) {
  return species.find((f) => f.id === id)?.name ?? "Unidentified fish";
}
