# by Richi Rod AKA @richionline / falken20

import requests
import os
import sys
import json

from src.logger import Log, console


# Weather Underground API data
STATION_ID = os.environ.get('STATION_ID')
API_KEY_WUNDERGROUND = os.environ.get('API_KEY_WUNDERGROUND')
URL_WEATHER_WUNDERGROUND_CURRENT = f"https://api.weather.com/v2/pws/observations/current?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY_WUNDERGROUND}"
URL_WEATHER_WUNDERGROUND_DAY = f"https://api.weather.com/v2/pws/history/daily?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY_WUNDERGROUND}" \
    f"&date=20220913"

 # TODO: Set the date in URL_WEATHER_WUNDERGROUND_DAY in param

# Weather EcoWitt API data
API_KEY_ECOWITT = os.environ.get('API_KEY_ECOWITT')
APPLICATION_KEY_ECOWITT = os.environ.get('APPLICATION_KEY')
STATION_MAC = os.environ.get('STATION_MAC')
URL_WEATHER_ECOWITT_CURRENT = f"https://api.ecowitt.net/api/v3/device/real_time?application_key={APPLICATION_KEY_ECOWITT}" \
    f"&api_key={API_KEY_ECOWITT}&mac={STATION_MAC}" \
    f"&temp_unitid=1&pressure_unitid=3&wind_speed_unitid=7&rainfall_unitid=12" \
    f"&call_back=all"
URL_WEATHER_ECOWITT_HISTOY = f"https://api.ecowitt.net/api/v3/device/history?application_key={APPLICATION_KEY_ECOWITT}" \
    f"&api_key={API_KEY_ECOWITT}&mac={STATION_MAC}&cycle_type=1day" \
    f"&temp_unitid=1&pressure_unitid=3&wind_speed_unitid=7&rainfall_unitid=12" \
    f"&call_back=outdoor.temperature,outdoor.humidity,wind.wind_speed,pressure.relative,solar_and_uvi.uvi" \
    f"&start_date=2022-09-01 00:00:00&end_date=2022-09-15 23:59:59" \
# TODO: Set dates

# API by https://sunrise-sunset.org/api
URL_SUNRISE_SUNSET = "https://api.sunrise-sunset.org/json?lat=40.727&lng=-4.074&date=today"


def get_api_data(url=URL_WEATHER_ECOWITT_CURRENT):
    """ Process to get current weather data  """
    Log.info(f'Getting weather data...')
    Log.debug(f"URL: {url}")

    try:
        # Getting a dataframe with the all data weather
        response = requests.get(url)
        dict_weather = json.loads(response.text)

        Log.debug(f'API data JSON: \n {dict_weather}')

        return dict_weather

    except Exception as err:
        Log.error("Erro getting data from API", err, sys)
        return None
