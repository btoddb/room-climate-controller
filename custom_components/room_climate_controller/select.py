"""Select platform: graph time-range selector and fan preset selectors."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DEFAULT_GRAPH_TIME_RANGE,
    FAN_PRESET_AUTO,
    GRAPH_TIME_RANGE_OPTIONS,
    KEY_FAN_PRESET,
    KEY_GRAPH_TIME_RANGE,
    KEY_PROFILE_FAN_PRESET,
    SIGNAL_ADD_PROFILE_ENTITIES,
)
from .entity import (
    ProfileRemovalMixin,
    hub_identifier,
    profile_device_info,
    room_device_info,
)
from .models import Profile, Room, profile_uid, room_uid

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .hub import RoomClimateConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RoomClimateConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up graph time-range select and per-room/per-profile fan preset selects."""
    hub = entry.runtime_data

    async_add_entities([GraphTimeRangeSelect(entry)])

    for room in hub.rooms.values():
        if room.has_fan and room.fan_entity:
            async_add_entities(
                [RoomFanPresetSelect(entry, room, hass)],
                config_subentry_id=room.room_id,
            )

    @callback
    def _add_profile(profile: Profile) -> None:
        room = hub.room_by_key(profile.room)
        if room is None or not room.has_fan or not room.fan_entity:
            return
        async_add_entities(
            [ProfileFanPresetSelect(entry, profile, hass)],
            config_subentry_id=room.room_id,
        )

    for profile in hub.profiles:
        _add_profile(profile)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_ADD_PROFILE_ENTITIES, _add_profile)
    )


# ---------------------------------------------------------------------------
# Hub-level graph time-range select (unchanged)
# ---------------------------------------------------------------------------


class GraphTimeRangeSelect(SelectEntity, RestoreEntity):
    """Hub-level selector for the number of hours the card's graphs show."""

    _attr_has_entity_name = True
    _attr_name = "Graph time range"
    _attr_icon = "mdi:chart-timeline-variant"
    _attr_options = GRAPH_TIME_RANGE_OPTIONS

    def __init__(self, entry: RoomClimateConfigEntry) -> None:
        """Initialize the select, attached to the hub device."""
        self._attr_unique_id = f"{entry.entry_id}_{KEY_GRAPH_TIME_RANGE}"
        self._attr_current_option = DEFAULT_GRAPH_TIME_RANGE
        self._attr_device_info = DeviceInfo(
            identifiers={hub_identifier(entry.entry_id)}
        )

    async def async_added_to_hass(self) -> None:
        """Restore the last selected option, falling back to the default."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state in self._attr_options:
            self._attr_current_option = last.state

    async def async_select_option(self, option: str) -> None:
        """Update the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()


# ---------------------------------------------------------------------------
# Per-room fan preset select (CC-26)
# ---------------------------------------------------------------------------


class RoomFanPresetSelect(SelectEntity, RestoreEntity):
    """
    Per-room Fan preset selector (CC-26).

    Options are ["Auto", *fan.preset_modes] read live from hass.states so late-loading
    fan integrations are handled gracefully. The entity is always created for rooms with
    a standalone fan; it is inert (single "Auto" option) when the fan has no presets.
    """

    _attr_has_entity_name = True
    _attr_name = "Fan preset"
    _attr_icon = "mdi:fan-auto"

    def __init__(
        self, entry: RoomClimateConfigEntry, room: Room, hass: HomeAssistant
    ) -> None:
        """Initialize."""
        self._attr_unique_id = room_uid(entry.entry_id, room.key, KEY_FAN_PRESET)
        self._attr_device_info = room_device_info(entry, room)
        self._fan_entity = room.fan_entity
        self._hass = hass
        self._attr_current_option = FAN_PRESET_AUTO
        self._room_key = room.key

    @property
    def options(self) -> list[str]:
        """Return Auto plus the fan's current preset_modes, read live."""
        if self._fan_entity:
            state = self._hass.states.get(self._fan_entity)
            if state is not None:
                preset_modes = state.attributes.get("preset_modes") or []
                if preset_modes:
                    return [FAN_PRESET_AUTO, *preset_modes]
        return [FAN_PRESET_AUTO]

    async def async_added_to_hass(self) -> None:
        """Restore last selection."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state:
            # Accept any previously stored option; stale values fall back to Auto
            # at the next evaluation cycle.
            self._attr_current_option = last.state

    async def async_select_option(self, option: str) -> None:
        """Update the selected preset."""
        self._attr_current_option = option
        self.async_write_ha_state()
        _LOGGER.info(
            "[room=%s] Fan preset → %s",
            self._room_key,
            option,
        )


# ---------------------------------------------------------------------------
# Per-profile fan preset select (PR-13)
# ---------------------------------------------------------------------------


class ProfileFanPresetSelect(ProfileRemovalMixin, SelectEntity, RestoreEntity):
    """
    Per-profile Fan preset selector (PR-13).

    Mirrors RoomFanPresetSelect but persists its value to the profile store.
    """

    _attr_has_entity_name = True
    _attr_name = "Fan preset"
    _attr_icon = "mdi:fan-auto"

    def __init__(
        self, entry: RoomClimateConfigEntry, profile: Profile, hass: HomeAssistant
    ) -> None:
        """Initialize."""
        self._entry = entry
        self._profile_id = profile.id
        self._attr_unique_id = profile_uid(
            entry.entry_id, profile.id, KEY_PROFILE_FAN_PRESET
        )
        self._attr_device_info = profile_device_info(entry, profile)
        room = entry.runtime_data.room_by_key(profile.room)
        self._fan_entity = room.fan_entity if room else None
        self._hass = hass
        self._attr_current_option = profile.fan_preset or FAN_PRESET_AUTO

    @property
    def options(self) -> list[str]:
        """Return Auto plus the fan's current preset_modes, read live."""
        if self._fan_entity:
            state = self._hass.states.get(self._fan_entity)
            if state is not None:
                preset_modes = state.attributes.get("preset_modes") or []
                if preset_modes:
                    return [FAN_PRESET_AUTO, *preset_modes]
        return [FAN_PRESET_AUTO]

    async def async_added_to_hass(self) -> None:
        """Restore state and connect removal signal."""
        await super().async_added_to_hass()
        self._connect_profile_removal()
        self._apply_to_profile()

    async def async_select_option(self, option: str) -> None:
        """Update the selected preset and persist to the profile store."""
        self._attr_current_option = option
        self.async_write_ha_state()
        self._apply_to_profile()
        hub = self._entry.runtime_data
        profile = hub.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        _LOGGER.info(
            "[room=%s profile=%s] Profile preset edited: fan preset → %s",
            room_key,
            self._profile_id,
            option,
        )

    @callback
    def _apply_to_profile(self) -> None:
        hub = self._entry.runtime_data
        profile = hub.get_profile(self._profile_id)
        if profile is None:
            return
        profile.fan_preset = (
            None
            if self._attr_current_option in (FAN_PRESET_AUTO, None)
            else self._attr_current_option
        )
        self.hass.async_create_task(hub.async_save())
