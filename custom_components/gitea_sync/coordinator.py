"""Sync coordinator for Gitea Config Sync."""
from __future__ import annotations

import asyncio
import fnmatch
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp

from .const import (
    ATTR_FILES_SYNCED,
    ATTR_LAST_COMMIT,
    ATTR_LAST_SYNC,
    ATTR_SYNC_STATUS,
    DEFAULT_BRANCH,
    DEFAULT_COMMIT_MESSAGE_PREFIX,
    DEFAULT_EXCLUDE_PATHS,
    DEFAULT_INCLUDE_PATHS,
    SYNC_STATUS_FAILED,
    SYNC_STATUS_IDLE,
    SYNC_STATUS_RUNNING,
    SYNC_STATUS_SUCCESS,
)
from .gitea_client import GiteaClient, GiteaApiError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = "/config"


class GiteaSyncCoordinator:
    """Manages sync between /config and a Gitea repository."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: GiteaClient,
        include_patterns: list[str],
        exclude_patterns: list[str],
        commit_prefix: str = DEFAULT_COMMIT_MESSAGE_PREFIX,
    ) -> None:
        self.hass = hass
        self.client = client
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self.commit_prefix = commit_prefix

        self.state: dict = {
            ATTR_SYNC_STATUS: SYNC_STATUS_IDLE,
            ATTR_LAST_SYNC: None,
            ATTR_LAST_COMMIT: None,
            ATTR_FILES_SYNCED: 0,
        }
        self._listeners: list = []
        self._lock = asyncio.Lock()

    def register_listener(self, callback) -> None:
        self._listeners.append(callback)

    def _notify(self) -> None:
        for cb in self._listeners:
            cb()

    def _matches(self, rel_path: str) -> bool:
        """Return True if rel_path should be synced."""
        for pat in self.exclude_patterns:
            pat = pat.strip()
            if not pat:
                continue
            if fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(
                os.path.basename(rel_path), pat
            ):
                return False
        for pat in self.include_patterns:
            pat = pat.strip()
            if not pat:
                continue
            if fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(
                os.path.basename(rel_path), pat
            ):
                return True
        return False

    def _collect_files(self) -> list[tuple[str, bytes]]:
        """Collect all matching files from /config."""
        result = []
        config_path = Path(CONFIG_DIR)
        for path in config_path.rglob("*"):
            if not path.is_file():
                continue
            rel = str(path.relative_to(config_path))
            if self._matches(rel):
                try:
                    result.append((rel, path.read_bytes()))
                except (OSError, PermissionError) as err:
                    _LOGGER.warning("Cannot read %s: %s", rel, err)
        return result

    async def sync_now(self, triggered_by: str = "manual") -> dict:
        """Push all matching files to Gitea. Returns result dict."""
        if self._lock.locked():
            return {"status": "already_running"}

        async with self._lock:
            self.state[ATTR_SYNC_STATUS] = SYNC_STATUS_RUNNING
            self._notify()

            files_synced = 0
            errors = []

            try:
                files = await self.hass.async_add_executor_job(self._collect_files)
                message = f"{self.commit_prefix}: {triggered_by} ({len(files)} files)"

                async with aiohttp.ClientSession() as session:
                    for rel_path, content in files:
                        try:
                            existing = await self.client.get_file(session, rel_path)
                            sha = existing["sha"] if existing else None

                            # Skip if content unchanged
                            if existing:
                                remote_content = existing.get("content", "").replace("\n", "")
                                import base64
                                remote_bytes = base64.b64decode(remote_content)
                                if remote_bytes == content:
                                    continue

                            await self.client.put_file(
                                session, rel_path, content, message, sha
                            )
                            files_synced += 1
                            _LOGGER.debug("Synced: %s", rel_path)

                        except GiteaApiError as err:
                            _LOGGER.error("Failed to sync %s: %s", rel_path, err)
                            errors.append(str(rel_path))

                    # Get latest commit SHA for state
                    commit = await self.client.get_latest_commit(session)
                    commit_sha = commit["sha"][:7] if commit else None

            except Exception as err:  # noqa: BLE001
                _LOGGER.error("Sync failed: %s", err)
                self.state[ATTR_SYNC_STATUS] = SYNC_STATUS_FAILED
                self._notify()
                return {"status": "failed", "error": str(err)}

            now = datetime.now(timezone.utc).isoformat()
            self.state.update(
                {
                    ATTR_SYNC_STATUS: SYNC_STATUS_SUCCESS if not errors else SYNC_STATUS_FAILED,
                    ATTR_LAST_SYNC: now,
                    ATTR_LAST_COMMIT: commit_sha,
                    ATTR_FILES_SYNCED: files_synced,
                }
            )
            self._notify()

            result = {
                "status": "success" if not errors else "partial",
                "files_synced": files_synced,
                "errors": errors,
                "commit": commit_sha,
                "timestamp": now,
            }
            _LOGGER.info(
                "Sync complete: %d files synced, %d errors", files_synced, len(errors)
            )
            return result

    async def sync_single_file(self, file_path: str) -> dict:
        """Sync a single file to Gitea."""
        abs_path = Path(CONFIG_DIR) / file_path
        if not abs_path.exists():
            return {"status": "failed", "error": "File not found"}

        try:
            content = await self.hass.async_add_executor_job(abs_path.read_bytes)
        except OSError as err:
            return {"status": "failed", "error": str(err)}

        message = f"{self.commit_prefix}: single file sync – {file_path}"
        try:
            async with aiohttp.ClientSession() as session:
                existing = await self.client.get_file(session, file_path)
                sha = existing["sha"] if existing else None
                await self.client.put_file(session, file_path, content, message, sha)
            return {"status": "success", "file": file_path}
        except GiteaApiError as err:
            return {"status": "failed", "error": str(err)}
