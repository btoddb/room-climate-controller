# Spec: Logging

All log messages use the Python logger hierarchy
(`custom_components.room_climate_controller.*`).  Filter by that namespace in HA's
**Settings → System → Logs** to see only RCC messages.  Each message embeds
`[room=<key>]` and/or `[profile=<id>]` tags so you can narrow results with
free-text search.

Runtime events (temperature/humidity changes, profile actions, toggle changes, room
lifecycle) are emitted at **INFO** level.  Diagnostic detail — per-step config-flow
progress, entity lists registered per platform — is emitted at **DEBUG** level and
requires `custom_components.room_climate_controller: debug` in the HA logger config
to appear.

## Log events

### Temperature and humidity changes (CC-L1, CC-L2)

- **CC-L1** When the controller detects a room's temperature sensor change:
  `[room=<key>] Temperature changed: <old> → <new>°F`
  Appends ` (device commanded: <cmds>)` listing the device commands the new state
  produces, when any. A sub-degree change that crosses no whole-degree threshold
  (CC-5) should produce none — the suffix is the diagnostic for unexpected commands.
- **CC-L2** When the controller detects a room's humidity sensor change:
  `[room=<key>] Humidity changed: <old> → <new>%%`
  Appends ` (device commanded: <cmds>)` as in CC-L1. The engine ignores humidity,
  so a humidity-only change should never list commands.

Logged by `controller.py` in `_on_change`.  The humidity sensor is now tracked
alongside the temperature sensor (was previously untracked); tracking it does not
affect control decisions since the engine ignores humidity.

### Profile events (CC-L3)

**Lifecycle**
- **CC-L3a** When a profile is applied (scheduled or explicit), including its presets:
  `[room=<key> profile=<id>] Profile '<name>' applied (scheduled|explicit): cooling on@72°F, heating off@68°F`
- **CC-L3b** When a scheduled profile fires but is skipped because manual mode is on:
  `[room=<key> profile=<id>] Profile '<name>' skipped: manual mode active`
- **CC-L3c** When a profile is created via the card:
  `[room=<key> profile=<id>] Profile created: '<name>'`
- **CC-L3d** When a profile is deleted via the card:
  `[room=<key> profile=<id>] Profile deleted: '<name>'`
- **CC-L3e** When a profile is renamed via the card:
  `[room=<key> profile=<id>] Profile renamed: '<old>' → '<new>'`
- **CC-L3f** When a profile's schedule is enabled or disabled via its switch entity:
  `[room=<key> profile=<id>] Profile schedule enabled|disabled`

