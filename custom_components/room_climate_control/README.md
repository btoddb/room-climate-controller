# Room Climate

A Home Assistant custom integration that manages per-room climate control and
scheduled daily climate **profiles** from the UI — replacing what used to be a
sprawl of `shell_command` + standalone Python + code-generated YAML + blueprints.

Everything runs **in-process**: rooms and profiles are configured through the UI,
their controls are **native entities**, and a reactive engine drives your real
`climate` / `fan` / `switch` devices from the room's setpoints.

## What it does

- **Per-room reactive control.** For each room you wire its devices (A/C, heater,
  standalone fan, optional companion fans and power switches) and a temperature
  sensor. The integration creates the room's live controls as entities
  (`number.*` targets/offsets, `switch.*` use-toggles / manual-mode /
  fan-only-override) and a `RoomController` reacts to them — choosing
  cool/heat/fan-only/off, fan speed tiers, and honoring a manual-mode kill switch.
  Supports combined heat-pumps and split A/C + heater setups.
- **Daily profiles.** A profile is a named, scheduled preset for a room (per-device
  target temps + use toggles + fan-only override). At its scheduled time (or via
  "apply now") it copies its presets onto the room's live entities and the
  controller takes it from there. Profiles are stored in `.storage` and edited
  through the card or their own entities (`switch.*`, `time.*`, `number.*`).

## Architecture

| Concern | Where |
|---|---|
| Hub + rooms | One config entry; each **room is a config subentry** (`config_flow.py`) |
| Profiles | Stored in `.storage` (`store.py`), managed over websocket (`websocket_api.py`) |
| Entities | Dynamic `number`/`switch`/`time`/`sensor` platforms, grouped by per-room and per-profile devices |
| Reactive engine | **Pure**, HA-free `engine.py` + `fan_logic.py` (unit-tested); executed by `controller.py` |
| Constraints | `constraints.py` clamps invalid target/offset combinations |
| Scheduling | `scheduler.py` (`async_track_time_change`), applying via `apply.py` |

The decision engine is deliberately a pure function — `compute_commands(inputs)`
returns an ordered list of device commands — so the bulk of the logic is testable
without Home Assistant (see `tests/`).

## Installation (manual)

1. Copy `custom_components/room_climate/` into your HA config's
   `custom_components/` directory.
2. Restart Home Assistant.
3. **Settings → Devices & Services → Add Integration → "Room Climate"**.
4. On the entry, choose **Add room** and wire one room's devices, sensors, limits,
   and timing. Repeat per room.

No YAML, no `secrets.yaml` token, no scripts to copy.

## The Lovelace card

The companion card (`www/.../room-climate-card`) talks to the integration over
websocket. Point its entity pickers at the room's generated entities (the editor
accepts the new `number`/`switch`/`time` domains). The card's profile panel
create/delete/rename/apply all go through the websocket API.

> The integration does not yet auto-register the card as a Lovelace resource;
> add it as a `module` resource (or deploy via the card's `deploy.sh`). Auto-
> registration is planned for the HACS-distributed build.

## Services

- `room_climate.apply_profile` `{ profile_id }` — apply a profile's presets now.
- `room_climate.set_manual_mode` `{ room, enabled }` — toggle a room's manual mode.

## Development

Run the pure-logic tests (no HA required):

```bash
python3 custom_components/room_climate/tests/test_engine.py
# or, with pytest:
pytest custom_components/room_climate/tests/
```

## Distributing via HACS

This integration is structured to be lifted into its own repository for HACS:

1. Create a repo whose root contains `custom_components/room_climate/`.
2. Add a root `hacs.json`:
   ```json
   { "name": "Room Climate", "render_readme": true }
   ```
3. Add it as a HACS **custom repository** (category: Integration). Users then
   install and "Add Integration" as above.

(`hacs.json` lives at the **repo root** of that dedicated repo, not inside the HA
config directory, which is why it isn't committed here.)
