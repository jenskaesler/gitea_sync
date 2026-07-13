"""Gitea Config Sync – HACS Integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CONF_AUTO_SYNC_INTERVAL,
    CONF_BRANCH,
    CONF_COMMIT_MESSAGE_PREFIX,
    CONF_EXCLUDE_PATHS,
    CONF_INCLUDE_PATHS,
    CONF_OWNER,
    CONF_REPO,
    CONF_SYNC_ON_START,
    CONF_TOKEN,
    CONF_URL,
    CONF_WATCH_FILES,
    DEFAULT_AUTO_SYNC_INTERVAL,
    DEFAULT_BRANCH,
    DEFAULT_COMMIT_MESSAGE_PREFIX,
    DEFAULT_EXCLUDE_PATHS,
    DEFAULT_INCLUDE_PATHS,
    DEFAULT_SYNC_ON_START,
    DEFAULT_WATCH_FILES,
    DOMAIN,
    SERVICE_SYNC_FILE,
    SERVICE_SYNC_NOW,
)
from .coordinator import GiteaSyncCoordinator
from .gitea_client import GiteaClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "button"]
CONFIG_DIR = "/config"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gitea Config Sync from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    data = {**entry.data, **entry.options}

    client = GiteaClient(
        url=data[CONF_URL],
        token=data[CONF_TOKEN],
        owner=data[CONF_OWNER],
        repo=data[CONF_REPO],
        branch=data.get(CONF_BRANCH, DEFAULT_BRANCH),
    )

    include_patterns = [
        p.strip()
        for p in data.get(CONF_INCLUDE_PATHS, DEFAULT_INCLUDE_PATHS).split(",")
        if p.strip()
    ]
    exclude_patterns = [
        p.strip()
        for p in data.get(CONF_EXCLUDE_PATHS, DEFAULT_EXCLUDE_PATHS).split(",")
        if p.strip()
    ]

    coordinator = GiteaSyncCoordinator(
        hass=hass,
        client=client,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        commit_prefix=data.get(CONF_COMMIT_MESSAGE_PREFIX, DEFAULT_COMMIT_MESSAGE_PREFIX),
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # ── Platforms ────────────────────────────────────────────────────────
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # ── Services ─────────────────────────────────────────────────────────
    async def handle_sync_now(call: ServiceCall) -> None:
        await coordinator.sync_now(triggered_by="service")

    async def handle_sync_file(call: ServiceCall) -> None:
        file_path = call.data.get("file_path", "")
        await coordinator.sync_single_file(file_path)

    hass.services.async_register(DOMAIN, SERVICE_SYNC_NOW, handle_sync_now)
    hass.services.async_register(DOMAIN, SERVICE_SYNC_FILE, handle_sync_file)

    # ── Sync on startup ──────────────────────────────────────────────────
    if data.get(CONF_SYNC_ON_START, DEFAULT_SYNC_ON_START):
        hass.async_create_task(coordinator.sync_now(triggered_by="startup"))

    # ── Interval-based sync ───────────────────────────────────────────────
    interval_minutes = int(data.get(CONF_AUTO_SYNC_INTERVAL, DEFAULT_AUTO_SYNC_INTERVAL))
    if interval_minutes > 0:
        async def _auto_sync(_now=None) -> None:
            await coordinator.sync_now(triggered_by=f"interval_{interval_minutes}min")

        cancel_interval = async_track_time_interval(
            hass, _auto_sync, timedelta(minutes=interval_minutes)
        )
        hass.data[DOMAIN][f"{entry.entry_id}_cancel_interval"] = cancel_interval
        _LOGGER.info("Auto-sync scheduled every %d minutes", interval_minutes)

    # ── File watcher ──────────────────────────────────────────────────────
    if data.get(CONF_WATCH_FILES, DEFAULT_WATCH_FILES):
        _setup_file_watcher(hass, coordinator, entry.entry_id)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


def _setup_file_watcher(
    hass: HomeAssistant, coordinator: GiteaSyncCoordinator, entry_id: str
) -> None:
    """Watch /config for changes using watchdog.
    
    IMPORTANT: The watchdog event handler runs in a separate thread.
    We must NEVER call hass.async_create_task() directly from that thread
    as it would raise:
        RuntimeError: calls hass.async_create_task from a thread 
        other than the event loop
    
    Instead we use asyncio.run_coroutine_threadsafe() to safely schedule
    coroutines from the watchdog thread onto the HA event loop.
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        loop = hass.loop  # capture event loop reference in the main thread

        class _Handler(FileSystemEventHandler):
            def __init__(self) -> None:
                self._pending_handle = None

            def _schedule_sync(self) -> None:
                """Schedule a debounced sync from the watchdog thread.
                
                Uses asyncio.run_coroutine_threadsafe() to safely cross
                the thread boundary into the HA event loop.
                """
                # Cancel any pending debounce timer (thread-safe via loop)
                if self._pending_handle is not None:
                    loop.call_soon_threadsafe(self._pending_handle.cancel)

                async def _debounced() -> None:
                    await asyncio.sleep(5)
                    await coordinator.sync_now(triggered_by="file_change")

                # Schedule coroutine safely from watchdog thread onto HA event loop
                future = asyncio.run_coroutine_threadsafe(_debounced(), loop)
                # Store the Future's cancel handle so we can cancel the debounce
                self._pending_handle = future

            def on_modified(self, event) -> None:
                if not event.is_directory:
                    self._schedule_sync()

            def on_created(self, event) -> None:
                if not event.is_directory:
                    self._schedule_sync()

            def on_deleted(self, event) -> None:
                if not event.is_directory:
                    self._schedule_sync()

        observer = Observer()
        observer.schedule(_Handler(), CONFIG_DIR, recursive=True)
        observer.start()
        hass.data[DOMAIN][f"{entry_id}_observer"] = observer
        _LOGGER.info("File watcher started for %s", CONFIG_DIR)

    except ImportError:
        _LOGGER.warning(
            "watchdog library not available — file watching disabled. "
            "Install via: pip install watchdog"
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Stop interval
    cancel_fn = hass.data[DOMAIN].pop(f"{entry.entry_id}_cancel_interval", None)
    if cancel_fn:
        cancel_fn()

    # Stop file watcher gracefully
    observer = hass.data[DOMAIN].pop(f"{entry.entry_id}_observer", None)
    if observer:
        observer.stop()
        observer.join()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update — reload the entry."""
    await hass.config_entries.async_reload(entry.entry_id)