**Edits** (any change to a profile's settings)
- **CC-L3g** When a profile preset temperature is changed:
  `[room=<key> profile=<id>] Profile preset edited: <device> target → <N>°F`
- **CC-L3h** When a profile preset use-device toggle is changed:
  `[room=<key> profile=<id>] Profile preset edited: <device> use → on|off`
- **CC-L3i** When a profile's A/C fan-only override preset is changed:
  `[room=<key> profile=<id>] Profile preset edited: fan-only override → on|off`
- **CC-L3j** When a profile's schedule time is changed:
  `[room=<key> profile=<id>] Profile schedule time → HH:MM`

### Toggle changes (CC-L4)

- **CC-L4** When a room's use toggle or manual-mode switch changes:
  `[room=<key>] Toggle '<display name>' → on|off`

Covers: **Use A/C**, **Use heater**, **Use fan**, **Manual mode**,
**A/C fan-only override**, **Heater fan-only override**.

### Room lifecycle (CC-L5)

- **CC-L5a** When a room is first added (integration startup or after config change):
  `[room=<key>] Room created: '<label>'`
- **CC-L5b** When a room's configuration changes (config flow re-saved):
  `[room=<key>] Room settings changed: '<label>'`
- **CC-L5c** When a room is removed:
  `[room=<key>] Room removed: '<label>'`

### Window events (CC-L6)

- **CC-L6** When a window sensor transitions to open or closed:
  `[room=<key>] Window <entity_id> opened|closed`

Logged by `controller.py` in `_on_change`. Only fires when the state value actually
changes (`old_state != new_state`). Unavailable/unknown states are not treated as
open (CC-21), so no log is emitted for those transitions.

### RCC device actions (CC-L7)

- **CC-L7** When an evaluation produces one or more non-`Delay` device commands:
  `[room=<key>] RCC commanded: <phrase>, <phrase>, ... (<threshold context>)`
  One line per evaluation (not one per command), e.g.
  `[room=office] RCC commanded: A/C → cool, A/C fan speed → high (temp 78°F; cooling target 72°F (med 75°F high 78°F))`.
  Each command is rendered as a short device + action phrase (`A/C → cool`,
  `A/C setpoint → 65°F`, `Fan speed → high`, `Fan direction → reverse`,
  `A/C power on`, etc.) so a customer's log shows *why* a device changed without
  needing engine internals.

Logged by `controller.py` in `_run`, at **INFO**, after the evaluation's commands
have all been attempted, using the same per-command resolution that sent them —
so the logged phrase always matches what was actually sent, even when an earlier
command in the sequence (e.g. a `SetHvacMode`) changed the device's live range
for a later one. The threshold context lists the room temperature and the
target/medium/high thresholds for each device type the room actually has — the
same data the troubleshooting scenarios in issue #14 need (e.g. "does the fan
have the right thresholds?").

### Room target/offset edits (CC-L8)

- **CC-L8** When a room's target temperature or medium/high offset number changes:
  `[room=<key>] <name> → <N>°F`
  e.g. `[room=office] Cooling target → 72°F`.

Logged by `number.py` in `RoomNumber.async_set_native_value`, at **INFO**, only when
the value actually changed (mirrors the existing `ProfilePresetNumber` pattern).

### Profile moved (CC-L9)

- **CC-L9** When a profile is moved to a different room via the card:
  `[room=<key> profile=<id>] Profile moved: <old room> → <new room>`

Logged by `websocket_api.py` in `ws_set_room`, at **INFO**, before the config entry
reload that rebuilds the profile's entities. `<key>` is the profile's new room.

### Device/fan capability dumps (CC-L10)

- **CC-L10** A one-line capability dump per configured climate/fan entity:
  `[room=<key>] A/C capabilities: <entity_id>: hvac_modes=[...], fan_only=yes|no, fan_modes=[...], min_temp=<N>, max_temp=<N>`
  `[room=<key>] Fan capabilities: <entity_id>: preset_modes=[...], reversible=yes|no, percentage_step=<N>`

Emitted at **DEBUG**:
- by `controller.py` (`RoomController._log_capabilities`) shortly after the
  controller starts and again after the delayed resubscribe, once entities have
  registered;
- by `config_flow.py` (`async_step_devices`) right after a climate/fan entity is
  selected in room setup — this directly answers "does this A/C have a
  `fan_only` mode?" from the config flow, before the room is even fully set up.

Both call sites share the formatting helpers `describe_climate_capabilities` /
`describe_fan_capabilities` in `entity.py` so the two dumps never drift. An
entity whose state isn't loaded yet logs `<entity_id> (unavailable)` rather than
raising.

### Resolved thresholds snapshot (CC-L11)

- **CC-L11** Once per evaluation, the resolved room temperature and per-device
  thresholds plus the use-toggle/window state:
  `[room=<key>] temp 78°F; cooling target 72°F (med 75°F high 78°F); use ac=on heater=off fan=off window_open=no`

Logged by `controller.py` in `_run`, at **DEBUG**, right after `_build_inputs`
succeeds. This is the other half of the CC-L7 context, but always emitted (even
when no command was produced) — it answers "what are the room's thresholds for
the A/C and Fan?" directly from the log, without changing the temperature again
to provoke a command.

### Copy/paste room settings (out of scope)

Copy and paste run entirely in the browser (`card/src/profiles/clipboard.ts`,
`copy-room-settings.ts`) and never call a websocket command, so the integration
cannot log the button presses themselves. This was confirmed out of scope for
issue #14. Their effects are still visible in the log once applied: paste writes
room numbers/switches (CC-L4/CC-L8) or creates a profile (CC-L3c).
