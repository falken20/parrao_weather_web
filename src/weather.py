# by Richi Rod AKA @richionline / falken20

import requests
import os
import sys
import json
from datetime import datetime

from src.logger import Log, console
from src.config import date_from, date_to


def get_api_data(url: str, date1=None, date2=None):
    """ Process to get current weather data  """
    Log.info(f'Getting weather data...')
    Log.debug(f"URL: {url}")

    global date_from, date_to

    date_from = date1 if date1 else datetime.today().strftime('%Y%m%d')
    date_to = date2 if date2 else datetime.today().strftime('%Y%m%d')

    try:
        # Getting a dataframe with the all data weather
        response = requests.get(url)
        dict_weather = json.loads(response.text)

        Log.debug(f'API data JSON: \n {dict_weather}')

        return dict_weather

    except Exception as err:
        Log.error("Erro getting data from API", err, sys)
        return None


def get_resume_data():
    pass
