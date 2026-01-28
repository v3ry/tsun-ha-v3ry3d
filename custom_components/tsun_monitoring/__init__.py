"""The TSUN Monitoring integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .api import TsunMonitoringAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TSUN Monitoring from a config entry."""
    api = TsunMonitoringAPI(
        username=entry.data["username"],
        password=entry.data["password"],
    )

    try:
        await hass.async_add_executor_job(api.authenticate)
    except Exception as err:
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err

    coordinator = TsunMonitoringCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class TsunMonitoringCoordinator(DataUpdateCoordinator):
    """Class to manage fetching TSUN Monitoring data."""

    def __init__(self, hass: HomeAssistant, api: TsunMonitoringAPI) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.hass.async_add_executor_job(self.api.get_stations)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
