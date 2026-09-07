import { useMemo } from "react";
import { View, Text, Platform } from "react-native";
import { WebView } from "react-native-webview";
import { models } from "@/generated/models";
import { viewerScript } from "@/generated/viewer";
export function ModelView({ id }: { id: string }) {
  const html = useMemo(
    () =>
      `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; connect-src blob:;"><style>html,body{margin:0;overflow:hidden;background:#e6e9dc;font:14px -apple-system,sans-serif;color:#183f35}canvas{display:block;touch-action:none}#loading{position:absolute;inset:45% 0;text-align:center;pointer-events:none}button{position:absolute;right:12px;bottom:12px;border:1px solid #99aa94;background:#f4f2e8;padding:10px 14px;border-radius:20px;color:#183f35}</style></head><body><div id="loading">Opening your specimen…</div><button id="reset">Reset view</button><script>window.MODEL=${JSON.stringify(models[id] ?? "")};</script><script>${viewerScript.replace(/<\/script/gi, "<\\/script")}</script></body></html>`,
    [id],
  );
  if (!models[id])
    return (
      <View
        style={{ height: 280, alignItems: "center", justifyContent: "center" }}
      >
        <Text>Model coming soon.</Text>
      </View>
    );
  return (
    <View
      style={{
        height: 300,
        borderRadius: 22,
        overflow: "hidden",
        backgroundColor: "#e6e9dc",
      }}
    >
      {Platform.OS === "web" ? (
        <iframe
          title="Interactive 3D specimen"
          srcDoc={html}
          style={{ border: 0, width: "100%", height: "100%" }}
          sandbox="allow-scripts"
        />
      ) : (
        <WebView
          source={{ html }}
          originWhitelist={["about:*"]}
          onShouldStartLoadWithRequest={(r) =>
            r.url === "about:blank" || r.url.startsWith("about:")
          }
          javaScriptEnabled
          scrollEnabled={false}
          bounces={false}
          style={{ backgroundColor: "#e6e9dc" }}
        />
      )}
    </View>
  );
}
