# Room Climate Control — Setup & Operations Guide

This document describes the per-room climate control mechanism implemented
by the [`room_climate_control`](../blueprints/automation/btoddb/room_climate_control.yaml) blueprint and its
companions. It is the operational reference; the formal requirements live
in [`room-climate-control.md`](./room-climate-control.md).

## Architecture at a glance

```
real sensors  →  abstraction template sensors (templates/room_climate_sensors.yaml)
                 incl. sensor.outdoor_temperature (weather)
                                       │
input_boolean × 4/room (+ fan_only override where supported) ──┐
input_number × 3 targets + 6 offsets/room ──┼──> room_climate_control blueprint
climate / fan entities  ────────────────────┘      ↓ (manual mode == off)
                                                   computed thresholds:
                                                   cool/fan: target + offset
                                                   heat: target - offset
                                                   ↓
                                                   climate.set_hvac_mode / set_temperature
                                                   climate.set_fan_mode  or  fan.set_percentage
                                                   fan.turn_on / fan.turn_off / fan.set_percentage

room_climate_constraints blueprint  ──>  watches targets + offsets,
                                         clamps invalid ordering/range, notifies
```

## Files in this change

| Purpose | File |
|---|---|
| Main blueprint | [`blueprints/automation/btoddb/room_climate_control.yaml`](../blueprints/automation/btoddb/room_climate_control.yaml) |
| Constraint validator blueprint | [`blueprints/automation/btoddb/room_climate_constraints.yaml`](../blueprints/automation/btoddb/room_climate_constraints.yaml) |
| Sensor abstraction layer | [`templates/room_climate_sensors.yaml`](../templates/room_climate_sensors.yaml) |
| Boolean helpers (15) | [`helpers/input_boolean/room_climate.yaml`](../helpers/input_boolean/room_climate.yaml) |
| Number helpers (27) | [`helpers/input_number/room_climate.yaml`](../helpers/input_number/room_climate.yaml) |
| Custom Lovelace card | [`www/btoddb/room-climate-card/`](../www/btoddb/room-climate-card/) (`room-climate-control-card.js`) |
| Todd's Bedroom control | [`automations/room_climate/room_climate_todds_bedroom.yaml`](../automations/room_climate/room_climate_todds_bedroom.yaml) |
| Todd's Bedroom constraints | [`automations/room_climate/room_climate_todds_bedroom_constraints.yaml`](../automations/room_climate/room_climate_todds_bedroom_constraints.yaml) |
| Office control | [`automations/room_climate/room_climate_office.yaml`](../automations/room_climate/room_climate_office.yaml) |
| Office constraints | [`automations/room_climate/room_climate_office_constraints.yaml`](../automations/room_climate/room_climate_office_constraints.yaml) |
| Main Floor control | [`automations/room_climate/room_climate_main_floor.yaml`](../automations/room_climate/room_climate_main_floor.yaml) |
| Main Floor constraints | [`automations/room_climate/room_climate_main_floor_constraints.yaml`](../automations/room_climate/room_climate_main_floor_constraints.yaml) |
| `configuration.yaml` edits | template / input_boolean / input_number includes + `automation room_climate: !include_dir_list automations/room_climate/` |
| Category / area registry script | [`scripts/room_climate_apply_categories_areas.py`](../scripts/room_climate_apply_categories_areas.py) |

## Categories and areas

Per the requirements, every room-climate helper, template sensor, and automation
is grouped under a category named **`Room Climate - {Room Name}`** (separate
category entries in the **Automations** and **Helpers** settings tables), and
assigned to that room’s **area** (`todd_s_bedroom`, `office`, `main_floor`).
`sensor.outdoor_temperature` is assigned to the **Outdoor** area only.

Registry updates are not available in YAML; apply them with:

```bash
python3 scripts/room_climate_apply_categories_areas.py
```

