"""Time platform: per-profile schedule time."""

from __future__ import annotations

import logging
from datetime import time
from typing import TYPE_CHECKING

from homeassistant.components.time import TimeEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.restore_state import RestoreEntity

from .const import KEY_PROFILE_TIME, SIGNAL_ADD_PROFILE_ENTITIES
from .entity import ProfileRemovalMixin, profile_device_info
from .models import Profile, normalize_time_hhmm, profile_uid

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .hub import RoomClimateConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RoomClimateConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up per-profile time entities."""
    hub = entry.runtime_data

    @callback
    def _add_profile(profile: Profile) -> None:
        room = hub.room_by_key(profile.room)
        if room is None:
            return
        async_add_entities(
            [ProfileTime(entry, profile)], config_subentry_id=room.room_id
        )

    for profile in hub.profiles:
        _add_profile(profile)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_ADD_PROFILE_ENTITIES, _add_profile)
    )


def _parse_hhmm(value: str | None) -> time | None:
    """Parse a stored ``HH:MM`` (or ``HH:MM:SS``) string into a time."""
    if not value:
        return None
    try:
        hh, mm = normalize_time_hhmm(value).split(":")
    except ValueError:
        return None
    return time(int(hh), int(mm))


class ProfileTime(ProfileRemovalMixin, TimeEntity, RestoreEntity):
    """The time of day a profile fires."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:clock-outline"

    def __init__(self, entry: RoomClimateConfigEntry, profile: Profile) -> None:
        """Initialize the time entity."""
        self._entry = entry
        self._profile_id = profile.id
        self._attr_unique_id = profile_uid(entry.entry_id, profile.id, KEY_PROFILE_TIME)
        self._attr_name = "Schedule time"
        self._attr_device_info = profile_device_info(entry, profile)
        self._attr_native_value = _parse_hhmm(profile.time)

    async def async_added_to_hass(self) -> None:
        """Restore last value and connect removal."""
        await super().async_added_to_hass()
        self._connect_profile_removal()
        if (last := await self.async_get_last_state()) is not None and (
            restored := _parse_hhmm(last.state)
        ) is not None:
            self._attr_native_value = restored
        self._sync_to_store()

    async def async_set_value(self, value: time) -> None:
        """Set a new schedule time."""
        old = self._attr_native_value
        self._attr_native_value = value
        self.async_write_ha_state()
        self._sync_to_store()
        if old != value:
            profile = self._entry.runtime_data.get_profile(self._profile_id)
            if profile is not None:
                _LOGGER.info(
                    "[room=%s profile=%s] Profile schedule time → %02d:%02d",
                    profile.room,
                    self._profile_id,
                    value.hour,
                    value.minute,
                )

    @callback
    def _sync_to_store(self) -> None:
        hub = self._entry.runtime_data
        profile = hub.get_profile(self._profile_id)
        if profile is None:
            return
        new_time = (
            f"{self._attr_native_value.hour:02d}:{self._attr_native_value.minute:02d}"
            if self._attr_native_value is not None
            else None
        )
        if profile.time != new_time:
            profile.time = new_time
            self.hass.async_create_task(hub.async_save())
