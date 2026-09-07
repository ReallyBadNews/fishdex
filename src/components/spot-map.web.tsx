import { View, Text } from "react-native";
import type { Coordinates } from "@/data/state";
export type MapPin = { id: string; title: string; coordinate: Coordinates };
export function SpotMap({
  pins,
}: {
  pins: MapPin[];
  onPick?: (coordinate: Coordinates) => void;
}) {
  return (
    <View
      style={{
        height: 240,
        backgroundColor: "#d9e3d8",
        borderRadius: 20,
        padding: 25,
        justifyContent: "center",
      }}
    >
      <Text style={{ color: "#183f35", fontSize: 20 }}>
        Your private fishing map
      </Text>
      <Text style={{ marginTop: 12 }}>
        Interactive maps are available on iPhone.
      </Text>
      {pins.map((p) => (
        <Text key={p.id}>{p.title}</Text>
      ))}
    </View>
  );
}
