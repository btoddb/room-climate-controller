# Spec: Logging

All log messages are emitted at **INFO** level and use the Python logger hierarchy
(`custom_components.room_climate_controller.*`).  Filter by that namespace in HA's
**Settings → System → Logs** to see only RCC messages.  Each message embeds
`[room=<key>]` and/or `[profile=<id>]` tags so you can narrow results with
free-text search.

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
