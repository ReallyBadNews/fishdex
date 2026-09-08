# Revision 4 model review

[Open the render gallery](index.html). Each tile is the app's transparent specimen render; click it for the oblique Blender render. The images show the actual geometry and materials used for export. Color management and reflections differ between Cycles and the app's Three.js renderer.

All 20 fish and 11 tackle models were rebuilt in Blender 5.2.1 LTS. Original and version 3 source libraries are preserved. The new editable libraries are in `assets/blender/v4` with packed textures, separate objects, and a camera/light rig. The runtime export joins only a separate scene copy.

## Refinements

| Models | Main changes |
|---|---|
| Largemouth and smallmouth bass | Different head and shoulder contours, distinct jaw lengths, opercular contours, nostrils, narrower fin rays, textured flanks; bronze cheek streaks on smallmouth. |
| Bluegill, pumpkinseed, green sunfish | Distinct body depths and mouth sizes; longer pointed pectorals; bluegill's soft-dorsal spot; fine cheek pigment and red-tipped opercular flap on pumpkinseed; pale fin margins on green sunfish. |
| Rock bass | Red iris, fine scale-row markings, six modeled anal spines. |
| Yellow perch, walleye, white bass | Separate dorsal fins; perch bars and orange lower fins; walleye dorsal patch and pale anal/lower-tail tips; six horizontal flank stripes on white bass. |
| Black and white crappie | Compressed bodies; irregular dark calico versus vertical bars; seven versus six dorsal spines. |
| Northern pike and muskellunge | Slender bodies, long jaws, rear dorsal/anal placement, light-on-dark versus dark-on-light pigment, patterned fins. |
| Brook and lake trout | Streamlined bodies, fine pale spots, rayless adipose fins; brook vermiculations, blue-haloed red spots, black/white lower-fin margins and nearly square tail; deeply forked lake-trout tail. |
| Channel and flathead catfish | Scaleless surface maps, four pairs of tapered barbels, dorsal spine and adipose fin; forked channel-catfish tail versus broad, flattened flathead head and rounded-square tail. |
| Brown, yellow, black bullheads | Compact bodies, blunt tails and scaleless skin; mottled brown, yellow with pale chin barbels, and darker black with contrasting fin rays. |
| Worm and soft plastic | Fine segment/color variation, a smoother clitellum on the natural worm, embedded pigment flecks on the artificial worm. |
| Minnow | Countershaded silver scales, small mouth and gill contours, paired pectoral/pelvic fins, anal fin and forked tail. A representative unbranded baitfish, not an added species. |
| Jig and spinnerbait | Curved flat skirt strands, a binding collar, weed guard and shaped single hook; metal blade surface variation on spinnerbait. |
| Spinner and spoon | Brushed metal roughness, finer line eyes, wound split rings and tapered treble points/barbs. |
| Crankbait and jerkbait | Smooth molded shell, conforming scale-foil paint and pearl belly, seated eyes, gill relief, clear polycarbonate bill, screw eyes and treble hardware. |
| Topwater popper | Tapered molded shell with a genuinely recessed concave mouth, inset line eye, paint and treble hardware. |
| Topwater frog | Curved ribbon legs, dielectric rubber materials and tapered double-hook points against the hollow body. |

## Reference basis and limits

Species field marks follow the Michigan DNR and Missouri Department of Conservation sources linked for every species in [the catalog](../../CATALOG.md). Reference pages were revisited for this pass. Supplemental bullhead comparison: [Florida Museum yellow bullhead account](https://www.floridamuseum.ufl.edu/fish/catfish/ictaluridae/yellow-bullhead/). Hard-lure construction was compared with [Rapala's Original Floating](https://www.rapala.com/us_en/original-floating?childSku=us-F09G) and [X-Rap construction notes](https://blog.rapala.com/news/go-all-day-crappie-fishing-with-the-x-rap-4/). Models are unbranded original examples; no reference photographs or illustrations are used as textures or bundled.

These are artistically normalized reference studies, not scans, measured anatomical reconstructions, or certified species-identification tools. Living fish vary with age, sex, habitat, season and lighting. Mouths are shown mostly closed; internal oral anatomy, full dentition, exact scale counts and every fin-ray count are not reconstructed. Soft fins use alpha blending to approximate thin membranes within the offline mobile renderer. Accuracy still benefits from expert anatomical review.

## Verification

The model test suite checks complete catalog coverage, embedded resources, preserved normal maps, UV variation after mesh joining, at most 16 material primitives, fewer than 100,000 triangles and 3 MiB per model, and a 64 MiB budget for all runtime GLBs. These budgets are guards against accidental growth, not measured device performance. The source manifest is verified by reopening library inventories and hashing each source/GLB. Native installation and touch performance still require a registered iPhone; a finished cloud build alone does not validate them.

The final local checks passed: TypeScript, all 12 tests, and Expo SDK 57 iOS bundle export. All 31 GLBs reached `ready` using the bundled viewer in a sandboxed browser frame with the app's offline content-security policy; [results](runtime-check.json). Rotation and reset were exercised, and the crankbait was checked in the app's tackle sheet. The viewer now supplies the stage color to the transmission pass so clear diving lips do not sample a white fallback. [App screenshot](app-crankbait.png), [all side renders](all-models.png), [all angled renders](all-angles.png).