Then restart Home Assistant (or reload). The script is idempotent. The
room → area/label mapping is derived from `daily_climate/rooms.json` (each
room's `key`, `label`, `area_id`, and `slug`); helper entity_ids come from
the naming convention and template sensors/automations are resolved from the
entity registry by `unique_id` (`room_climate_<slug>_*`). After onboarding a
new room, add it to `rooms.json` and add its category IDs to `CATEGORY_IDS`
in the script, then re-run — no per-entity edits.

## Required dependencies

### Local custom card

- **Resource URL**: `/local/btoddb/room-climate-card/room-climate-control-card.js?v=1.4.2`
- **Card type**: `custom:room-climate-control`
- **Climate profiles** (v1.1.0+): expandable **Profiles** section on each room card;
  set **Climate profile room key** in the editor (or auto-detect from `manual_mode`).
  See [daily_climate_routines_setup.md](./daily_climate_routines_setup.md).

Registered in Lovelace resources (`.storage/lovelace_resources` or
**Settings → Dashboards → Resources**). After pulling changes, restart HA
and hard-refresh the browser (Ctrl+F5).

Rebuild after editing card source:

```bash
cd www/btoddb/room-climate-card && npm install && npm run build
```

### HACS (graph popups)

Install **lovelace-plotly-graph-card** via HACS for Energy/History graphs.
Uses the UI helper `input_select.time_range` for graph range. The history
graph plots actual device state (not the Use toggles): cooling/heating
traces are on only in `cool` / `heat` mode; `fan_only` counts as off.

Decluttering-card, browser_mod, mushroom, and tailwindcss are **not**
required for room climate dashboards.

## Per-room mapping

### Todd's Bedroom
- **Temperature abstraction**: `sensor.todd_s_bedroom_room_temperature`
  (wraps `sensor.todd_s_bedroom_temp`).
- **Humidity abstraction**: `sensor.todd_s_bedroom_room_humidity` (wraps
  `sensor.todd_s_bedroom_temp_humidity`).
- **Power abstraction**: `sensor.todd_s_bedroom_room_power` (wraps
  `sensor.4_17_living_rm_todd_s_bed_outlets_power_minute_average`).
- **A/C**: `climate.todd_s_a_c` (SmartIR; `hvac_modes`: off / cool /
  fan_only; `fan_modes`: Auto / Low / Medium / High; range 60-86 °F).
- **Heater**: `climate.todd_s_envi_heater_todd_s_envi_heater` (Envi; heat
  only, no fan_modes; range 45-95 °F).
- **Standalone fan**: `fan.todd_s_bedroom_fan_dreo`.

### Office
- **Temperature abstraction**: `sensor.office_room_temperature` (wraps
  `sensor.office_temperature`).
- **Humidity abstraction**: `sensor.office_room_humidity` (wraps
  `sensor.office_climate_sensor_3_humidity`).
- **Power abstraction**: `sensor.office_room_power` (wraps
  `sensor.8_21_office_henry_s_bed_power_minute_average`).
- **A/C**: `climate.office_a_c` (Matter; `hvac_modes`: off / cool only; no
  `fan_modes`; range 45-95 °F).
- **A/C companion fan**: `fan.office_a_c` (drives fan speed since
  `climate.office_a_c` has no `fan_modes`). Matter exposes
  `preset_modes` low/medium/high — blueprint uses `fan.set_preset_mode`,
  not `fan.set_percentage`.
- **A/C power switch**: `switch.office_a_c_power` (Matter power toggle;
  must be on before `climate.set_*` commands work — wired via blueprint
  `ac_power_switch` input).
- **Command timing**: `command_delay_seconds: 3`, `power_on_delay_seconds: 5`
  (Matter needs pauses between power, HVAC mode, target temp, and fan commands).
- **Heater**: none.
- **Standalone fan**: `fan.office_ceiling_fan`.
- **Heating helpers / constraints / daily routines**: Office has no heater.
  Set `validate_heating: false` on the constraints automation and
  `office_has_heating: false` on daily climate routines. The room climate
  card omits `heater_entity`; the daily routine card hides the heating row.
- Because the A/C does not list `fan_only` in `hvac_modes`, there is no
  fan-only override helper for Office. It cools or powers off; use the
  ceiling fan toggle for circulation.

### Main Floor
- **Temperature abstraction**: `sensor.main_floor_room_temperature` (wraps
  `sensor.main_floor_temp`).
- **Humidity abstraction**: `sensor.main_floor_room_humidity` (wraps
  `sensor.living_room_climate_sensor_2_humidity`).
- **Power abstraction**: `sensor.main_floor_room_power` (wraps
  `sensor.3_9_11_heat_pump_power_minute_average` — Emporia Vue heat-pump
  circuit, in watts).
- **A/C and heater**: same entity, `climate.main_floor_heat_pump`. Wired
  to both `ac_climate` and `heater_climate` so the blueprint takes the
  combined-decision branch and chooses a single hvac mode (no cool/heat
  conflict). **Fan Ovr** is offered on the Cooling row only
  (`use_main_floor_room_ac_fan_only_override`); there is no separate heater
  fan-only override helper.
- **Standalone fan**: none.
- **Fan helpers / constraints / daily routines**: Main Floor has no standalone
  fan. Set `validate_fan: false` on the constraints automation and
  `main_floor_has_fan: false` on daily climate routines. The room climate
  card omits `fan_entity`; the daily routine card hides the fan row.
- **Range note**: the heat pump's Sensibo integration reports
  `min_temp=0, max_temp=1` (bogus). The `input_number` helpers use
  pragmatic defaults — cooling 60-86 °F, heating 45-80 °F. If you swap
  the heat pump for a device that reports real ranges, update
  [`helpers/input_number/room_climate.yaml`](../helpers/input_number/room_climate.yaml).

## Helper naming convention

For each room `<r>` (∈ `todds_bedroom`, `office_room`, `main_floor_room`),
the helpers are:

| Helper | Purpose | Type |
|---|---|---|
| `input_boolean.use_<r>_ac` | Enable A/C automation | toggle |
| `input_boolean.use_<r>_heater` | Enable heater automation | toggle |
| `input_boolean.use_<r>_fan` | Enable standalone-fan automation; off turns fan off | toggle |
| `input_boolean.<r>_climate_manual_mode` | Pause automation entirely | toggle |
| `input_boolean.use_<r>_ac_fan_only_override` | Use A/C fan-only override (devices with `fan_only` only) | toggle |
| `input_boolean.use_<r>_heater_fan_only_override` | Use heater fan-only override (separate heater climate only; not used on shared heat pumps) | toggle |
| `input_number.<r>_target_cooling_temp` | Target °F for cooling | box (device min/max) |
| `input_number.<r>_cooling_medium_offset` | °F above target for Medium fan tier | slider 1–20 |
| `input_number.<r>_cooling_high_offset` | °F above target for High fan tier | slider 1–20 |
| `input_number.<r>_target_heating_temp` | Target °F for heating | box (device min/max) |
| `input_number.<r>_heating_medium_offset` | °F below target for Medium fan tier | slider 1–20 |
| `input_number.<r>_heating_high_offset` | °F below target for High fan tier | slider 1–20 |
| `input_number.<r>_target_fan_temp` | Target °F for standalone fan device | box (device min/max) |
| `input_number.<r>_fan_medium_offset` | °F above target for Medium fan speed | slider 1–20 |
| `input_number.<r>_fan_high_offset` | °F above target for High fan speed | slider 1–20 |

Notes:
- Todd's Bedroom uses `todds_bedroom_` for both kinds of helpers (no
  `_room_` infix).
