# by Richi Rod AKA @richionline / falken20

from flask import Flask, render_template, url_for, request, jsonify
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from collections import OrderedDict, deque
from threading import Lock
from time import time
import os
import sys

from src.logger import Log, console
from src.weather import get_api_data, get_summary_data
from src.utils import convert_date, check_cache
from src.api import api_bp
from src.config import (URL_SUNRISE_SUNSET, URL_WEATHER_ECOWITT_CURRENT,
                        URL_WEATHER_WUNDERGROUND_CURRENT, URL_WEATHER_WUNDERGROUND_DAY, URL_WEATHER_ECOWITT_HISTOY,
                        GA_MEASUREMENT_ID)

# Looking for .env file for environment vars
load_dotenv(find_dotenv())

# Block debug mode in production
_is_production = os.environ.get('ENV_PRO', 'N').upper() == 'Y'
if _is_production and os.environ.get('FLASK_DEBUG', '0') == '1':
    raise RuntimeError("FLASK_DEBUG must not be enabled in production (ENV_PRO=Y)")

app = Flask(__name__, template_folder="../templates",
            static_folder="../static")

# Require a secret key for signed cookies / sessions
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key:
    if _is_production:
        raise RuntimeError("FLASK_SECRET_KEY environment variable is required in production")
    app.secret_key = os.urandom(32).hex()
    Log.warning("FLASK_SECRET_KEY not set. Using ephemeral key for non-production only")

# Only auto-reload templates outside production
app.config['TEMPLATES_AUTO_RELOAD'] = not _is_production

# Simple in-memory rate limiter (per-IP + path)
_RATE_LIMITS = {
    "/": (60, 60),
    "/home": (60, 60),
    "/api/rain-today": (30, 60),
}
# Hard cap on tracked (ip, path) keys to prevent unbounded memory growth from
# spoofed clients or large numbers of distinct IPs. Oldest entries are evicted.
_RATE_LIMIT_MAX_KEYS = int(os.environ.get("RATE_LIMIT_MAX_KEYS", "10000"))
# Only honor X-Forwarded-For when running behind a trusted proxy. Otherwise the
# header is attacker-controlled and can be used to inflate the key space or
# bypass per-IP rate limits.
_TRUST_PROXY = os.environ.get("TRUST_PROXY", "N").upper() == "Y"
# Optional allowlist of proxy IPs that are allowed to set X-Forwarded-For.
# When set, the header is only honored if request.remote_addr matches one of
# these IPs. This prevents spoofing when the app is also reachable directly.
_TRUSTED_PROXIES = {
    ip.strip()
    for ip in os.environ.get("TRUSTED_PROXIES", "").split(",")
    if ip.strip()
}
_request_history = OrderedDict()
_rate_limit_lock = Lock()


def _client_ip():
    if _TRUST_PROXY:
        # If an allowlist is configured, only trust the header when the direct
        # peer is one of the declared proxies. Otherwise fall back to the
        # direct peer address.
        if not _TRUSTED_PROXIES or request.remote_addr in _TRUSTED_PROXIES:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                # Take the left-most entry (the original client). Only safe
                # because we have validated the request came from a trusted
                # proxy; otherwise this value is attacker-controlled.
                return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


@app.before_request
def enforce_request_policy():
    # Block state-changing methods by default (app is read-only)
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        return jsonify({"error": "Method not allowed"}), 405

    if request.endpoint == "static":
        return None

    max_requests, window_seconds = _RATE_LIMITS.get(request.path, (120, 60))
    key = (_client_ip(), request.path)
    now = time()

    with _rate_limit_lock:
        timestamps = _request_history.get(key)
        if timestamps is None:
            timestamps = deque()
            _request_history[key] = timestamps
        else:
            # Mark this key as most-recently-used for LRU eviction.
            _request_history.move_to_end(key)

        while timestamps and timestamps[0] <= now - window_seconds:
            timestamps.popleft()

        if len(timestamps) >= max_requests:
            if not timestamps:
                _request_history.pop(key, None)
            return jsonify({"error": "Too many requests"}), 429

        timestamps.append(now)

        # Defensive cleanup: drop empty deques and enforce a hard cap on the
        # number of tracked keys (LRU eviction) so spoofed IPs cannot exhaust
        # memory.
        while len(_request_history) > _RATE_LIMIT_MAX_KEYS:
            _request_history.popitem(last=False)

    return None


