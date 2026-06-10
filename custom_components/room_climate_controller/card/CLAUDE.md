# Lovelace card — guidance

The companion card (`custom:room-climate-control`), built with **Lit + TypeScript**.
The integration serves it at `/room_climate_controller/` and auto-registers it as a
frontend module — there is **no** Lovelace resource to add and no HA restart needed.
UX behavior is specified in
[../../../requirements/spec/card-ux.md](../../../requirements/spec/card-ux.md).

## Building

- **Edit only `src/*.ts`.** Never hand-edit the generated `www/*.js` bundle or the
  `room-climate-control-card.js` here — they're build output.
- **`scripts/deploy.sh`** (from repo root) is the normal path: it bumps the patch
  version, syncs the console banner in `src/index.ts`, runs `npm install && npm run
  build` (rollup), and copies the bundle into the integration's `www/`. After it
  runs, **hard-refresh** the browser (Ctrl+Shift+R) — no HA restart.
- For a build without the version bump/deploy: `npm install && npm run build` here.
- Node/npm comes from the devcontainer's Node feature; it is **not** part of the base
  Python image, so `scripts/develop` (HA) doesn't provide it.
- **Never hand-edit `package.json`'s `version`** — `deploy.sh` owns it.
- **Banner-regex trap:** `deploy.sh` rewrites the **first** `v\d+.\d+.\d+`-shaped
  string in `src/index.ts` to sync the version. Don't add any other `vX.Y.Z`-looking
  literal earlier in that file, or the version sync silently targets the wrong string.
- **Dependencies:** the only runtime dependency is `lit`. Don't add npm dependencies
  without asking first — extra libs bloat the single-file bundle.

## Layout

- `index.ts` — entry/registration + version banner (kept in sync by `deploy.sh`).
- `room-climate-control.ts` — the main card; `room-climate-control-editor.ts` — its visual editor.
- `profiles-panel.ts` + `profiles/` + `profile-styles.ts` — the Profiles section.
- `settings-ui.ts`, `graph-configs.ts`, `graph-overlay.ts` — settings dialog and the plotly energy/history graphs.
- `resolve-room.ts` / `schema.ts` / `types.ts` / `ha-types.ts` / `helpers.ts` / `styles.ts` — shared plumbing.

## Contract with the integration

`schema.ts` / `types.ts` mirror the websocket message shapes defined in the
integration's `websocket_api.py`. They are two halves of one contract — change a
message shape on one side and you must update the other.

## UX musts (see card-ux.md for the full list)

- Consistent button styling everywhere (UX-1).
- **No layout shift on button press** — signal success by appearance, not size; don't reflow the dialog (UX-6).
- Hide device sections a room doesn't have (UX-2); show a fan that's off as "Off", not 0% (UX-5).
- Avoid `browser_mod` unless there's no alternative — ask first (UX-3).
