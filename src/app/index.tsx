import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  Image,
  ScrollView,
  Pressable,
  StyleSheet,
  Alert,
  Linking,
  ActivityIndicator,
  Platform,
  Animated,
  AccessibilityInfo,
  Modal,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import * as Location from "expo-location";
import * as Sharing from "expo-sharing";
import * as DocumentPicker from "expo-document-picker";
import * as Speech from "expo-speech";
import * as Haptics from "expo-haptics";
import { captureRef } from "react-native-view-shot";
import {
  species,
  baits,
  baitModel,
  fishName,
  type SpeciesId,
} from "@/data/catalog";
import {
  initialJournal,
  uid,
  colors,
  removeProfile,
  mergeCatchEdit,
  badges,
  type Journal,
  type Catch,
  type Coordinates,
  type Profile,
  type Spot,
} from "@/data/state";
import {
  loadJournal,
  persistJournal,
  savePhoto,
  photoUri,
  exportBackup,
  readBackup,
  restoreBackup,
} from "@/data/storage";
import { weightGuide } from "@/data/weight";
import { ModelView } from "@/components/model-view";
import { SpotMap } from "@/components/spot-map";
import {
  Button,
  Field,
  Select,
  Sheet,
  Copy,
  Title,
  C,
  s,
} from "@/components/journal-ui";

const pictures: Record<string, number> = {
  bluegill: require("../../assets/specimens/bluegill.png"),
  bass: require("../../assets/specimens/bass.png"),
  pike: require("../../assets/specimens/pike.png"),
};
const dateLabel = (date: string) =>
  new Date(date).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
const dateInput = (iso: string) => {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
};
const speciesOptions = [
  ...species.map((f) => ({ value: f.id, label: f.name })),
  { value: "unknown", label: "Not sure / another species" },
];
const baitOptions = baits.map((b) => ({ value: b, label: b }));
function error(e: unknown) {
  Alert.alert(
    "Something needs attention",
    e instanceof Error ? e.message : "Please try again.",
  );
}
function confirm(
  title: string,
  message: string,
  action: () => void,
  destructive = false,
) {
  if (Platform.OS === "web") {
    if (window.confirm(`${title}\n${message}`)) action();
  } else
    Alert.alert(title, message, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Continue",
        style: destructive ? "destructive" : "default",
        onPress: action,
      },
    ]);
}
async function currentCoordinate(): Promise<Coordinates | undefined> {
  if (Platform.OS === "web") return;
  const permission = await Location.requestForegroundPermissionsAsync();
  if (!permission.granted) return;
  const result = await Promise.race([
    Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced }),
    new Promise<undefined>((r) => setTimeout(() => r(undefined), 10000)),
  ]);
  if (!result) return;
  return {
    latitude: result.coords.latitude,
    longitude: result.coords.longitude,
    accuracy: result.coords.accuracy ?? undefined,
    timestamp: result.timestamp,
  };
}
type Draft = {
  photo?: string;
  source: Catch["source"];
  speciesId: SpeciesId;
  date: string;
  dateConfirmed: boolean;
  profileId: string;
  coordinate?: Coordinates;
};
type Page = "journal" | "collection" | "spots" | "kit";
type Overlay =
  | { kind: "profiles" }
  | { kind: "profile"; id?: string }
  | { kind: "scan" }
  | { kind: "confirm" }
  | { kind: "catchDate" }
  | { kind: "fish"; id: string }
  | { kind: "catch"; id: string }
  | { kind: "edit"; id: string }
  | { kind: "reveal"; id: string; isNew: boolean }
  | { kind: "spot"; id?: string; coordinate?: Coordinates }
  | { kind: "tackle"; id: string; name: string }
  | null;
