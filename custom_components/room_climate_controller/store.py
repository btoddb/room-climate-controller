"""Persistent storage for Room Climate profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.storage import Store

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .const import STORAGE_KEY, STORAGE_VERSION
from .models import Profile


class ProfileStore:
    """Load/save the list of profiles to HA's ``.storage``."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the store."""
        self._store: Store[dict] = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    async def async_load(self) -> list[Profile]:
        """Load profiles, returning an empty list on first run."""
        data = await self._store.async_load()
        if not data:
            return []
        return [Profile.from_dict(item) for item in data.get("profiles", [])]

    async def async_save(self, profiles: list[Profile]) -> None:
        """Persist all profiles."""
        await self._store.async_save(
            {"profiles": [profile.to_dict() for profile in profiles]}
        )
