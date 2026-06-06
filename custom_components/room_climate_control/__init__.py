"""The Room Climate integration."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from . import websocket_api
from .apply import async_apply_profile
from .constraints import ConstraintsValidator
from .const import DOMAIN, KEY_MANUAL_MODE, PLATFORMS
from .controller import RoomController
from .entity import resolve_room_entity
from .hub import RoomClimateConfigEntry, RoomClimateHub
from .models import format_profile_id
from .scheduler import ProfileScheduler

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_APPLY_PROFILE = "apply_profile"
SERVICE_SET_MANUAL_MODE = "set_manual_mode"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register websocket commands and services (once)."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/room_climate", str(Path(__file__).parent / "www"), cache_headers=False)]
    )
    websocket_api.async_setup(hass)

    def _loaded_entry() -> RoomClimateConfigEntry | None:
        return next(
            (
                entry
                for entry in hass.config_entries.async_entries(DOMAIN)
                if entry.state is ConfigEntryState.LOADED
            ),
            None,
        )

    async def _apply_profile(call: ServiceCall) -> None:
        entry = _loaded_entry()
        if entry is None:
            return
        profile = entry.runtime_data.get_profile(
            format_profile_id(call.data["profile_id"])
        )
        if profile is not None:
            await async_apply_profile(entry, profile, force=True)

    async def _set_manual_mode(call: ServiceCall) -> None:
        entry = _loaded_entry()
        if entry is None:
            return
        room = entry.runtime_data.room_by_key(call.data["room"])
        if room is None:
            return
        manual = resolve_room_entity(
            hass, entry.entry_id, room.key, KEY_MANUAL_MODE, "switch"
        )
        if manual:
            await hass.services.async_call(
                "switch",
                "turn_on" if call.data["enabled"] else "turn_off",
                {"entity_id": manual},
                blocking=True,
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_APPLY_PROFILE,
        _apply_profile,
        schema=vol.Schema({vol.Required("profile_id"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MANUAL_MODE,
        _set_manual_mode,
        schema=vol.Schema(
            {vol.Required("room"): cv.string, vol.Required("enabled"): cv.boolean}
        ),
    )
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: RoomClimateConfigEntry
) -> bool:
    """Set up Room Climate from a config entry."""
    hub = RoomClimateHub(hass, entry)
    await hub.async_load()
    entry.runtime_data = hub

    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="Room Climate",
        name=entry.title,
        entry_type=dr.DeviceEntryType.SERVICE,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Start a reactive controller + constraints validator per room.
    for room in hub.rooms.values():
        controller = RoomController(hass, entry, room)
        validator = ConstraintsValidator(hass, entry, room)
        hub.controllers[room.key] = controller
        hub.validators[room.key] = validator
        controller.async_start()
        validator.async_start()

    # Start the profile scheduler.
    hub.scheduler = ProfileScheduler(hass, entry)
    hub.scheduler.async_start()

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: RoomClimateConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(
    hass: HomeAssistant, entry: RoomClimateConfigEntry
) -> None:
    """Reload when subentries (rooms) change."""
    await hass.config_entries.async_reload(entry.entry_id)
