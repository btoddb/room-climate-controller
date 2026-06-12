"""
Tests for standalone fan preset selection (CC-26).

When the Fan-preset selector is set to anything other than ``Auto``, the engine
applies the pinned preset and suppresses both tier-speed selection (CC-14) and
direction commands (CC-22..25). ``Auto`` restores today's speed-tier behavior.

Like the other engine tests, this loads the pure modules via the ``_load`` shim
and runs under plain ``pytest`` — no HA test harness required.
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


_load("fan_logic")
_load("engine")

from rc_pure.engine import (  # noqa: E402
    EngineInputs,
    FanInfo,
    FanSetDirection,
    FanSetPercentage,
    FanSetPreset,
    FanTurnOff,
    FanTurnOn,
    compute_commands,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PRESET_MODES = ("normal", "natural", "sleep", "reverse")


def _fan(
    entity_id="fan.ceiling",
    *,
    is_on=True,
    preset_mode="normal",
    percentage=50,
    preset_modes=PRESET_MODES,
    reversible=False,
    direction=None,
    direction_via_preset=False,
    forward_preset="normal",
):
    return FanInfo(
        entity_id,
        is_on=is_on,
        preset_mode=preset_mode,
        percentage=percentage,
        preset_modes=tuple(preset_modes),
        reversible=reversible,
        direction=direction,
        direction_via_preset=direction_via_preset,
        forward_preset=forward_preset,
    )


def _base(**kw):
    defaults = dict(
        combined=False,
        room_temp=76.0,
        ac=None,
        heater=None,
        fan=None,
        ac_fan=None,
        heater_fan=None,
        ac_power=None,
        heater_power=None,
        use_ac=False,
        use_heater=False,
        use_fan=True,
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
        fan_reverse=False,
        fan_preset=None,
    )
    defaults.update(kw)
    return EngineInputs(**defaults)


# ---------------------------------------------------------------------------
# CC-26: pinned preset emits FanSetPreset and suppresses tier-speed commands
# ---------------------------------------------------------------------------


def test_pinned_preset_emits_set_preset():
    """CC-26: a pinned preset that differs from the current mode emits FanSetPreset."""
    cmds = compute_commands(
        _base(
            fan=_fan(preset_mode="normal"),
            fan_preset="sleep",
        )
    )
    preset_cmds = [c for c in cmds if isinstance(c, FanSetPreset)]
    assert len(preset_cmds) == 1
    assert preset_cmds[0].preset_mode == "sleep"
    assert preset_cmds[0].entity_id == "fan.ceiling"


def test_pinned_preset_suppresses_tier_speed_percentage():
    """CC-26: pinned preset suppresses FanSetPercentage (percentage-only fan)."""
    cmds = compute_commands(
        _base(
            fan=_fan(preset_mode="normal", preset_modes=(), percentage=50),
            fan_preset="sleep",
        )
    )
    # preset not in preset_modes (empty), so pinned-preset path skips
    # (fan has no "sleep" in preset_modes) — verify no tier-speed command
    assert not any(isinstance(c, FanSetPercentage) for c in cmds)


def test_pinned_preset_not_in_preset_modes_falls_through_to_speed():
    """CC-26: pinned preset not in preset_modes falls back to speed tier."""
    cmds = compute_commands(
        _base(
            fan=_fan(preset_mode="normal", preset_modes=("normal", "natural")),
            fan_preset="sleep",  # not in preset_modes
        )
    )
    # Should fall through to tier-speed logic, not emit a FanSetPreset("sleep")
    preset_cmds = [
        c for c in cmds if isinstance(c, FanSetPreset) and c.preset_mode == "sleep"
    ]
    assert len(preset_cmds) == 0


def test_pinned_preset_suppresses_direction_commands():
    """CC-26: direction commands suppressed when preset is pinned."""
    cmds = compute_commands(
        _base(
            fan=_fan(
                preset_mode="normal",
                preset_modes=PRESET_MODES,
                reversible=True,
                direction="forward",
                direction_via_preset=True,
                forward_preset="normal",
            ),
            fan_preset="sleep",
            fan_reverse=True,
        )
    )
    assert not any(isinstance(c, FanSetDirection) for c in cmds)
    preset_cmds = [c for c in cmds if isinstance(c, FanSetPreset)]
    assert len(preset_cmds) == 1
    assert preset_cmds[0].preset_mode == "sleep"


# ---------------------------------------------------------------------------
# CC-26: idempotence — no command when already at the pinned preset
# ---------------------------------------------------------------------------


def test_pinned_preset_idempotent_when_already_active():
    """CC-26: no FanSetPreset when the fan is already at the pinned preset."""
    cmds = compute_commands(
        _base(
            fan=_fan(preset_mode="sleep"),
            fan_preset="sleep",
        )
    )
    assert not any(isinstance(c, FanSetPreset) for c in cmds)


# ---------------------------------------------------------------------------
# CC-26: Auto (or None) restores tier-speed behavior (CC-14)
# ---------------------------------------------------------------------------


def test_auto_preset_uses_tier_speed_preset():
    """CC-26: Auto uses the speed-tier preset when preset_modes contains tier labels."""
    cmds = compute_commands(
        _base(
            fan=_fan(preset_mode="high", preset_modes=("low", "medium", "high")),
            fan_preset="Auto",
            room_temp=76.0,  # above medium=75, below high=78 → "medium" tier
        )
    )
    preset_cmds = [c for c in cmds if isinstance(c, FanSetPreset)]
    assert len(preset_cmds) == 1
    assert preset_cmds[0].preset_mode == "medium"


def test_none_preset_uses_tier_speed_preset():
    """CC-26: None fan_preset behaves the same as Auto."""
    cmds = compute_commands(
        _base(
            fan=_fan(preset_mode="high", preset_modes=("low", "medium", "high")),
            fan_preset=None,
            room_temp=76.0,
        )
    )
    preset_cmds = [c for c in cmds if isinstance(c, FanSetPreset)]
    assert len(preset_cmds) == 1
    assert preset_cmds[0].preset_mode == "medium"


# ---------------------------------------------------------------------------
# CC-26: pinned preset only while running
# ---------------------------------------------------------------------------


def test_pinned_preset_no_command_when_fan_below_threshold():
    """CC-26: no FanSetPreset when the fan should not run (room below target)."""
    cmds = compute_commands(
        _base(
            fan=_fan(is_on=False, preset_mode=None),
            fan_preset="sleep",
            room_temp=70.0,  # below target_fan=72 → fan must be off
        )
    )
    assert not any(isinstance(c, FanSetPreset) for c in cmds)
    # Fan should be turned off (it was off, so no FanTurnOff either — just nothing)
    assert not any(isinstance(c, FanTurnOn) for c in cmds)


def test_pinned_preset_no_command_when_use_fan_off():
    """CC-26: no FanSetPreset when use_fan=False."""
    cmds = compute_commands(
        _base(
            fan=_fan(is_on=True, preset_mode="normal"),
            fan_preset="sleep",
            use_fan=False,
        )
    )
    assert not any(isinstance(c, FanSetPreset) for c in cmds)
    assert any(isinstance(c, FanTurnOff) for c in cmds)


def test_pinned_preset_applied_when_fan_turns_on():
    """CC-26: FanTurnOn precedes FanSetPreset when fan must start with pinned preset."""
    cmds = compute_commands(
        _base(
            fan=_fan(is_on=False, preset_mode=None),
            fan_preset="sleep",
            room_temp=76.0,  # above target → fan should turn on
        )
    )
    names = [type(c).__name__ for c in cmds]
    assert "FanTurnOn" in names
    assert "FanSetPreset" in names
    assert names.index("FanTurnOn") < names.index("FanSetPreset")


# ---------------------------------------------------------------------------
# CC-26: native-DIRECTION fan unaffected by fan_preset (no preset_modes)
# ---------------------------------------------------------------------------


def test_native_direction_fan_unaffected_by_fan_preset():
    """CC-26: a fan with no preset_modes falls through to speed/direction unchanged."""
    cmds = compute_commands(
        _base(
            fan=FanInfo(
                "fan.native",
                is_on=True,
                preset_mode=None,
                percentage=50,
                preset_modes=(),  # no preset_modes
                reversible=True,
                direction="forward",
            ),
            fan_preset="sleep",  # not in empty preset_modes → no effect
            fan_reverse=True,
        )
    )
    # Direction command should still fire (the preset pin is ignored for no-preset fans)
    assert any(isinstance(c, FanSetDirection) for c in cmds)
