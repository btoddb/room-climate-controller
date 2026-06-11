"""
Tests for the pure reactive engine and fan logic.

These modules have no Home Assistant imports, so the test loads them directly
(via the ``_load`` shim, bypassing the package ``__init__``) and runs under plain
``pytest`` — no HA test harness required::

    pytest custom_components/room_climate_controller/tests/
"""

import importlib.util
import pathlib
import sys
import types

_PKG = pathlib.Path(__file__).resolve().parents[1]


def _load(name: str):
    """Load a pure module under a throwaway package so relative imports work."""
    if "rc_pure" not in sys.modules:
        pkg = types.ModuleType("rc_pure")
        pkg.__path__ = [str(_PKG)]
        sys.modules["rc_pure"] = pkg
    spec = importlib.util.spec_from_file_location(
        f"rc_pure.{name}", _PKG / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"rc_pure.{name}"] = module
    spec.loader.exec_module(module)
    return module


fan_logic = _load("fan_logic")
engine = _load("engine")

from rc_pure.engine import (  # noqa: E402
    ClimateInfo,
    EngineInputs,
    FanInfo,
    FanSetPercentage,
    FanSetPreset,
    SetFanMode,
    SetHvacMode,
    SetTemperature,
    SwitchInfo,
    SwitchTurnOn,
    any_window_open,
    compute_commands,
)


def _types(cmds):
    return [type(c).__name__ for c in cmds]


def _base(**kw):
    defaults = dict(
        combined=False,
        room_temp=72.0,
        ac=None,
        heater=None,
        fan=None,
        ac_fan=None,
        heater_fan=None,
        ac_power=None,
        heater_power=None,
        use_ac=False,
        use_heater=False,
        use_fan=False,
        ac_fan_only_override=False,
        heater_fan_only_override=False,
        target_cooling=72.0,
        cooling_medium=75.0,
        cooling_high=78.0,
        target_heating=68.0,
        heating_medium=65.0,
        heating_high=62.0,
        target_fan=72.0,
        fan_medium=75.0,
        fan_high=78.0,
        command_delay_ms=2000,
        power_on_delay_ms=3000,
    )
    defaults.update(kw)
    return EngineInputs(**defaults)


def _climate(
    hvac="off",
    fan_mode=None,
    fan_modes=(),
    min_temp=62.0,
    set_temp=True,
    hvac_modes=("off", "cool"),
):
    return ClimateInfo(
        entity_id="climate.ac",
        hvac_mode=hvac,
        fan_mode=fan_mode,
        hvac_modes=hvac_modes,
        fan_modes=tuple(fan_modes),
        min_temp=min_temp,
        supports_set_temp=set_temp,
    )


# --- fan_logic --------------------------------------------------------------
def test_cooling_tiers():
    assert fan_logic.cooling_speed(70, 75, 78) == ("low", 10)
    assert fan_logic.cooling_speed(76, 75, 78) == ("medium", 50)
    assert fan_logic.cooling_speed(80, 75, 78) == ("high", 100)


def test_heating_tiers():
    assert fan_logic.heating_speed(60, 65, 62) == ("high", 100)
    assert fan_logic.heating_speed(64, 65, 62) == ("medium", 50)
    assert fan_logic.heating_speed(70, 65, 62) == ("low", 10)


def test_fan_mode_matching():
    assert fan_logic.match_fan_mode(["low", "medium", "high"], "high") == "high"
    assert fan_logic.match_fan_mode(["quiet", "strong"], "low") == "quiet"
    assert fan_logic.match_fan_mode(["quiet", "strong"], "high") == "strong"
    assert fan_logic.match_fan_mode(["medium_low"], "medium") == "medium_low"
    # "high" must not match "medium_high"
    assert fan_logic.match_fan_mode(["medium_high"], "high") == ""
    assert fan_logic.match_fan_mode(["auto"], "low") == ""


