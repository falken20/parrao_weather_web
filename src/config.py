# by Richi Rod AKA @richionline / falken20
from datetime import datetime
import os


_IS_PRODUCTION = os.environ.get('ENV_PRO', 'N').upper() == 'Y'

# When ENV_PRO=Y and an env var is missing, we transparently fetch the value
# from Google Cloud Secret Manager. Required env vars to enable this:
#   - GCP_PROJECT_ID: target GCP project that owns the secrets.
# The service account running App Engine must have the role
# `roles/secretmanager.secretAccessor` on each secret (or project-wide).
_SECRET_MANAGER_ENABLED = _IS_PRODUCTION and bool(os.environ.get('GCP_PROJECT_ID'))
_SECRET_CACHE: dict = {}
_SECRET_CLIENT = None


def _get_secret_client():
    """Lazily build a Secret Manager client. Imported on demand so the
    dependency is only required in production deployments."""
    global _SECRET_CLIENT
    if _SECRET_CLIENT is None:
        from google.cloud import secretmanager  # type: ignore
        _SECRET_CLIENT = secretmanager.SecretManagerServiceClient()
    return _SECRET_CLIENT


def _fetch_from_secret_manager(name: str) -> str:
    """Fetch the latest version of a secret named `name` from Secret Manager.

    Returns an empty string if the secret cannot be retrieved; callers decide
    whether the value is mandatory.
    """
    project_id = os.environ.get('GCP_PROJECT_ID', '')
    if not project_id:
        return ""
    try:
        client = _get_secret_client()
        secret_path = f"projects/{project_id}/secrets/{name}/versions/latest"
        response = client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8").strip()
    except Exception:
        # Do not leak secret payloads or stack traces here. The caller will
        # raise a generic RuntimeError if the secret is required.
        return ""


def _read_env(name: str, required: bool = False) -> str:
    """Read a configuration value with the following precedence:
      1. Process environment variable (always wins, useful for local/dev).
      2. Google Cloud Secret Manager (only in production with GCP_PROJECT_ID).
    Values are cached in-memory to avoid repeated API calls."""
    if name in _SECRET_CACHE:
        return _SECRET_CACHE[name]

    value = os.environ.get(name, "")
    if not value and _SECRET_MANAGER_ENABLED:
        value = _fetch_from_secret_manager(name)

    if not value and required:
        raise RuntimeError(f"Required configuration value {name!r} is not set")

    _SECRET_CACHE[name] = value
    return value


# Weather Underground API data
STATION_ID = _read_env('STATION_ID', required=_IS_PRODUCTION)
API_KEY_WUNDERGROUND = _read_env('API_KEY_WUNDERGROUND', required=_IS_PRODUCTION)
URL_WEATHER_WUNDERGROUND_CURRENT = f"https://api.weather.com/v2/pws/observations/current?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY_WUNDERGROUND}"
URL_WEATHER_WUNDERGROUND_DAY = f"https://api.weather.com/v2/pws/history/daily?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY_WUNDERGROUND}" \
    f"&date={datetime.today().strftime('%Y%m%d')}"

# Weather EcoWitt API data
API_KEY_ECOWITT = _read_env('API_KEY_ECOWITT', required=_IS_PRODUCTION)
APPLICATION_KEY_ECOWITT = _read_env('APPLICATION_KEY', required=_IS_PRODUCTION)
STATION_MAC = _read_env('STATION_MAC', required=_IS_PRODUCTION)
URL_WEATHER_ECOWITT_CURRENT = f"https://api.ecowitt.net/api/v3/device/real_time?application_key={APPLICATION_KEY_ECOWITT}" \
    f"&api_key={API_KEY_ECOWITT}&mac={STATION_MAC}" \
    f"&temp_unitid=1&pressure_unitid=3&wind_speed_unitid=7&rainfall_unitid=12" \
    f"&call_back=all"
URL_WEATHER_ECOWITT_HISTOY = f"https://api.ecowitt.net/api/v3/device/history?application_key={APPLICATION_KEY_ECOWITT}" \
    f"&api_key={API_KEY_ECOWITT}&mac={STATION_MAC}" \
    f"&temp_unitid=1&pressure_unitid=3&wind_speed_unitid=7&rainfall_unitid=12" \
    f"&call_back=outdoor.temperature,outdoor.humidity,wind.wind_speed,pressure.relative,solar_and_uvi.uvi" \
    f",rainfall.yearly"
#   f"&cycle_type=1day&start_date={date_from} 00:00:00&end_date={date_to} 23:59:59" \

# API by https://sunrise-sunset.org/api
URL_SUNRISE_SUNSET = "https://api.sunrise-sunset.org/json?lat=40.727&lng=-4.074&date=today"

# Optional GA tracking ID for template rendering
GA_MEASUREMENT_ID = _read_env('GA_MEASUREMENT_ID', required=False)
