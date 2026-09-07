# Fishdex

A private, offline-first Expo SDK 57 iPhone fishing journal for a family. Separate editable local anglers share named fishing spots. Twenty Michigan inland sport fish unlock after a confirmed catch. Includes 20 original Blender fish models and 11 bait/lure models, camera/library photos, optional GPS, journal editing, read-aloud field notes, backup/restore with photos, and location-free catch cards.

## Run and validate

```sh
npm ci
npm run typecheck
npm test
npx expo start
```

The iPhone app is the product. The web target is a UI preview with separate local data; camera persistence, backup, and maps need the native app. No Xcode installation is available on the current development machine, so native installation is through EAS.

## Installable previews

```sh
eas build --platform ios --profile preview
```

The preview is an internally distributed release build with a bundled JavaScript payload and models. It does not need Metro at the lake. The project uses the owner's personal Apple team and Expo project configured in app.json. Signing must be configured in EAS; target iPhones must be registered using `eas device:create` before building.

`.eas/workflows/preview.yml` validates code and builds an iPhone preview on pushes to main when the Expo GitHub integration is connected. It can also run manually:

```sh
eas workflow:run .eas/workflows/preview.yml
```

`.github/workflows/check.yml` checks every PR, including iOS bundle export. TestFlight later uses the `testflight` build and submit profiles; no public App Store release is configured.

## What this field edition does and does not do

- Camera view takes a photo; users choose the species by comparing field marks. **Automatic live/photo species recognition is not implemented or validated.** No fake predictions, confidence scores, or remote inference requests.
- Weight guides require a manually entered length. Bluegill and pike use Wisconsin DNR length formulas; bass uses standard-weight coefficients from Ohio OFIS Appendix 4.2. These are rough references, not photo measurements, statistical confidence ranges, or eligible weight records.
- Unknown sex is hidden. Known sex can be entered manually.
- Original 3D models have species-specific body shapes, markings, fins, eyes, and barbels where appropriate. They require further anatomical and artistic refinement before being described as highly accurate or photorealistic. No AR yet.
- Catch data and photos are stored locally. Map imagery can need internet. Offline GPS acquisition depends on device conditions. Photos imported from the library require date confirmation and do not get the current GPS location automatically.
- Backups include private coordinates and photos; share cards intentionally omit location and notes, and are rasterized rather than sharing original photo metadata. Uninstalling deletes local data: export a backup first.

## Assets and sources

`assets/models/fishdex-source.blend` preserves all earlier Blender scenes. [The source archive](assets/blender/README.md) contains editable version 3 scenes and a verified inventory. `scripts/modeling/` contains editable model-generation scripts. `assets/models/*.glb` are runtime exports; `assets/specimens/` holds rendered previews. `npm run models:bundle` embeds GLBs and the Three.js viewer for offline use. No external model hosting or CDN is used. Third-party renderer licenses remain in `src/generated/viewer.ts` and `node_modules/three/LICENSE`.

The full roster, field-mark references, and modeling scope are in [docs/CATALOG.md](docs/CATALOG.md). Facts use Michigan DNR and Missouri Department of Conservation field guides. Agency illustrations are not bundled. Weight sources: [Wisconsin DNR](https://dnr.wisconsin.gov/topic/Fishing/questions/estfishweight), [Ohio OFIS Appendix 4.2](https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/NPSMP/docs/OFIS.pdf).

Accepted product decisions and remaining delivery gates: [docs/SCOPE.md](docs/SCOPE.md).
