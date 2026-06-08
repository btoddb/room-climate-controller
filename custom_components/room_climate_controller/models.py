"""
Data models and shared helpers for Room Climate.

Pure logic (no Home Assistant imports) so it can be unit-tested and reused across
the config flow, websocket API, scheduler, and entity platforms.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from .const import (
    CONF_AC_CLIMATE,
    CONF_AC_FAN_ENTITY,
    CONF_AC_FAN_ONLY,
    CONF_AC_POWER_SWITCH,
    CONF_AREA_ID,
    CONF_COMBINED,
    CONF_COMMAND_DELAY,
    CONF_FAN_ENTITY,
    CONF_HAS_AC,
    CONF_HAS_FAN,
    CONF_HAS_HEATER,
    CONF_HEATER_CLIMATE,
    CONF_HEATER_FAN_ENTITY,
    CONF_HEATER_FAN_ONLY,
    CONF_HEATER_POWER_SWITCH,
    CONF_HUMIDITY_SENSOR,
    CONF_LABEL,
    CONF_LIMITS,
    CONF_POWER_ON_DELAY,
    CONF_POWER_SENSOR,
    CONF_ROOM_KEY,
    CONF_TEMPERATURE_SENSOR,
    DEFAULT_COMMAND_DELAY,
    DEFAULT_LIMITS,
    DEFAULT_POWER_ON_DELAY,
    DEVICE_COOLING,
    DEVICE_FAN,
    DEVICE_HEATING,
    DEVICE_TYPES,
    PROFILE_DEFAULT_ICON,
)

_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::\d{2})?$")


# ---------------------------------------------------------------------------
# ID / time helpers (ported from daily_climate_lib.py)
# ---------------------------------------------------------------------------
def normalize_time_hhmm(value: str) -> str:
    """Validate and normalize a profile run time to HH:MM (24h)."""
    raw = str(value).strip()
    m = _TIME_RE.match(raw)
    if not m:
        raise ValueError(f"Invalid time {value!r}; use HH:MM (24-hour)")
    hour, minute = int(m.group(1)), int(m.group(2))
    if hour > 23 or minute > 59:
        raise ValueError(f"Invalid time {value!r}")
    return f"{hour:02d}:{minute:02d}"


def format_profile_id(profile_id: str | int) -> str:
    """Canonical id (e.g. 8 and 08 → 08); non-numeric ids pass through."""
    s = str(profile_id).strip()
    if s.isdigit():
        return f"{int(s):02d}"
    return s


def slugify_profile_id(name: str) -> str:
    """Derive a fallback profile id from a display name."""
    base = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return base[:32] or "profile"


def next_profile_id(existing_ids: Iterable[str]) -> str:
    """Return the next 2-digit numeric id not already used."""
    ids = {format_profile_id(pid) for pid in existing_ids}
    numeric = [int(pid) for pid in ids if pid.isdigit()]
    if numeric:
        candidate = max(numeric) + 1
    else:
        candidate = 1
    while f"{candidate:02d}" in ids:
        candidate += 1
    return f"{candidate:02d}"


# ---------------------------------------------------------------------------
# Room model (from a config subentry)
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Room:
    """A configured room and its physical devices."""

    room_id: str  # subentry_id
    key: str
    label: str
    area_id: str | None
    has_ac: bool
    has_heater: bool
    has_fan: bool
    combined: bool
    ac_climate: str | None
    heater_climate: str | None
    fan_entity: str | None
    ac_fan_entity: str | None
    heater_fan_entity: str | None
    ac_power_switch: str | None
    heater_power_switch: str | None
    temperature_sensor: str | None
    humidity_sensor: str | None
    power_sensor: str | None
    ac_fan_only: bool
    heater_fan_only: bool
    limits: dict[str, dict[str, float]]
    command_delay: float
    power_on_delay: float

    @classmethod
    def from_subentry(cls, subentry_id: str, data: Mapping[str, Any]) -> Room:
        """Build a Room from a config subentry's stored data."""
        limits = {
            device: {
                "min": float(
                    data.get(CONF_LIMITS, {})
                    .get(device, {})
                    .get("min", DEFAULT_LIMITS[device]["min"])
                ),
                "max": float(
                    data.get(CONF_LIMITS, {})
                    .get(device, {})
                    .get("max", DEFAULT_LIMITS[device]["max"])
                ),
            }
            for device in DEVICE_TYPES
        }
        return cls(
            room_id=subentry_id,
            key=str(data[CONF_ROOM_KEY]),
            label=str(data.get(CONF_LABEL) or data[CONF_ROOM_KEY]),
            area_id=data.get(CONF_AREA_ID) or None,
            has_ac=bool(data.get(CONF_HAS_AC, True)),
            has_heater=bool(data.get(CONF_HAS_HEATER, False)),
            has_fan=bool(data.get(CONF_HAS_FAN, False)),
            combined=bool(data.get(CONF_COMBINED, False)),
            ac_climate=data.get(CONF_AC_CLIMATE) or None,
            heater_climate=data.get(CONF_HEATER_CLIMATE) or None,
            fan_entity=data.get(CONF_FAN_ENTITY) or None,
            ac_fan_entity=data.get(CONF_AC_FAN_ENTITY) or None,
            heater_fan_entity=data.get(CONF_HEATER_FAN_ENTITY) or None,
            ac_power_switch=data.get(CONF_AC_POWER_SWITCH) or None,
            heater_power_switch=data.get(CONF_HEATER_POWER_SWITCH) or None,
            temperature_sensor=data.get(CONF_TEMPERATURE_SENSOR) or None,
            humidity_sensor=data.get(CONF_HUMIDITY_SENSOR) or None,
            power_sensor=data.get(CONF_POWER_SENSOR) or None,
            ac_fan_only=bool(data.get(CONF_AC_FAN_ONLY, False)),
            heater_fan_only=bool(data.get(CONF_HEATER_FAN_ONLY, False)),
            limits=limits,
            command_delay=float(data.get(CONF_COMMAND_DELAY, DEFAULT_COMMAND_DELAY)),
            power_on_delay=float(data.get(CONF_POWER_ON_DELAY, DEFAULT_POWER_ON_DELAY)),
        )

    def supports(self, device: str) -> bool:
        """Whether this room has the given device type (cooling/heating/fan)."""
        if device == DEVICE_COOLING:
            return self.has_ac
        if device == DEVICE_HEATING:
            return self.has_heater
        if device == DEVICE_FAN:
            return self.has_fan
        return False

    @property
    def devices(self) -> tuple[str, ...]:
        """Device types available in this room, in canonical order."""
        return tuple(d for d in DEVICE_TYPES if self.supports(d))


