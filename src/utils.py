# by Richi Rod AKA @richionline / falken20

import datetime
from dateutil import tz

from src.logger import Log


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

    date = datetime.datetime.strptime(date, format_date)
    # Set date to UTC
    date = date.replace(tzinfo=from_zone)
    # Convert to time zone
    date = date.astimezone(to_zone)
    Log.info(f"Date tranformed: {date}")

    return date
