"""Constants for the TSUN Monitoring integration."""

DOMAIN = "tsun_monitoring"

API_BASE_URL = "https://pro.talent-monitoring.com"
API_AUTH_URL = f"{API_BASE_URL}/oauth2-s/oauth/token"
API_STATION_URL = f"{API_BASE_URL}/station-s/station/query/list"
API_STATION_HISTORY_DAY_URL = (
	f"{API_BASE_URL}/station-s/station/statistic/history/day"
)
API_WEATHER_DAY_URL = f"{API_BASE_URL}/dict-s/weather/record/day"
API_STATION_STATUS_COUNT_URL = f"{API_BASE_URL}/station-s/station/query/status/count"
API_STATION_MANAGE_URL = f"{API_BASE_URL}/station-s/station/manage"
API_STATION_ENERGY_SAVED_URL = f"{API_BASE_URL}/station-s/station/statistic/energy-saved"
API_STATION_CURRENT_FLOW_URL = (
	f"{API_BASE_URL}/station-s/station/statistic/current/flow"
)
API_STATION_SCENE_URL = f"{API_BASE_URL}/station-s/station/manage/getStationScene"
API_STATION_ALERT_LIST_URL = f"{API_BASE_URL}/station-s/station/alert/list"

CLIENT_ID = "sdl_client"
IDENTITY_TYPE = "2"
SYSTEM = "TSUN"
