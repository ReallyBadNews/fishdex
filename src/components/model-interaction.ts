import { createContext } from "react";

// Each viewer owns its lock so unmounting one cannot unlock another.
export const ModelInteraction = createContext<
  (owner: symbol, active: boolean) => void
>(() => {});
