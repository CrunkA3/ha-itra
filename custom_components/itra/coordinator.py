"""Async data coordinator for the ITRA integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_LAST_UPDATED_BY_COORDINATOR,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_USER_AGENT,
    DOMAIN,
)
from .parser import parse_itra_html

_LOGGER = logging.getLogger(__name__)


class ItraDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls the ITRA RunnerSpace page periodically."""

    def __init__(
        self,
        hass: HomeAssistant,
        runner_url: str,
        update_interval_seconds: int = DEFAULT_UPDATE_INTERVAL,
        user_agent: str = "",
    ) -> None:
        """Initialise the coordinator."""
        self.runner_url = runner_url
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self._session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _fetch_html(self) -> str:
        """Download the runner page and return the raw HTML string."""
        headers = {"User-Agent": self.user_agent}
        try:
            async with self._session.get(
                self.runner_url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"ITRA page returned HTTP {response.status} for {self.runner_url}"
                    )
                return await response.text()
        except aiohttp.ClientError as exc:
            raise UpdateFailed(
                f"Network error while fetching {self.runner_url}: {exc}"
            ) from exc

    @staticmethod
    def _parse_html(html: str) -> dict[str, Any]:
        """Delegate to the standalone parser (kept for backwards compatibility in tests)."""
        return parse_itra_html(html)

    # ------------------------------------------------------------------
    # DataUpdateCoordinator hook
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and parse the ITRA page; called by the coordinator framework."""
        _LOGGER.debug("Fetching ITRA data from %s", self.runner_url)
        try:
            html = await self._fetch_html()
        except UpdateFailed:
            raise
        except Exception as exc:  # noqa: BLE001
            raise UpdateFailed(f"Unexpected error fetching ITRA data: {exc}") from exc

        try:
            data = parse_itra_html(html)
        except Exception as exc:  # noqa: BLE001
            raise UpdateFailed(f"Failed to parse ITRA HTML: {exc}") from exc

        data[ATTR_LAST_UPDATED_BY_COORDINATOR] = datetime.now(tz=timezone.utc).isoformat()
        _LOGGER.debug(
            "ITRA data updated: level_count=%s, level=%s",
            data["level_count"],
            data["level"],
        )
        return data
