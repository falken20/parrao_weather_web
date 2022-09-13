# by Richi Rod AKA @richionline / falken20

import os
from flask import Flask, render_template, url_for
from dotenv import load_dotenv, find_dotenv


from src.logger import Log, console
from src.weather import get_api_data
from src.weather import URL_SUNRISE_SUNSET, URL_WEATHER_ECOWITT_CURRENT, URL_WEATHER_WUNDERGROUND_CURRENT, URL_WEATHER_WUNDERGROUND_DAY

console.rule("Cercedilla Weather Web")

# Looking for .env file for environment vars
load_dotenv(find_dotenv())

app = Flask(__name__, template_folder="../templates",
            static_folder="../static")
# Set this var to True to be able to make any web change and take the changes with refresh
app.config['TEMPLATES_AUTO_RELOAD'] = True


def transform_date(data: dict) -> dict:
    """Transform dates in UTC format from dict obj to CEST format

    Args:
        obj (dict): Struct from API data

    Returns:
        _type_: Struct with dates in CEST formar
    """
    sunrise_date = data["sunrise"]
    sunset_date = data["sunset"]


@app.route("/")
@app.route("/home")
def home():
    Log.info(f"Access to home page")
    url_for('static', filename='main.css')

    # For Weather Underground API data
    weather_current = get_api_data(URL_WEATHER_WUNDERGROUND_CURRENT)
    weather_day = get_api_data(URL_WEATHER_WUNDERGROUND_DAY)

    weather_data = get_api_data(URL_WEATHER_ECOWITT_CURRENT)
    sunrise_sunset = get_api_data(
        URL_SUNRISE_SUNSET)  # TODO: Update to UTC time

    sunrise_sunset = transform_date(sunrise_sunset)

    return render_template("main.html",
                           weather_data=weather_data,
                           sunrise_sunset=sunrise_sunset,
                           weather_current=weather_current["observations"][0],
                           weather_day=weather_day["observations"][0])


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")