- Office and Main Floor use `office_room_` and `main_floor_room_` for both
  kinds of helpers.
- `input_number` target `min`/`max` track each room's climate device range.
- **Computed thresholds** (used by the blueprint, not stored):
  - Cooling / fan: `medium = target + medium_offset`, `high = target + high_offset`
  - Heating: `medium = target - medium_offset`, `high = target - high_offset`
    (high offset must be greater than medium offset so `high < medium < target`)

## Threshold offset migration

When upgrading from absolute `*_medium_temp` / `*_high_temp` helpers, derive
offsets from saved values (clamp 1–20):

- **Cooling / fan**: `medium_offset = round(medium_temp - target)`, `high_offset = round(high_temp - target)`
- **Heating**: `medium_offset = round(target - medium_temp)`, `high_offset = round(target - high_temp)`

Set via **Developer Tools → Services** → `input_number.set_value`, or the
card Settings dialog sliders after reload. Remove orphaned `input_number.*_temp`
entities from **Settings → Devices & services → Helpers** if they remain in
the UI registry.

## Blueprint input contract

`room_climate_control` inputs, grouped:

- **Sensors**: `temperature_sensor` (required), `humidity_sensor`,
  `power_sensor`.
- **Devices**: `ac_climate`, `heater_climate`, `fan_entity`,
  `ac_fan_entity`, `heater_fan_entity` (all optional but at least one of
  ac/heater/fan should be set for the automation to do anything).
