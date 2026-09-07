import MapView, { Marker } from "react-native-maps";
import type { Coordinates } from "@/data/state";
export type MapPin = { id: string; title: string; coordinate: Coordinates };
export function SpotMap({
  pins,
  onPick,
}: {
  pins: MapPin[];
  onPick?: (coordinate: Coordinates) => void;
}) {
  const center = pins[0]?.coordinate ?? { latitude: 44.3, longitude: -85.5 };
  return (
    <MapView
      key={pins.map((p) => p.id).join(",")}
      style={{ height: 280, borderRadius: 20 }}
      initialRegion={{
        ...center,
        latitudeDelta: pins.length ? 0.07 : 4,
        longitudeDelta: pins.length ? 0.07 : 4,
      }}
      onLongPress={(e) => onPick?.(e.nativeEvent.coordinate)}
      showsUserLocation={false}
    >
      {pins.map((p) => (
        <Marker
          key={p.id}
          coordinate={p.coordinate}
          title={p.title}
          pinColor="#183F35"
        />
      ))}
    </MapView>
  );
}
