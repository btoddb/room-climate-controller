# Spec: Per-room climate control

The integration maintains each room's target temperature (and drives fan speed)
by reactively controlling that room's real `climate` / `fan` / `switch` devices.
The decision logic is a **pure function**,
[`compute_commands(inputs)`](../../custom_components/room_climate_controller/engine.py);
[`controller.py`](../../custom_components/room_climate_controller/controller.py)
gathers live state, calls it, and executes the returned commands. Manual-mode
gating is the controller's job — the engine assumes control is active.

## Devices & wiring

A room has up to three **device types**, in canonical order: **cooling** (A/C),
**heating** (heater), **fan** (standalone). A room only has the devices it's
configured with; absent devices are ignored in all rules, entities, and the card.
A room may also have optional **window sensors** that suppress conditioning
while any is open (CC-20).

- **CC-1** Each device type has an independent **Use** toggle. Use on → the engine may drive that device. Use off → the device is turned off unless another rule supersedes it (see fan-only override).
- **CC-2** A **combined** room wires one `climate` entity to *both* cooling and heating (a heat pump). It's modeled by `combined=True` with `ac_climate == heater_climate`; the engine runs the combined branch instead of separate A/C + heater branches.
- **CC-3** A climate device is **fan-capable** if its `hvac_modes` include `fan_only` or it exposes any `fan_modes`. Fan speed is driven either via the climate's own `fan_mode` or, failing that, a configured **companion fan** entity (`ac_fan_entity` / `heater_fan_entity`).
- **CC-4** A device may have an optional **power switch** (`ac_power_switch` / `heater_power_switch`). The engine powers it on (then waits `power_on_delay`) before driving the climate, and powers it off when the decision is OFF.

## Per-room controls (entities)

For each device the room has, the integration creates live entities the engine
reads and the card/profiles write:

- **Target temp** — `number.*` (`target_cooling_temp` / `target_heating_temp` / `target_fan_temp`).
- **Medium offset** and **High offset** — `number.*`, range **1–20 °F** (`OFFSET_MIN`/`OFFSET_MAX`). They define the fan-speed thresholds (CC-7).
- **Use** toggle — `switch.*` (`use_ac` / `use_heater` / `use_fan`).
- **Manual mode** — one `switch.*` per room (`manual_mode`).
- **Fan-only override** — `switch.*` per applicable device (see CC-12).

## Temperature comparison

- **CC-5** All comparisons **truncate to whole degrees** (`int(value)`) — room temp, targets, and thresholds alike. Displays may show tenths.

## Idempotent command emission

- **CC-19** The engine emits a device command **only when it changes the device's state**. Every command is gated against the device's currently-reported state and skipped when already satisfied: HVAC-mode / setpoint / fan-mode sets against the climate's reported mode/setpoint/fan_mode, and turn-on/turn-off of climates, fans, and power switches against their current on/off state. Combined with CC-5, a fractional sensor change that leaves the truncated comparison unchanged produces **no commands** — important because many devices (e.g. heat pumps) audibly chirp on every received command.

## Thresholds & fan-speed tiers

Speed is a 3-tier function of how far the room is past the target:

- **CC-6** Fan-speed tiers are **Low / Medium / High**, mapped to `10% / 50% / 100%` for percentage-controlled fans. For devices with named `fan_modes`, the tier label is matched onto the device's modes (preference list + substring fallback in [`fan_logic.py`](../../custom_components/room_climate_controller/fan_logic.py)).
- **CC-7** Thresholds derive from the target plus the offsets:
  - **Cooling / fan** (hotter ⇒ faster): `medium = target + medium_offset`, `high = target + high_offset`, with `target < medium < high`. Room `≥ high` ⇒ High; `≥ medium` ⇒ Medium; else Low.
  - **Heating** (colder ⇒ faster): `medium = target − medium_offset`, `high = target − high_offset`, with `high < medium < target`. Room `≤ high` ⇒ High; `≤ medium` ⇒ Medium; else Low.
- **CC-8** The **high offset must exceed the medium offset** (constraint, clamped — see CC-16).

## Cooling (A/C) control — split rooms