- **Toggles**: `use_ac_toggle`, `use_heater_toggle`, `use_fan_toggle`,
  `manual_mode_toggle`, optional `ac_fan_only_override_toggle` and
  `heater_fan_only_override_toggle`.
- **Cooling**: `target_cooling_temp`, `cooling_medium_offset`,
  `cooling_high_offset`.
- **Timing**: `command_delay_seconds`, `power_on_delay_seconds`.
- **Heating**: `target_heating_temp`, `heating_medium_offset`,
  `heating_high_offset`.
- **Fan device**: `target_fan_temp`, `fan_medium_offset`, `fan_high_offset`.

Design points worth knowing:
- **A/C device setpoint**: in cool or climate `fan_only` mode, the blueprint
  sets the climate target to the entity's `min_temp` attribute, or **65 °F**
  if unknown. `target_cooling` is only the room threshold that turns cooling
  on; fan speed (companion fan or climate `fan_modes`) controls comfort.
- **Combined climate device** (heat pump): wire the same `climate.*`
  entity to both `ac_climate` and `heater_climate`. The blueprint detects
  `ac_climate == heater_climate` and takes the combined branch, which
  computes one `hvac_mode` (cool / heat / fan_only / off) and one target
  temperature per run.
- **A/C HVAC** (matches requirements): cool when room temp > target; at or
  below target the device is **off** unless **Fan Ovr** is on.
- **Heater HVAC**: heat when room temp < target; when use heater is on but
  the room is warm enough, **fan_only** if the device has a fan (per
  requirements); otherwise off. **Fan Ovr** also enables fan_only when use
  heater is off and use fan is on.
- **Fan Ovr** (`ac_fan_only_override_toggle` / `heater_fan_only_override_toggle`):
  when on, `fan_only` if the device use toggle is on but inactive. If the device
  use toggle is off: `fan_only` when the room has no standalone fan, or when
  `use_fan` is on; off when the room has a fan but `use_fan` is off. Heater also
  uses native `fan_only` when use heater is on, the room is warm enough, and the
  device has a fan. On a **shared heat pump** (`ac_climate == heater_climate`),
  only the A/C fan-only override toggle applies; the dashboard shows Fan Ovr on
  the Cooling row only.
- **Companion fan entity** (`ac_fan_entity` / `heater_fan_entity`): drives
  fan speed while cooling/heating when the climate lacks `fan_modes` (Office:
  `fan.office_a_c` during cool only; no fan_only on `climate.office_a_c`).
- **Use toggles**: when off, the blueprint turns that device off unless another
  rule supersedes (e.g. **Fan Ovr** on a climate entity). When on, normal
  threshold rules apply.
