# by Richi Rod AKA @richionline / falken20
#
# REST API endpoints. Add new routes here as the API grows.

import sys
import os
from datetime import datetime

from flask import Blueprint, jsonify, request

from src.logger import Log
from src.weather import get_api_data
from src.config import URL_WEATHER_ECOWITT_CURRENT


api_bp = Blueprint("api", __name__, url_prefix="/api")

# Cache for daily rain status
_rain_cache = {"date": None, "rained_today": None}
API_ACCESS_KEY = os.environ.get("API_ACCESS_KEY", "")


@api_bp.route("/rain-today")
def rain_today():
    """Return whether it has rained today based on EcoWitt daily rainfall.

    Caches the result for the current day to avoid repeated API calls.
    """
    try:
        if API_ACCESS_KEY and request.headers.get("X-API-Key") != API_ACCESS_KEY:
            return jsonify({"error": "Unauthorized"}), 401

        today = datetime.today().strftime('%Y%m%d')

        # Check if we have a cached result for today
        if _rain_cache["date"] == today and _rain_cache["rained_today"] is not None:
            Log.info(f"Returning cached rain status for {today}")
            return jsonify({"rained_today": _rain_cache["rained_today"]}), 200

        Log.info("Getting rain status for today...")
        weather_data = get_api_data(URL_WEATHER_ECOWITT_CURRENT)
        rainfall_daily = float(weather_data["data"]["rainfall"]["daily"]["value"])
        rained_today = rainfall_daily > 0

        # Cache the result for today
        _rain_cache["date"] = today
        _rain_cache["rained_today"] = rained_today

        return jsonify({"rained_today": rained_today}), 200
    except KeyError as e:
        Log.error(f"KeyError in rain today endpoint: {e}", err=e, sys=sys)
        return jsonify({"error": "Data processing error occurred"}), 500
    except (TypeError, ValueError) as e:
        Log.error(f"ValueError in rain today endpoint: {e}", err=e, sys=sys)
        return jsonify({"error": "Data processing error occurred"}), 500
    except Exception as e:
        Log.error(f"Exception in rain today endpoint: {e}", err=e, sys=sys)
        return jsonify({"error": "Website under maintenance"}), 500
