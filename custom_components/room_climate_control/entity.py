"""Base entities and device-info helpers for Room Climate."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_REMOVE_PROFILE
from .models import Profile, Room, profile_uid, room_uid


def resolve_room_entity(
    hass: HomeAssistant, entry_id: str, room_key: str, key: str, domain: str
) -> str | None:
    """Resolve a room live entity's id from its deterministic unique_id."""
    return er.async_get(hass).async_get_entity_id(
        domain, DOMAIN, room_uid(entry_id, room_key, key)
    )


def resolve_profile_entity(
    hass: HomeAssistant, entry_id: str, profile_id: str, key: str, domain: str
) -> str | None:
    """Resolve a profile entity's id from its deterministic unique_id."""
    return er.async_get(hass).async_get_entity_id(
        domain, DOMAIN, profile_uid(entry_id, profile_id, key)
    )


def hub_identifier(entry_id: str) -> tuple[str, str]:
    """Identifier tuple for the hub service device."""
    return (DOMAIN, entry_id)


def room_device_info(entry: ConfigEntry, room: Room) -> DeviceInfo:
    """Device grouping all of a room's live entities."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_room_{room.key}")},
        name=room.label,
        manufacturer="Room Climate",
        model="Room",
        via_device=hub_identifier(entry.entry_id),
    )


def profile_device_info(entry: ConfigEntry, profile: Profile) -> DeviceInfo:
    """Device grouping all of a profile's preset entities."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_profile_{profile.id}")},
        name=profile.name,
        manufacturer="Room Climate",
        model="Daily profile",
        via_device=hub_identifier(entry.entry_id),
    )


class ProfileRemovalMixin:
    """Removes a profile entity when its profile is deleted via dispatcher.

    Classes set ``self._profile_id`` and call ``_connect_profile_removal()``
    from their own ``async_added_to_hass``.
    """

    _profile_id: str

    def _connect_profile_removal(self) -> None:
        self.async_on_remove(  # type: ignore[attr-defined]
            async_dispatcher_connect(
                self.hass,  # type: ignore[attr-defined]
                SIGNAL_REMOVE_PROFILE,
                self._on_remove_signal,
            )
        )

    @callback
    def _on_remove_signal(self, profile_id: str) -> None:
        if profile_id == self._profile_id:
            self.hass.async_create_task(  # type: ignore[attr-defined]
                self.async_remove(force_remove=True)  # type: ignore[attr-defined]
            )
