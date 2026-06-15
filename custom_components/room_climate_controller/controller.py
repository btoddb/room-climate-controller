"""Per-room reactive controller: gathers state, runs the engine, drives devices."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import replace
from typing import TYPE_CHECKING

from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later, async_track_state_change_event

from .const import (
    DOMAIN,
    KEY_AC_FAN_ONLY,
    KEY_FAN_REVERSE,
    KEY_HEATER_FAN_ONLY,
    KEY_HIGH_OFFSET,
    KEY_MANUAL_MODE,
    KEY_MEDIUM_OFFSET,
    KEY_TARGET,
    KEY_USE,
)
from .engine import (
    ClimateInfo,
    Command,
    Delay,
    EngineInputs,
    FanInfo,
    FanSetDirection,
    FanSetPercentage,
    FanSetPreset,
    FanTurnOff,
    FanTurnOn,
    SetFanMode,
    SetHvacMode,
    SetTemperature,
    SwitchInfo,
    SwitchTurnOff,
    SwitchTurnOn,
    TurnOffClimate,
    any_window_open,
    clamp_setpoint,
    compute_commands,
)
from .entity import fan_direction_via_preset, fan_supports_direction
from .models import Room, room_uid

if TYPE_CHECKING:
    from .hub import RoomClimateConfigEntry

_LOGGER = logging.getLogger(__name__)

_INVALID = (None, "", STATE_UNKNOWN, STATE_UNAVAILABLE, "none")


def _service_for(cmd: Command) -> tuple[str, str, dict]:  # noqa: PLR0911
    """Map a command to a (domain, service, data) service call."""
    if isinstance(cmd, SetHvacMode):
        return (
            "climate",
            "set_hvac_mode",
            {
                "entity_id": cmd.entity_id,
                "hvac_mode": cmd.hvac_mode,
            },
        )
    if isinstance(cmd, TurnOffClimate):
        return "climate", "turn_off", {"entity_id": cmd.entity_id}
    if isinstance(cmd, SetTemperature):
        return (
            "climate",
            "set_temperature",
            {
                "entity_id": cmd.entity_id,
                "temperature": cmd.temperature,
                "hvac_mode": cmd.hvac_mode,
            },
        )
    if isinstance(cmd, SetFanMode):
        return (
            "climate",
            "set_fan_mode",
            {
                "entity_id": cmd.entity_id,
                "fan_mode": cmd.fan_mode,
            },
        )
    if isinstance(cmd, FanTurnOn):
        return "fan", "turn_on", {"entity_id": cmd.entity_id}
    if isinstance(cmd, FanTurnOff):
        return "fan", "turn_off", {"entity_id": cmd.entity_id}
    if isinstance(cmd, FanSetPreset):
        return (
            "fan",
            "set_preset_mode",
            {
                "entity_id": cmd.entity_id,
                "preset_mode": cmd.preset_mode,
            },
        )
    if isinstance(cmd, FanSetPercentage):
        return (
            "fan",
            "set_percentage",
            {
                "entity_id": cmd.entity_id,
                "percentage": cmd.percentage,
            },
        )
    if isinstance(cmd, FanSetDirection):
        if cmd.via_preset:
            preset = "reverse" if cmd.direction == "reverse" else cmd.forward_preset
            return (
                "fan",
                "set_preset_mode",
                {"entity_id": cmd.entity_id, "preset_mode": preset},
            )
        return (
            "fan",
            "set_direction",
            {
                "entity_id": cmd.entity_id,
                "direction": cmd.direction,
            },
        )
    if isinstance(cmd, SwitchTurnOn):
        return "switch", "turn_on", {"entity_id": cmd.entity_id}
    if isinstance(cmd, SwitchTurnOff):
        return "switch", "turn_off", {"entity_id": cmd.entity_id}
    msg = f"Unknown command {cmd!r}"
    raise ValueError(msg)


class RoomController:
    """Reacts to a room's live entities and commands the physical devices."""

    def __init__(
        self, hass: HomeAssistant, entry: RoomClimateConfigEntry, room: Room
    ) -> None:
        """Initialize the controller."""
        self.hass = hass
        self.entry = entry
        self.room = room
        self._unsub_state = None
        self._tracked: frozenset[str] = frozenset()
        self._task: asyncio.Task | None = None

    # -- lifecycle -----------------------------------------------------------
    @callback
    def async_start(self) -> None:
        """Subscribe and run an initial evaluation."""
        self._resubscribe()
        self.async_request_run()
        # Pick up our own entities that register a moment after setup.
        self.entry.async_on_unload(
            async_call_later(self.hass, 3, self._delayed_resubscribe)
        )
        self.entry.async_on_unload(self.async_stop)

    @callback
    def async_stop(self) -> None:
        """Cancel work and unsubscribe."""
        if self._task and not self._task.done():
            self._task.cancel()
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None

    @callback
    def _delayed_resubscribe(self, _now: object) -> None:
        self._resubscribe()
        self.async_request_run()

    # -- subscriptions -------------------------------------------------------
    @callback
    def _resubscribe(self) -> None:
        ids = self._tracked_ids()
        if ids == self._tracked:
            return
        self._tracked = ids
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None
        if ids:
            self._unsub_state = async_track_state_change_event(
                self.hass, list(ids), self._on_change
            )

    def _tracked_ids(self) -> frozenset[str]:
        """Temp/humidity sensors plus whichever room live entities currently resolve."""
        ids: set[str] = set()
        if self.room.temperature_sensor:
            ids.add(self.room.temperature_sensor)
        if self.room.humidity_sensor:
            ids.add(self.room.humidity_sensor)
        ids.update(self.room.window_sensors)
        for device in self.room.devices:
            for key in (
                KEY_USE[device],
                KEY_TARGET[device],
                KEY_MEDIUM_OFFSET[device],
                KEY_HIGH_OFFSET[device],
            ):
                domain = "switch" if key.startswith("use_") else "number"
                if eid := self._resolve(key, domain):
                    ids.add(eid)
        for key in (
            KEY_MANUAL_MODE,
            KEY_AC_FAN_ONLY,
            KEY_HEATER_FAN_ONLY,
            KEY_FAN_REVERSE,
        ):
            if eid := self._resolve(key, "switch"):
                ids.add(eid)
        return frozenset(ids)

    @callback
    def _on_change(self, event: Event[EventStateChangedData]) -> None:
        data = event.data
        entity_id: str = data["entity_id"]
        old = data["old_state"]
        new = data["new_state"]
        old_val = old.state if old else None
        new_val = new.state if new else None
        if old_val != new_val:
            if entity_id == self.room.temperature_sensor:
                _LOGGER.info(
                    "[room=%s] Temperature changed: %s → %s°F%s",
                    self.room.key,
                    old_val,
                    new_val,
                    self._command_suffix(),
                )
            elif entity_id == self.room.humidity_sensor:
                _LOGGER.info(
                    "[room=%s] Humidity changed: %s → %s%%%s",
                    self.room.key,
                    old_val,
                    new_val,
                    self._command_suffix(),
                )
            elif entity_id in self.room.window_sensors:
                state_label = "opened" if new_val == "on" else "closed"
                _LOGGER.info(
                    "[room=%s] Window %s %s",
                    self.room.key,
                    entity_id,
                    state_label,
                )
        self._resubscribe()
        self.async_request_run()

    def _resolve(self, cmd: Command) -> Command:
        """
        Resolve a command against the device's *live* state before it is sent.

        Currently this clamps a ``SetTemperature`` into the device's reported
        ``min_temp``/``max_temp`` range (CC-9). Used by both ``_run`` (at send
        time) and ``_command_suffix`` (the diagnostic) so the logged value
        matches what is actually sent. The diagnostic reads the range in the
        device's *current* mode, so for a command sequence that first switches
        HVAC mode it is a best-effort prediction; ``_run`` resolves each command
        in order, after the preceding mode switch, against the real range.
        """
        if isinstance(cmd, SetTemperature):
            state = self.hass.states.get(cmd.entity_id)
            attrs = state.attributes if state else {}
            temperature = clamp_setpoint(
                cmd.temperature, attrs.get("min_temp"), attrs.get("max_temp")
            )
            if temperature != cmd.temperature:
                return replace(cmd, temperature=temperature)
        return cmd

    def _command_suffix(self) -> str:
        """
        Describe the device commands the current state would produce, if any.

        Returns ``" (device commanded: <cmds>)"`` listing the non-delay commands,
        or ``""`` when nothing would be sent. The command list is the diagnostic
        that explains *why* a device reacted to a sub-degree sensor change.
        """
        inputs = self._build_inputs()
        if inputs is None:
            return ""
        cmds = [
            self._resolve(c)
            for c in compute_commands(inputs)
            if not isinstance(c, Delay)
        ]
        if not cmds:
            return ""
        return f" (device commanded: {', '.join(repr(c) for c in cmds)})"

    # -- evaluation ----------------------------------------------------------
    @callback
    def async_request_run(self) -> None:
        """Restart the evaluation task (restart semantics, like the blueprint)."""
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = self.hass.async_create_task(
            self._run(), f"{DOMAIN} control {self.room.key}"
        )

    async def _run(self) -> None:
        try:
            inputs = self._build_inputs()
            if inputs is None:
                return
            for cmd in compute_commands(inputs):
                if isinstance(cmd, Delay):
                    await asyncio.sleep(cmd.ms / 1000)
                    continue
                # Resolve against the device's *live* range, read now rather
                # than from the build-time snapshot: an A/C reports a
                # mode-dependent range (off vs cool), and any preceding
                # SetHvacMode has already switched it, so this reflects the
                # range the device will actually validate against (CC-9).
                domain, service, data = _service_for(self._resolve(cmd))
                # Isolate each call: one device rejecting a command (e.g. a
                # transient out-of-range setpoint) must not abandon the
                # remaining commands for this room.
                try:
                    await self.hass.services.async_call(
                        domain, service, data, blocking=True
                    )
                except asyncio.CancelledError:
                    raise
                except Exception:
                    _LOGGER.exception(
                        "Room %s: command failed: %s.%s %s",
                        self.room.key,
                        domain,
                        service,
                        data,
                    )
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOGGER.exception("Room %s: control evaluation failed", self.room.key)

    def _build_inputs(self) -> EngineInputs | None:
        """Read all live + device state; None if manual mode or invalid temp."""
        room = self.room
        # Default to manual (dormant) when the state can't be read, so a lost or
        # not-yet-restored switch state never silently re-activates control.
        if self._switch_state(KEY_MANUAL_MODE, default=True):
            return None
        room_temp = self._temperature()
        if room_temp is None:
            return None

        target_cooling = self._number(KEY_TARGET["cooling"], 72.0)
        target_heating = self._number(KEY_TARGET["heating"], 68.0)
        target_fan = self._number(KEY_TARGET["fan"], 72.0)
        cool_med = self._number(KEY_MEDIUM_OFFSET["cooling"], 3.0)
        cool_high = self._number(KEY_HIGH_OFFSET["cooling"], 6.0)
        heat_med = self._number(KEY_MEDIUM_OFFSET["heating"], 3.0)
        heat_high = self._number(KEY_HIGH_OFFSET["heating"], 6.0)
        fan_med = self._number(KEY_MEDIUM_OFFSET["fan"], 3.0)
        fan_high = self._number(KEY_HIGH_OFFSET["fan"], 6.0)

        return EngineInputs(
            combined=room.combined,
            room_temp=room_temp,
            ac=self._climate_info(room.ac_climate) if room.has_ac else None,
            heater=(
                self._climate_info(room.heater_climate)
                if room.has_heater and not room.combined
                else None
            ),
            fan=self._fan_info(room.fan_entity) if room.has_fan else None,
            ac_fan=self._fan_info(room.ac_fan_entity),
            heater_fan=self._fan_info(room.heater_fan_entity),
            ac_power=self._switch_info(room.ac_power_switch),
            heater_power=self._switch_info(room.heater_power_switch),
            use_ac=self._switch_state(KEY_USE["cooling"], default=False),
            use_heater=self._switch_state(KEY_USE["heating"], default=False),
            use_fan=self._switch_state(KEY_USE["fan"], default=False),
            ac_fan_only_override=self._switch_state(KEY_AC_FAN_ONLY, default=False),
            heater_fan_only_override=self._switch_state(
                KEY_HEATER_FAN_ONLY, default=False
            ),
            target_cooling=target_cooling,
            cooling_medium=target_cooling + cool_med,
            cooling_high=target_cooling + cool_high,
            target_heating=target_heating,
            heating_medium=target_heating - heat_med,
            heating_high=target_heating - heat_high,
            target_fan=target_fan,
            fan_medium=target_fan + fan_med,
            fan_high=target_fan + fan_high,
            command_delay_ms=int(room.command_delay * 1000),
            power_on_delay_ms=int(room.power_on_delay * 1000),
            window_open=self._window_open(),
            fan_reverse=self._switch_state(KEY_FAN_REVERSE, default=False),
        )

    # -- state readers -------------------------------------------------------
    def _resolve(self, key: str, domain: str) -> str | None:
        return er.async_get(self.hass).async_get_entity_id(
            domain, DOMAIN, room_uid(self.entry.entry_id, self.room.key, key)
        )

    def _temperature(self) -> float | None:
        if not self.room.temperature_sensor:
            return None
        state = self.hass.states.get(self.room.temperature_sensor)
        if state is None or state.state in _INVALID:
            return None
        try:
            return float(state.state)
        except TypeError, ValueError:
            return None

    def _number(self, key: str, default: float) -> float:
        eid = self._resolve(key, "number")
        if eid and (state := self.hass.states.get(eid)) and state.state not in _INVALID:
            try:
                return float(state.state)
            except TypeError, ValueError:
                return default
        return default

    def _switch_state(self, key: str, *, default: bool) -> bool:
        eid = self._resolve(key, "switch")
        if eid and (state := self.hass.states.get(eid)):
            return state.state == STATE_ON
        return default

    def _window_open(self) -> bool:
        """
        Return True if ANY of the room's window sensors reads open (CC-20).

        Missing/unavailable/unknown sensors are treated as closed (CC-21); the
        aggregation + fail-safe live in the pure engine helper.
        """
        states = (self.hass.states.get(eid) for eid in self.room.window_sensors)
        return any_window_open(s.state if s else None for s in states)

    def _climate_info(self, entity_id: str | None) -> ClimateInfo | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        attrs = state.attributes
        features = int(attrs.get("supported_features") or 0)
        raw_setpoint = attrs.get("temperature")
        return ClimateInfo(
            entity_id=entity_id,
            hvac_mode=attrs.get("hvac_mode") or state.state,
            fan_mode=attrs.get("fan_mode"),
            hvac_modes=tuple(attrs.get("hvac_modes") or ()),
            fan_modes=tuple(attrs.get("fan_modes") or ()),
            min_temp=attrs.get("min_temp"),
            supports_set_temp=bool(features & 1),
            current_setpoint=float(raw_setpoint) if raw_setpoint is not None else None,
        )

    def _fan_info(self, entity_id: str | None) -> FanInfo | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        attrs = state.attributes
        preset_modes = tuple(attrs.get("preset_modes") or ())
        via_preset = fan_direction_via_preset(self.hass, entity_id)
        if via_preset:
            forward_preset = next((p for p in preset_modes if p != "reverse"), "normal")
            direction = (
                "reverse" if attrs.get("preset_mode") == "reverse" else "forward"
            )
            _LOGGER.debug(
                "[room=%s] %s direction via preset; presets=%s fwd=%s cur=%s",
                self.room.key,
                entity_id,
                preset_modes,
                forward_preset,
                direction,
            )
        else:
            forward_preset = "normal"
            direction = attrs.get("direction")
        return FanInfo(
            entity_id=entity_id,
            is_on=state.state == STATE_ON,
            preset_mode=attrs.get("preset_mode"),
            percentage=int(attrs.get("percentage") or 0),
            preset_modes=preset_modes,
            reversible=fan_supports_direction(self.hass, entity_id),
            direction=direction,
            direction_via_preset=via_preset,
            forward_preset=forward_preset,
        )

    def _switch_info(self, entity_id: str | None) -> SwitchInfo | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        return SwitchInfo(entity_id=entity_id, is_on=state.state == STATE_ON)
