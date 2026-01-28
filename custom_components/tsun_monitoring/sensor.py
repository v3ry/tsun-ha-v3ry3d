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
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES = {
    # Generation sensors
    "generation_power": {
        "name": "Generation Power",
        "key": "generationPower",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "generation_total": {
        "name": "Generation Total",
        "key": "generationTotal",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "generation_value": {
        "name": "Generation Value Daily",
        "key": "generationValue",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "generation_value_month": {
        "name": "Generation Month",
        "key": "generationValueMonth",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "generation_value_year": {
        "name": "Generation Year",
        "key": "generationValueYear",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    # Battery sensors
    "battery_power": {
        "name": "Battery Power",
        "key": "batteryPower",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "battery_soc": {
        "name": "Battery SOC",
        "key": "batterySoc",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "battery_rated_power": {
        "name": "Battery Rated Power",
        "key": "batteryRatedPower",
        "unit": UnitOfPower.KILO_WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": None,
    },
    "battery_rated_capacity": {
        "name": "Battery Rated Capacity",
        "key": "batteryRatedCapacity",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": None,
    },
    "charge_value": {
        "name": "Battery Charge Today",
        "key": "chargeValue",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "discharge_value": {
        "name": "Battery Discharge Today",
        "key": "dischargeValue",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "charge_upload_total": {
        "name": "Battery Charge Total",
        "key": "chargeUploadTotal",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "discharge_upload_total": {
        "name": "Battery Discharge Total",
        "key": "dischargeUploadTotal",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    # Consumption sensors
    "use_power": {
        "name": "Use Power",
        "key": "usePower",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # System sensors
    "installed_capacity": {
        "name": "Installed Capacity",
        "key": "installedCapacity",
        "unit": UnitOfPower.KILO_WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": None,
    },
}

TEXT_SENSOR_TYPES = {
    "network_status": {
        "name": "Network Status",
        "key": "networkStatus",
    },
    "battery_status": {
        "name": "Battery Status",
        "key": "batteryStatus",
    },
    "power_system_type": {
        "name": "Power System Type",
        "key": "powerSystemType",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TSUN Monitoring sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for item in coordinator.data:
        station = item.get("station", {})
        station_id = station.get("id")
        station_name = station.get("name", "Unknown")

        # Add numeric sensors
        for sensor_type, sensor_config in SENSOR_TYPES.items():
            entities.append(
                TsunMonitoringSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                    sensor_config["name"],
                    sensor_config["key"],
                    sensor_config["unit"],
                    sensor_config["device_class"],
                    sensor_config["state_class"],
                )
            )

        # Add text sensors
        for sensor_type, sensor_config in TEXT_SENSOR_TYPES.items():
            entities.append(
                TsunMonitoringTextSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                    sensor_config["name"],
                    sensor_config["key"],
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
        data_key: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._station_name = station_name
        self._sensor_type = sensor_type
        self._data_key = data_key
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
        for item in self.coordinator.data:
            station = item.get("station", {})
            if station.get("id") == self._station_id:
                value = station.get(self._data_key)
                return value if value is not None else 0
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        for item in self.coordinator.data:
            station = item.get("station", {})
            if station.get("id") == self._station_id:
                attrs = {
                    "location": station.get("locationAddress"),
                    "power_type": station.get("powerType"),
                    "geography_type": station.get("geographyType"),
                    "operation_type": station.get("operationType"),
                    "power_system_type": station.get("powerSystemType"),
                    "last_update": station.get("lastUpdateTime"),
                    "operating": station.get("operating"),
                }
                
                if station.get("lastUpdateTime"):
                    try:
                        timestamp = station["lastUpdateTime"]
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
        data_key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._station_name = station_name
        self._sensor_type = sensor_type
        self._data_key = data_key
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
        for item in self.coordinator.data:
            station = item.get("station", {})
            if station.get("id") == self._station_id:
                return station.get(self._data_key, "Unknown")
        return None
