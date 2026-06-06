"""Fires profiles at their scheduled time and on explicit apply."""

from __future__ import annotations

from collections.abc import Callable
import logging

from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_change,
)

from .apply import async_apply_profile
from .const import KEY_PROFILE_ENABLED, KEY_PROFILE_TIME
from .entity import resolve_profile_entity
from .hub import RoomClimateConfigEntry
from .models import normalize_time_hhmm

_LOGGER = logging.getLogger(__name__)


class ProfileScheduler:
    """Registers time triggers for enabled profiles and re-registers on change."""

    def __init__(self, hass: HomeAssistant, entry: RoomClimateConfigEntry) -> None:
        """Initialize the scheduler."""
        self.hass = hass
        self.entry = entry
        self._time_unsubs: dict[str, Callable[[], None]] = {}
        self._state_unsub: Callable[[], None] | None = None
        self._tracked: frozenset[str] = frozenset()

    @callback
    def async_start(self) -> None:
        """Schedule all profiles and watch their enabled/time entities."""
        self.async_refresh()
        self.entry.async_on_unload(
            async_call_later(self.hass, 3, lambda _now: self.async_refresh())
        )
        self.entry.async_on_unload(self.async_stop)

    @callback
    def async_stop(self) -> None:
        """Cancel all triggers and subscriptions."""
        for unsub in self._time_unsubs.values():
            unsub()
        self._time_unsubs.clear()
        if self._state_unsub:
            self._state_unsub()
            self._state_unsub = None

    @callback
    def async_refresh(self) -> None:
        """Re-register time triggers and re-subscribe to profile entities."""
        self._reschedule()
        self._resubscribe_state()

    @callback
    def _reschedule(self) -> None:
        for unsub in self._time_unsubs.values():
            unsub()
        self._time_unsubs.clear()
        for profile in self.entry.runtime_data.profiles:
            if not profile.enabled or not profile.time:
                continue
            try:
                hh, mm = normalize_time_hhmm(profile.time).split(":")
            except ValueError:
                continue
            self._time_unsubs[profile.id] = async_track_time_change(
                self.hass,
                self._make_fire(profile.id),
                hour=int(hh),
                minute=int(mm),
                second=0,
            )

    def _make_fire(self, profile_id: str) -> Callable:
        @callback
        def _fire(_now) -> None:
            profile = self.entry.runtime_data.get_profile(profile_id)
            if profile is None or not profile.enabled:
                return
            self.hass.async_create_task(
                async_apply_profile(self.entry, profile, force=False),
                f"apply profile {profile_id}",
            )

        return _fire

    @callback
    def _resubscribe_state(self) -> None:
        ids: set[str] = set()
        for profile in self.entry.runtime_data.profiles:
            for key, domain in (
                (KEY_PROFILE_ENABLED, "switch"),
                (KEY_PROFILE_TIME, "time"),
            ):
                if eid := resolve_profile_entity(
                    self.hass, self.entry.entry_id, profile.id, key, domain
                ):
                    ids.add(eid)
        frozen = frozenset(ids)
        if frozen == self._tracked:
            return
        self._tracked = frozen
        if self._state_unsub:
            self._state_unsub()
            self._state_unsub = None
        if frozen:
            self._state_unsub = async_track_state_change_event(
                self.hass, list(frozen), self._on_entity_change
            )

    @callback
    def _on_entity_change(self, event: Event[EventStateChangedData]) -> None:
        self._reschedule()
