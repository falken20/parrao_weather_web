import requests
import os
import sys
import json

from src.logger import Log, console


# Weather station API data
STATION_ID = os.environ.get('STATION_ID')
API_KEY = os.environ.get('API_KEY')
URL_WEATHER_CURRENT = f"https://api.weather.com/v2/pws/observations/current?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY}"

URL_WEATHER_DAY = f"https://api.weather.com/v2/pws/observations/all/1day?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY}"

URL_WEATHER_HISTORY = f"https://api.weather.com/v2/pws/history/daily?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY}" \
    f"&date="




def get_weather_data(url=URL_WEATHER_CURRENT):
    """ Process to get current weather data  """
    Log.info(f'Getting weather data...')

    try:
        # Getting a dataframe with the all data weather
        response = requests.get(url)
        dict_weather = json.loads(response.text)

        Log.debug(
            f'Weather data JSON: \n {dict_weather}')

        return dict_weather["observations"][0]
    except Exception as err:
        Log.error(
            f'ERROR getting weather data at line {sys.exc_info()[2].tb_lineno}: {err}')
        return None