- **Standalone `fan_entity`**: when `use_fan` is on and room temp is above
  `target_fan_temp`, power on and set speed from medium/high thresholds (10 /
  50 / 100%); otherwise power off (including when `use_fan` is off).
- **Sensor abstraction**: blueprint inputs accept the per-room
  abstraction template sensors (e.g. `sensor.todd_s_bedroom_room_temperature`),
  not the underlying physical sensors. Re-mapping a room to a new
  underlying sensor is a one-line edit in
  [`templates/room_climate_sensors.yaml`](../templates/room_climate_sensors.yaml).
- **Humidity**: monitored on the dashboard only; not used in automation logic.

## Fan-speed mapping

For climate entities with `fan_modes`, the blueprint picks the device's
fan mode by case-insensitive substring match against the labels
`high` / `medium` / `low`. Examples:

- `climate.todd_s_a_c` fan_modes `["Auto","High","Low","Medium"]` →
  `high` → `"High"`, `medium` → `"Medium"`, `low` → `"Low"`.
- `climate.main_floor_heat_pump` fan_modes `["quiet","low","medium_low",
  "medium","medium_high","high","auto","strong"]` → exact/priority match:
  `low` → `"low"`, `medium` → `"medium"`, `high` → `"high"` (avoids
  `medium_high` / `medium_low` substring false positives).
- **Fan Ovr with both use toggles off** (shared heat pump): fan speed uses
  **cooling** thresholds (`target_cooling` + offsets), not standalone-fan
  `target_fan` helpers.

For the standalone `fan_entity`, the blueprint drives speed via
`fan.set_percentage`: low → 10%, medium → 50%, high → 100%.