# --- engine -----------------------------------------------------------------
def test_split_ac_cool_with_fan_high():
    cmds = compute_commands(
        _base(
            ac=_climate(fan_modes=("low", "medium", "high")),
            use_ac=True,
            room_temp=80.0,
        )
    )
    assert _types(cmds) == [
        "SetHvacMode",
        "Delay",
        "SetTemperature",
        "Delay",
        "SetFanMode",
    ]
    assert cmds[0].hvac_mode == "cool"
    # A/C is driven to its lowest settable temp (min_temp=62 here), not a 65 floor.
    assert isinstance(cmds[2], SetTemperature) and cmds[2].temperature == 62
    assert isinstance(cmds[4], SetFanMode) and cmds[4].fan_mode == "high"


def test_split_ac_off_when_use_off():
    cmds = compute_commands(_base(ac=_climate(hvac="cool"), use_ac=False))
    assert _types(cmds) == ["SetHvacMode", "Delay", "TurnOffClimate"]
    assert cmds[0].hvac_mode == "off"


def test_ac_fan_only_override():
    cmds = compute_commands(
        _base(
            ac=_climate(
                hvac_modes=("off", "cool", "fan_only"), fan_modes=("low", "high")
            ),
            use_ac=True,
            room_temp=70.0,
            ac_fan_only_override=True,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "fan_only" for c in cmds)


def test_power_switch_gating():
    cmds = compute_commands(
        _base(
            ac=_climate(),
            ac_power=SwitchInfo("switch.ac_power", is_on=False),
            use_ac=True,
            room_temp=80.0,
        )
    )
    assert isinstance(cmds[0], SwitchTurnOn)


def test_combined_heat_pump_heats():
    cmds = compute_commands(
        _base(
            combined=True,
            ac=_climate(hvac_modes=("off", "cool", "heat"), fan_modes=("low", "high")),
            use_ac=True,
            use_heater=True,
            room_temp=60.0,
            target_heating=68.0,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "heat" for c in cmds)
    assert any(isinstance(c, SetTemperature) and c.temperature == 68 for c in cmds)


def test_standalone_fan_medium():
    cmds = compute_commands(
        _base(
            fan=FanInfo(
                "fan.tower",
                is_on=False,
                preset_mode=None,
                percentage=0,
                preset_modes=("low", "medium", "high"),
            ),
            use_fan=True,
            room_temp=76.0,
        )
    )
    assert _types(cmds) == ["FanTurnOn", "Delay", "FanSetPreset"]
    assert isinstance(cmds[2], FanSetPreset) and cmds[2].preset_mode == "medium"


def test_companion_fan_percentage():
    cmds = compute_commands(
        _base(
            ac=_climate(fan_modes=()),
            ac_fan=FanInfo(
                "fan.companion",
                is_on=False,
                preset_mode=None,
                percentage=0,
                preset_modes=(),
            ),
            use_ac=True,
            room_temp=80.0,
        )
    )
    assert any(isinstance(c, FanSetPercentage) and c.percentage == 100 for c in cmds)


def test_no_redundant_fan_mode():
    cmds = compute_commands(
        _base(
            ac=_climate(
                hvac="cool", fan_mode="high", fan_modes=("low", "medium", "high")
            ),
            use_ac=True,
            room_temp=80.0,
        )
    )
    assert not any(isinstance(c, SetFanMode) for c in cmds)


def test_split_heater_heats():
    """Heater-alone (no AC, not combined) drives to HEAT with the heating target."""
    cmds = compute_commands(
        _base(
            heater=_climate(
                hvac="off", hvac_modes=("off", "heat"), fan_modes=("low", "high")
            ),
            use_heater=True,
            room_temp=60.0,
            target_heating=68.0,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "heat" for c in cmds)
    assert any(isinstance(c, SetTemperature) and c.temperature == 68 for c in cmds)


def test_combined_off_when_uses_disabled():
    """Combined device with neither use selected turns the climate off, no setpoint."""
    cmds = compute_commands(
        _base(
            combined=True,
            ac=_climate(
                hvac="heat",
                hvac_modes=("off", "cool", "heat"),
                fan_modes=("low", "high"),
            ),
            use_ac=False,
            use_heater=False,
            room_temp=60.0,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "off" for c in cmds)
    assert not any(isinstance(c, SetTemperature) for c in cmds)


def test_split_ac_truncates_before_compare():
    """Comparisons truncate to whole degrees: 72.9 -> 72, so 72 > 72 is False."""
    cmds = compute_commands(
        _base(
            ac=_climate(hvac="off", fan_modes=("low", "high")),
            use_ac=True,
            room_temp=72.9,  # truncates to 72, not rounded up to 73
            target_cooling=72.0,
        )
    )
    assert not any(isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cmds)

    # One whole degree warmer (73) does cross the threshold and triggers cooling.
    cmds_hot = compute_commands(
        _base(
            ac=_climate(hvac="off", fan_modes=("low", "high")),
            use_ac=True,
            room_temp=73.0,
            target_cooling=72.0,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cmds_hot)


def test_combined_fan_only_uses_cooling_tiers():
    """Combined FAN_ONLY with AC in use picks cooling fan tiers."""
    cmds = compute_commands(
        _base(
            combined=True,
            ac=_climate(
                hvac="cool",
                hvac_modes=("off", "cool", "heat", "fan_only"),
                fan_modes=("low", "high"),
            ),
            use_ac=True,
            use_heater=True,
            room_temp=72.0,  # within deadband: no cool, no heat
            target_cooling=75.0,
            target_heating=68.0,
            cooling_medium=75.0,
            cooling_high=78.0,
            ac_fan_only_override=True,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "fan_only" for c in cmds)
    # cooling_speed(72, 75, 78) -> "low"
    assert any(isinstance(c, SetFanMode) and c.fan_mode == "low" for c in cmds)


def test_combined_fan_only_heater_only_uses_heating_tiers():
    """
    Combined FAN_ONLY with only the heater in use picks heating fan tiers.

    Chosen so heating and cooling tiers diverge: heating_speed(63, 65, 62) -> "medium"
    while cooling_speed(63, 75, 78) -> "low", proving the heating path is taken.
    """
    cmds = compute_commands(
        _base(
            combined=True,
            ac=_climate(
                hvac="heat",
                hvac_modes=("off", "cool", "heat", "fan_only"),
                fan_modes=("low", "medium", "high"),
            ),
            use_ac=False,
            use_heater=True,
            room_temp=63.0,  # >= target_heating, so no active heating
            target_heating=62.0,
            heating_medium=65.0,
            heating_high=62.0,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "fan_only" for c in cmds)
    assert any(isinstance(c, SetFanMode) and c.fan_mode == "medium" for c in cmds)


# --- window sensor (CC-20 / CC-21) ------------------------------------------
def test_window_open_blocks_split_ac():
    """CC-20: open window suppresses Cool regardless of temp delta / Use toggle."""
    cmds = compute_commands(
        _base(
            ac=_climate(hvac="off", fan_modes=("low", "high")),
            use_ac=True,
            room_temp=80.0,
            window_open=True,
        )
    )
    assert not any(isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cmds)
    assert not any(isinstance(c, SetTemperature) for c in cmds)


def test_window_open_turns_off_running_ac():
    """CC-20: an A/C actively cooling is turned off when the window opens."""
    cmds = compute_commands(
        _base(
            ac=_climate(hvac="cool", fan_modes=("low", "high")),
            use_ac=True,
            room_temp=80.0,
            window_open=True,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "off" for c in cmds)
    assert not any(isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cmds)


def test_window_open_turns_off_running_heater():
    """CC-20: a (non-fan) heater actively heating is turned off on window open."""
    cmds = compute_commands(
        _base(
            heater=_climate(hvac="heat", hvac_modes=("off", "heat")),
            use_heater=True,
            room_temp=60.0,
            target_heating=68.0,
            window_open=True,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "off" for c in cmds)
    assert not any(isinstance(c, SetHvacMode) and c.hvac_mode == "heat" for c in cmds)


def test_window_open_combined_blocks_both():
    """CC-20: a combined heat pump conditions in neither direction when open."""
    cooling = compute_commands(
        _base(
            combined=True,
            ac=_climate(hvac="cool", hvac_modes=("off", "cool", "heat")),
            use_ac=True,
            room_temp=80.0,
            window_open=True,
        )
    )
    assert not any(
        isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cooling
    )

    heating = compute_commands(
        _base(
            combined=True,
            ac=_climate(hvac="heat", hvac_modes=("off", "cool", "heat")),
            use_heater=True,
            room_temp=60.0,
            target_heating=68.0,
            window_open=True,
        )
    )
    assert not any(
        isinstance(c, SetHvacMode) and c.hvac_mode == "heat" for c in heating
    )


def test_window_close_resumes_cooling():
    """CC-20: closing the window re-enables Cool (pure re-evaluation)."""
    cmds = compute_commands(
        _base(
            ac=_climate(hvac="off", fan_modes=("low", "high")),
            use_ac=True,
            room_temp=80.0,
            window_open=False,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cmds)
    assert any(isinstance(c, SetTemperature) for c in cmds)


def test_window_open_standalone_fan_unaffected():
    """CC-20: the standalone fan runs identically open or closed."""

    def _run(*, window_open):
        return compute_commands(
            _base(
                fan=FanInfo(
                    "fan.tower",
                    is_on=False,
                    preset_mode=None,
                    percentage=0,
                    preset_modes=("low", "medium", "high"),
                ),
                use_fan=True,
                room_temp=80.0,
                window_open=window_open,
            )
        )

    assert _types(_run(window_open=True)) == _types(_run(window_open=False))
    assert any(type(c).__name__ == "FanTurnOn" for c in _run(window_open=True))


def test_window_open_targets_written_but_suppressed():
    """CC-20: a just-applied profile's low target still can't cool while open."""
    cmds = compute_commands(
        _base(
            ac=_climate(hvac="off", fan_modes=("low", "high")),
            use_ac=True,
            room_temp=80.0,
            target_cooling=68.0,  # freshly applied aggressive cooling target
            window_open=True,
        )
    )
    assert not any(isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cmds)


def test_window_open_ac_fan_only_override_still_runs():
    """CC-20: fan-only override is circulation, not conditioning — still runs."""
    cmds = compute_commands(
        _base(
            ac=_climate(
                hvac_modes=("off", "cool", "fan_only"), fan_modes=("low", "high")
            ),
            use_ac=True,
            room_temp=80.0,
            ac_fan_only_override=True,
            window_open=True,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "fan_only" for c in cmds)
    assert not any(isinstance(c, SetHvacMode) and c.hvac_mode == "cool" for c in cmds)


def test_window_open_heater_native_fan_only():
    """CC-20: a fan-capable heater still runs native fan-only with the window open."""
    cmds = compute_commands(
        _base(
            heater=_climate(
                hvac="heat",
                hvac_modes=("off", "heat", "fan_only"),
                fan_modes=("low", "high"),
            ),
            use_heater=True,
            room_temp=60.0,
            target_heating=68.0,
            window_open=True,
        )
    )
    assert any(isinstance(c, SetHvacMode) and c.hvac_mode == "fan_only" for c in cmds)
    assert not any(isinstance(c, SetHvacMode) and c.hvac_mode == "heat" for c in cmds)


# --- multi-window aggregation + fail-safe (CC-20 / CC-21) -------------------
def test_no_window_sensors_is_closed():
    """CC-21: a room with no window sensors is never "open"."""
    assert any_window_open(()) is False


def test_single_window_open_and_closed():
    """CC-20: one sensor — open when "on", closed otherwise."""
    assert any_window_open(("on",)) is True
    assert any_window_open(("off",)) is False


def test_two_windows_aggregate_any_open():
    """CC-20: with two sensors the room is open if EITHER reads "on"."""
    assert any_window_open(("off", "off")) is False  # both closed
    assert any_window_open(("on", "on")) is True  # both open
    assert any_window_open(("off", "on")) is True  # one open
    assert any_window_open(("on", "off")) is True  # one open (order-independent)


def test_window_failsafe_bad_states_are_closed():
    """CC-21: missing/unavailable/unknown readings are treated as closed."""
    assert any_window_open((None,)) is False
    assert any_window_open(("unavailable", "unknown")) is False
    # A good "on" still wins even when another sensor is unavailable.
    assert any_window_open(("unavailable", "on")) is True
