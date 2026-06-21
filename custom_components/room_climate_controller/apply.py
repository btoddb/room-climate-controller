"""
Apply a profile's presets to its room's live entities.

This only writes the room's live ``number``/``switch`` entities; the room's
``RoomController`` then reacts and drives the hardware.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import STATE_ON

from .const import (
    KEY_AC_FAN_ONLY,
    KEY_FAN_REVERSE,
    KEY_MANUAL_MODE,
    KEY_TARGET,
    KEY_USE,
    LOGGER_PROFILE,
)
from .entity import resolve_room_entity

if TYPE_CHECKING:
    from .hub import RoomClimateConfigEntry
    from .models import Profile

_PROFILE_LOGGER = logging.getLogger(LOGGER_PROFILE)


async def async_apply_profile(
    entry: RoomClimateConfigEntry, profile: Profile, *, force: bool = False
) -> None:
    """
    Copy a profile's presets onto its room's live entities.

    ``force=False`` (scheduled fire) skips when manual mode is on, mirroring the
    old blueprint. ``force=True`` (explicit "apply now") always applies.
    """
    hass = entry.runtime_data.hass
    room = entry.runtime_data.room_by_key(profile.room)
    if room is None:
        return

    if not force:
        manual = resolve_room_entity(
            hass, entry.entry_id, room.key, KEY_MANUAL_MODE, "switch"
        )
        if manual and hass.states.is_state(manual, STATE_ON):
            _PROFILE_LOGGER.info(
                "[room=%s profile=%s] Profile '%s' skipped: manual mode active",
                room.key,
                profile.name,
                profile.name,
            )
            return

    settings = ", ".join(
        f"{device} {'on' if p.use else 'off'}@{int(p.temp)}°F"
        for device in room.devices
        if (p := profile.presets.get(device)) is not None
    )
    _PROFILE_LOGGER.info(
        "[room=%s profile=%s] Profile '%s' applied (%s): %s",
        room.key,
        profile.name,
        profile.name,
        "explicit" if force else "scheduled",
        settings or "no presets",
    )
    for device in room.devices:
        preset = profile.presets.get(device)
        if preset is None:
            continue
        if use_eid := resolve_room_entity(
            hass, entry.entry_id, room.key, KEY_USE[device], "switch"
        ):
            await hass.services.async_call(
                "switch",
                "turn_on" if preset.use else "turn_off",
                {"entity_id": use_eid},
                blocking=True,
            )
        if target_eid := resolve_room_entity(
            hass, entry.entry_id, room.key, KEY_TARGET[device], "number"
        ):
            await hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": target_eid, "value": preset.temp},
                blocking=True,
            )

    if (
        room.has_ac
        and room.ac_fan_only
        and (
            ov_eid := resolve_room_entity(
                hass, entry.entry_id, room.key, KEY_AC_FAN_ONLY, "switch"
            )
        )
    ):
        await hass.services.async_call(
            "switch",
            "turn_on" if profile.fan_override else "turn_off",
            {"entity_id": ov_eid},
            blocking=True,
        )

    if (
        room.has_fan
        and room.fan_entity
        and (
            rev_eid := resolve_room_entity(
                hass, entry.entry_id, room.key, KEY_FAN_REVERSE, "switch"
            )
        )
    ):
        await hass.services.async_call(
            "switch",
            "turn_on" if profile.fan_reverse else "turn_off",
            {"entity_id": rev_eid},
            blocking=True,
        )