# ---------------------------------------------------------------------------
# Profile model (stored in .storage, source of truth for preset values)
# ---------------------------------------------------------------------------
@dataclass
class DevicePreset:
    """A profile's per-device preset: whether to apply it and the target temp."""

    use: bool = False
    temp: float = 0.0


@dataclass
class Profile:
    """A scheduled climate preset for a room."""

    id: str
    name: str
    room: str  # room key
    icon: str = PROFILE_DEFAULT_ICON
    enabled: bool = True
    time: str | None = None  # "HH:MM"
    fan_override: bool = False
    presets: dict[str, DevicePreset] = field(default_factory=dict)

    @classmethod
    def with_defaults(cls, *, id: str, name: str, room: Room) -> Profile:
        """Create a profile with preset defaults (uses off, temps at room min)."""
        return cls(
            id=format_profile_id(id),
            name=name.strip(),
            room=room.key,
            presets={
                device: DevicePreset(use=False, temp=room.limits[device]["min"])
                for device in room.devices
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "room": self.room,
            "icon": self.icon,
            "enabled": self.enabled,
            "time": self.time,
            "fan_override": self.fan_override,
            "presets": {
                device: {"use": p.use, "temp": p.temp}
                for device, p in self.presets.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Profile:
        """Deserialize from storage."""
        return cls(
            id=format_profile_id(data["id"]),
            name=str(data["name"]),
            room=str(data["room"]),
            icon=str(data.get("icon") or PROFILE_DEFAULT_ICON),
            enabled=bool(data.get("enabled", True)),
            time=data.get("time"),
            fan_override=bool(data.get("fan_override", False)),
            presets={
                device: DevicePreset(
                    use=bool(p.get("use", False)),
                    temp=float(p.get("temp", 0.0)),
                )
                for device, p in (data.get("presets") or {}).items()
            },
        )

    def reassigned_to(self, room: Room) -> Profile:
        """Return a copy moved to ``room``, re-seeding presets for its devices."""
        presets = {
            device: self.presets.get(
                device, DevicePreset(use=False, temp=room.limits[device]["min"])
            )
            for device in room.devices
        }
        return replace(self, room=room.key, presets=presets)


# ---------------------------------------------------------------------------
# Deterministic unique_id builders (used by platforms + controller/scheduler)
# ---------------------------------------------------------------------------
def room_uid(entry_id: str, room_key: str, key: str) -> str:
    """Unique id for a per-room entity."""
    return f"{entry_id}_room_{room_key}_{key}"


def profile_uid(entry_id: str, profile_id: str, key: str) -> str:
    """Unique id for a per-profile entity."""
    return f"{entry_id}_profile_{profile_id}_{key}"


def find_time_conflict(
    profiles: Iterable[Profile],
    room_key: str,
    new_time: str,
    *,
    exclude_id: str | None = None,
) -> str | None:
    """Return the id of a profile already scheduled at ``new_time`` in the room."""
    normalized = normalize_time_hhmm(new_time)
    exclude = format_profile_id(exclude_id) if exclude_id else None
    for profile in profiles:
        if profile.room != room_key:
            continue
        if exclude and profile.id == exclude:
            continue
        if profile.time and normalize_time_hhmm(profile.time) == normalized:
            return profile.id
    return None
