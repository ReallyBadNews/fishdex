// Keep a pinch locked until its last pointer ends, including cancelled captures.
/** @param {EventTarget} lifecycle */
export function installInteractionGuards(target, report, lifecycle = window) {
  const pointers = new Set();
  const start = (event) => {
    const wasEmpty = pointers.size === 0;
    pointers.add(event.pointerId);
    if (wasEmpty) report("gesture:start");
  };
  const end = (event) => {
    if (pointers.delete(event.pointerId) && pointers.size === 0)
      report("gesture:end");
  };
  const release = () => {
    pointers.clear();
    report("gesture:end");
  };
  target.addEventListener("pointerdown", start);
  for (const name of ["pointerup", "pointercancel", "lostpointercapture"]) {
    target.addEventListener(name, end);
  }
  target.addEventListener("touchmove", (event) => event.preventDefault(), {
    passive: false,
  });
  lifecycle.addEventListener("blur", release);
  lifecycle.addEventListener("pagehide", release);
}
