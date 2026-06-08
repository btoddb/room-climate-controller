"""Switch platform: room use/manual toggles and profile preset toggles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DEVICE_USE_ICONS,
    KEY_AC_FAN_ONLY,
    KEY_HEATER_FAN_ONLY,
    KEY_MANUAL_MODE,
    KEY_PROFILE_ENABLED,
    KEY_PROFILE_FAN_OVERRIDE,
    KEY_PROFILE_USE,
    KEY_USE,
    SIGNAL_ADD_PROFILE_ENTITIES,
)
from .entity import ProfileRemovalMixin, profile_device_info, room_device_info
from .hub import RoomClimateConfigEntry
from .models import Profile, Room, profile_uid, room_uid


@dataclass(frozen=True)
class _SwitchSpec:
    key: str
    name: str
    icon: str
    default_on: bool = False


def _room_specs(room: Room) -> list[_SwitchSpec]:
    specs: list[_SwitchSpec] = []
    for device in room.devices:
        specs.append(
            _SwitchSpec(
                key=KEY_USE[device],
                name={
                    "cooling": "Use A/C",
                    "heating": "Use heater",
                    "fan": "Use fan",
                }[device],
                icon=DEVICE_USE_ICONS[device],
            )
        )
    specs.append(
        _SwitchSpec(
            key=KEY_MANUAL_MODE,
            name="Manual mode",
            icon="mdi:hand-back-right",
            default_on=True,  # a new room starts dormant until explicitly activated
        )
    )
    if room.has_ac and room.ac_fan_only:
        specs.append(
            _SwitchSpec(
                key=KEY_AC_FAN_ONLY, name="A/C fan-only override", icon="mdi:fan-auto"
            )
        )
    if room.has_heater and room.heater_fan_only:
        specs.append(
            _SwitchSpec(
                key=KEY_HEATER_FAN_ONLY,
                name="Heater fan-only override",
                icon="mdi:fan-auto",
            )
        )
    return specs


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RoomClimateConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up room and profile switch entities."""
    hub = entry.runtime_data

    for room in hub.rooms.values():
        async_add_entities(
            [RoomSwitch(entry, room, spec) for spec in _room_specs(room)],
            config_subentry_id=room.room_id,
        )

    @callback
    def _add_profile(profile: Profile) -> None:
        room = hub.room_by_key(profile.room)
        if room is None:
            return
        entities: list[SwitchEntity] = [ProfileEnabledSwitch(entry, profile)]
        for device in room.devices:
            entities.append(ProfileUseSwitch(entry, profile, device))
        if room.has_ac and room.ac_fan_only:
            entities.append(ProfileFanOverrideSwitch(entry, profile))
        async_add_entities(entities, config_subentry_id=room.room_id)

    for profile in hub.profiles:
        _add_profile(profile)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_ADD_PROFILE_ENTITIES, _add_profile)
    )


class _BaseRestoreSwitch(SwitchEntity, RestoreEntity):
    """A switch whose on/off state persists across restarts."""

    _attr_has_entity_name = True

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is not None:
            self._attr_is_on = last.state == "on"
        elif self._attr_is_on is None:
            self._attr_is_on = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        self._attr_is_on = True
        self.async_write_ha_state()
        self._on_change()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        self._attr_is_on = False
        self.async_write_ha_state()
        self._on_change()

    @callback
    def _on_change(self) -> None:
        """Hook for subclasses to persist state."""


class RoomSwitch(_BaseRestoreSwitch):
    """A per-room toggle (use device / manual mode / fan-only override)."""

    def __init__(
        self, entry: RoomClimateConfigEntry, room: Room, spec: _SwitchSpec
    ) -> None:
        """Initialize the room switch."""
        self._attr_unique_id = room_uid(entry.entry_id, room.key, spec.key)
        self._attr_name = spec.name
        self._attr_icon = spec.icon
        self._attr_is_on = spec.default_on
        self._attr_device_info = room_device_info(entry, room)


class _BaseProfileSwitch(ProfileRemovalMixin, _BaseRestoreSwitch):
    """Profile preset switch that persists its value to the profile store."""

    def __init__(self, entry: RoomClimateConfigEntry, profile: Profile) -> None:
        """Initialize common profile-switch state."""
        self._entry = entry
        self._profile_id = profile.id
        self._attr_device_info = profile_device_info(entry, profile)

    async def async_added_to_hass(self) -> None:
        """Restore state and connect removal."""
        await super().async_added_to_hass()
        self._connect_profile_removal()
        self._on_change()

    @callback
    def _apply_to_profile(self, profile: Profile) -> None:
        """Subclasses write self._attr_is_on into the profile."""

    @callback
    def _on_change(self) -> None:
        hub = self._entry.runtime_data
        profile = hub.get_profile(self._profile_id)
        if profile is None:
            return
        self._apply_to_profile(profile)
        self.hass.async_create_task(hub.async_save())


class ProfileEnabledSwitch(_BaseProfileSwitch):
    """Whether a profile fires on its schedule."""

    def __init__(self, entry: RoomClimateConfigEntry, profile: Profile) -> None:
        """Initialize."""
        super().__init__(entry, profile)
        self._attr_unique_id = profile_uid(
            entry.entry_id, profile.id, KEY_PROFILE_ENABLED
        )
        self._attr_name = None  # primary entity → uses the device (profile) name
        self._attr_icon = profile.icon
        self._attr_is_on = profile.enabled

    @callback
    def _apply_to_profile(self, profile: Profile) -> None:
        profile.enabled = bool(self._attr_is_on)


class ProfileUseSwitch(_BaseProfileSwitch):
    """Whether a profile applies a given device's preset."""

    def __init__(
        self, entry: RoomClimateConfigEntry, profile: Profile, device: str
    ) -> None:
        """Initialize."""
        super().__init__(entry, profile)
        self._device = device
        self._attr_unique_id = profile_uid(
            entry.entry_id, profile.id, KEY_PROFILE_USE[device]
        )
        self._attr_name = {
            "cooling": "Use cooling",
            "heating": "Use heating",
            "fan": "Use fan",
        }[device]
        self._attr_icon = DEVICE_USE_ICONS[device]
        preset = profile.presets.get(device)
        self._attr_is_on = bool(preset.use) if preset else False

    @callback
    def _apply_to_profile(self, profile: Profile) -> None:
        preset = profile.presets.get(self._device)
        if preset is not None:
            preset.use = bool(self._attr_is_on)


class ProfileFanOverrideSwitch(_BaseProfileSwitch):
    """A profile's A/C fan-only override preset."""

    def __init__(self, entry: RoomClimateConfigEntry, profile: Profile) -> None:
        """Initialize."""
        super().__init__(entry, profile)
        self._attr_unique_id = profile_uid(
            entry.entry_id, profile.id, KEY_PROFILE_FAN_OVERRIDE
        )
        self._attr_name = "Fan-only override"
        self._attr_icon = "mdi:fan-auto"
        self._attr_is_on = profile.fan_override

    @callback
    def _apply_to_profile(self, profile: Profile) -> None:
        profile.fan_override = bool(self._attr_is_on)
