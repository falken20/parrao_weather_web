# by Richi Rod AKA @richionline / falken20

import requests
import os
import sys
import json
from datetime import datetime, date

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
        Log.error("Error getting data from API", err, sys)
        return {}


def get_month_dates():
    """Get the first date and the current date for the current month"""
    current_date = datetime.today()
    first_month = date(current_date.year, current_date.month, 1)

    return first_month.strftime('%Y%m%d'), current_date.strftime('%Y%m%d')


def get_year_dates():
    """Get the first date and the current date for the current year"""
    current_date = datetime.today()
    first_year = date(current_date.year, 1, 1)

    return first_year.strftime('%Y%m%d'), current_date.strftime('%Y%m%d')


def get_summary_data(url: str) -> dict:
    """Methos to generate a dict object with all summary data weather for a current month
    and current year.

    Args:
        url (str): URL for getting weather data

    Returns:
        dict: Object with al summary data
    """
    try:
        Log.info("Getting summary data...")

        date_from, date_to = get_month_dates()
        Log.debug(f"Dates for summary month data: {date_from} - {date_to}")
        month_summary = get_api_data(url, date1=date_from, date2=date_to)

        date_from, date_to = get_year_dates()
        Log.debug(f"Dates for summary year data: {date_from} - {date_to}")
        year_summary = get_api_data(url, date1=date_from, date2=date_to)


        return {}

    except Exception as err:
        Log.error("Error calculating summary data", err, sys)
        return {}
