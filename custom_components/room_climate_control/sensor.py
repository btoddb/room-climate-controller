"""Sensor platform: per-room temperature/humidity/power mirrors.

These wrap the user-configured source sensors so the rest of the system (and
dashboards) reference a stable ``sensor.<room>_room_*`` entity even if the
underlying device sensor is swapped out later — the role the old
``templates/room_climate_sensors.yaml`` played.
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import KEY_ROOM_HUMIDITY, KEY_ROOM_POWER, KEY_ROOM_TEMPERATURE
from .entity import room_device_info
from .hub import RoomClimateConfigEntry
from .models import Room, room_uid


@dataclass(frozen=True)
class _SensorSpec:
    key: str
    name: str
    source: str
    device_class: SensorDeviceClass
    icon: str


def _room_specs(room: Room) -> list[_SensorSpec]:
    specs: list[_SensorSpec] = []
    if room.temperature_sensor:
        specs.append(
            _SensorSpec(
                KEY_ROOM_TEMPERATURE,
                "Temperature",
                room.temperature_sensor,
                SensorDeviceClass.TEMPERATURE,
                "mdi:thermometer",
            )
        )
    if room.humidity_sensor:
        specs.append(
            _SensorSpec(
                KEY_ROOM_HUMIDITY,
                "Humidity",
                room.humidity_sensor,
                SensorDeviceClass.HUMIDITY,
                "mdi:water-percent",
            )
        )
    if room.power_sensor:
        specs.append(
            _SensorSpec(
                KEY_ROOM_POWER,
                "Power",
                room.power_sensor,
                SensorDeviceClass.POWER,
                "mdi:flash",
            )
        )
    return specs


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RoomClimateConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up per-room mirror sensors."""
    hub = entry.runtime_data
    for room in hub.rooms.values():
        specs = _room_specs(room)
        if specs:
            async_add_entities(
                [RoomMirrorSensor(entry, room, spec) for spec in specs],
                config_subentry_id=room.room_id,
            )


class RoomMirrorSensor(SensorEntity):
    """Mirrors a source sensor's value, unit, and availability."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, entry: RoomClimateConfigEntry, room: Room, spec: _SensorSpec
    ) -> None:
        """Initialize the mirror."""
        self._source = spec.source
        self._attr_unique_id = room_uid(entry.entry_id, room.key, spec.key)
        self._attr_name = spec.name
        self._attr_icon = spec.icon
        self._attr_device_class = spec.device_class
        self._attr_device_info = room_device_info(entry, room)

    async def async_added_to_hass(self) -> None:
        """Subscribe to the source and seed the initial value."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._source], self._handle_source
            )
        )
        self._update_from_source()

    @callback
    def _handle_source(self, event: Event[EventStateChangedData]) -> None:
        self._update_from_source()
        self.async_write_ha_state()

    @callback
    def _update_from_source(self) -> None:
        state = self.hass.states.get(self._source)
        if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            self._attr_available = False
            return
        self._attr_available = True
        try:
            self._attr_native_value = float(state.state)
        except (TypeError, ValueError):
            self._attr_native_value = state.state
        self._attr_native_unit_of_measurement = state.attributes.get(
            "unit_of_measurement"
        )
