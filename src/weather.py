# by Richi Rod AKA @richionline / falken20

import requests
import sys
import json
from datetime import datetime, date
from functools import lru_cache

from src.logger import Log
# from .utils import timed_lru_cache


def get_api_data(url: str, cycle_type: str = "1day", date1=None, date2=None):
    """ Process to get current weather data  """
    Log.info(f'Getting weather data ({date1} - {date2})...')

    # Check if date params have data
    date_from = date1 if date1 else None
    date_to = date2 if date2 else None
    if date_from and date_to:  # Calling to API EcoWitt history
        url += f"&cycle_type={cycle_type}&start_date={date_from} 00:00:00&end_date={date_to} 23:59:59"
    Log.debug(f"URL: {url}")

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


@lru_cache(maxsize=5)
# @timed_lru_cache(seconds=5, maxsize=4) # Personal decorator in utils.py it extends from @lru_cache
def get_summary_data(url: str) -> dict:
    """Method to generate a dict object with all summary data weather for a current month
    and current year.

    Args:
        url (str): URL for getting weather data

    Returns:
        dict: Object with al summary data
    """
    try:
        Log.info("Getting summary data for current month and current year...")

        date_from, date_to = get_month_dates()
        Log.debug(f"Dates for summary month data: {date_from} - {date_to}")
        month_summary = get_api_data(
            url, cycle_type="4hour", date1=date_from, date2=date_to)
        month_summary = get_summary(month_summary)

        date_from, date_to = get_year_dates()
        Log.debug(f"Dates for summary year data: {date_from} - {date_to}")
        year_summary = get_api_data(
            url, cycle_type="1day", date1=date_from, date2=date_to)
        year_summary = get_summary(year_summary)

        return month_summary, year_summary

    except Exception as err:
        Log.error("Error calculating summary data", err, sys)
        return {}


def get_summary(data: dict) -> dict:
    """Method to get the min and max data for the information in data

    Args:
        data (dict): Weather data

    Returns:
        dict: Weather data calculated
    """
    try:
        Log.info("Getting summary for data...")
        data_summary = dict()
        data_summary["temperature"] = get_min_max(
            data["data"]["outdoor"]["temperature"]["list"])
        data_summary["wind"] = get_min_max(
            data["data"]["wind"]["wind_speed"]["list"])
        data_summary["humidity"] = get_min_max(
            data["data"]["outdoor"]["humidity"]["list"])
        data_summary["pressure"] = get_min_max(
            data["data"]["pressure"]["relative"]["list"])
        data_summary["uvi"] = get_min_max(
            data["data"]["solar_and_uvi"]["uvi"]["list"])

        return data_summary

    except Exception as err:
        Log.error("Error getting summary data", err, sys)
        return {}


def get_min_max(data: dict) -> dict:
    """Method to get the min and max for a certain param like temperature, wind, etc

    Args:
        data (dict): Dict of data

    Returns:
        dict: Max and min for the data
    """
    try:
        Log.info(f"Calculating Min/Max for data with {len(data)} elements...")
        Log.debug(f"Data: {data}")

        values = [float(x) for x in list(data.values())]
        result = dict(min=min(values), max=max(values))
        # result = dict(min=min(data.values()), max=max(data.values()))
        # result = dict(min='{0:.2f}'.format(min(data.values())), max='{0:.2f}'.format(max(data.values())))

        Log.debug(f"The min and max are: {result}")
        return result

    except Exception as err:
        Log.error("Error calculating max and min", err, sys)
        return {}
