# Fan preset selection for standalone fans

**Status:** in progress
**Touches:** climate-control, profiles, card-ux

## Goal

Standalone fans (e.g. Dreo ceiling fans) expose a `preset_modes` list that includes
device modes such as `sleep`, `natural`, `reverse`, in addition to speed tiers.
This adds a per-room/per-profile **Fan preset** selector so the user can pin a
specific mode; `Auto` (the default) preserves today's temperature-driven speed
behavior. For fans that express direction as a preset (e.g. Dreo), the dropdown
supersedes the binary Fan-reverse toggle.

## Behavior

1. **Auto-detect preset support** — no config-flow toggle. A standalone fan has
   preset support when its HA entity's `preset_modes` list is non-empty. Detection
   is live at evaluation time, not at platform setup.

2. Each room with a standalone fan gets a **Fan preset** `select.*` entity. Its
   options are `["Auto", *fan.preset_modes]` read live from `hass.states`. The
   entity is created unconditionally (live options handle the late-loading case)
   and is inert when the fan has no presets (only option is "Auto").

3. **Pinned preset wins while running.** When the Fan-preset selector is set to
   anything other than `Auto`:
   - The engine still turns the fan on/off based on room temperature vs `target_fan` (CC-13).
   - While the fan is running, the engine applies the pinned preset via
     `fan.set_preset_mode` instead of computing a Low/Med/High speed tier.
   - Speed tier selection (CC-14) and direction commands (CC-22–25) are **suppressed**.
   - Idempotent: the command is omitted when `fan.preset_mode` already matches.

4. **Auto** restores today's CC-14 speed-tier behavior, unchanged.

5. **Preset supersedes reverse toggle for preset-mode fans.** A fan whose direction
   is expressed via `preset_modes` (CC-22 preset path, `direction_via_preset=True`)
   no longer receives direction commands from the Fan-reverse switch when a
   non-`Auto` preset is active. The `reverse` mode is available as a selectable
   option in the dropdown.

6. Native-`DIRECTION` fans (no `preset_modes`) are **unaffected** — they continue
   using the existing Fan-reverse toggle and direction commands (CC-22–25).

7. **Profiles** carry a `fan_preset` field (`str | None`). Scheduled and explicit
   applies write the room's Fan-preset select; the controller reacts per rule 3.

## UI

- **Settings dialog**: a **Fan preset** dropdown replaces the **Reverse** toggle in
  the Fan section when `fan_preset_select` is populated and has more than one option
  (i.e. the fan actually has presets). Native-direction fans keep the Reverse toggle
  (UX-28 unchanged for them). See UX-30.
- **Profiles panel**: the Fan row shows the Fan-preset dropdown (bound to the
  per-profile select entity) when presets exist, else the existing Reverse toggle
  (UX-21 extended via UX-30).
- **Main card Fan mode text**: when a non-`Auto` preset is active and the fan is
  running, the mode text shows the preset name (e.g. `50% (Sleep)`). Extends UX-29.

## Out of scope

- Preset selection for A/C or heater companion fans.
- Exposing the preset list in the config flow.
- Presets on fans that only support native `FanEntityFeature.DIRECTION` (no
  `preset_modes`).

## Acceptance criteria

- [ ] Engine tests CC-26 pass: pinned preset emits `FanSetPreset`, suppresses tier
      speed and direction; `Auto` leaves today's behavior unchanged; idempotence.
- [ ] `select.<room>_fan_preset` entity appears for every room with a standalone fan;
      options update live from `hass.states`.
- [ ] Selecting a non-Auto preset while the fan is running issues `fan.set_preset_mode`.
- [ ] Selecting `Auto` restores tier-speed control on the next evaluation.
- [ ] Per-profile `select.*` entity persists `fan_preset` to storage.
- [ ] Profile apply writes the room's Fan-preset select (scheduled and explicit).
- [ ] Card (UX-30): Fan-preset dropdown visible in settings dialog and profiles panel
      for preset fans; Reverse toggle hidden; native-direction fans unaffected.
- [ ] Existing CC-22..25 and engine tests continue to pass unchanged.
