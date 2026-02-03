# by Richi Rod AKA @richionline / falken20

from flask import Flask, render_template, url_for
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import sys

from src.logger import Log, console
from src.weather import get_api_data, get_summary_data
from src.utils import convert_date, check_cache
from src.config import (URL_SUNRISE_SUNSET, URL_WEATHER_ECOWITT_CURRENT,
                        URL_WEATHER_WUNDERGROUND_CURRENT, URL_WEATHER_WUNDERGROUND_DAY, URL_WEATHER_ECOWITT_HISTOY)

# Looking for .env file for environment vars
load_dotenv(find_dotenv())

app = Flask(__name__, template_folder="../templates",
            static_folder="../static")
# Set this var to True to be able to make any web change and take the changes with refresh
app.config['TEMPLATES_AUTO_RELOAD'] = True

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
                               year_summary=year_summary)
    except KeyError as e:
        Log.error(f"KeyError in home page: {e}", err=e, sys=sys)
        return render_template("error.html", message="Data processing error occurred"), 500
    except ValueError as e:
        Log.error(f"ValueError in home page: {e}", err=e, sys=sys)
        return render_template("error.html", message="Website under maintenance"), 500
    except Exception as e:
        Log.error(f"Exception in home page: {e}", err=e, sys=sys)
        return render_template("error.html", message="Website under maintenance"), 500
