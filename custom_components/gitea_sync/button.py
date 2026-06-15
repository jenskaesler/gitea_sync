"""Button platform for Gitea Config Sync."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GiteaSyncNowButton(coordinator, entry)])


class GiteaSyncNowButton(ButtonEntity):
    """Button to trigger an immediate sync."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:upload-network"
    _attr_name = "Jetzt synchronisieren"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_sync_now"

    async def async_press(self) -> None:
        await self._coordinator.sync_now(triggered_by="button")
