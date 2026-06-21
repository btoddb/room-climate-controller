"""Profile.ensure_preset: backfilling a preset for a device added after creation."""

from __future__ import annotations

from custom_components.room_climate_controller.models import DevicePreset, Profile


def _profile(**presets: DevicePreset) -> Profile:
    return Profile(id="01", name="Morning", room="main_floor", presets=presets)


def test_ensure_preset_creates_missing_default() -> None:
    profile = _profile(cooling=DevicePreset(use=True, temp=75.0))

    preset = profile.ensure_preset("fan")

    assert preset is profile.presets["fan"]
    assert preset.use is False
    assert preset.temp == 0.0


def test_ensure_preset_returns_existing_without_replacing() -> None:
    existing = DevicePreset(use=True, temp=72.0)
    profile = _profile(fan=existing)

    preset = profile.ensure_preset("fan")

    assert preset is existing
