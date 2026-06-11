"""
Runtime root object for a Room Climate config entry.

Holds the live rooms (built from config subentries), the profiles (loaded from
storage), the per-room reactive controllers, and the profile scheduler. Stored on
``config_entry.runtime_data`` and shared by the platforms, websocket API, and
services.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

from .const import SUBENTRY_TYPE_ROOM
from .models import Profile, Room, format_profile_id
from .store import ProfileStore

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .constraints import ConstraintsValidator
    from .controller import RoomController
    from .scheduler import ProfileScheduler

type RoomClimateConfigEntry = ConfigEntry[RoomClimateHub]


class RoomClimateHub:
    """Shared runtime state for the integration."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the hub."""
        self.hass = hass
        self.entry = entry
        self.store = ProfileStore(hass)
        self.profiles: list[Profile] = []
        self.rooms: dict[str, Room] = {}
        self.controllers: dict[str, RoomController] = {}
        self.validators: dict[str, ConstraintsValidator] = {}
        self.scheduler: ProfileScheduler | None = None

    # -- loading -------------------------------------------------------------
    async def async_load(self) -> None:
        """Load profiles from storage and build rooms from subentries."""
        self.profiles = await self.store.async_load()
        self.rebuild_rooms()

    def rebuild_rooms(self) -> None:
        """(Re)build the room map from the entry's room subentries."""
        old = self.rooms
        rooms: dict[str, Room] = {}
        for subentry_id, subentry in self.entry.subentries.items():
            if subentry.subentry_type != SUBENTRY_TYPE_ROOM:
                continue
            room = Room.from_subentry(subentry_id, subentry.data)
            rooms[room.key] = room
            if room.key not in old:
                _LOGGER.info("[room=%s] Room created: '%s'", room.key, room.label)
            elif old[room.key] != room:
                _LOGGER.info(
                    "[room=%s] Room settings changed: '%s'", room.key, room.label
                )
        for key in set(old) - set(rooms):
            _LOGGER.info("[room=%s] Room removed: '%s'", key, old[key].label)
        self.rooms = rooms

    async def async_save(self) -> None:
        """Persist the current profile list."""
        await self.store.async_save(self.profiles)

    # -- lookups -------------------------------------------------------------
    def room_by_key(self, key: str) -> Room | None:
        """Return the room with the given key, if any."""
        return self.rooms.get(key)

    def room_by_subentry(self, subentry_id: str) -> Room | None:
        """Return the room backed by the given subentry id, if any."""
        return next((r for r in self.rooms.values() if r.room_id == subentry_id), None)

    def get_profile(self, profile_id: str) -> Profile | None:
        """Return the profile with the given id, if any."""
        canonical = format_profile_id(profile_id)
        return next((p for p in self.profiles if p.id == canonical), None)

    @property
    def profile_ids(self) -> list[str]:
        """All current profile ids."""
        return [p.id for p in self.profiles]
