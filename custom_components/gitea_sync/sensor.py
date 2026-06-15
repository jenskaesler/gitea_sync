"""Sensor platform for Gitea Config Sync."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_FILES_SYNCED,
    ATTR_LAST_COMMIT,
    ATTR_LAST_SYNC,
    ATTR_SYNC_STATUS,
    DOMAIN,
    SYNC_STATUS_IDLE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GiteaSyncSensor(coordinator, entry)])


class GiteaSyncSensor(SensorEntity):
    """Sensor showing the current sync status."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:git"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = "Gitea Sync Status"
        coordinator.register_listener(self._on_update)

    def _on_update(self) -> None:
        self.schedule_update_ha_state()

    @property
    def native_value(self) -> str:
        return self._coordinator.state.get(ATTR_SYNC_STATUS, SYNC_STATUS_IDLE)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            ATTR_LAST_SYNC: self._coordinator.state.get(ATTR_LAST_SYNC),
            ATTR_LAST_COMMIT: self._coordinator.state.get(ATTR_LAST_COMMIT),
            ATTR_FILES_SYNCED: self._coordinator.state.get(ATTR_FILES_SYNCED, 0),
        }

    @property
    def icon(self) -> str:
        status = self.native_value
        return {
            "running": "mdi:sync",
            "success": "mdi:check-circle",
            "failed": "mdi:alert-circle",
        }.get(status, "mdi:git")
