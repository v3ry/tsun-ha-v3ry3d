"""Platform for sensor integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TSUN Monitoring sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for station in coordinator.data:
        station_id = station.get("id")
        station_name = station.get("name", "Unknown")

        # Generation Power (current)
        entities.append(
            TsunMonitoringSensor(
                coordinator,
                station_id,
                station_name,
                "generation_power",
                "Generation Power",
                UnitOfPower.WATT,
                SensorDeviceClass.POWER,
                SensorStateClass.MEASUREMENT,
            )
        )

        # Generation Total (daily)
        entities.append(
            TsunMonitoringSensor(
                coordinator,
                station_id,
                station_name,
                "generation_total",
                "Generation Total",
                UnitOfEnergy.KILO_WATT_HOUR,
                SensorDeviceClass.ENERGY,
                SensorStateClass.TOTAL_INCREASING,
            )
        )

        # Installed Capacity
        entities.append(
            TsunMonitoringSensor(
                coordinator,
                station_id,
                station_name,
                "installed_capacity",
                "Installed Capacity",
                UnitOfPower.KILO_WATT,
                SensorDeviceClass.POWER,
                None,
            )
        )

        # Network Status
        entities.append(
            TsunMonitoringTextSensor(
                coordinator,
                station_id,
                station_name,
                "network_status",
                "Network Status",
            )
        )

    async_add_entities(entities)


class TsunMonitoringSensor(CoordinatorEntity, SensorEntity):
    """Representation of a TSUN Monitoring Sensor."""

    def __init__(
        self,
        coordinator,
        station_id: int,
        station_name: str,
        sensor_type: str,
        sensor_name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._station_name = station_name
        self._sensor_type = sensor_type
        self._attr_name = f"{station_name} {sensor_name}"
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": self._station_name,
            "manufacturer": "TSUN",
            "model": "Solar Station",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        for station in self.coordinator.data:
            if station.get("id") == self._station_id:
                if self._sensor_type == "generation_power":
                    return station.get("generationPower", 0.0)
                elif self._sensor_type == "generation_total":
                    return station.get("generationTotal", 0.0)
                elif self._sensor_type == "installed_capacity":
                    return station.get("installedCapacity", 0.0)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        for station in self.coordinator.data:
            if station.get("id") == self._station_id:
                attrs = {
                    "location": station.get("locationAddress"),
                    "power_type": station.get("powerType"),
                    "geography_type": station.get("geographyType"),
                    "operation_type": station.get("operationType"),
                    "last_update": station.get("lastUpdateTime"),
                }
                
                if station.get("lastUpdateTime"):
                    try:
                        timestamp = station["lastUpdateTime"] / 1000
                        attrs["last_update_formatted"] = datetime.fromtimestamp(
                            timestamp
                        ).isoformat()
                    except (ValueError, TypeError):
                        pass
                        
                return {k: v for k, v in attrs.items() if v is not None}
        return {}


class TsunMonitoringTextSensor(CoordinatorEntity, SensorEntity):
    """Representation of a TSUN Monitoring Text Sensor."""

    def __init__(
        self,
        coordinator,
        station_id: int,
        station_name: str,
        sensor_type: str,
        sensor_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._station_name = station_name
        self._sensor_type = sensor_type
        self._attr_name = f"{station_name} {sensor_name}"
        self._attr_unique_id = f"{station_id}_{sensor_type}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": self._station_name,
            "manufacturer": "TSUN",
            "model": "Solar Station",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        for station in self.coordinator.data:
            if station.get("id") == self._station_id:
                if self._sensor_type == "network_status":
                    return station.get("networkStatus", "Unknown")
        return None
