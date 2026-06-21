"""Switch platform: room use/manual toggles and profile preset toggles."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DEVICE_USE_ICONS,
    KEY_AC_FAN_ONLY,
    KEY_FAN_REVERSE,
    KEY_HEATER_FAN_ONLY,
    KEY_MANUAL_MODE,
    KEY_PROFILE_ENABLED,
    KEY_PROFILE_FAN_OVERRIDE,
    KEY_PROFILE_FAN_REVERSE,
    KEY_PROFILE_USE,
    KEY_USE,
    LOGGER_PROFILE,
    LOGGER_SETTINGS,
    SIGNAL_ADD_PROFILE_ENTITIES,
)
from .entity import ProfileRemovalMixin, profile_device_info, room_device_info
from .models import Profile, Room, profile_uid, room_uid

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .hub import RoomClimateConfigEntry

_LOGGER = logging.getLogger(__name__)
_SETTINGS_LOGGER = logging.getLogger(LOGGER_SETTINGS)
_PROFILE_LOGGER = logging.getLogger(LOGGER_PROFILE)


@dataclass(frozen=True)
class _SwitchSpec:
    key: str
    name: str
    icon: str
    default_on: bool = False


def _room_specs(room: Room) -> list[_SwitchSpec]:
    specs: list[_SwitchSpec] = [
        _SwitchSpec(
            key=KEY_USE[device],
            name={
                "cooling": "Use A/C",
                "heating": "Use heater",
                "fan": "Use fan",
            }[device],
            icon=DEVICE_USE_ICONS[device],
        )
        for device in room.devices
    ]
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
    # Created for every room with a standalone fan — reversibility is detected
    # live from the entity, which may not be loaded at platform setup (CC-22);
    # the switch is inert for non-reversible fans (CC-24).
    if room.has_fan and room.fan_entity:
        specs.append(
            _SwitchSpec(key=KEY_FAN_REVERSE, name="Fan reverse", icon="mdi:rotate-left")
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
        specs = _room_specs(room)
        _LOGGER.debug(
            "[room=%s] switch: %s",
            room.key,
            ", ".join(s.name for s in specs),
        )
        async_add_entities(
            [RoomSwitch(entry, room, spec) for spec in specs],
            config_subentry_id=room.room_id,
        )

    @callback
    def _add_profile(profile: Profile) -> None:
        room = hub.room_by_key(profile.room)
        if room is None:
            return
        entities: list[SwitchEntity] = [
            ProfileEnabledSwitch(entry, profile),
            *(ProfileUseSwitch(entry, profile, device) for device in room.devices),
        ]
        if room.has_ac and room.ac_fan_only:
            entities.append(ProfileFanOverrideSwitch(entry, profile))
        if room.has_fan and room.fan_entity:
            entities.append(ProfileFanReverseSwitch(entry, profile))
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

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn on."""
        self._attr_is_on = True
        self.async_write_ha_state()
        self._on_change()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn off."""
        self._attr_is_on = False
        self.async_write_ha_state()
        self._on_change()

    @callback
    def _on_change(self) -> None:
        """Override in subclasses to persist state after a toggle."""


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
        self._room_key = room.key

    @callback
    def _on_change(self) -> None:
        _SETTINGS_LOGGER.info(
            "[room=%s] Toggle '%s' → %s",
            self._room_key,
            self._attr_name,
            "on" if self._attr_is_on else "off",
        )


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
        """Write self._attr_is_on into the profile; override in subclasses."""

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

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Enable profile schedule."""
        await super().async_turn_on(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile schedule enabled",
            room_key,
            profile_name,
        )

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Disable profile schedule."""
        await super().async_turn_off(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile schedule disabled",
            room_key,
            profile_name,
        )

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

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Enable device preset."""
        await super().async_turn_on(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile preset edited: %s use → on",
            room_key,
            profile_name,
            self._device,
        )

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Disable device preset."""
        await super().async_turn_off(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile preset edited: %s use → off",
            room_key,
            profile_name,
            self._device,
        )

    @callback
    def _apply_to_profile(self, profile: Profile) -> None:
        preset = profile.ensure_preset(self._device)
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

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Enable fan-only override preset."""
        await super().async_turn_on(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile preset edited: fan-only override → on",
            room_key,
            profile_name,
        )

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Disable fan-only override preset."""
        await super().async_turn_off(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile preset edited: fan-only override → off",
            room_key,
            profile_name,
        )

    @callback
    def _apply_to_profile(self, profile: Profile) -> None:
        profile.fan_override = bool(self._attr_is_on)


class ProfileFanReverseSwitch(_BaseProfileSwitch):
    """A profile's standalone-fan reverse-direction preset (PR-12)."""

    def __init__(self, entry: RoomClimateConfigEntry, profile: Profile) -> None:
        """Initialize."""
        super().__init__(entry, profile)
        self._attr_unique_id = profile_uid(
            entry.entry_id, profile.id, KEY_PROFILE_FAN_REVERSE
        )
        self._attr_name = "Fan reverse"
        self._attr_icon = "mdi:rotate-left"
        self._attr_is_on = profile.fan_reverse

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Enable fan reverse preset."""
        await super().async_turn_on(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile preset edited: fan reverse → on",
            room_key,
            profile_name,
        )

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Disable fan reverse preset."""
        await super().async_turn_off(**_kwargs)
        profile = self._entry.runtime_data.get_profile(self._profile_id)
        room_key = profile.room if profile else "unknown"
        profile_name = profile.name if profile else "unknown"
        _PROFILE_LOGGER.info(
            "[room=%s profile=%s] Profile preset edited: fan reverse → off",
            room_key,
            profile_name,
        )

    @callback
    def _apply_to_profile(self, profile: Profile) -> None:
        profile.fan_reverse = bool(self._attr_is_on)
