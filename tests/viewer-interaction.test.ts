import test from "node:test";
import assert from "node:assert/strict";
import { installInteractionGuards } from "../scripts/viewer-interaction.js";

test("model gestures remain locked through a pinch and recover from cancellation or leaving the app", () => {
  const canvas = new EventTarget();
  const lifecycle = new EventTarget();
  const messages: string[] = [];
  installInteractionGuards(
    canvas,
    (message: string) => messages.push(message),
    lifecycle,
  );
  const pointer = (name: string, pointerId: number) => {
    canvas.dispatchEvent(Object.assign(new Event(name), { pointerId }));
  };
  pointer("pointerdown", 1);
  pointer("pointerdown", 2);
  pointer("pointerup", 1);
  pointer("lostpointercapture", 1);
  assert.deepEqual(messages, ["gesture:start"]);
  pointer("pointercancel", 2);
  assert.deepEqual(messages, ["gesture:start", "gesture:end"]);
  pointer("pointerdown", 3);
  lifecycle.dispatchEvent(new Event("blur"));
  assert.equal(messages.at(-1), "gesture:end");
  pointer("pointerdown", 4);
  assert.equal(messages.at(-1), "gesture:start");
  lifecycle.dispatchEvent(new Event("pagehide"));
  assert.equal(messages.at(-1), "gesture:end");
  const move = new Event("touchmove", { cancelable: true });
  canvas.dispatchEvent(move);
  assert.equal(move.defaultPrevented, true);
});