- **CC-9** Decision: if **Use A/C** on **and** room > target_cooling → **Cool**. Else if fan-only override applies (CC-12) → **Fan Only**. Else → **Off**.
- The engine controls comfort via fan speed, so the climate's own setpoint is driven to its **lowest settable value** (`min_temp`), or **65 °F** when the device doesn't report one.
- Fan speed while cooling follows the cooling tiers (CC-7) via climate `fan_mode` or the companion `ac_fan`.

## Heating control — split rooms

- **CC-10** Decision: if **Use heater** on **and** room < target_heating → **Heat** (setpoint = target_heating, truncated). Else if the heater is fan-capable and (Use heater on **or** fan-only override applies) → **Fan Only**. Else → **Off**.
- Fan speed while heating/fan-only follows the heating tiers (CC-7).

## Combined heat-pump control

- **CC-11** A combined climate picks one decision for the single entity: **Cool** (Use A/C on & room > target_cooling), **Heat** (Use heater on & room < target_heating), **Fan Only** (when an override/native-fan condition holds), else **Off**. Setpoint is the heating target when heating, otherwise the cooling floor (CC-9). For a combined device, **fan-only override is offered for cooling only** (CC-12).

## Fan-only override

- **CC-12** Available only on **fan-capable cooling/heating** devices (and cooling-only on combined). When a device would otherwise turn **off**, the override can instead run it in **fan-only** mode:
  - **Use on, but not actively heating/cooling** → fan-only.
  - **Use off** → fan-only **only if** the room has no standalone fan, *or* its standalone fan's Use toggle is on; otherwise off.
  - Heaters additionally run fan-only **natively** whenever Use heater is on and they're not actively heating (no override needed).

## Standalone fan control

- **CC-13** The fan runs when **Use fan** on **and** room > target_fan; otherwise it's turned off.
- **CC-14** While on, speed follows the cooling-style tiers (CC-7) against `target_fan` + fan offsets, mapped to 10/50/100% or the fan's preset modes.

## Manual mode

- **CC-15** When a room's **manual mode** switch is on, the engine does not drive that room — the user's manual device settings stand. Turning it off resumes control, which may overwrite settings per the rules. Scheduled profile applies are skipped in manual mode; an explicit "apply now" overrides this (see `profiles.md`).

## Window sensors

A room may configure zero or more optional **window** `binary_sensor`s
(`window_sensors`). They only affect their own room's conditioning.

- **CC-20** A room counts as **window open** when **any** of its window sensors reads `on`. While open, the engine suppresses the **Cool** and **Heat** decisions — a device actively cooling/heating is turned off via the normal OFF path. **Fan-only is not suppressed**: the standalone fan (CC-13), a fan-capable heater's native fan-only, and the fan-only overrides (CC-12) still run, because they circulate air without spending heating/cooling energy. Profile applies still write uses/targets (see `profiles.md`); suppression is enforced at evaluation, so closing every window re-evaluates each device against the current targets with no re-apply. Manual mode (CC-15) still gates first — an open window never overrides a manually driven device.
- **CC-21** Fail-safe: a window sensor reading `unavailable`/`unknown` is treated as **closed**, per sensor. A room with all sensors closed (or none configured) behaves exactly as a room with no window sensor — conditioning is never suppressed on bad/missing data.

## Constraints (advisory clamping)

[`constraints.py`](../../custom_components/room_climate_controller/constraints.py)
watches a room's target/offset numbers; on an invalid combination it **clamps**
the offending value and raises a **persistent notification** (HA notifications
tab) — non-blocking, no deprecated notify methods.

- **CC-16** High offset > medium offset (per device).
- **CC-17** **Heating target must stay below cooling target** (when the room has both).
- **CC-18** A device's `target ± high_offset` must stay within that device's configured min/max limits; the high offset is clamped to fit.
- The validator ignores the echo of its own clamp writes so two rules can't ping-pong a value.

## Command timing

- **CC-19** Commands are spaced by `command_delay` (default 2 s) and a longer `power_on_delay` (default 3 s) after powering a switch, to let devices settle. The engine emits explicit `Delay` commands; the controller honors them.
