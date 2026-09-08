# Michigan inland sport-fish catalog

This release covers 20 selected native inland sport-fish species and 11 representative bait/lure types. It is the common sport-fish phase, not an exhaustive list of Michigan fish. Introduced trout and salmon, hybrids, and the wider minnow/darter/sucker catalog remain outside this phase.

Every entry has an original Blender model, offline GLB, rendered thumbnail, field clues, and journal support. Body dimensions are normalized artistic proportions, not measurements. Models represent species, not individual catches or a particular sex. They remain illustrative species studies, not photorealistic or independently certified anatomical models.

## Species and references

| Species | Scientific name | Field-mark reference |
|---|---|---|
| Bluegill | Lepomis macrochirus | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/bluegill) |
| Largemouth bass | Micropterus nigricans | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/largemouth) |
| Northern pike | Esox lucius | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/pike) |
| Smallmouth bass | Micropterus dolomieu | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/smallmouth) |
| Yellow perch | Perca flavescens | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/yellow-perch) |
| Walleye | Sander vitreus | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/walleye) |
| Pumpkinseed | Lepomis gibbosus | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/pumpkinseed) |
| Green sunfish | Lepomis cyanellus | [Agency guide](https://mdc.mo.gov/discover-nature/field-guide/green-sunfish) |
| Rock bass | Ambloplites rupestris | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/rock-bass) |
| Black crappie | Pomoxis nigromaculatus | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/crappie) |
| White crappie | Pomoxis annularis | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/crappie) |
| Channel catfish | Ictalurus punctatus | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/catfish) |
| Flathead catfish | Pylodictis olivaris | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/flathead-catfish) |
| Brown bullhead | Ameiurus nebulosus | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/bullheads) |
| Yellow bullhead | Ameiurus natalis | [Agency guide](https://mdc.mo.gov/discover-nature/field-guide/yellow-bullhead) |
| Black bullhead | Ameiurus melas | [Agency guide](https://mdc.mo.gov/discover-nature/field-guide/black-bullhead) |
| Muskellunge | Esox masquinongy | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/muskie) |
| Brook trout | Salvelinus fontinalis | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/brook-trout) |
| Lake trout | Salvelinus namaycush | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/lake-trout) |
| White bass | Morone chrysops | [Agency guide](https://www.michigan.gov/dnr/education/michigan-species/fish-species/white-bass) |

No agency illustrations or photographs are bundled. Text is paraphrased; all model geometry, markings, and preview renders are original. The Michigan DNR bullhead page uses an older genus for black bullhead; Ameiurus melas follows the linked Missouri field guide.

## Tackle

Worm, Minnow, Jig, Spinner, Crankbait, Soft plastic, Topwater frog, Spoon, Spinnerbait, Jerkbait, Topwater popper. Other and Not recorded are journal choices without invented generic models. Each modeled type appears in the bait selector and tackle box. Models are unbranded examples; hook, skirt, paint, and hardware choices vary by real lure.

## Realism pass and archives

The third pass adds irregular pigment patterns, tangent-space scale relief, radial iris detail, cheek relief, thinner tapered fin rays, and wet-skin materials. Lures use coated paint, polished metal, and translucent diving lips. The viewer generates its reflection environment locally, without an HDR download.

All earlier scenes are preserved in the original source library. Version 3 keeps separate editable and runtime scenes with packed textures. See [the archive index](../assets/blender/README.md) for opening and reusing them. Render comparisons are in [model-review](model-review/index.html).

## Rebuild

The current fourth pass refines head/shoulder profiles, jaw rims, gill contours, fin shapes and branching rays, species pigment patterns, and smooth scaleless catfish skin. Tackle adds conforming scale paint, smooth molded bodies, a recessed popper cup, clear diving lips, wound split rings, tapered hooks, ribbon skirts, and textured natural/artificial worms. Minnow now has paired pelvic fins and an anal fin. The exported meshes share UV names so joining retains the correct skin and fin mapping.

Run `blender -b --factory-startup --python-exit-code 1 --python scripts/modeling/build_refined.py -- bass` from the checkout, substituting any catalog ID. A fresh Blender process per asset limits memory. Sources go to `assets/blender/v4`; the earlier archives stay intact. Run `npm run models:bundle` to update the embedded assets. [Review all 31 models](model-review/v4/index.html); [refinement notes and references](model-review/v4/README.md).
