"""The ITRA integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_RUNNER_URL,
    CONF_UPDATE_INTERVAL,
    CONF_USER_AGENT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .coordinator import ItraDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ITRA from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Merge options on top of data so that options-flow changes take effect
    config = {**entry.data, **entry.options}

    runner_url: str = config[CONF_RUNNER_URL]
    update_interval: int = config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    user_agent: str = config.get(CONF_USER_AGENT, "")

    coordinator = ItraDataUpdateCoordinator(
        hass=hass,
        runner_url=runner_url,
        update_interval_seconds=update_interval,
        user_agent=user_agent,
    )

    # Perform the first refresh; raises ConfigEntryNotReady on failure so HA
    # will automatically retry with exponential back-off.
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Re-initialise the coordinator when options change
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options updates by reloading the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
