# Integration code — guidance

Python custom integration `room_climate_controller`. Behavior is specified in
[../../requirements/](../../requirements/) (start at `requirements/README.md`);
this file is about *how the code is laid out and tested*.

## Module map

| File | Responsibility |
|---|---|
| `engine.py` | **Pure** decision engine — `compute_commands(inputs)` returns ordered device commands. No HA imports. |
| `fan_logic.py` | **Pure** 3-tier fan-speed selection + device `fan_mode` matching. |
| `controller.py` | HA glue: gathers live state into `EngineInputs`, calls the engine, executes commands, honors manual mode. |
| `scheduler.py` | Fires profiles at their scheduled time (`async_track_time_change`). |
| `apply.py` | Copies a profile's presets onto the room's live entities. |
| `constraints.py` | Advisory clamping of invalid target/offset combinations + persistent notifications. |
| `config_flow.py` | Hub config entry + one **room per config subentry**. |
| `models.py` | `Room` / `Profile` data models and pure ID/time helpers. No HA imports. |
| `store.py` | Profile persistence in `.storage`. |
| `websocket_api.py` | Card ↔ integration profile CRUD. |
| `const.py` | All config keys, entity-key maps, defaults, limits. |
| `number.py` / `switch.py` / `time.py` / `select.py` / `sensor.py` | Dynamic entity platforms (per-room and per-profile). |

## Rules

- **Python 3.14+.** Format and lint with **ruff** (`scripts/lint`); make coding choices with ruff's rules in mind.
- **Keep `engine.py`, `fan_logic.py`, and `models.py` HA-free** — that's what makes the control logic unit-testable in plain Python. Don't add `homeassistant` imports there.
- **Entity identity is deterministic.** Use `room_uid()` / `profile_uid()` (`models.py`) and the `KEY_*` maps (`const.py`) — don't hand-build unique_ids.

## Tests

The engine is tested without Home Assistant:

```bash
python3 custom_components/room_climate_controller/tests/test_engine.py
# or: pytest custom_components/room_climate_controller/tests/
```

Add a failing engine test before changing control logic; map cases to the `CC-*`
rules in `requirements/spec/climate-control.md`.
