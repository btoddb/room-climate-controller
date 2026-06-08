"""Base entities and device-info helpers for Room Climate."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
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


def resolve_hub_entity(
    hass: HomeAssistant, entry_id: str, key: str, domain: str
) -> str | None:
    """Resolve a hub-scoped entity id (e.g. the outdoor temperature mirror)."""
    return er.async_get(hass).async_get_entity_id(domain, DOMAIN, f"{entry_id}_{key}")


def hub_identifier(entry_id: str) -> tuple[str, str]:
    """Identifier tuple for the hub service device."""
    return (DOMAIN, entry_id)


def room_device_info(entry: ConfigEntry, room: Room) -> DeviceInfo:
    """Device grouping all of a room's live entities."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_room_{room.key}")},
        name=room.label,
        manufacturer="Room Climate Controller",
        model="Room",
        via_device=hub_identifier(entry.entry_id),
    )


def profile_device_info(entry: ConfigEntry, profile: Profile) -> DeviceInfo:
    """Device grouping all of a profile's preset entities."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_profile_{profile.id}")},
        name=profile.name,
        manufacturer="Room Climate Controller",
        model="Daily profile",
        via_device=hub_identifier(entry.entry_id),
    )


@callback
def async_assign_areas(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Place each room's device — and its profiles' devices — in the room's area.

    Only fills a device with no area yet, so a manual move in the UI is preserved.
    Devices register a moment after platform setup, so callers also schedule a
    delayed pass.
    """
    hub = getattr(entry, "runtime_data", None)
    if hub is None:
        return
    dev_reg = dr.async_get(hass)

    def _assign(suffix: str, area_id: str | None) -> None:
        if not area_id:
            return
        device = dev_reg.async_get_device(
            identifiers={(DOMAIN, f"{entry.entry_id}_{suffix}")}
        )
        if device is not None and device.area_id is None:
            dev_reg.async_update_device(device.id, area_id=area_id)

    for room in hub.rooms.values():
        _assign(f"room_{room.key}", room.area_id)
    for profile in hub.profiles:
        room = hub.room_by_key(profile.room)
        if room is not None:
            _assign(f"profile_{profile.id}", room.area_id)


@callback
def async_migrate_profile_subentries(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Drop the legacy "no subentry" link from profile devices.

    Profiles used to register without a config subentry; they now belong to their
    room's subentry. Devices created before that change keep both links and so
    appear twice in the UI — remove the stale ``None`` membership once the room
    link is present. Devices register a moment after setup, so callers also
    schedule a delayed pass.
    """
    hub = getattr(entry, "runtime_data", None)
    if hub is None:
        return
    dev_reg = dr.async_get(hass)
    for profile in hub.profiles:
        room = hub.room_by_key(profile.room)
        if room is None:
            continue
        device = dev_reg.async_get_device(
            identifiers={(DOMAIN, f"{entry.entry_id}_profile_{profile.id}")}
        )
        if device is None:
            continue
        subentries = device.config_entries_subentries.get(entry.entry_id, set())
        if None in subentries and room.room_id in subentries:
            dev_reg.async_update_device(
                device.id,
                remove_config_entry_id=entry.entry_id,
                remove_config_subentry_id=None,
            )


class ProfileRemovalMixin:
    """
    Removes a profile entity when its profile is deleted via dispatcher.

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