export default function Fishdex() {
  const [journal, setJournal] = useState<Journal>(initialJournal);
  const state = useRef(journal);
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [page, setPage] = useState<Page>("journal");
  const [overlay, setOverlay] = useState<Overlay>(null);
  const [busy, setBusy] = useState(false);
  const [draft, setDraft] = useState<Draft>();
  const [permission, requestPermission] = useCameraPermissions();
  const camera = useRef<CameraView>(null);
  const gps = useRef<Promise<Coordinates | undefined>>(
    Promise.resolve(undefined),
  );
  const [ready, setReady] = useState(false);
  const [filter, setFilter] = useState("all");
  const [toast, setToast] = useState("");
  const saveLock = useRef(false);
  useEffect(() => {
    try {
      const j = loadJournal();
      persistJournal(j);
      state.current = j;
      setJournal(j);
    } catch (e) {
      setLoadError(
        e instanceof Error ? e.message : "Could not load your journal.",
      );
    }
    setLoaded(true);
  }, []);
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(""), 3500);
      return () => clearTimeout(t);
    }
  }, [toast]);
  const commit = (fn: (j: Journal) => Journal) => {
    const next = fn(state.current);
    persistJournal(next);
    state.current = next;
    setJournal(next);
  };
  const close = () => {
    if (busy) return;
    void Speech.stop();
    setOverlay(null);
  };
  const profile = journal.profiles.find(
    (p) => p.id === journal.activeProfileId,
  )!;
  const catches = journal.catches
    .filter((c) => c.profileId === profile.id)
    .sort((a, b) => Date.parse(b.date) - Date.parse(a.date));
  const discovered = new Set(
    catches.map((c) => c.speciesId).filter((id) => id !== "unknown"),
  );
  const run = async (fn: () => Promise<void>) => {
    if (saveLock.current) return;
    saveLock.current = true;
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      error(e);
    } finally {
      saveLock.current = false;
      setBusy(false);
    }
  };
  function startScan() {
    setDraft(undefined);
    setReady(false);
    gps.current = Promise.resolve(undefined);
    setOverlay({ kind: "scan" });
  }
  async function capture(source: "camera" | "library" | "manual") {
    await run(async () => {
      let uri: string | undefined;
      let date = new Date().toISOString();
      if (source === "camera") {
        const photo = await camera.current?.takePictureAsync({ quality: 0.85 });
        if (!photo) return;
        uri = photo.uri;
        gps.current = currentCoordinate().catch(() => undefined);
      }
      if (source === "library") {
        const result = await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ["images"],
          quality: 0.9,
          exif: true,
        });
        if (result.canceled) return;
        uri = result.assets[0].uri;
        const raw = result.assets[0].exif?.DateTimeOriginal;
        if (typeof raw === "string") {
          const parsed = new Date(
            raw
              .replace(/^(\d{4}):(\d{2}):(\d{2})/, "$1-$2-$3")
              .replace(" ", "T"),
          );
          if (Number.isFinite(parsed.getTime())) date = parsed.toISOString();
        }
      }
      const photo = uri ? await savePhoto(uri) : undefined;
      if (source === "manual")
        gps.current = currentCoordinate().catch(() => undefined);
      setDraft({
        source,
        photo,
        date,
        dateConfirmed: source !== "library",
        profileId: profile.id,
        speciesId: "unknown",
      });
      setOverlay({ kind: "confirm" });
    });
  }
  async function caughtIt(snapshot = draft) {
    if (!snapshot) return;
    if (!snapshot.dateConfirmed) {
      setOverlay({ kind: "catchDate" });
      return;
    }
    await run(async () => {
      const c: Catch = {
        id: uid(),
        profileId: snapshot.profileId,
        speciesId: snapshot.speciesId,
        date: snapshot.date,
        photo: snapshot.photo,
        bait: state.current.profiles.find((p) => p.id === snapshot.profileId)!
          .bait,
        source: snapshot.source,
        coordinate: snapshot.coordinate,
      };
      const isNew =
        c.speciesId !== "unknown" &&
        !state.current.catches.some(
          (old) =>
            old.profileId === c.profileId && old.speciesId === c.speciesId,
        );
      commit((j) => ({ ...j, catches: [c, ...j.catches] }));
      setOverlay({ kind: "reveal", id: c.id, isNew });
      setDraft(undefined);
      void Haptics.notificationAsync(
        Haptics.NotificationFeedbackType.Success,
      ).catch(() => {});
      if (snapshot.source !== "library") {
        void gps.current.then((coordinate) => {
          if (coordinate) {
            try {
              commit((j) => ({
                ...j,
                catches: j.catches.map((old) =>
                  old.id === c.id && !old.coordinate && !old.spotId
                    ? { ...old, coordinate }
                    : old,
                ),
              }));
            } catch {
              /* Catch itself is already safely saved; location is optional. */
            }
          }
        });
      }
    });
  }
  const updateCatch = (c: Catch, locationEdited: boolean) => {
    try {
      commit((j) => ({
        ...j,
        catches: j.catches.map((old) =>
          old.id === c.id ? mergeCatchEdit(old, c, locationEdited) : old,
        ),
      }));
      setOverlay({ kind: "catch", id: c.id });
      setToast("Details saved");
    } catch (e) {
      error(e);
    }
  };
  const backup = () =>
    run(async () => {
      const uri = await exportBackup(state.current);
      await Sharing.shareAsync(uri, {
        mimeType: "application/json",
        UTI: "public.json",
        dialogTitle: "Save Fishdex backup",
      });
    });
  const restore = async () => {
    let data: Awaited<ReturnType<typeof readBackup>> | undefined;
    await run(async () => {
      const picked = await DocumentPicker.getDocumentAsync({
        type: ["application/json", "public.json"],
        copyToCacheDirectory: true,
      });
      if (!picked.canceled) data = await readBackup(picked.assets[0].uri);
    });
    if (!data) return;
    const selected = data;
    confirm(
      "Replace this journal?",
      `This backup contains ${selected.journal.profiles.length} anglers and ${selected.journal.catches.length} catches. Export your current journal first if you want to keep it.`,
      () => {
        void run(async () => {
          const j = await restoreBackup(selected);
          state.current = j;
          setJournal(j);
          setLoadError("");
          setOverlay(null);
          setToast("Journal restored");
        });
      },
      true,
    );
  };
  const fishImage = (id: string, locked = false, height = 150) => (
    <Image
      accessibilityLabel={
        locked ? "Undiscovered fish silhouette" : fishName(id)
      }
      source={pictures[id] ?? pictures.bluegill}
      resizeMode="contain"
      style={{
        width: "100%",
        height,
        tintColor: locked ? "#687C68" : undefined,
        opacity: locked ? 0.48 : 1,
      }}
    />
  );
  if (!loaded)
    return (
      <SafeAreaView style={styles.root}>
        <ActivityIndicator color={C.forest} />
      </SafeAreaView>
    );
  if (loadError)
    return (
      <SafeAreaView style={[styles.root, { padding: 25, gap: 20 }]}>
        <Title>Your journal needs attention</Title>
        <Copy>{loadError}</Copy>
        <Copy>Your saved data has not been overwritten.</Copy>
        <Button
          label="Try loading again"
          onPress={() => {
            try {
              const j = loadJournal();
              state.current = j;
              setJournal(j);
              setLoadError("");
            } catch (e) {
              error(e);
            }
          }}
        />
        <Button label="Restore a backup" secondary onPress={restore} />
      </SafeAreaView>
    );
  return (
    <SafeAreaView style={styles.root} edges={["top", "left", "right"]}>
      <View style={styles.header}>
        <View>
          <Text style={styles.brand}>
            Fishdex<Text style={{ color: C.lake }}> ≋</Text>
          </Text>
          <Text style={s.small}>A journal of wild discoveries</Text>
        </View>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Switch angler, current ${profile.name}`}
          onPress={() => setOverlay({ kind: "profiles" })}
          style={styles.profile}
        >
          <View style={[styles.avatar, { backgroundColor: profile.color }]}>
            <Text style={styles.avatarText}>{profile.name.slice(0, 1)}</Text>
          </View>
          <Text style={{ color: C.forest, fontWeight: "600" }}>
            {profile.name} ⌄
          </Text>
        </Pressable>
      </View>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {page === "journal" && (
          <>
            <View style={styles.greeting}>
              <Text style={styles.date}>
                {new Date().toLocaleDateString(undefined, {
                  weekday: "long",
                  month: "long",
                  day: "numeric",
                })}
              </Text>
              <Title>Good days start{"\n"}by the water.</Title>
              <Copy muted>
                {catches.length
                  ? `${profile.name}, your next discovery is out there.`
                  : `Your field journal is ready, ${profile.name}.`}
              </Copy>
            </View>
            <View style={styles.hero}>
              <View style={styles.waterline} />
              <Text style={styles.heroTag}>Michigan inland waters</Text>
              {fishImage("bluegill", false, 190)}
              <View style={[s.row, { justifyContent: "space-between" }]}>
                <View>
                  <Text style={styles.heroTitle}>What will you find?</Text>
                  <Text
                    style={{ color: "#E1EBD8", fontSize: 14, marginTop: 5 }}
                  >
                    Three species. So many stories ahead.
                  </Text>
                </View>
              </View>
              <Button label="◎  Log a catch" secondary onPress={startScan} />
            </View>
            <View style={styles.stats}>
              {[
                { value: catches.length, label: "Catches" },
                { value: `${discovered.size} / 3`, label: "Discovered" },
                {
                  value: badges(journal, profile.id).filter((b) => b.earned)
                    .length,
                  label: "Badges",
                },
              ].map((a) => (
                <View key={a.label} style={{ flex: 1 }}>
                  <Text style={styles.statValue}>{a.value}</Text>
                  <Text style={s.small}>{a.label}</Text>
                </View>
              ))}
            </View>
            <View style={[s.row, { justifyContent: "space-between" }]}>
              <Text style={s.sectionTitle}>In the field</Text>
              <Text style={s.small}>Saved on this phone</Text>
            </View>
            {!catches.length ? (
              <View style={styles.empty}>
                <Text style={{ fontSize: 32, color: C.lake }}>≋</Text>
                <Text style={styles.emptyTitle}>The first page is yours.</Text>
                <Copy muted>
                  Take a photo of your catch, choose the fish, and tap “Caught
                  it!”
                </Copy>
                <Button
                  label="Add a catch without a photo"
                  secondary
                  onPress={() => capture("manual")}
                />
              </View>
            ) : (
              catches
                .slice(0, 5)
                .map((c) => (
                  <CatchRow
                    key={c.id}
                    c={c}
                    onPress={() => setOverlay({ kind: "catch", id: c.id })}
                  />
                ))
            )}
            <View style={styles.note}>
              <Text style={styles.noteTitle}>A little field wisdom</Text>
              <Copy>
                Look at the mouth, the markings, and where the fins sit. Every
                fish has clues.
              </Copy>
            </View>
          </>
        )}
        {page === "collection" && (
          <>
            <Title>{profile.name}’s discoveries</Title>
            <Copy muted>Catch a fish to bring its silhouette to life.</Copy>
            <View style={styles.progressTrack}>
              <View
                style={[
                  styles.progressFill,
                  { width: `${(discovered.size / 3) * 100}%` },
                ]}
              />
            </View>
            <Text style={s.small}>
              {discovered.size} of 3 species discovered
            </Text>
            {species.map((f) => {
              const unlocked = discovered.has(f.id);
              return (
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel={`${f.name}, ${unlocked ? "discovered" : "not caught yet"}`}
                  key={f.id}
                  style={[
                    styles.specimen,
                    { backgroundColor: unlocked ? f.color + "44" : "#E6E9DD" },
                  ]}
                  onPress={() => setOverlay({ kind: "fish", id: f.id })}
                >
                  <View style={[s.row, { justifyContent: "space-between" }]}>
                    <Text style={{ color: C.forest, fontWeight: "600" }}>
                      {unlocked ? "✦ Discovered" : "◇ Still out there"}
                    </Text>
                    <Text style={s.small}>
                      {catches.filter((c) => c.speciesId === f.id).length}{" "}
                      caught
                    </Text>
                  </View>
                  {fishImage(f.id, !unlocked, 155)}
                  <Text style={s.sectionTitle}>{f.name}</Text>
                  <Text style={s.small}>{f.title}</Text>
                </Pressable>
              );
            })}
            <Text style={s.sectionTitle}>Field badges</Text>
            <View style={styles.badges}>
              {badges(journal, profile.id).map((b) => (
                <View
                  key={b.name}
                  style={[styles.badge, { opacity: b.earned ? 1 : 0.45 }]}
                >
                  <Text style={{ fontSize: 32, color: C.forest }}>
                    {b.icon}
                  </Text>
                  <Text
                    style={{ fontSize: 13, textAlign: "center", color: C.ink }}
                  >
                    {b.name}
                  </Text>
                  <Text style={s.small}>
                    {b.earned ? "Earned" : "To discover"}
                  </Text>
                </View>
              ))}
            </View>
            <Text style={s.sectionTitle}>All catches</Text>
            <Select
              label="Filter journal"
              value={filter}
              options={[
                { label: "All species", value: "all" },
                ...speciesOptions,
              ]}
              onChange={setFilter}
            />
            {catches
              .filter((c) => filter === "all" || filter === c.speciesId)
              .map((c) => (
                <CatchRow
                  key={c.id}
                  c={c}
                  onPress={() => setOverlay({ kind: "catch", id: c.id })}
                />
              ))}
          </>
        )}
        {page === "spots" && (
          <>
            <Title>Our fishing spots</Title>
            <Copy muted>
              Family places, kept private. Long-press the map to mark a new
              spot.
            </Copy>
            <SpotMap
              pins={[
                ...journal.spots
                  .filter((p) => p.coordinate)
                  .map((p) => ({
                    id: p.id,
                    title: p.name,
                    coordinate: p.coordinate!,
                  })),
                ...catches
                  .filter((c) => c.coordinate)
                  .map((c) => ({
                    id: c.id,
                    title: fishName(c.speciesId),
                    coordinate: c.coordinate!,
                  })),
              ]}
              onPick={(coordinate) => setOverlay({ kind: "spot", coordinate })}
            />
            <Text style={s.small}>
              Pins and spot names stay on this phone. Map imagery may need a
              connection.
            </Text>
            <Button
              label="＋ Add a fishing spot"
              onPress={() => setOverlay({ kind: "spot" })}
            />
            {!journal.spots.length && (
              <Copy muted>
                Save a favorite dock, pond, or stretch of shoreline.
              </Copy>
            )}
            {journal.spots.map((spot) => (
              <Pressable
                accessibilityRole="button"
                key={spot.id}
                style={styles.spotRow}
                onPress={() => setOverlay({ kind: "spot", id: spot.id })}
              >
                <Text style={{ fontSize: 26, color: C.lake }}>⌖</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.rowTitle}>{spot.name}</Text>
                  <Text style={s.small}>
                    {journal.catches.filter((c) => c.spotId === spot.id).length}{" "}
                    family catches{spot.coordinate ? " · Pin saved" : ""}
                  </Text>
                </View>
                <Text>›</Text>
              </Pressable>
            ))}
          </>
        )}
        {page === "kit" && (
          <>
            <Title>Our field kit</Title>
            <Copy muted>Ready for a day by the water.</Copy>
            <View style={s.card}>
              <Text style={s.sectionTitle}>On the line</Text>
              <Select
                label={`${profile.name}’s current bait`}
                value={profile.bait}
                options={baitOptions}
                onChange={(bait) => {
                  try {
                    commit((j) => ({
                      ...j,
                      profiles: j.profiles.map((p) =>
                        p.id === profile.id ? { ...p, bait } : p,
                      ),
                    }));
                  } catch (e) {
                    error(e);
                  }
                }}
              />
              <Copy muted>New catches remember this choice.</Copy>
              {baitModel[profile.bait] && (
                <Button
                  secondary
                  label="Inspect bait in 3D"
                  onPress={() =>
                    setOverlay({
                      kind: "tackle",
                      id: baitModel[profile.bait],
                      name: profile.bait,
                    })
                  }
                />
              )}
            </View>
            <Text style={s.sectionTitle}>The tackle box</Text>
            <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}>
              {Object.entries(baitModel).map(([name, id]) => (
                <Pressable
                  accessibilityRole="button"
                  key={id}
                  onPress={() => setOverlay({ kind: "tackle", id, name })}
                  style={styles.tackle}
                >
                  <Text style={{ fontSize: 18, color: C.forest }}>⌁</Text>
                  <Text style={{ fontSize: 15, color: C.ink }}>{name}</Text>
                  <Text style={s.small}>Inspect in 3D</Text>
                </Pressable>
              ))}
            </View>
            <Button
              label="Manage anglers"
              secondary
              onPress={() => setOverlay({ kind: "profiles" })}
            />
            <View style={s.rule} />
            <Text style={s.sectionTitle}>Keep the memories</Text>
            <Copy muted>
              Backups include all anglers, photos, catches, and private spots.
              Save one to Files before changing phones.
            </Copy>
            <Button
              label={busy ? "Preparing…" : "Export a backup"}
              onPress={backup}
              disabled={busy}
            />
            <Button
              label="Restore a backup"
              secondary
              onPress={restore}
              disabled={busy}
            />
            <View style={s.rule} />
            <Text style={s.sectionTitle}>About this field edition</Text>
            <Copy muted>
              Photos and catch records stay on this phone. Species are chosen by
              you; automatic photo recognition is still being developed. Add
              length for a rough weight guide. Unknown sex stays hidden.
            </Copy>
            <Copy muted>
              Fish facts: Michigan DNR. Original 3D models made in Blender.
              Models are field-guide representations and are being refined.
            </Copy>
            <Pressable
              accessibilityRole="link"
              onPress={() =>
                Linking.openURL(
                  "https://www.michigan.gov/dnr/education/michigan-species/fish-species",
                )
              }
            >
              <Text style={{ color: C.lake, textDecorationLine: "underline" }}>
                Explore Michigan DNR fish species
              </Text>
            </Pressable>
          </>
        )}
      </ScrollView>
      {toast ? (
        <View accessibilityLiveRegion="polite" style={styles.toast}>
          <Text style={{ color: C.paper }}>{toast}</Text>
        </View>
      ) : null}
      <SafeAreaView edges={["bottom"]} style={styles.navSafe}>
        <View style={styles.nav}>
          {(
            [
              { id: "journal", icon: "≋", label: "Journal" },
              { id: "collection", icon: "◇", label: "Fishdex" },
              { id: "spots", icon: "⌖", label: "Spots" },
              { id: "kit", icon: "⌁", label: "Field kit" },
            ] as const
          ).map((item) => (
            <Pressable
              accessibilityRole="tab"
              accessibilityState={{ selected: page === item.id }}
              key={item.id}
              onPress={() => setPage(item.id)}
              style={styles.navItem}
            >
              <Text
                style={{
                  fontSize: 25,
                  color: page === item.id ? C.forest : "#7C897A",
                }}
              >
                {item.icon}
              </Text>
              <Text
                style={{
                  fontSize: 12,
                  fontWeight: page === item.id ? "700" : "400",
                  color: page === item.id ? C.forest : C.muted,
                }}
              >
                {item.label}
              </Text>
            </Pressable>
          ))}
        </View>
      </SafeAreaView>
      <Modal
        visible={overlay !== null}
        animationType="slide"
        presentationStyle="fullScreen"
        onRequestClose={close}
      >
        {overlay?.kind === "profiles" && (
          <Sheet title="Our anglers" onClose={close}>
            <Copy>
              Everyone gets their own discoveries. Fishing spots belong to the
              whole crew.
            </Copy>
            {journal.profiles.map((p) => (
              <View key={p.id} style={styles.spotRow}>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel={`Use ${p.name}'s journal`}
                  style={[s.row, { flex: 1 }]}
                  onPress={() => {
                    try {
                      commit((j) => ({ ...j, activeProfileId: p.id }));
                      setOverlay(null);
                      setFilter("all");
                    } catch (e) {
                      error(e);
                    }
                  }}
                >
                  <View
                    style={[
                      styles.avatar,
                      {
                        backgroundColor: p.color,
                        width: 48,
                        height: 48,
                        borderRadius: 24,
                      },
                    ]}
                  >
                    <Text style={styles.avatarText}>{p.name[0]}</Text>
                  </View>
                  <View>
                    <Text style={styles.rowTitle}>
                      {p.name}
                      {p.id === profile.id ? " ✓" : ""}
                    </Text>
                    <Text style={s.small}>
                      {
                        journal.catches.filter((c) => c.profileId === p.id)
                          .length
                      }{" "}
                      catches
                    </Text>
                  </View>
                </Pressable>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel={`Edit ${p.name}`}
                  onPress={() => setOverlay({ kind: "profile", id: p.id })}
                  style={{ padding: 14 }}
                >
                  <Text style={{ color: C.lake }}>Edit</Text>
                </Pressable>
              </View>
            ))}
            <Button
              label="＋ Add an angler"
              onPress={() => setOverlay({ kind: "profile" })}
            />
          </Sheet>
        )}
        {overlay?.kind === "profile" && (
          <ProfileEditor
            key={overlay.id ?? "new"}
            journal={journal}
            id={overlay.id}
            onClose={() => setOverlay({ kind: "profiles" })}
            onSave={(id, name, color) => {
              try {
                commit((j) => ({
                  ...j,
                  profiles: id
                    ? j.profiles.map((p) =>
                        p.id === id ? { ...p, name, color } : p,
                      )
                    : [
                        ...j.profiles,
                        { id: uid(), name, color, bait: "Not recorded" },
                      ],
                }));
                setOverlay({ kind: "profiles" });
              } catch (e) {
                error(e);
              }
            }}
            onRemove={(id, target) => {
              try {
                commit((j) => removeProfile(j, id, target));
                setOverlay({ kind: "profiles" });
              } catch (e) {
                error(e);
              }
            }}
          />
        )}
        {overlay?.kind === "scan" && (
          <Sheet title="A new discovery" onClose={close} scroll={false}>
            <View style={{ flex: 1, padding: 20, gap: 14 }}>
              <Copy>
                Photograph the whole fish from the side. You’ll choose its
                species next.
              </Copy>
              <View style={styles.camera}>
                {permission?.granted && Platform.OS !== "web" ? (
                  <CameraView
                    ref={camera}
                    style={StyleSheet.absoluteFill}
                    facing="back"
                    mode="picture"
                    onCameraReady={() => setReady(true)}
                    onMountError={() =>
                      error(
                        new Error(
                          "Camera could not open. You can use an existing photo or save without one.",
                        ),
                      )
                    }
                  />
                ) : (
                  <View style={{ padding: 25, gap: 18 }}>
                    <Text style={{ fontSize: 36, color: C.paper }}>◎</Text>
                    <Text style={{ color: C.paper, fontSize: 18 }}>
                      A photo for your field journal
                    </Text>
                    <Button
                      secondary
                      label="Enable camera"
                      onPress={() => {
                        void requestPermission().then((p) => {
                          if (!p.granted)
                            Alert.alert(
                              "Camera access is off",
                              "Enable camera access in Settings, or choose a photo.",
                              [
                                { text: "Not now" },
                                {
                                  text: "Open Settings",
                                  onPress: () => Linking.openSettings(),
                                },
                              ],
                            );
                        });
                      }}
                    />
                  </View>
                )}
                <View pointerEvents="none" style={styles.frame} />
              </View>
              <Button
                label={busy ? "Saving photo…" : "◎  Take photo"}
                disabled={busy || !ready}
                onPress={() => capture("camera")}
              />
              <View style={s.row}>
                <View style={{ flex: 1 }}>
                  <Button
                    secondary
                    label="Choose photo"
                    disabled={busy}
                    onPress={() => capture("library")}
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <Button
                    secondary
                    label="No photo"
                    disabled={busy}
                    onPress={() => capture("manual")}
                  />
                </View>
              </View>
            </View>
          </Sheet>
        )}
        {overlay?.kind === "confirm" && draft && (
          <Sheet
            title="Choose your fish"
            onClose={close}
            footer={
              <Button
                label={busy ? "Saving catch…" : "Caught it!"}
                onPress={() => void caughtIt()}
                disabled={busy}
              />
            }
          >
            {draft.photo && (
              <Image
                source={{ uri: photoUri(draft.photo) }}
                style={styles.catchPhoto}
              />
            )}
            <Copy>
              Match the clues below. If you’re not sure, save now and identify
              it later.
            </Copy>
            <Select
              label="Caught by"
              value={draft.profileId}
              options={journal.profiles.map((p) => ({
                label: p.name,
                value: p.id,
              }))}
              onChange={(profileId) => setDraft({ ...draft, profileId })}
            />
            {species.map((f) => (
              <Pressable
                accessibilityRole="button"
                accessibilityState={{ selected: draft.speciesId === f.id }}
                key={f.id}
                style={[
                  styles.fishChoice,
                  draft.speciesId === f.id && styles.selected,
                ]}
                onPress={() => setDraft({ ...draft, speciesId: f.id })}
              >
                <Image
                  source={pictures[f.id]}
                  resizeMode="contain"
                  style={{ width: 100, height: 72 }}
                />
                <View style={{ flex: 1, gap: 5 }}>
                  <Text style={styles.rowTitle}>
                    {f.name}
                    {draft.speciesId === f.id ? " ✓" : ""}
                  </Text>
                  <Text style={s.small}>{f.clues}</Text>
                </View>
              </Pressable>
            ))}
            <Button
              secondary
              label={
                draft.speciesId === "unknown"
                  ? "✓ Not sure / another species"
                  : "Not sure / another species"
              }
              onPress={() => setDraft({ ...draft, speciesId: "unknown" })}
            />
            <Copy muted>
              Bait:{" "}
              {journal.profiles.find((p) => p.id === draft.profileId)?.bait}.
              You can add or change details after saving.
            </Copy>
          </Sheet>
        )}
        {overlay?.kind === "catchDate" && draft && (
          <Sheet title="When was it caught?" onClose={close}>
            <Copy>
              One last detail: check the date for this imported photo, then save
              your catch. If the photo had no date, we started with today.
            </Copy>
            <DateField
              value={draft.date}
              confirmLabel={busy ? "Saving catch…" : "Save catch"}
              disabled={busy}
              onChange={(date) => {
                if (date) {
                  void caughtIt({ ...draft, date, dateConfirmed: true });
                }
              }}
            />
            <Copy muted>
              Imported photos have no fishing location until you choose one. You
              can add a spot and other details after saving.
            </Copy>
            <Button
              secondary
              label="Back to fish"
              disabled={busy}
              onPress={() => setOverlay({ kind: "confirm" })}
            />
          </Sheet>
        )}
        {overlay?.kind === "fish" && (
          <Sheet title="Field guide" onClose={close}>
            {(() => {
              const f = species.find((f) => f.id === overlay.id)!;
              return (
                <>
                  <Text style={{ color: C.lake, fontWeight: "600" }}>
                    {discovered.has(f.id)
                      ? "✦ In your collection"
                      : "◇ Find it on your next adventure"}
                  </Text>
                  <Title>{f.name}</Title>
                  <Text style={s.small}>{f.scientific}</Text>
                  {discovered.has(f.id) ? (
                    <ModelView id={f.id} />
                  ) : (
                    <View style={s.card}>
                      {fishImage(f.id, true, 200)}
                      <Copy muted>
                        Confirm your first catch to unlock this 3D specimen.
                      </Copy>
                    </View>
                  )}
                  <Text style={s.small}>
                    {discovered.has(f.id)
                      ? "Drag to rotate. Pinch to look closer."
                      : "Read its clues before you head out."}
                  </Text>
                  <Text style={s.sectionTitle}>{f.title}</Text>
                  <Copy>{f.habitat}</Copy>
                  {discovered.has(f.id) && (
                    <View style={s.card}>
                      <Text style={s.sectionTitle}>Your field records</Text>
                      <Copy>
                        {catches.filter((c) => c.speciesId === f.id).length}{" "}
                        confirmed catches
                      </Copy>
                      <Copy muted>
                        Longest measured:{" "}
                        {Math.max(
                          0,
                          ...catches
                            .filter((c) => c.speciesId === f.id)
                            .map((c) => c.length ?? 0),
                        ) || "—"}{" "}
                        inches
                      </Copy>
                      <Copy muted>
                        Heaviest weighed:{" "}
                        {Math.max(
                          0,
                          ...catches
                            .filter((c) => c.speciesId === f.id)
                            .map((c) => c.weight ?? 0),
                        ) || "—"}{" "}
                        pounds
                      </Copy>
                    </View>
                  )}
                  {f.facts.map((fact) => (
                    <View key={fact} style={styles.fact}>
                      <Text style={{ color: C.lake }}>✦</Text>
                      <View style={{ flex: 1 }}>
                        <Copy>{fact}</Copy>
                      </View>
                    </View>
                  ))}
                  <Button
                    secondary
                    label="Listen to the field notes"
                    onPress={() => {
                      void Speech.stop();
                      Speech.speak(`${f.name}. ${f.facts.join(" ")}`, {
                        rate: 0.85,
                      });
                    }}
                  />
                  <Text style={s.small}>
                    Field notes adapted from Michigan DNR.
                  </Text>
                  <Button label="Log a catch" onPress={startScan} />
                </>
              );
            })()}
          </Sheet>
        )}
        {overlay?.kind === "reveal" &&
          journal.catches.find((c) => c.id === overlay.id) && (
            <Sheet title="In the journal" onClose={close}>
              <Reveal
                c={journal.catches.find((c) => c.id === overlay.id)!}
                isNew={overlay.isNew}
              />
              <Button
                label="Add details"
                onPress={() => setOverlay({ kind: "edit", id: overlay.id })}
              />
              <Button label="Back to fishing" secondary onPress={close} />
            </Sheet>
          )}
        {overlay?.kind === "catch" &&
          journal.catches.find((c) => c.id === overlay.id) && (
            <CatchDetail
              c={journal.catches.find((c) => c.id === overlay.id)!}
              journal={journal}
              onClose={close}
              onEdit={() => setOverlay({ kind: "edit", id: overlay.id })}
              onDelete={() =>
                confirm(
                  "Remove this catch?",
                  "This catch will leave the journal. Collection progress will update.",
                  () => {
                    try {
                      commit((j) => ({
                        ...j,
                        catches: j.catches.filter((c) => c.id !== overlay.id),
                      }));
                      setOverlay(null);
                    } catch (e) {
                      error(e);
                    }
                  },
                  true,
                )
              }
            />
          )}
        {overlay?.kind === "edit" &&
          journal.catches.find((c) => c.id === overlay.id) && (
            <CatchEditor
              key={overlay.id}
              c={journal.catches.find((c) => c.id === overlay.id)!}
              journal={journal}
              onClose={() => setOverlay({ kind: "catch", id: overlay.id })}
              onSave={updateCatch}
            />
          )}
        {overlay?.kind === "spot" && (
          <SpotEditor
            key={overlay.id ?? "new"}
            spot={journal.spots.find((p) => p.id === overlay.id)}
            coordinate={overlay.coordinate}
            onClose={close}
            onSave={(spot) => {
              try {
                commit((j) => ({
                  ...j,
                  spots: j.spots.some((p) => p.id === spot.id)
                    ? j.spots.map((p) => (p.id === spot.id ? spot : p))
                    : [...j.spots, spot],
                }));
                setOverlay(null);
              } catch (e) {
                error(e);
              }
            }}
            onDelete={(id) =>
              confirm(
                "Remove this spot?",
                "Catch coordinates will be kept, but the saved spot name will be removed.",
                () => {
                  try {
                    commit((j) => ({
                      ...j,
                      spots: j.spots.filter((p) => p.id !== id),
                      catches: j.catches.map((c) =>
                        c.spotId === id ? { ...c, spotId: undefined } : c,
                      ),
                    }));
                    setOverlay(null);
                  } catch (e) {
                    error(e);
                  }
                },
                true,
              )
            }
          />
        )}
        {overlay?.kind === "tackle" && (
          <Sheet title="The tackle box" onClose={close}>
            <Title>{overlay.name}</Title>
            <ModelView id={overlay.id} />
            <Copy muted>Drag to rotate. Pinch to inspect.</Copy>
            <Button
              label={`Use ${overlay.name.toLowerCase()}`}
              onPress={() => {
                try {
                  commit((j) => ({
                    ...j,
                    profiles: j.profiles.map((p) =>
                      p.id === profile.id ? { ...p, bait: overlay.name } : p,
                    ),
                  }));
                  setOverlay(null);
                  setToast("Bait selected for your next catch");
                } catch (e) {
                  error(e);
                }
              }}
            />
          </Sheet>
        )}
      </Modal>
    </SafeAreaView>
  );
}
function CatchRow({ c, onPress }: { c: Catch; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${fishName(c.speciesId)}, ${dateLabel(c.date)}`}
      onPress={onPress}
      style={styles.catchRow}
    >
      <Image
        source={
          c.photo
            ? { uri: photoUri(c.photo) }
            : (pictures[c.speciesId] ?? pictures.bluegill)
        }
        resizeMode={c.photo ? "cover" : "contain"}
        style={[
          styles.rowPhoto,
          !c.photo &&
            c.speciesId === "unknown" && { tintColor: "#687C68", opacity: 0.5 },
        ]}
      />
      <View style={{ flex: 1, gap: 4 }}>
        <Text style={styles.rowTitle}>
          {c.nickname || fishName(c.speciesId)}
        </Text>
        <Text style={s.small}>
          {dateLabel(c.date)}
          {c.length ? ` · ${c.length} in` : ""}
        </Text>
        <Text style={s.small}>
          {c.bait === "Not recorded" ? "Bait not recorded" : c.bait}
        </Text>
      </View>
      <Text style={{ color: C.lake, fontSize: 24 }}>›</Text>
    </Pressable>
  );
}
function DateField({
  value,
  onChange,
  confirmLabel = "Confirm catch date",
  disabled = false,
}: {
  value: string;
  onChange: (v: string | undefined) => void;
  confirmLabel?: string;
  disabled?: boolean;
}) {
  const [text, setText] = useState(dateInput(value));
  const [invalid, setInvalid] = useState(false);
  return (
    <>
      <Field
        label="Catch date and time"
        value={text}
        editable={!disabled}
        placeholder="YYYY-MM-DD HH:mm"
        onChangeText={(value) => {
          setText(value);
          onChange(undefined);
          setInvalid(false);
        }}
      />
      <Button
        secondary
        label={confirmLabel}
        disabled={disabled}
        onPress={() => {
          const parsed = new Date(text.replace(" ", "T"));
          const ok =
            /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(text) &&
            Number.isFinite(parsed.getTime()) &&
            dateInput(parsed.toISOString()) === text;
          if (ok) {
            onChange(parsed.toISOString());
            setInvalid(false);
          } else {
            setInvalid(true);
            onChange(undefined);
          }
        }}
      />
      {invalid && (
        <Text style={{ color: "#9A4141" }}>
          Use YYYY-MM-DD HH:mm, for example 2026-09-07 14:30.
        </Text>
      )}
    </>
  );
}
function Reveal({ c, isNew }: { c: Catch; isNew: boolean }) {
  const scale = useRef(new Animated.Value(0.92)).current;
  useEffect(() => {
    void AccessibilityInfo.isReduceMotionEnabled().then((reduced) => {
      if (reduced) scale.setValue(1);
      else
        Animated.spring(scale, {
          toValue: 1,
          useNativeDriver: true,
          damping: 9,
        }).start();
    });
  }, [scale]);
  return (
    <>
      <Text style={{ textAlign: "center", color: C.lake, fontSize: 18 }}>
        ✦ {isNew ? "New discovery!" : "Catch saved!"}
      </Text>
      <Title>{fishName(c.speciesId)}</Title>
      <Animated.View style={{ transform: [{ scale }] }}>
        {c.speciesId !== "unknown" ? (
          <ModelView id={c.speciesId} />
        ) : c.photo ? (
          <Image
            source={{ uri: photoUri(c.photo) }}
            style={styles.catchPhoto}
          />
        ) : (
          <View style={s.card}>
            <Copy>A mystery for your field journal.</Copy>
          </View>
        )}
      </Animated.View>
      <Copy>
        {isNew
          ? "Your collection just came to life. This species is yours to explore."
          : "Another story from a day by the water."}
      </Copy>
      <Copy muted>
        Your catch is saved. Add bait, measurements, or a nickname whenever you
        like.
      </Copy>
    </>
  );
}
function ProfileEditor({
  journal,
  id,
  onClose,
  onSave,
  onRemove,
}: {
  journal: Journal;
  id?: string;
  onClose: () => void;
  onSave: (id: string | undefined, name: string, color: string) => void;
  onRemove: (id: string, target?: string) => void;
}) {
  const original = journal.profiles.find((p) => p.id === id);
  const [name, setName] = useState(original?.name ?? "");
  const [color, setColor] = useState(
    original?.color ?? colors[journal.profiles.length % colors.length],
  );
  const [target, setTarget] = useState(
    journal.profiles.find((p) => p.id !== id)?.id ?? "",
  );
  return (
    <Sheet title={id ? "Edit angler" : "A new angler"} onClose={onClose}>
      <Field
        label="Angler name"
        value={name}
        onChangeText={setName}
        maxLength={40}
      />
      <Text style={s.label}>Choose a color</Text>
      <View style={s.row}>
        {colors.map((c) => (
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={`Choose ${c} color`}
            accessibilityState={{ selected: color === c }}
            key={c}
            onPress={() => setColor(c)}
            style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: c,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text style={{ color: "white", fontSize: 22 }}>
              {c === color ? "✓" : ""}
            </Text>
          </Pressable>
        ))}
      </View>
      <Button
        label="Save angler"
        disabled={!name.trim()}
        onPress={() => onSave(id, name.trim(), color)}
      />
      {id && journal.profiles.length > 1 && (
        <>
          <View style={s.rule} />
          <Text style={s.sectionTitle}>Remove this profile</Text>
          <Select
            label="What happens to their catches?"
            value={target}
            options={[
              ...journal.profiles
                .filter((p) => p.id !== id)
                .map((p) => ({ label: `Keep under ${p.name}`, value: p.id })),
              { label: "Delete their catches", value: "delete" },
            ]}
            onChange={setTarget}
          />
          <Button
            label="Remove angler"
            danger
            onPress={() =>
              confirm(
                `Remove ${original?.name}?`,
                target === "delete"
                  ? "Their catches will also be deleted."
                  : "Their catches will be transferred to the selected angler.",
                () => onRemove(id, target === "delete" ? undefined : target),
                true,
              )
            }
          />
        </>
      )}
    </Sheet>
  );
}
function CatchEditor({
  c,
  journal,
  onClose,
  onSave,
}: {
  c: Catch;
  journal: Journal;
  onClose: () => void;
  onSave: (c: Catch, locationEdited: boolean) => void;
}) {
  const [d, setD] = useState(c);
  const locationEdited = useRef(false);
  useEffect(() => {
    if (!locationEdited.current)
      setD((old) => ({ ...old, coordinate: c.coordinate, spotId: c.spotId }));
  }, [c.coordinate, c.spotId]);
  const [length, setLength] = useState(c.length?.toString() ?? "");
  const [weight, setWeight] = useState(c.weight?.toString() ?? "");
  const [dateText, setDateText] = useState(dateInput(c.date));
  const [message, setMessage] = useState("");
  const [locating, setLocating] = useState(false);
  const guide = weightGuide(d.speciesId, Number(length));
  function save() {
    const parse = (v: string, max: number) =>
      !v.trim()
        ? undefined
        : Number.isFinite(Number(v)) && Number(v) > 0 && Number(v) <= max
          ? Number(v)
          : NaN;
    const l = parse(length, 100),
      w = parse(weight, 200);
    const date = new Date(dateText.replace(" ", "T"));
    if (Number.isNaN(l) || Number.isNaN(w)) {
      setMessage(
        "Enter a positive length in inches and weight in pounds, or leave them blank.",
      );
      return;
    }
    if (
      !/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(dateText) ||
      !Number.isFinite(date.getTime()) ||
      dateInput(date.toISOString()) !== dateText
    ) {
      setMessage("Use a valid date and time: YYYY-MM-DD HH:mm.");
      return;
    }
    onSave(
      { ...d, length: l, weight: w, date: date.toISOString() },
      locationEdited.current,
    );
  }
  return (
    <Sheet title="Catch details" onClose={onClose}>
      <Select
        label="Species"
        value={d.speciesId}
        options={speciesOptions}
        onChange={(v) => setD({ ...d, speciesId: v as SpeciesId })}
      />
      <Select
        label="Angler"
        value={d.profileId}
        options={journal.profiles.map((p) => ({ label: p.name, value: p.id }))}
        onChange={(profileId) => setD({ ...d, profileId })}
      />
      <Field
        label="Nickname (optional)"
        value={d.nickname ?? ""}
        maxLength={80}
        onChangeText={(nickname) => setD({ ...d, nickname })}
      />
      <Select
        label="Bait"
        value={d.bait}
        options={baitOptions}
        onChange={(bait) => setD({ ...d, bait })}
      />
      <Field
        label="Length (inches)"
        value={length}
        onChangeText={setLength}
        keyboardType="decimal-pad"
        placeholder="Optional"
      />
      <Field
        label="Measured weight (pounds)"
        value={weight}
        onChangeText={setWeight}
        keyboardType="decimal-pad"
        placeholder="From a scale, if you have one"
      />
      {guide !== undefined && !weight && (
        <View style={s.card}>
          <Text style={s.label}>
            Length-based weight guide: about {guide.toFixed(2)} lb
          </Text>
          <Copy muted>
            A rough reference from length and species, not a measurement. Fish
            of the same length can weigh differently. This is not used for
            records.
          </Copy>
        </View>
      )}
      <Field
        label="Catch date and time"
        value={dateText}
        onChangeText={setDateText}
        placeholder="YYYY-MM-DD HH:mm"
      />
      <Select
        label="Fishing spot"
        value={d.spotId ?? ""}
        options={[
          { label: "No named spot", value: "" },
          ...journal.spots.map((p) => ({ label: p.name, value: p.id })),
        ]}
        onChange={(spotId) => {
          locationEdited.current = true;
          const spot = journal.spots.find((p) => p.id === spotId);
          setD({
            ...d,
            spotId: spotId || undefined,
            coordinate: spot?.coordinate ?? d.coordinate,
          });
        }}
      />
      <Copy muted>
        {d.coordinate
          ? `Private pin saved${d.coordinate.accuracy ? ` (GPS accuracy about ${Math.round(d.coordinate.accuracy)} m)` : ""}.`
          : "No location saved."}
      </Copy>
      <Button
        secondary
        label={locating ? "Finding location…" : "Use my current location"}
        disabled={locating}
        onPress={() =>
          confirm(
            "Use where you are now?",
            "Only use this if you are at the place where the fish was caught.",
            () => {
              setLocating(true);
              void currentCoordinate()
                .then((coordinate) => {
                  if (coordinate) {
                    locationEdited.current = true;
                    setD((old) => ({ ...old, coordinate, spotId: undefined }));
                  } else
                    error(
                      new Error(
                        "Could not get a location. You can choose a named spot later.",
                      ),
                    );
                })
                .catch(error)
                .finally(() => setLocating(false));
            },
          )
        }
      />
      {d.coordinate && (
        <Button
          secondary
          label="Remove location"
          onPress={() => {
            locationEdited.current = true;
            setD({ ...d, coordinate: undefined, spotId: undefined });
          }}
        />
      )}
      <Select
        label="Released or kept"
        value={d.disposition ?? ""}
        options={[
          { label: "Not recorded", value: "" },
          { label: "Released", value: "released" },
          { label: "Kept", value: "kept" },
        ]}
        onChange={(v) =>
          setD({ ...d, disposition: (v as Catch["disposition"]) || undefined })
        }
      />
      <Select
        label="Sex, if known"
        value={d.sex ?? ""}
        options={[
          { label: "Unknown (hidden)", value: "" },
          { label: "Male", value: "male" },
          { label: "Female", value: "female" },
        ]}
        onChange={(v) => setD({ ...d, sex: (v as Catch["sex"]) || undefined })}
      />
      <Field
        label="Field notes"
        value={d.notes ?? ""}
        onChangeText={(notes) => setD({ ...d, notes })}
        multiline
        maxLength={5000}
        placeholder="What made this catch memorable?"
      />
      {message && <Text style={{ color: "#9A4141" }}>{message}</Text>}
      <Button label="Save details" onPress={save} />
    </Sheet>
  );
}
function CatchDetail({
  c,
  journal,
  onClose,
  onEdit,
  onDelete,
}: {
  c: Catch;
  journal: Journal;
  onClose: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const card = useRef<View>(null);
  const [sharing, setSharing] = useState(false);
  const profile = journal.profiles.find((p) => p.id === c.profileId)!;
  const spot = journal.spots.find((p) => p.id === c.spotId);
  const guide = weightGuide(c.speciesId, c.length);
  return (
    <Sheet title="A page from the field" onClose={onClose}>
      <View ref={card} collapsable={false} style={styles.shareCard}>
        <Text style={styles.brand}>Fishdex ≋</Text>
        {c.photo ? (
          <Image
            source={{ uri: photoUri(c.photo) }}
            style={styles.catchPhoto}
          />
        ) : (
          <Image
            source={pictures[c.speciesId] ?? pictures.bluegill}
            resizeMode="contain"
            style={{
              height: 200,
              width: "100%",
              tintColor: c.speciesId === "unknown" ? "#687C68" : undefined,
            }}
          />
        )}
        <Title>{c.nickname || fishName(c.speciesId)}</Title>
        {c.nickname && <Copy>{fishName(c.speciesId)}</Copy>}
        <Copy>
          {profile.name}’s catch · {dateLabel(c.date)}
        </Copy>
        {c.length && (
          <Text style={styles.rowTitle}>
            {c.length} inches{c.weight ? ` · ${c.weight} lb measured` : ""}
          </Text>
        )}
        {!c.length && c.weight && <Copy>{c.weight} lb measured</Copy>}
        <Text style={s.small}>A day by the water. A story to keep.</Text>
      </View>
      {c.speciesId !== "unknown" && <ModelView id={c.speciesId} />}
      <View style={s.card}>
        <Copy>Bait: {c.bait}</Copy>
        <Copy>
          Time:{" "}
          {new Date(c.date).toLocaleTimeString(undefined, {
            hour: "numeric",
            minute: "2-digit",
          })}
        </Copy>
        {spot && <Copy>Spot: {spot.name}</Copy>}
        {c.sex && <Copy>Sex: {c.sex}</Copy>}
        {c.disposition && (
          <Copy>
            {c.disposition === "released"
              ? "Released to swim another day"
              : "Kept"}
          </Copy>
        )}
        {guide !== undefined && !c.weight && (
          <Copy muted>
            Length-based guide: about {guide.toFixed(2)} lb. Not a measured
            weight.
          </Copy>
        )}
        {c.notes && <Copy>{c.notes}</Copy>}
      </View>
      {c.coordinate && (
        <SpotMap
          pins={[
            {
              id: c.id,
              title: spot?.name ?? "Catch location",
              coordinate: c.coordinate,
            },
          ]}
        />
      )}
      <Button label="Edit catch details" onPress={onEdit} />
      <Button
        label={sharing ? "Preparing card…" : "Share catch card"}
        secondary
        disabled={sharing}
        onPress={() => {
          setSharing(true);
          void captureRef(card, {
            format: "png",
            quality: 1,
            result: "tmpfile",
          })
            .then((uri) =>
              Sharing.shareAsync(uri, {
                mimeType: "image/png",
                UTI: "public.png",
              }),
            )
            .catch(error)
            .finally(() => setSharing(false));
        }}
      />
      <Copy muted>
        The shared card includes the angler’s name and photo. Location, private
        notes, and photo metadata are left out.
      </Copy>
      <Button label="Remove catch" secondary onPress={onDelete} />
    </Sheet>
  );
}
function SpotEditor({
  spot,
  coordinate,
  onClose,
  onSave,
  onDelete,
}: {
  spot?: Spot;
  coordinate?: Coordinates;
  onClose: () => void;
  onSave: (spot: Spot) => void;
  onDelete: (id: string) => void;
}) {
  const [name, setName] = useState(spot?.name ?? "");
  const [pin, setPin] = useState(spot?.coordinate ?? coordinate);
  const [busy, setBusy] = useState(false);
  return (
    <Sheet
      title={spot ? "Edit fishing spot" : "A favorite place"}
      onClose={onClose}
    >
      <Field
        label="Spot name"
        value={name}
        onChangeText={setName}
        maxLength={80}
        placeholder="Grandpa’s lake"
      />
      <SpotMap
        pins={
          pin
            ? [{ id: "draft", title: name || "New spot", coordinate: pin }]
            : []
        }
        onPick={setPin}
      />
      <Copy muted>Long-press the map to place a private pin.</Copy>
      <Button
        label={busy ? "Finding your spot…" : "Use my current location"}
        secondary
        disabled={busy}
        onPress={() => {
          setBusy(true);
          void currentCoordinate()
            .then((c) => {
              if (c) setPin(c);
              else
                error(
                  new Error(
                    "Location is unavailable. Save a name now, or long-press the map.",
                  ),
                );
            })
            .catch(error)
            .finally(() => setBusy(false));
        }}
      />
      {pin && (
        <Copy muted>
          Pin: {pin.latitude.toFixed(5)}, {pin.longitude.toFixed(5)}
        </Copy>
      )}
      <Button
        label="Save fishing spot"
        disabled={!name.trim() || busy}
        onPress={() =>
          onSave({ id: spot?.id ?? uid(), name: name.trim(), coordinate: pin })
        }
      />
      {spot && (
        <Button
          secondary
          label="Remove spot"
          onPress={() => onDelete(spot.id)}
        />
      )}
    </Sheet>
  );
}
const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.paper },
  header: {
    paddingHorizontal: 22,
    paddingTop: 10,
    paddingBottom: 18,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderColor: C.line,
  },
  brand: {
    fontFamily: "Georgia",
    fontSize: 29,
    fontWeight: "700",
    color: C.forest,
  },
  profile: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    padding: 7,
    backgroundColor: "#E7ECDC",
    borderRadius: 30,
  },
  avatar: {
    width: 30,
    height: 30,
    borderRadius: 15,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarText: { fontSize: 16, color: "white", fontWeight: "700" },
  content: {
    padding: 22,
    gap: 22,
    paddingBottom: 35,
    maxWidth: 650,
    width: "100%",
    alignSelf: "center",
  },
  greeting: { gap: 12 },
  date: { color: C.lake, fontSize: 14 },
  hero: {
    backgroundColor: C.forest,
    borderRadius: 26,
    padding: 22,
    overflow: "hidden",
    gap: 18,
  },
  heroTag: { color: "#CBDDC3", fontSize: 14 },
  heroTitle: { fontFamily: "Georgia", fontSize: 25, color: C.paper },
  waterline: {
    position: "absolute",
    borderWidth: 1,
    borderColor: "#52735D",
    width: 380,
    height: 190,
    borderRadius: 200,
    top: 40,
    left: -30,
    transform: [{ rotate: "-12deg" }],
    opacity: 0.6,
  },
  stats: {
    flexDirection: "row",
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderColor: C.line,
    paddingBottom: 20,
  },
  statValue: {
    fontFamily: "Georgia",
    fontSize: 31,
    color: C.forest,
    marginBottom: 5,
  },
  empty: { gap: 13, paddingVertical: 10 },
  emptyTitle: { fontFamily: "Georgia", fontSize: 23, color: C.forest },
  note: {
    padding: 20,
    borderLeftWidth: 3,
    borderColor: C.gold,
    backgroundColor: "#EDEEDC",
    gap: 8,
  },
  noteTitle: { fontFamily: "Georgia", fontSize: 20, color: C.forest },
  navSafe: {
    backgroundColor: "#F9FAF3",
    borderTopWidth: 1,
    borderColor: C.line,
  },
  nav: { flexDirection: "row", paddingTop: 8, paddingBottom: 8 },
  navItem: { flex: 1, alignItems: "center", gap: 3, minHeight: 48 },
  progressTrack: {
    height: 7,
    backgroundColor: "#D9E1D0",
    borderRadius: 4,
    overflow: "hidden",
  },
  progressFill: { height: 7, backgroundColor: C.forest },
  specimen: { padding: 20, borderRadius: 22, gap: 6 },
  badges: { flexDirection: "row", gap: 8 },
  badge: {
    flex: 1,
    padding: 12,
    backgroundColor: "#E6E9D9",
    borderRadius: 18,
    alignItems: "center",
    gap: 8,
  },
  spotRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    paddingVertical: 17,
    borderBottomWidth: 1,
    borderColor: C.line,
  },
  rowTitle: { fontWeight: "600", fontSize: 17, color: C.ink },
  catchRow: {
    flexDirection: "row",
    gap: 14,
    alignItems: "center",
    paddingBottom: 18,
    borderBottomWidth: 1,
    borderColor: C.line,
  },
  rowPhoto: {
    width: 80,
    height: 82,
    borderRadius: 12,
    backgroundColor: "#E2E8D9",
  },
  tackle: {
    width: "47%",
    padding: 18,
    gap: 8,
    backgroundColor: "#E6EBDD",
    borderRadius: 18,
  },
  camera: {
    flex: 1,
    minHeight: 220,
    backgroundColor: "#244339",
    borderRadius: 24,
    overflow: "hidden",
    alignItems: "center",
    justifyContent: "center",
  },
  frame: {
    position: "absolute",
    width: "88%",
    height: "60%",
    borderWidth: 1.5,
    borderColor: "#E2EDDC",
    borderRadius: 60,
  },
  catchPhoto: {
    width: "100%",
    height: 250,
    borderRadius: 18,
    backgroundColor: "#DDE5D5",
  },
  fishChoice: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderWidth: 1,
    borderColor: C.line,
    borderRadius: 18,
    gap: 10,
  },
  selected: {
    borderColor: C.forest,
    borderWidth: 2,
    backgroundColor: "#E0E9D6",
  },
  fact: {
    flexDirection: "row",
    gap: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderColor: C.line,
  },
  shareCard: {
    backgroundColor: C.paper,
    padding: 20,
    gap: 16,
    borderRadius: 20,
  },
  toast: {
    position: "absolute",
    bottom: 100,
    alignSelf: "center",
    backgroundColor: C.forest,
    padding: 16,
    borderRadius: 20,
  },
});
