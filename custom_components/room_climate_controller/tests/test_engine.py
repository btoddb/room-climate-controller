"""Tests for the pure reactive engine and fan logic.

These modules have no Home Assistant imports, so the test loads them directly
(bypassing the package ``__init__``) and runs with plain ``pytest`` or
``python3 tests/test_engine.py`` — no HA test harness required.
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


def _climate(hvac="off", fan_mode=None, fan_modes=(), min_temp=62.0, set_temp=True,
             hvac_modes=("off", "cool")):
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
        _base(ac=_climate(fan_modes=("low", "medium", "high")), use_ac=True, room_temp=80.0)
    )
    assert _types(cmds) == [
        "SetHvacMode", "Delay", "SetTemperature", "Delay", "SetFanMode",
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
            ac=_climate(hvac_modes=("off", "cool", "fan_only"), fan_modes=("low", "high")),
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
            fan=FanInfo("fan.tower", is_on=False, preset_mode=None, percentage=0,
                        preset_modes=("low", "medium", "high")),
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
            ac_fan=FanInfo("fan.companion", is_on=False, preset_mode=None,
                           percentage=0, preset_modes=()),
            use_ac=True,
            room_temp=80.0,
        )
    )
    assert any(isinstance(c, FanSetPercentage) and c.percentage == 100 for c in cmds)


def test_no_redundant_fan_mode():
    cmds = compute_commands(
        _base(
            ac=_climate(hvac="cool", fan_mode="high", fan_modes=("low", "medium", "high")),
            use_ac=True,
            room_temp=80.0,
        )
    )
    assert not any(isinstance(c, SetFanMode) for c in cmds)


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  ok   {name}")
            except AssertionError as exc:
                failed += 1
                print(f"  FAIL {name}: {exc}")
    print("ALL PASSED" if not failed else f"{failed} FAILED")
    sys.exit(1 if failed else 0)
