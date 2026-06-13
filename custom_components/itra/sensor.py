"""Sensor platform for the ITRA integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_LAST_UPDATED_BY_COORDINATOR,
    ATTR_RAW_HTML_SNIPPET,
    CONF_RUNNER_URL,
    DOMAIN,
    SENSOR_LEVEL_COUNT,
    SENSOR_PERFORMANCE_LEVEL,
)
from .coordinator import ItraDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ITRA sensors from a config entry."""
    coordinator: ItraDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            ItraLevelCountSensor(coordinator, entry),
            ItraPerformanceLevelSensor(coordinator, entry),
        ]
    )


class _ItraBaseSensor(CoordinatorEntity[ItraDataUpdateCoordinator], SensorEntity):
    """Base class shared by both ITRA sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ItraDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        translation_key: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_key = sensor_key
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_translation_key = translation_key
        self._attr_icon = icon

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information to group both sensors under one device."""
        runner_url: str = self._entry.data[CONF_RUNNER_URL]
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"ITRA – {self._entry.title}",
            "manufacturer": "ITRA",
            "model": "RunnerSpace",
            "configuration_url": runner_url,
        }


class ItraLevelCountSensor(_ItraBaseSensor):
    """Sensor reporting the ITRA index (level-count) as an integer."""

    def __init__(
        self,
        coordinator: ItraDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the ITRA index sensor."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            sensor_key=SENSOR_LEVEL_COUNT,
            translation_key="itra_level_count",
            icon="mdi:numeric",
        )

    @property
    def native_value(self) -> int | None:
        """Return the ITRA index value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("level_count")

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return "measurement"


class ItraPerformanceLevelSensor(_ItraBaseSensor):
    """Sensor reporting the ITRA performance level as a string."""

    def __init__(
        self,
        coordinator: ItraDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the performance-level sensor."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            sensor_key=SENSOR_PERFORMANCE_LEVEL,
            translation_key="itra_performance_level",
            icon="mdi:podium",
        )

    @property
    def native_value(self) -> str | None:
        """Return the ITRA performance level string."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("level", "unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if self.coordinator.data is None:
            return {}
        return {
            ATTR_RAW_HTML_SNIPPET: self.coordinator.data.get(ATTR_RAW_HTML_SNIPPET, ""),
            ATTR_LAST_UPDATED_BY_COORDINATOR: self.coordinator.data.get(
                ATTR_LAST_UPDATED_BY_COORDINATOR
            ),
        }
