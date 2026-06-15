"""Config flow for Gitea Config Sync."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

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
)
from .gitea_client import GiteaApiError, GiteaClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Required(CONF_TOKEN): str,
        vol.Required(CONF_OWNER): str,
        vol.Required(CONF_REPO): str,
        vol.Optional(CONF_BRANCH, default=DEFAULT_BRANCH): str,
    }
)

STEP_PATHS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_INCLUDE_PATHS, default=DEFAULT_INCLUDE_PATHS): str,
        vol.Optional(CONF_EXCLUDE_PATHS, default=DEFAULT_EXCLUDE_PATHS): str,
        vol.Optional(
            CONF_COMMIT_MESSAGE_PREFIX, default=DEFAULT_COMMIT_MESSAGE_PREFIX
        ): str,
    }
)

STEP_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_AUTO_SYNC_INTERVAL, default=DEFAULT_AUTO_SYNC_INTERVAL
        ): vol.All(int, vol.Range(min=0, max=1440)),
        vol.Optional(CONF_SYNC_ON_START, default=DEFAULT_SYNC_ON_START): bool,
        vol.Optional(CONF_WATCH_FILES, default=DEFAULT_WATCH_FILES): bool,
    }
)


class GiteaSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Gitea Config Sync."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                client = GiteaClient(
                    user_input[CONF_URL],
                    user_input[CONF_TOKEN],
                    user_input[CONF_OWNER],
                    user_input[CONF_REPO],
                    user_input.get(CONF_BRANCH, DEFAULT_BRANCH),
                )
                async with aiohttp.ClientSession() as session:
                    await client.test_connection(session)
                self._data.update(user_input)
                return await self.async_step_paths()
            except GiteaApiError as err:
                msg = str(err)
                if "Invalid token" in msg:
                    errors["base"] = "invalid_token"
                elif "Not found" in msg:
                    errors["base"] = "repo_not_found"
                else:
                    errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_paths(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_schedule()

        return self.async_show_form(
            step_id="paths",
            data_schema=STEP_PATHS_SCHEMA,
        )

    async def async_step_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=f"{self._data[CONF_OWNER]}/{self._data[CONF_REPO]}",
                data=self._data,
            )

        return self.async_show_form(
            step_id="schedule",
            data_schema=STEP_SCHEDULE_SCHEMA,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GiteaSyncOptionsFlow(config_entry)


class GiteaSyncOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Gitea Config Sync."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._entry.options or self._entry.data

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_INCLUDE_PATHS,
                    default=current.get(CONF_INCLUDE_PATHS, DEFAULT_INCLUDE_PATHS),
                ): str,
                vol.Optional(
                    CONF_EXCLUDE_PATHS,
                    default=current.get(CONF_EXCLUDE_PATHS, DEFAULT_EXCLUDE_PATHS),
                ): str,
                vol.Optional(
                    CONF_AUTO_SYNC_INTERVAL,
                    default=current.get(CONF_AUTO_SYNC_INTERVAL, DEFAULT_AUTO_SYNC_INTERVAL),
                ): vol.All(int, vol.Range(min=0, max=1440)),
                vol.Optional(
                    CONF_SYNC_ON_START,
                    default=current.get(CONF_SYNC_ON_START, DEFAULT_SYNC_ON_START),
                ): bool,
                vol.Optional(
                    CONF_WATCH_FILES,
                    default=current.get(CONF_WATCH_FILES, DEFAULT_WATCH_FILES),
                ): bool,
                vol.Optional(
                    CONF_COMMIT_MESSAGE_PREFIX,
                    default=current.get(
                        CONF_COMMIT_MESSAGE_PREFIX, DEFAULT_COMMIT_MESSAGE_PREFIX
                    ),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
