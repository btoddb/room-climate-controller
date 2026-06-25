# Plan: Up/down target-temp arrows on the main card

## Context

The proposal ([add-up-down-target-temp-controls.md](add-up-down-target-temp-controls.md))
asks for up/down triangle buttons on the main card so each room device's target
temperature can be nudged ±1°F directly from the card, without opening the
settings dialog or the more-info entity dialog.

This is a **card-only** change. The card already receives each device's target
helper entity ID (`target_cooling` / `target_heating` / `target_fan`) in its
resolved config, and Home Assistant `number` entities expose `min` / `max` /
`step` in their state attributes (set from the room's configured limits in
[number.py:52-70](../../custom_components/room_climate_controller/number.py#L52-L70)).
So the card has everything it needs to read the current target, the device's
range, and write a new value via the existing `number.set_value` path. **No
backend, websocket, or schema change is required.**

### Decisions (confirmed with user)
- **Device range (constraint #3):** clamp on the card to the number entity's own
  `min`/`max`; **disable** the up arrow at `max` and the down arrow at `min`
  (opacity-only, no layout shift per UX-6).
- **Cross-device rule (cooling must stay above heating):** rely on the existing
  server-side validator in
  [constraints.py](../../custom_components/room_climate_controller/constraints.py)
  (`_heating_below_cooling`, clamps to `cooling_target − 1`). This is acceptable
  *because the card reads the target live from `hass.states`*, so when the server
  clamps the number entity HA pushes a new state and the card's displayed
  "X°F target" corrects itself to reality. No client-side duplication of that rule.
- **Toggle independence (constraint #5):** automatically satisfied — the arrows
  write the number entity, which is independent of the Use / Fan Ovr switches.

## Changes

### 1. `card/src/helpers.ts` — read the number entity's limits
Add a small helper next to `getTargetTemp` ([helpers.ts:81-99](../../custom_components/room_climate_controller/card/src/helpers.ts#L81-L99)):

```ts
/** Read a number entity's min/max (from HA `number.*` attributes), with fallbacks. */
export function getNumberLimits(
  hass: HomeAssistant,
  helperId: string
): { min: number; max: number } {
  const attrs = hass.states[helperId]?.attributes ?? {};
  const min = Number(attrs.min);
  const max = Number(attrs.max);
  return {
    min: Number.isFinite(min) ? min : -Infinity,
    max: Number.isFinite(max) ? max : Infinity,
  };
}
```
Reuse the existing `setInputNumber`
([helpers.ts:89-99](../../custom_components/room_climate_controller/card/src/helpers.ts#L89-L99))
for the write — it's already domain-aware (`number.*` / `input_number.*`).

### 2. `card/src/room-climate-control.ts` — render the arrows column
In the `addDevice` closure ([room-climate-control.ts:228-301](../../custom_components/room_climate_controller/card/src/room-climate-control.ts#L228-L301)):

- After computing `targetTemp` ([line 244](../../custom_components/room_climate_controller/card/src/room-climate-control.ts#L244)),
  read limits: `const { min, max } = getNumberLimits(this.hass, targetHelper);`
- Add an adjust handler (uses the already-rounded current target so repeated
  presses step cleanly):
  ```ts
  const adjust = (delta: number) => {
    const next = Math.min(max, Math.max(min, targetTemp + delta));
    if (next !== targetTemp) setInputNumber(this.hass, targetHelper, next);
  };
  ```
- Insert a new `temp-arrows` column as the **first** child of `.device-toggles`
  ([line 276](../../custom_components/room_climate_controller/card/src/room-climate-control.ts#L276)),
  i.e. to the **left** of the Fan Ovr / spacer and the Use toggle:
  ```ts
  <div class="temp-arrows">
    <button class="temp-arrow-btn" aria-label="Raise ${label} target"
      .disabled=${targetTemp >= max} @click=${() => adjust(1)}>
      <ha-icon icon="mdi:menu-up"></ha-icon>
    </button>
    <button class="temp-arrow-btn" aria-label="Lower ${label} target"
      .disabled=${targetTemp <= min} @click=${() => adjust(-1)}>
      <ha-icon icon="mdi:menu-down"></ha-icon>
    </button>
  </div>
  ```
  `mdi:menu-up` / `mdi:menu-down` are the upward / downward (upside-down) filled
  triangles the proposal asks for, stacked one above the other.
- **Alignment:** every device row's `.device-toggles` already lays out fixed-width
  columns in a row, so adding `temp-arrows` as the first column keeps the arrows
  vertically aligned across Cooling / Heating / Fan rows.
- **Manual Mode row** ([lines 342-358](../../custom_components/room_climate_controller/card/src/room-climate-control.ts#L342-L358))
  has a `.device-toggles` but no target — prepend a matching-width arrows spacer
  (`<div class="temp-arrows-spacer" aria-hidden="true"></div>`) so its Use toggle
  stays aligned with the others. (The window-status row uses a different layout and
  needs nothing.)

### 3. `card/src/styles.ts` — column + button styling
Add near the toggle/column styles ([styles.ts:58-102](../../custom_components/room_climate_controller/card/src/styles.ts#L58-L102)),
reusing the shared button visual language from `.rcc-btn`
([styles.ts:129-156](../../custom_components/room_climate_controller/card/src/styles.ts#L129-L156))
for consistency (UX-1) but compact enough for a stacked pair:

```css
.temp-arrows { display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 2px; width: 36px; flex-shrink: 0; }
.temp-arrows-spacer { width: 36px; flex-shrink: 0; }
.temp-arrow-btn { display: flex; align-items: center; justify-content: center;
  width: 32px; height: 20px; padding: 0; border: none; border-radius: 6px;
  background: var(--secondary-background-color, rgba(0,0,0,0.05));
  color: var(--primary-text-color); cursor: pointer; --mdc-icon-size: 18px; }
.temp-arrow-btn:hover:not(:disabled) { filter: brightness(1.04); }
.temp-arrow-btn:active:not(:disabled) { filter: brightness(0.96); }
.temp-arrow-btn:disabled { opacity: 0.5; cursor: not-allowed; filter: none; }
```
Disabled state changes opacity only — no size/layout shift (UX-6).

### 4. Build & ship
Run `scripts/deploy.sh` from the repo root (bumps the card version, syncs the
`src/index.ts` banner, runs `npm run build`, copies the bundle into `www/`) — per
[card/CLAUDE.md](../../custom_components/room_climate_controller/card/CLAUDE.md). Never
hand-edit `www/*.js` or `card/package.json`'s version.

## Out of scope / non-changes
- No change to `engine.py`, `controller.py`, `constraints.py`, `number.py`,
  `websocket_api.py`, or `schema.ts` / `types.ts` — the contract is unchanged.
- Step size is fixed at 1°F (matches the proposal and the number entity's
  `step: 1`).

## Verification
1. **Build:** `cd custom_components/room_climate_controller/card && npm install && npm run build`
   (confirms the TypeScript compiles), then `scripts/deploy.sh` from repo root.
2. **Run HA:** background `scripts/develop`, hard-refresh (Ctrl+Shift+R), open a
   room card with cooling + heating + fan configured.
3. **Acceptance checks** (from the proposal):
   - Up arrow raises that device's target +1°F; down arrow lowers it −1°F (read
     back from the "X°F target" line and the entity).
   - At the device's configured max, the up arrow is greyed/disabled; at min, the
     down arrow is greyed/disabled — target never leaves the device range.
   - Push the **heating** target up toward the cooling target: the server clamps it
     to stay below cooling, and the card's displayed heating target updates to the
     clamped value (confirms "displayed target reflects reality"). Same in reverse
     for lowering cooling toward heating.
   - Toggle Use / Fan Ovr off, then adjust the target — the arrows still work and
     the toggles are unaffected.
4. **Regression:** `pytest custom_components/room_climate_controller/tests/`
   (should be untouched, since no Python changed) and `scripts/lint` (revert any
   stray diffs under vendored `custom_components/dreo/`).
