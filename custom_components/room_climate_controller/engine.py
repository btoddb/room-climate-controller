"""
Pure reactive-control engine (no Home Assistant imports).

``compute_commands(inputs)`` is a pure function of the current room/device state
that returns the ordered list of device commands to issue. The HA-coupled
``controller.py`` gathers state into :class:`EngineInputs`, calls this, and
executes the returned commands. Keeping it pure makes the control logic
unit-testable with plain ``python3``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .fan_logic import cooling_speed, heating_speed, match_fan_mode

COOL = "cool"
HEAT = "heat"
FAN_ONLY = "fan_only"
OFF = "off"

_OFF_LIKE = frozenset({"off", "unavailable", "unknown", "none", "", None})


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ClimateInfo:
    """Current state + capabilities of a climate entity."""

    entity_id: str
    hvac_mode: str
    fan_mode: str | None
    hvac_modes: tuple[str, ...]
    fan_modes: tuple[str, ...]
    min_temp: float | None
    supports_set_temp: bool

    @property
    def has_fan(self) -> bool:
        """Treat fan_only support or any fan_modes as fan-capable."""
        return "fan_only" in self.hvac_modes or bool(self.fan_modes)


@dataclass(frozen=True)
class FanInfo:
    """Current state of a fan entity."""

    entity_id: str
    is_on: bool
    preset_mode: str | None
    percentage: int
    preset_modes: tuple[str, ...]


@dataclass(frozen=True)
class SwitchInfo:
    """Current state of a power switch."""

    entity_id: str
    is_on: bool


@dataclass(frozen=True)
class EngineInputs:
    """Everything the decision needs — config, live values, and device state."""

    combined: bool
    room_temp: float
    # devices (None when the room lacks them)
    ac: ClimateInfo | None
    heater: ClimateInfo | None
    fan: FanInfo | None
    ac_fan: FanInfo | None
    heater_fan: FanInfo | None
    ac_power: SwitchInfo | None
    heater_power: SwitchInfo | None
    # use toggles + overrides
    use_ac: bool
    use_heater: bool
    use_fan: bool
    ac_fan_only_override: bool
    heater_fan_only_override: bool
    # setpoints / thresholds
    target_cooling: float
    cooling_medium: float
    cooling_high: float
    target_heating: float
    heating_medium: float
    heating_high: float
    target_fan: float
    fan_medium: float
    fan_high: float
    command_delay_ms: int
    power_on_delay_ms: int
    # window sensor: True when the room's window is open. Suppresses active
    # cooling/heating (Cool/Heat) only — fan-only circulation is unaffected.
    window_open: bool = False

    # derived helpers ----------------------------------------------------
    @property
    def has_ac(self) -> bool:
        """Return True when an AC climate entity is configured."""
        return self.ac is not None

    @property
    def has_heater(self) -> bool:
        """Return True when a heater climate entity is configured."""
        return self.heater is not None

    @property
    def has_fan(self) -> bool:
        """Return True when a standalone fan entity is configured."""
        return self.fan is not None

    @property
    def ac_setpoint_int(self) -> int:
        """Return the AC climate setpoint (device min or 65 °F floor)."""
        # The engine controls comfort via fan speed, so the climate's own target
        # is driven to its lowest settable value (max cooling), or 65 °F when the
        # device doesn't report a min_temp.
        min_temp = self.ac.min_temp if self.ac else None
        return round(min_temp if min_temp is not None else 65)

    @property
    def target_heating_int(self) -> int:
        """Return the heating target truncated to whole degrees."""
        return int(self.target_heating)

    @property
    def fan_needs_on(self) -> bool:
        """Return True when the standalone fan should run."""
        return self.use_fan and int(self.room_temp) > int(self.target_fan)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Command:
    """Base class for an emitted device command."""


@dataclass(frozen=True)
class Delay(Command):
    """Pause between commands (milliseconds)."""

    ms: int


@dataclass(frozen=True)
class SetHvacMode(Command):
    """Set the HVAC mode on a climate entity."""

    entity_id: str
    hvac_mode: str


@dataclass(frozen=True)
class TurnOffClimate(Command):
    """Turn off a climate entity."""

    entity_id: str


@dataclass(frozen=True)
class SetTemperature(Command):
    """Set the target temperature on a climate entity."""

    entity_id: str
    temperature: int
    hvac_mode: str


@dataclass(frozen=True)
class SetFanMode(Command):
    """Set the fan mode on a climate entity."""

    entity_id: str
    fan_mode: str


@dataclass(frozen=True)
class FanTurnOn(Command):
    """Turn on a fan entity."""

    entity_id: str


@dataclass(frozen=True)
class FanTurnOff(Command):
    """Turn off a fan entity."""

    entity_id: str


@dataclass(frozen=True)
class FanSetPreset(Command):
    """Set the preset mode on a fan entity."""

    entity_id: str
    preset_mode: str


@dataclass(frozen=True)
class FanSetPercentage(Command):
    """Set the speed percentage on a fan entity."""

    entity_id: str
    percentage: int


@dataclass(frozen=True)
class SwitchTurnOn(Command):
    """Turn on a switch entity."""

    entity_id: str


@dataclass(frozen=True)
class SwitchTurnOff(Command):
    """Turn off a switch entity."""

    entity_id: str


@dataclass
class _Out:
    """Mutable command accumulator."""

    items: list[Command] = field(default_factory=list)

    def add(self, *cmds: Command) -> None:
        self.items.extend(cmds)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def compute_commands(inp: EngineInputs) -> list[Command]:
    """
    Return the ordered commands for the current state.

    Manual-mode gating is the controller's job; this assumes control is active.
    """
    out = _Out()
    if inp.combined and inp.ac is not None:
        _combined(inp, out)
    else:
        if inp.ac is not None:
            _split_ac(inp, out)
        if inp.heater is not None:
            _split_heater(inp, out)
    if inp.fan is not None:
        _standalone_fan(inp, out)
    return out.items


# ---------------------------------------------------------------------------
# Combined heat-pump branch
# ---------------------------------------------------------------------------
def _combined(inp: EngineInputs, out: _Out) -> None:  # noqa: PLR0912
    ac = inp.ac
    assert ac is not None
    room = int(inp.room_temp)
    needs_cool = inp.use_ac and not inp.window_open and room > int(inp.target_cooling)
    needs_heat = (
        inp.use_heater and not inp.window_open and room < int(inp.target_heating)
    )
    uses_disabled = not inp.use_ac and not inp.use_heater
    ac_override_fan_only = (
        inp.ac_fan_only_override
        and ac.has_fan
        and (
            (inp.use_ac and not needs_cool)
            or (not inp.use_ac and (not inp.has_fan or inp.use_fan))
        )
    )
    native_heater_fan_only = (
        inp.use_heater and ac.has_fan and not needs_heat and not uses_disabled
    )
    if uses_disabled:
        use_fan_only = (
            inp.ac_fan_only_override and ac.has_fan and (not inp.has_fan or inp.use_fan)
        )
    else:
        use_fan_only = ac_override_fan_only or native_heater_fan_only

    if uses_disabled and not use_fan_only:
        decision = OFF
    elif needs_cool:
        decision = COOL
    elif needs_heat:
        decision = HEAT
    elif use_fan_only:
        decision = FAN_ONLY
    else:
        decision = OFF

    target = inp.target_heating_int if decision == HEAT else inp.ac_setpoint_int
    current = ac.hvac_mode

    if inp.ac_power and decision in (COOL, HEAT, FAN_ONLY) and not inp.ac_power.is_on:
        out.add(SwitchTurnOn(inp.ac_power.entity_id), Delay(inp.power_on_delay_ms))
    if decision not in {OFF, current}:
        out.add(SetHvacMode(ac.entity_id, decision), Delay(inp.command_delay_ms))
    if decision == OFF and current not in _OFF_LIKE:
        out.add(
            SetHvacMode(ac.entity_id, OFF),
            Delay(inp.command_delay_ms),
            TurnOffClimate(ac.entity_id),
        )
    if decision != OFF and ac.supports_set_temp:
        out.add(SetTemperature(ac.entity_id, target, decision))
    if inp.ac_power and decision == OFF:
        out.add(Delay(inp.command_delay_ms), SwitchTurnOff(inp.ac_power.entity_id))

    if ac.fan_modes and decision != OFF:
        out.add(Delay(inp.command_delay_ms))
        label = _combined_speed_label(inp, decision)
        matched = match_fan_mode(ac.fan_modes, label)
        if matched:
            out.add(SetFanMode(ac.entity_id, matched))


def _combined_speed_label(inp: EngineInputs, decision: str) -> str:
    """Pick cooling vs heating tiers for the combined climate fan."""
    if decision == HEAT:
        return heating_speed(inp.room_temp, inp.heating_medium, inp.heating_high)[0]
    if decision == COOL:
        return cooling_speed(inp.room_temp, inp.cooling_medium, inp.cooling_high)[0]
    if decision == FAN_ONLY:
        if inp.use_heater and not inp.use_ac:
            return heating_speed(inp.room_temp, inp.heating_medium, inp.heating_high)[0]
        # use_ac, or neither use selected: fall back to cooling tiers.
        return cooling_speed(inp.room_temp, inp.cooling_medium, inp.cooling_high)[0]
    return "low"


# ---------------------------------------------------------------------------
# Split A/C branch
# ---------------------------------------------------------------------------
def _split_ac(inp: EngineInputs, out: _Out) -> None:
    ac = inp.ac
    assert ac is not None
    needs_cool = (
        inp.use_ac
        and not inp.window_open
        and int(inp.room_temp) > int(inp.target_cooling)
    )
    override_fan_only = (
        inp.ac_fan_only_override
        and ac.has_fan
        and (
            (inp.use_ac and not needs_cool)
            or (not inp.use_ac and (not inp.has_fan or inp.use_fan))
        )
    )
    decision = COOL if needs_cool else (FAN_ONLY if override_fan_only else OFF)
    current = ac.hvac_mode

    if inp.ac_power and decision in (COOL, FAN_ONLY) and not inp.ac_power.is_on:
        out.add(SwitchTurnOn(inp.ac_power.entity_id), Delay(inp.power_on_delay_ms))
    if decision not in {OFF, current}:
        out.add(SetHvacMode(ac.entity_id, decision), Delay(inp.command_delay_ms))
    if decision == OFF:
        out.add(
            SetHvacMode(ac.entity_id, OFF),
            Delay(inp.command_delay_ms),
            TurnOffClimate(ac.entity_id),
        )
    if decision in (COOL, FAN_ONLY) and ac.supports_set_temp:
        out.add(SetTemperature(ac.entity_id, inp.ac_setpoint_int, decision))
    if inp.ac_power and decision == OFF:
        out.add(SwitchTurnOff(inp.ac_power.entity_id))

    has_fan_modes = bool(ac.fan_modes)
    if not (has_fan_modes or inp.ac_fan):
        return
    if decision in (COOL, FAN_ONLY):
        out.add(Delay(inp.command_delay_ms))
        label, percent = cooling_speed(
            inp.room_temp, inp.cooling_medium, inp.cooling_high
        )
        matched = match_fan_mode(ac.fan_modes, label)
        _emit_climate_fan(
            out, ac, has_fan_modes, matched, inp.ac_fan, label, percent, inp
        )
    elif decision == OFF and inp.ac_fan:
        out.add(FanTurnOff(inp.ac_fan.entity_id))


# ---------------------------------------------------------------------------
# Split heater branch
# ---------------------------------------------------------------------------
def _split_heater(inp: EngineInputs, out: _Out) -> None:
    heater = inp.heater
    assert heater is not None
    needs_heat = (
        inp.use_heater
        and not inp.window_open
        and int(inp.room_temp) < int(inp.target_heating)
    )
    native_fan_only = inp.use_heater and not needs_heat and heater.has_fan
    override_fan_only = (
        inp.heater_fan_only_override
        and heater.has_fan
        and (
            (inp.use_heater and not needs_heat)
            or (not inp.use_heater and (not inp.has_fan or inp.use_fan))
        )
    )
    decision = (
        HEAT
        if needs_heat
        else (FAN_ONLY if (native_fan_only or override_fan_only) else OFF)
    )
    current = heater.hvac_mode

    if inp.heater_power and decision in (HEAT, FAN_ONLY) and not inp.heater_power.is_on:
        out.add(SwitchTurnOn(inp.heater_power.entity_id), Delay(inp.power_on_delay_ms))
    if decision not in {OFF, current}:
        out.add(SetHvacMode(heater.entity_id, decision), Delay(inp.command_delay_ms))
    if decision == OFF and current != OFF:
        out.add(SetHvacMode(heater.entity_id, OFF), Delay(inp.command_delay_ms))
    if decision == OFF:
        out.add(TurnOffClimate(heater.entity_id))
    if decision in (HEAT, FAN_ONLY) and heater.supports_set_temp:
        out.add(SetTemperature(heater.entity_id, inp.target_heating_int, decision))
    if inp.heater_power and decision == OFF:
        out.add(SwitchTurnOff(inp.heater_power.entity_id))

    has_fan_modes = bool(heater.fan_modes)
    if not (has_fan_modes or inp.heater_fan):
        return
    if decision in (HEAT, FAN_ONLY):
        out.add(Delay(inp.command_delay_ms))
        label, percent = heating_speed(
            inp.room_temp, inp.heating_medium, inp.heating_high
        )
        matched = match_fan_mode(heater.fan_modes, label)
        _emit_climate_fan(
            out, heater, has_fan_modes, matched, inp.heater_fan, label, percent, inp
        )
    elif decision == OFF and inp.heater_fan:
        out.add(FanTurnOff(inp.heater_fan.entity_id))
    elif decision == OFF and has_fan_modes and current != OFF:
        out.add(SetHvacMode(heater.entity_id, OFF))


def _emit_climate_fan(  # noqa: PLR0913
    out: _Out,
    climate: ClimateInfo,
    has_fan_modes: bool,  # noqa: FBT001
    matched: str,
    companion: FanInfo | None,
    label: str,
    percent: int,
    inp: EngineInputs,
) -> None:
    """Set climate fan_mode if available, else drive a companion fan entity."""
    if has_fan_modes and matched:
        if climate.fan_mode != matched:
            out.add(SetFanMode(climate.entity_id, matched))
        return
    if companion is None:
        return
    if label in companion.preset_modes:
        if not companion.is_on:
            out.add(FanTurnOn(companion.entity_id), Delay(inp.command_delay_ms))
        if (companion.preset_mode or "").lower() != label:
            out.add(FanSetPreset(companion.entity_id, label))
    else:
        if not companion.is_on:
            out.add(FanTurnOn(companion.entity_id), Delay(inp.command_delay_ms))
        if companion.percentage != percent:
            out.add(FanSetPercentage(companion.entity_id, percent))


# ---------------------------------------------------------------------------
# Standalone fan (shared by both branches)
# ---------------------------------------------------------------------------
def _standalone_fan(inp: EngineInputs, out: _Out) -> None:
    fan = inp.fan
    assert fan is not None
    if not inp.fan_needs_on:
        out.add(FanTurnOff(fan.entity_id))
        return
    label, percent = cooling_speed(inp.room_temp, inp.fan_medium, inp.fan_high)
    if not fan.is_on:
        out.add(FanTurnOn(fan.entity_id), Delay(inp.command_delay_ms))
    if label in fan.preset_modes:
        if (fan.preset_mode or "").lower() != label:
            out.add(FanSetPreset(fan.entity_id, label))
    elif fan.percentage != percent:
        out.add(FanSetPercentage(fan.entity_id, percent))
