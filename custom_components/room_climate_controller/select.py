"""
Select platform: the hub's graph time-range helper.

The dashboard card's energy/history graphs read this entity's state as the number
of hours to show. The integration owns it so a fresh install has a working
time-range selector without the user creating an ``input_select`` helper.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DEFAULT_GRAPH_TIME_RANGE,
    GRAPH_TIME_RANGE_OPTIONS,
    KEY_GRAPH_TIME_RANGE,
)
from .entity import hub_identifier

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .hub import RoomClimateConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: RoomClimateConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the hub-level graph time-range select."""
    async_add_entities([GraphTimeRangeSelect(entry)])


class GraphTimeRangeSelect(SelectEntity, RestoreEntity):
    """Hub-level selector for the number of hours the card's graphs show."""

    _attr_has_entity_name = True
    _attr_name = "Graph time range"
    _attr_icon = "mdi:chart-timeline-variant"
    _attr_options = GRAPH_TIME_RANGE_OPTIONS

    def __init__(self, entry: RoomClimateConfigEntry) -> None:
        """Initialize the select, attached to the hub device."""
        self._attr_unique_id = f"{entry.entry_id}_{KEY_GRAPH_TIME_RANGE}"
        self._attr_current_option = DEFAULT_GRAPH_TIME_RANGE
        self._attr_device_info = DeviceInfo(
            identifiers={hub_identifier(entry.entry_id)}
        )

    async def async_added_to_hass(self) -> None:
        """Restore the last selected option, falling back to the default."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state in self._attr_options:
            self._attr_current_option = last.state

    async def async_select_option(self, option: str) -> None:
        """Update the selected option."""
        old = self._attr_current_option
        self._attr_current_option = option
        self.async_write_ha_state()
        if old != option:
            _LOGGER.info("Graph time range → %s", option)
