"""API client for TSUN Monitoring."""
from __future__ import annotations

import logging
from typing import Any

import requests

from .const import (
    API_AUTH_URL,
    API_STATION_URL,
    CLIENT_ID,
    IDENTITY_TYPE,
    SYSTEM,
)

_LOGGER = logging.getLogger(__name__)


class TsunMonitoringAPI:
    """API client for TSUN Monitoring."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate with the API."""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "Host": "pro.talent-monitoring.com",
            "log-channel": "android",
            "log-client-inner-version": "18",
            "log-client-version": "1.0.15",
            "log-lan": "fr",
            "log-platform-code": "TSUN",
            "log-system-version": "9",
            "User-Agent": "okhttp/4.9.3",
        }

        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": CLIENT_ID,
            "identity_type": IDENTITY_TYPE,
            "system": SYSTEM,
        }

        try:
            response = self.session.post(
                API_AUTH_URL,
                headers=headers,
                data=data,
                timeout=30,
            )
            response.raise_for_status()
            
            json_data = response.json()
            self.access_token = json_data.get("access_token")
            self.refresh_token = json_data.get("refresh_token")
            
            _LOGGER.info("Authentication successful")
            return True
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Authentication failed: %s", err)
            raise

    def get_stations(self) -> list[dict[str, Any]]:
        """Get all stations data."""
        if not self.access_token:
            self.authenticate()

        headers = {
            "Accept-Encoding": "gzip",
            "authorization": f"bearer {self.access_token}",
            "Connection": "Keep-Alive",
            "Content-Length": "136",
            "Content-Type": "application/json",
            "Host": "pro.talent-monitoring.com",
            "log-channel": "android",
            "log-client-inner-version": "18",
            "log-client-version": "1.0.15",
            "log-lan": "fr",
            "log-platform-code": "TSUN",
            "log-system-version": "9",
            "User-Agent": "okhttp/4.9.3",
        }

        body = {
            "region": {
                "nationId": None,
                "level1": None,
                "level2": None,
                "level3": None,
                "level4": None,
                "level5": None,
            },
            "returnTag": True,
            "powerTypeList": None,
        }

        params = {
            "order.direction": "ASC",
            "order.property": "name",
            "page": "1",
            "size": "9999",
        }

        try:
            response = self.session.post(
                API_STATION_URL,
                headers=headers,
                json=body,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            
            json_data = response.json()
            stations = json_data.get("data", [])
            
            _LOGGER.info("Retrieved %d stations", len(stations))
            return stations
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get stations: %s", err)
            raise
