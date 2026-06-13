"""Config flow for the ITRA integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_RUNNER_URL,
    CONF_UPDATE_INTERVAL,
    CONF_USER_AGENT,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_USER_AGENT,
    DOMAIN,
    ITRA_RUNNER_URL_PREFIX,
    MIN_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_RUNNER_URL): str,
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            int, vol.Range(min=MIN_UPDATE_INTERVAL)
        ),
        vol.Optional(CONF_USER_AGENT, default=""): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            int, vol.Range(min=MIN_UPDATE_INTERVAL)
        ),
        vol.Optional(CONF_USER_AGENT, default=""): str,
    }
)


def _validate_runner_url(url: str) -> bool:
    """Return True if *url* points to an ITRA RunnerSpace profile."""
    return url.startswith(ITRA_RUNNER_URL_PREFIX) and len(url) > len(
        ITRA_RUNNER_URL_PREFIX
    )


async def _test_connection(session: aiohttp.ClientSession, url: str, user_agent: str) -> bool:
    """Try to reach the ITRA page; return True on HTTP 200."""
    headers = {"User-Agent": user_agent or DEFAULT_USER_AGENT}
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            return resp.status == 200
    except aiohttp.ClientError as exc:
        _LOGGER.debug("Connection test failed: %s", exc)
        return False


class ItraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the ITRA config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            runner_url: str = user_input[CONF_RUNNER_URL].strip().rstrip("/")
            user_input[CONF_RUNNER_URL] = runner_url

            if not _validate_runner_url(runner_url):
                errors[CONF_RUNNER_URL] = "invalid_url"
            else:
                # Deduplicate by URL
                await self.async_set_unique_id(runner_url)
                self._abort_if_unique_id_configured()

                # Test connectivity
                session = async_get_clientsession(self.hass)
                user_agent = user_input.get(CONF_USER_AGENT, "")
                reachable = await _test_connection(session, runner_url, user_agent)
                if not reachable:
                    errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(
                    title=runner_url.removeprefix(ITRA_RUNNER_URL_PREFIX),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> ItraOptionsFlow:
        """Return the options flow handler."""
        return ItraOptionsFlow(config_entry)


class ItraOptionsFlow(config_entries.OptionsFlow):
    """Handle ITRA options (re-configure interval and user-agent)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options or self._config_entry.data
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=current.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                ): vol.All(int, vol.Range(min=MIN_UPDATE_INTERVAL)),
                vol.Optional(
                    CONF_USER_AGENT,
                    default=current.get(CONF_USER_AGENT, ""),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