# Register REST API blueprint
app.register_blueprint(api_bp)


@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com "
        "https://cdn.jsdelivr.net https://www.googletagmanager.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self' https://www.google-analytics.com; "
        "object-src 'none'; base-uri 'self'"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), camera=(), microphone=()'
    if _is_production:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


# Cache info
get_summary_data.cache_clear()
console.print(f"CACHE: {get_summary_data.cache_info()}", style="yelloW")

console.rule("Cercedilla Weather Web")


def transform_sun_time(data: dict, today: str) -> dict:
    """Transform sunrise/sunset time in UTC format to CEST.

    Args:
        data (dict): Struct from API data
        today (str): Today date

    Returns:
        dict: Struct with dates in CEST format
    """
    results = data.get("results")
    if not isinstance(results, dict):
        raise KeyError("results")

    sunrise = results.get("sunrise")
    sunset = results.get("sunset")
    if sunrise is None or sunset is None:
        raise KeyError("sunrise/sunset")

    Log.info(f"Dictionary dates: {data}")
    # Set "%Y%m%d %I:%M:%S %p" format
    sunrise_date_str = f"{today} {sunrise}"
    sunset_date_str = f"{today} {sunset}"
    Log.info(f"Dates to transform: {sunrise_date_str} - {sunset_date_str}")

    date_format = "%Y%m%d %I:%M:%S %p"
    sunrise_date = convert_date(
        sunrise_date_str, "UTC", "Europe/Madrid", date_format)
    sunset_date = convert_date(
        sunset_date_str, "UTC", "Europe/Madrid", date_format)

    # Update time fields with the CEST time
    results["sunrise"] = datetime.strftime(sunrise_date, "%H:%M:%S")
    results["sunset"] = datetime.strftime(sunset_date, "%H:%M:%S")

    return data


@app.route("/")
@app.route("/home")
def home():
    try:
        Log.info("Access to home page")
        url_for('static', filename='main.css')

        today = datetime.today().strftime('%Y%m%d')

        # For Weather Underground API data
        Log.info("Getting weather Wunderground current...")
        weather_current = get_api_data(URL_WEATHER_WUNDERGROUND_CURRENT)
        Log.info("Getting weather Wunderground day...")
        weather_day = get_api_data(URL_WEATHER_WUNDERGROUND_DAY)

        # For EcoWitt API data
        Log.info("Getting weather Ecowitt current...")
        weather_data = get_api_data(URL_WEATHER_ECOWITT_CURRENT)

        # For SunSet-Sunrise API data
        Log.info("Getting sunrise-sunset...")
        sunrise_sunset = get_api_data(URL_SUNRISE_SUNSET)
        # Convert UTC time to CEST time
        sunrise_sunset = transform_sun_time(sunrise_sunset, today)

        # Get summary weather data for month and year
        Log.info("Getting weather Ecowitt history...")
        month_summary, year_summary = get_summary_data(URL_WEATHER_ECOWITT_HISTOY)

        check_cache(minutes=180)

        # Format year summary rain to 2 decimals
        if isinstance(year_summary["rainfall"], float):
            year_summary['rainfall'] = "{:.2f}".format(float(year_summary['rainfall']))

        Log.info_dict("Weather data", weather_data, "DEBUG")

        return render_template("main.html",
                               weather_data=weather_data,
                               sunrise_sunset=sunrise_sunset,
                               weather_current=weather_current["observations"][0],
                               weather_day=weather_day["observations"][0],
                               month_summary=month_summary,
                               year_summary=year_summary,
                               ga_measurement_id=GA_MEASUREMENT_ID)
    except KeyError as e:
        Log.error(f"KeyError in home page: {e}", err=e, sys=sys)
        return render_template("error.html", message="Data processing error occurred"), 500
    except ValueError as e:
        Log.error(f"ValueError in home page: {e}", err=e, sys=sys)
        return render_template("error.html", message="Website under maintenance"), 500
    except Exception as e:
        Log.error(f"Exception in home page: {e}", err=e, sys=sys)
        return render_template("error.html", message="Website under maintenance"), 500
