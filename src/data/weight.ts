import type { SpeciesId } from "./catalog.ts";
// Length-only guides, never measurements and never used for weight records.
// Bluegill/pike: Wisconsin DNR, /topic/Fishing/questions/estfishweight.
// Bass: standard-weight coefficients, Ohio OFIS Appendix 4.2 (mm, grams).
export function weightGuide(
  species: SpeciesId,
  inches?: number,
): number | undefined {
  if (!inches || !Number.isFinite(inches)) return;
  if (species === "bluegill" && inches >= 3.2 && inches <= 16)
    return inches ** 3 / 1200;
  if (species === "pike" && inches >= 10 && inches <= 60)
    return inches ** 3 / 3500;
  if (species === "bass" && inches >= 6 && inches <= 32)
    return 10 ** (-5.316 + 3.191 * Math.log10(inches * 25.4)) / 453.59237;
}
