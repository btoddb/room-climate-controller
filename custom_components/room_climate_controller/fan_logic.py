"""
Pure fan-speed logic (no Home Assistant imports, fully unit-testable).

Ports the 3-tier speed selection and the device ``fan_mode`` matching from
``room_climate_control.yaml``.
"""

from __future__ import annotations

from collections.abc import Sequence

# Speed tiers as (label, percentage).
LOW = ("low", 10)
MEDIUM = ("medium", 50)
HIGH = ("high", 100)

_PREF: dict[str, list[str]] = {
    "low": ["low", "quiet"],
    "medium": ["medium", "medium_low", "medium_high"],
    "high": ["high", "strong"],
}


def cooling_speed(room_temp: float, medium: float, high: float) -> tuple[str, int]:
    """Hotter rooms cool harder: speed rises as temp passes target+offsets."""
    if room_temp >= high:
        return HIGH
    if room_temp >= medium:
        return MEDIUM
    return LOW


def heating_speed(room_temp: float, medium: float, high: float) -> tuple[str, int]:
    """Colder rooms heat harder: ``medium``/``high`` are target-offset (high < medium)."""
    if room_temp <= high:
        return HIGH
    if room_temp <= medium:
        return MEDIUM
    return LOW


def match_fan_mode(fan_modes: Sequence[str], label: str) -> str:
    """
    Map a low/medium/high label onto a device's actual ``fan_modes``.

    Returns the matching device mode, or ``""`` if none fits — mirroring the
    blueprint's preference list plus substring fallback (with the high↔medium
    and medium↔medium_low/high exclusions).
    """
    for want in _PREF.get(label, []):
        for fm in fan_modes:
            if fm.lower() == want:
                return fm
    for fm in fan_modes:
        fm_l = fm.lower()
        if label in fm_l:
            if label == "high" and "medium" in fm_l:
                continue
            if label == "medium" and fm_l in ("medium_low", "medium_high"):
                continue
            return fm
    return ""