For climate entities without `fan_modes`, the blueprint instead drives
the companion `ac_fan_entity` / `heater_fan_entity` via
`fan.set_percentage`: low → 10%, medium → 50%, high → 100% (matching the
standalone fan and the requirement's 10/50/100 mapping).

## Manual mode

When `input_boolean.<r>_climate_manual_mode` is `on`, the blueprint's
condition step short-circuits and no commands are sent. Use this when
you've fiddled with the device by hand and want the automation to leave
it alone for a while.

A user can also turn off all three `use_*` toggles to achieve a similar
"do nothing" state, but the device states reported in the dashboard will
still update because the blueprint will run, see "use_ac off", and set
the climate to `off`. Manual mode skips even that.

When manual mode is flipped from `on` → `off`, the automation
re-evaluates immediately (it's wired as a trigger on the `off` state of
the manual-mode toggle) so the climate state resyncs without waiting for
another input change.

## Constraint validator

[`room_climate_constraints`](../blueprints/automation/btoddb/room_climate_constraints.yaml) watches the same
3 targets and 6 offsets. It enforces ordering and range by clamping values
and creating a notification via `persistent_notification.create` (HA notifications tab):

- `target_heating < target_cooling`
- Cooling / fan: `medium_offset < high_offset`; `target + high_offset` ≤ target helper `max`
- Heating: `medium_offset < high_offset`; `target - high_offset` ≥ target helper `min`

Deployed for all three rooms via `*_constraints.yaml` in
`automations/room_climate/`.

## Outdoor temperature abstraction

[`templates/room_climate_sensors.yaml`](../templates/room_climate_sensors.yaml)
defines `sensor.outdoor_temperature`, wrapping
`sensor.btoddb_weather_outdoor_temperature`. The history graph on every
room view uses this entity so outdoor data can be re-pointed in one place.

## Dashboard usage

Room climate cards live on the **BToddB's Home** dashboard
(`lovelace.btoddb_s_home`): Todd's Bedroom, Office, and Main Floor each
use a `custom:room-climate-control` card wired to that room's backend.

### Card config keys (offsets)

Lovelace YAML uses `cooling_medium_offset`, `cooling_high_offset`, etc.
(not the legacy `cooling_medium` / `cooling_high` absolute-temp keys).

### Adding the card to any dashboard

1. Edit dashboard → **Add card** → search **Room Climate Control**.
2. Fill in the config dialog (room name, sensors, devices, backend helpers).
3. Omit optional device fields for devices the room does not have.

Each card shows: large room heading, temp/humidity, a devices panel (info
on the left; Fan Ovr and Use toggles aligned in a column on the right, plus a
**Manual Mode** row with the same **Use** toggle column), and Settings /
Energy / History dialogs. Standalone fan rows show **Off** in the Mode column
when the fan is off (not the last speed percentage). Settings shows room
sensors, target inputs, and medium/high **offset sliders** (with computed
°F shown) for each device section. Devices that support toggling built-in
lights or sound can add an optional `ac_device_button`, `heater_device_button`,
or `fan_device_button` on the card config (Lovelace `tap_action`, usually
`perform-action` → `remote.send_command`). Todd's Bedroom A/C uses this for
display lights/sound via `remote.todd_s_bedroom_remote`. The button disables
for 1 second after press as visual feedback. Footer and settings buttons share
the same `rcc-btn` styling. Plotly graphs use `input_select.time_range`.

## Onboarding a new room

1. Add three template sensors to
   [`templates/room_climate_sensors.yaml`](../templates/room_climate_sensors.yaml)
   following the existing pattern. Use the underlying sensor that
   reports the right value.
2. Add 4 `input_boolean` and 9 `input_number` entries in the two
   `helpers/` files: 3 targets (box, device min/max) + 6 offsets (slider 1–20).
3. Add control and constraints automations under `automations/room_climate/`.
4. Add a **Room Climate Control** card to any dashboard via the UI card
   picker or YAML (`type: custom:room-climate-control`).
5. Add the room to [`daily_climate/rooms.json`](../daily_climate/rooms.json)
   (with `area_id` and `slug`) and add its category IDs to `CATEGORY_IDS` in
   [`scripts/room_climate_apply_categories_areas.py`](../scripts/room_climate_apply_categories_areas.py),
   then run it (template sensors/automations resolve by `unique_id`, helpers by
   naming convention — no per-entity list to maintain).
6. Reload helpers, automations, and Lovelace (or restart HA).

## Legacy automations

These automations are superseded by room climate blueprints. **Disable them in the
Home Assistant UI** (Settings → Automations). Do not add `enabled: false` in YAML
for UI-managed automations — that can break them; UI disable state is preserved
in `.storage` instead.

| Automation | Replaced by |
|---|---|
| `automations/todds_bedroom_cooling.yaml` | Room Climate · Todd's Bedroom |
| `automations/todd_s_bedroom_heating.yaml` | Room Climate · Todd's Bedroom |
| Todd's Bedroom Fans | Room Climate · Todd's Bedroom |
| Heating/Cooling options changed | Room climate automations |
| Office Fans | Room Climate · Office |
| Office Heating/Cooling options change | Room Climate · Office |
| Office A/C | Room Climate · Office |
| Main Heating/Cooling options changed | Room Climate · Main Floor |

Active control uses **Room Climate ·** automations in `automations/room_climate/`
and `use_<room>_*` / offset helpers on the **BToddB** dashboard cards.

## Verification & smoke test

After HA restart and HACS install of **lovelace-plotly-graph-card**:

1. `ha core check` passes.
2. Six automations visible: control + constraints for each room.
3. **BToddB** dashboard room climate cards show without configuration errors.
4. Card appears in the card picker; config dialog completes without hanging.
5. Flip `input_boolean.use_todds_bedroom_ac` and confirm `climate.todd_s_a_c` responds.
6. Change a cooling offset slider in Settings; fan tier shifts at the expected room temp.
7. Set `medium_offset >= high_offset` briefly; constraints automation clamps and notifies.
