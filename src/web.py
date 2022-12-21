# by Richi Rod AKA @richionline / falken20

from flask import Flask, render_template, url_for
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

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
    """Transform time in UTC format from dict obj to CEST format

    Args:
        data (dict): Struct from API data
        today (str): Today date

    Returns:
        _type_: Struct with dates in CEST formar
    """
    Log.info(f"Dictionary dates: {data}")
    # Set "%Y%m%d %I:%M:%S %p" format
    sunrise_date = f"{today} {data['results']['sunrise']}"
    sunset_date = f"{today} {data['results']['sunset']}"
    Log.info(f"Dates to transform: {sunrise_date} - {sunset_date}")

    sunrise_date = convert_date(
        sunrise_date, "UTC", "Europe/Madrid", "%Y%m%d %I:%M:%S %p")
    sunset_date = convert_date(
        sunset_date, "UTC", "Europe/Madrid", "%Y%m%d %I:%M:%S %p")

    # Update time fields with the CEST time
    data['results']['sunrise'] = datetime.strftime(sunrise_date, "%H:%M:%S")
    data['results']['sunset'] = datetime.strftime(sunset_date, "%H:%M:%S")

    return data


@app.route("/")
@app.route("/home")
def home():
    Log.info("Access to home page")
    url_for('static', filename='main.css')

    today = datetime.today().strftime('%Y%m%d')

    # For Weather Underground API data
    weather_current = get_api_data(URL_WEATHER_WUNDERGROUND_CURRENT)
    weather_day = get_api_data(URL_WEATHER_WUNDERGROUND_DAY)

    # For EcoWitt API data
    weather_data = get_api_data(URL_WEATHER_ECOWITT_CURRENT)

    # For SunSet-Sunrise API data
    sunrise_sunset = get_api_data(URL_SUNRISE_SUNSET)
    # Convert UTC time to CEST time
    sunrise_sunset = transform_sun_time(sunrise_sunset, today)

    # Get summary weather data for month and year
    month_summary, year_summary = get_summary_data(URL_WEATHER_ECOWITT_HISTOY)

    check_cache(minutes=180)

    return render_template("main.html",
                           weather_data=weather_data,
                           sunrise_sunset=sunrise_sunset,
                           weather_current=weather_current["observations"][0],
                           weather_day=weather_day["observations"][0],
                           month_summary=month_summary,
                           year_summary=year_summary)
