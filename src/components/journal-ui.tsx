import { useCallback, useRef, useState, type ReactNode } from "react";
import { ModelInteraction } from "./model-interaction";
import {
  Text,
  View,
  Pressable,
  TextInput,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  type TextInputProps,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
export const C = {
  forest: "#183F35",
  reed: "#B7CA9D",
  paper: "#F4F2E8",
  lake: "#527D8A",
  ink: "#223B34",
  gold: "#D8AE55",
  line: "#D8DECE",
  muted: "#647468",
  white: "#FFFFFF",
};
export function Copy({
  children,
  muted = false,
}: {
  children: ReactNode;
  muted?: boolean;
}) {
  return <Text style={[s.copy, muted && { color: C.muted }]}>{children}</Text>;
}
export function Title({ children }: { children: ReactNode }) {
  return <Text style={s.title}>{children}</Text>;
}
export function Button({
  label,
  onPress,
  secondary = false,
  disabled = false,
  danger = false,
}: {
  label: string;
  onPress: () => void;
  secondary?: boolean;
  disabled?: boolean;
  danger?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        s.button,
        secondary && s.secondary,
        danger && { backgroundColor: "#9A4141" },
        (pressed || disabled) && { opacity: 0.55 },
      ]}
    >
      <Text style={[s.buttonText, secondary && { color: C.forest }]}>
        {label}
      </Text>
    </Pressable>
  );
}
export function Field({ label, ...props }: TextInputProps & { label: string }) {
  return (
    <View style={{ gap: 7 }}>
      <Text style={s.label}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        placeholderTextColor="#7E8A7B"
        style={[
          s.input,
          props.multiline && { minHeight: 100, textAlignVertical: "top" },
        ]}
        {...props}
      />
    </View>
  );
}
export function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: { label: string; value: string }[];
  onChange: (v: string) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <View style={{ gap: 7 }}>
      <Text style={s.label}>{label}</Text>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`${label}: ${options.find((o) => o.value === value)?.label ?? "Choose"}`}
        accessibilityState={{ expanded: open }}
        style={[s.input, s.row]}
        onPress={() => setOpen(!open)}
      >
        <Text style={{ fontSize: 16, color: C.ink, flex: 1 }}>
          {options.find((o) => o.value === value)?.label ?? "Choose"}
        </Text>
        <Text style={{ color: C.forest }}>⌄</Text>
      </Pressable>
      {open && (
        <View style={s.options}>
          {options.map((o) => (
            <Pressable
              key={o.value}
              accessibilityRole="button"
              onPress={() => {
                onChange(o.value);
                setOpen(false);
              }}
              style={[
                s.option,
                o.value === value && { backgroundColor: "#E0E8D5" },
              ]}
            >
              <Text style={{ fontSize: 16, color: C.ink }}>
                {o.value === value ? "✓  " : ""}
                {o.label}
              </Text>
            </Pressable>
          ))}
        </View>
      )}
    </View>
  );
}
export function Sheet({
  title,
  children,
  onClose,
  scroll = true,
  footer,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  scroll?: boolean;
  footer?: ReactNode;
}) {
  const scrollRef = useRef<ScrollView>(null);
  const owners = useRef(new Set<symbol>());
  const [interacting, setInteracting] = useState(false);
  const holdModelGesture = useCallback((owner: symbol, active: boolean) => {
    if (active) owners.current.add(owner);
    else owners.current.delete(owner);
    const locked = owners.current.size > 0;
    // Apply immediately, before the next React render and native pan movement.
    scrollRef.current?.setNativeProps({ scrollEnabled: !locked });
    setInteracting(locked);
  }, []);
  return (
    <ModelInteraction.Provider value={holdModelGesture}>
      <SafeAreaView style={{ flex: 1, backgroundColor: C.paper }}>
        <View
          style={[
            s.row,
            {
              paddingHorizontal: 22,
              paddingVertical: 12,
              borderBottomWidth: 1,
              borderColor: C.line,
            },
          ]}
        >
          <Text
            style={{
              flex: 1,
              fontFamily: "Georgia",
              fontSize: 23,
              color: C.forest,
            }}
          >
            {title}
          </Text>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Close"
            onPress={onClose}
            style={{ padding: 12 }}
          >
            <Text style={{ fontSize: 18, color: C.forest }}>Close</Text>
          </Pressable>
        </View>
        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          {scroll ? (
            <ScrollView
              ref={scrollRef}
              scrollEnabled={!interacting}
              keyboardShouldPersistTaps="handled"
              contentContainerStyle={{
                padding: 22,
                gap: 20,
                paddingBottom: 40,
              }}
            >
              {children}
            </ScrollView>
          ) : (
            children
          )}
          {footer && (
            <View
              style={{
                padding: 16,
                borderTopWidth: 1,
                borderColor: C.line,
                backgroundColor: C.paper,
              }}
            >
              {footer}
            </View>
          )}
        </KeyboardAvoidingView>
      </SafeAreaView>
    </ModelInteraction.Provider>
  );
}
export const s = StyleSheet.create({
  copy: { fontSize: 16, lineHeight: 24, color: C.ink },
  title: {
    fontFamily: "Georgia",
    fontSize: 34,
    lineHeight: 40,
    color: C.forest,
  },
  label: { fontWeight: "600", fontSize: 15, color: C.ink },
  row: { flexDirection: "row", alignItems: "center", gap: 12 },
  button: {
    backgroundColor: C.forest,
    paddingVertical: 17,
    paddingHorizontal: 22,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 56,
  },
  buttonText: { fontSize: 17, fontWeight: "600", color: C.paper },
  secondary: {
    backgroundColor: "#E3E9DB",
    borderWidth: 1,
    borderColor: C.line,
  },
  input: {
    backgroundColor: "#FAFBF5",
    borderWidth: 1,
    borderColor: "#C5D0BC",
    borderRadius: 12,
    padding: 15,
    fontSize: 17,
    color: C.ink,
    minHeight: 52,
  },
  options: {
    borderWidth: 1,
    borderColor: C.line,
    borderRadius: 12,
    overflow: "hidden",
  },
  option: {
    padding: 15,
    backgroundColor: "#FAFBF5",
    borderBottomWidth: 1,
    borderColor: C.line,
    minHeight: 50,
  },
  card: { backgroundColor: "#E6EBDD", padding: 22, borderRadius: 24, gap: 14 },
  rule: { height: 1, backgroundColor: C.line },
  sectionTitle: { fontFamily: "Georgia", fontSize: 24, color: C.forest },
  small: { fontSize: 13, color: C.muted, lineHeight: 19 },
});
