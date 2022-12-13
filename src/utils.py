# by Richi Rod AKA @richionline / falken20

from dateutil import tz
from functools import lru_cache, wraps
from datetime import datetime, timedelta
import sys

from src.logger import Log
from .weather import get_summary_data

previous_cache = datetime.now()


def convert_date(date: str, from_zone: str = "UTC", to_zone: str = "Europe/Madrid",
                 format_date: str = "%Y%m%d %I:%M:%S %p") -> str:
    """Transform a date into different time zones

    Args:
        date (str): date to transform
        from_zone (str, optional): Time zone from. Defaults to "UTC".
        to_zone (str, optional): Time zone to. Defaults to "CEST".
        format_date (str, optional): Date time format for the date argument

    Returns:
        str: Date transformed
    """
    Log.info(
        f"Method to transform the date {date} from {from_zone} to {to_zone}.")

    from_zone = tz.gettz(from_zone)
    to_zone = tz.gettz(to_zone)

    date = datetime.strptime(date, format_date)
    # Set date to UTC
    date = date.replace(tzinfo=from_zone)
    # Convert to time zone
    date = date.astimezone(to_zone)
    Log.info(f"Date tranformed: {date}")

    return date


# New decorator that extends @lru_cache. If the caller tries to access an item that’s past its lifetime,
# then the cache won’t return its content, forcing the caller to fetch the article from the network.
def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


def check_cache(minutes: int = 60):
    # Cache info:
    # hits is the number of calls that @lru_cache returned directly from memory because they existed in the cache.
    # misses is the number of calls that didn’t come from memory and were computed.
    # maxsize is the size of the cache as you defined it with the maxsize attribute of the decorator.
    # currsize  is the current size of the cache.
    global previous_cache
    Log.info(f"CACHE: {get_summary_data.cache_info()}", style="yelloW")
    Log.info(
        f"Checking expiration time for cache({minutes=})...", style="yellow")
    Log.debug(f"Previous cache: {previous_cache}", style="yellow")
    Log.debug(f"Current time: {datetime.now()}", style="yellow")
    difference = (datetime.now() - previous_cache).seconds / 60
    Log.info(f"Cache span: {int(difference)} minutes", style="yellow")
    if difference > minutes:
        Log.info("Cleaning cache by expiration...", style="yellow")
        get_summary_data.cache_clear()
        previous_cache = datetime.now()
        Log.info(f"CACHE: {get_summary_data.cache_info()}", style="yellow")
