"""API client for TSUN Monitoring."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

import requests

from .const import (
    API_AUTH_URL,
    API_STATION_ALERT_LIST_URL,
    API_STATION_CURRENT_FLOW_URL,
    API_STATION_ENERGY_SAVED_URL,
    API_STATION_HISTORY_DAY_URL,
    API_STATION_MANAGE_URL,
    API_STATION_SCENE_URL,
    API_STATION_STATUS_COUNT_URL,
    API_STATION_URL,
    API_WEATHER_DAY_URL,
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

    def _default_headers(self) -> dict[str, str]:
        """Return the common API headers used by the official app."""
        return {
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

    def _authorized_headers(self, content_type: str | None = None) -> dict[str, str]:
        """Return authorization headers with optional content type."""
        headers = self._default_headers()
        if content_type:
            headers["Content-Type"] = content_type
        headers["authorization"] = f"bearer {self.access_token}"
        return headers

    def _request_with_reauth(self, method: str, url: str, **kwargs) -> requests.Response:
        """Perform a request and retry once on unauthorized responses."""
        self._ensure_authenticated()

        headers = kwargs.pop("headers", {})
        if "authorization" not in headers:
            headers = {**headers, "authorization": f"bearer {self.access_token}"}

        response = self.session.request(method, url, headers=headers, timeout=30, **kwargs)

        if response.status_code == 401:
            _LOGGER.info("Access token expired, trying to re-authenticate")
            self.access_token = None
            if not self.refresh_access_token():
                self.authenticate()
            headers["authorization"] = f"bearer {self.access_token}"
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=30,
                **kwargs,
            )

        response.raise_for_status()
        return response

    def authenticate(self) -> bool:
        """Authenticate with the API."""
        headers = self._default_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

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

    def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            return False

        headers = self._default_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
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
            self.refresh_token = json_data.get("refresh_token", self.refresh_token)

            if not self.access_token:
                _LOGGER.warning("Token refresh response did not include access_token")
                return False

            _LOGGER.info("Token refresh successful")
            return True

        except requests.exceptions.RequestException as err:
            _LOGGER.warning("Token refresh failed: %s", err)
            return False

    def _ensure_authenticated(self) -> None:
        """Ensure an access token is available."""
        if self.access_token:
            return

        if self.refresh_access_token():
            return

        self.authenticate()

    def get_stations(self) -> list[dict[str, Any]]:
        """Get all stations data."""
        headers = self._authorized_headers(content_type="application/json")

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
            try:
                station_status_count = self.get_station_status_count()
            except requests.exceptions.RequestException as err:
                _LOGGER.warning("Failed to get station status count: %s", err)
                station_status_count = None

            response = self._request_with_reauth(
                "POST",
                API_STATION_URL,
                headers=headers,
                json=body,
                params=params,
            )

            json_data = response.json()
            stations = json_data.get("data", [])

            for item in stations:
                station = item.get("station", {})
                station_id = station.get("id")
                if not station_id:
                    continue

                if station_status_count is not None:
                    item["station_status_count"] = station_status_count

                try:
                    history_data = self.get_station_history_day(station_id)
                    item["station_history_day"] = history_data.get("stationStatisticDay")
                    item["station_history_power_list"] = history_data.get(
                        "stationStatisticPowerList", []
                    )
                    item["station_history_segment_day"] = history_data.get(
                        "stationStatisticSegmentDay"
                    )
                except requests.exceptions.RequestException as err:
                    _LOGGER.warning(
                        "Failed to get day history for station %s: %s", station_id, err
                    )

                try:
                    region_nation_id = station.get("regionNationId")
                    region_level1 = station.get("regionLevel1")
                    region_level2 = station.get("regionLevel2")
                    if (
                        region_nation_id is not None
                        and region_level1 is not None
                        and region_level2 is not None
                    ):
                        item["weather_day"] = self.get_weather_day(
                            region_nation_id,
                            region_level1,
                            region_level2,
                        )
                except requests.exceptions.RequestException as err:
                    _LOGGER.warning(
                        "Failed to get day weather for station %s: %s", station_id, err
                    )

                try:
                    item["station_manage"] = self.get_station_manage(station_id)
                except requests.exceptions.RequestException as err:
                    _LOGGER.warning(
                        "Failed to get station manage for station %s: %s",
                        station_id,
                        err,
                    )

                try:
                    item["station_energy_saved"] = self.get_station_energy_saved(station_id)
                except requests.exceptions.RequestException as err:
                    _LOGGER.warning(
                        "Failed to get station energy saved for station %s: %s",
                        station_id,
                        err,
                    )

                try:
                    item["station_current_flow"] = self.get_station_current_flow(station_id)
                except requests.exceptions.RequestException as err:
                    _LOGGER.warning(
                        "Failed to get station current flow for station %s: %s",
                        station_id,
                        err,
                    )

                try:
                    item["station_scene"] = self.get_station_scene(station_id)
                except requests.exceptions.RequestException as err:
                    _LOGGER.warning(
                        "Failed to get station scene for station %s: %s", station_id, err
                    )

                try:
                    item["station_alerts"] = self.get_station_alerts(station_id)
                except requests.exceptions.RequestException as err:
                    _LOGGER.warning(
                        "Failed to get station alerts for station %s: %s", station_id, err
                    )

            _LOGGER.info("Retrieved %d stations", len(stations))
            return stations

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get stations: %s", err)
            raise

    def get_station_history_day(self, station_id: int) -> dict[str, Any]:
        """Get station day history used by charts in the official app."""
        now = datetime.now()
        params = {
            "year": f"{now.year:04d}",
            "month": f"{now.month:02d}",
            "day": f"{now.day:02d}",
        }
        headers = self._authorized_headers()

        response = self._request_with_reauth(
            "GET",
            f"{API_STATION_HISTORY_DAY_URL}/{station_id}",
            headers=headers,
            params=params,
        )
        return response.json()

    def get_weather_day(
        self,
        region_nation_id: int,
        region_level1: int,
        region_level2: int,
    ) -> list[dict[str, Any]]:
        """Get day weather forecast used by charts in the official app."""
        now = datetime.now()
        params = {
            "year": f"{now.year:04d}",
            "month": f"{now.month:02d}",
            "day": f"{now.day:02d}",
            "regionNationId": str(region_nation_id),
            "regionLevel1": str(region_level1),
            "regionLevel2": str(region_level2),
            "lan": "fr",
        }
        headers = self._authorized_headers()

        response = self._request_with_reauth(
            "GET",
            API_WEATHER_DAY_URL,
            headers=headers,
            params=params,
        )
        data = response.json()
        return data if isinstance(data, list) else []

    def get_station_status_count(self) -> dict[str, Any]:
        """Get station communication and alert summary counts."""
        headers = self._authorized_headers(content_type="application/json")
        body = {
            "region": {
                "nationId": None,
                "level1": None,
                "level2": None,
                "level3": None,
                "level4": None,
                "level5": None,
            },
            "powerTypeList": None,
        }
        response = self._request_with_reauth(
            "POST",
            API_STATION_STATUS_COUNT_URL,
            headers=headers,
            json=body,
        )
        data = response.json()
        return data if isinstance(data, dict) else {}

    def get_station_manage(self, station_id: int) -> dict[str, Any]:
        """Get station metadata and settings."""
        headers = self._authorized_headers()
        response = self._request_with_reauth(
            "GET",
            f"{API_STATION_MANAGE_URL}/{station_id}",
            headers=headers,
        )
        data = response.json()
        return data if isinstance(data, dict) else {}

    def get_station_energy_saved(self, station_id: int) -> dict[str, Any]:
        """Get station environmental impact metrics."""
        headers = self._authorized_headers()
        response = self._request_with_reauth(
            "GET",
            f"{API_STATION_ENERGY_SAVED_URL}/{station_id}",
            headers=headers,
        )
        data = response.json()
        return data if isinstance(data, dict) else {}

    def get_station_current_flow(self, station_id: int) -> dict[str, Any]:
        """Get current flow data for the selected day."""
        now = datetime.now()
        params = {
            "year": f"{now.year:04d}",
            "month": f"{now.month:02d}",
            "day": f"{now.day:02d}",
        }
        headers = self._authorized_headers()
        response = self._request_with_reauth(
            "GET",
            f"{API_STATION_CURRENT_FLOW_URL}/{station_id}",
            headers=headers,
            params=params,
        )
        data = response.json()
        return data if isinstance(data, dict) else {}

    def get_station_scene(self, station_id: int) -> str | None:
        """Get station scene identifier."""
        headers = self._authorized_headers()
        response = self._request_with_reauth(
            "GET",
            f"{API_STATION_SCENE_URL}/{station_id}",
            headers=headers,
        )
        data = response.text.strip()
        return data or None

    def get_station_alerts(self, station_id: int) -> dict[str, Any]:
        """Get latest station alerts."""
        headers = self._authorized_headers(content_type="application/json")
        params = {
            "page": "1",
            "size": "50",
            "order.direction": "DESC",
            "order.property": "startTime",
        }
        body = {
            "stationIdList": [station_id],
            "alertStatusList": None,
            "alertTypeList": None,
            "startTime": None,
            "endTime": None,
            "word": None,
        }
        response = self._request_with_reauth(
            "POST",
            API_STATION_ALERT_LIST_URL,
            headers=headers,
            params=params,
            json=body,
        )
        data = response.json()
        return data if isinstance(data, dict) else {}
