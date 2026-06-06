# Climate Profiles — Setup & Operations Guide

Operational reference for [daily-climate-routines.md](./daily-climate-routines.md).

## Architecture

```
daily_climate/profiles.yaml  →  sync  →  helpers + automations (one room each)
Room Climate card (Profiles section)  →  edit / run / copy profiles for that room
```

Each profile stores presets for **use toggles**, **fan override**, and **target temps** for one room.

Room keys: `todds_bedroom`, `office_room`, `main_floor_room`.

## Profile mutations (add / delete / rename / set-room)

All run through **`scripts/daily_climate_run.py`** via `shell_command` plus **HA script actions** for reload/finalize (shell cannot call `input_boolean.reload` reliably — API 401).

**Add flow:** script sets `input_text.daily_climate_op_request` JSON → `add-prepare` (YAML + sync) → helper **reload** in the script → set schedule time → `add-complete` (profile preset defaults only; does **not** call Apply-now). Use **Use room settings** on the card before Create to copy live room values into the new profile after add. Default presets: use toggles off, target temps at device minimums (e.g. office cooling 45 °F).

Optional: `daily_climate_api_token` in **`secrets.yaml`** for CLI/direct Python only.

- **File lock** (`daily_climate/.profile_ops.lock`) serializes mutations so concurrent shell commands cannot corrupt `profiles.yaml`.
- **Op results** for the card are written only to `/local/btoddb/daily-climate-op-result.json` (monotonic `v`); the card polls that file (and the optional `input_text` mirror).

**Add:** one shell — YAML + sync + reload + set time/presets (full pipeline inside the lock).

**Delete:** one shell — CLI delete + sync + reload (inside the lock).

**Rename / set-room:** one shell each; HA script may `script.reload` afterward for Apply-now YAML.

## Room climate card

Resource: `/local/btoddb/room-climate-card/room-climate-control-card.js?v=1.4.2`

In the card editor, set **Climate profile room key** (or rely on auto-detect from the manual mode entity, e.g. `input_boolean.office_room_climate_manual_mode` → `office_room`).

The **Profiles** section on each room card (below Settings / Energy / History):

- Lists profiles for that room, sorted by run time (`HH:MM · name`)
- Expand a profile to edit time, enabled, use toggles, fan override, and preset temps
- Toolbar first: **Copy room**, then **Add** (opens name + time + Create/Cancel; default time is the next 15-minute mark after now, skipping times already used in the room)
- Profile list below, sorted by run time; expanding a profile keeps focus on that profile when a time change reorders the list
- **Apply now**, **Copy**, **Paste** per profile
- Action buttons show success/failure via icon/color only (label and button size stay fixed)
- Two profiles on the same room cannot share the same run time

Profile UI lives only on the room climate card (the standalone daily-routine card was removed).

## Fresh start / purge all profiles

```bash
ha core stop
python3 scripts/daily_climate_purge_profiles.py
ha core start
```

This clears `profiles.yaml`, regenerates empty helper files, and removes orphaned `daily_routine_*` entities and `daily_climate_routine_*` automations from `.storage`.

Add profiles from the room card (**Add** in Profiles) or CLI:

```bash
python3 scripts/daily_climate_profile_cli.py add "Before I wake up" todds_bedroom 06:30
```

## Categories

After adding or renaming profiles, the add/delete/rename/set-room scripts run sync and **reload scripts** where needed so Apply now includes the new profile. You can also run `python3 scripts/daily_climate_sync_profiles.py` then **Reload scripts** in HA.

Profile sync (`daily_climate_sync_profiles.py`, or add/delete/rename from the card) automatically assigns the **Room Profiles** automation category. You can also run manually:

```bash
python3 scripts/daily_climate_apply_categories.py
```

## Manual mode

Scheduled runs skip rooms with **manual mode** on. **Apply now** copies preset values to live helpers directly (works even when the profile is disabled; does not check manual mode).
