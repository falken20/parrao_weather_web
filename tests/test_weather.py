import pytest
from unittest.mock import patch, MagicMock
from src import weather, web
from src import logger

from src.config import (URL_SUNRISE_SUNSET, URL_WEATHER_ECOWITT_CURRENT,
                        URL_WEATHER_WUNDERGROUND_CURRENT, URL_WEATHER_WUNDERGROUND_DAY, URL_WEATHER_ECOWITT_HISTOY)


@pytest.mark.performance
def test_get_summary_data():
    """Performance test: measures execution time of get_summary_data with caching.
    
    This test uses timeit to measure cache effectiveness by running the function
    multiple times. It's marked as a performance test and can be skipped in regular
    test runs using: pytest -m "not performance"
    """
    # Test the time for getting data from url using timeit.repeat
    from timeit import repeat

    setup_code = "from src import weather, web"
    stmt = "weather.get_summary_data(web.URL_WEATHER_ECOWITT_HISTOY)"
    times = repeat(setup=setup_code, stmt=stmt, repeat=4, number=2)

    logger.Log.debug(f"*** Execution params: -Repeat: 4, - Times: 2")
    logger.Log.debug(f"*** Execution times: {times}")
    logger.Log.debug(f"*** Minimum execution time: {min(times)}")
    
    logger.Log.debug(f"*** Current Cache info: {weather.get_summary_data.cache_info()}")
    # cleaning cache
    weather.get_summary_data.cache_clear()
    logger.Log.debug(f"*** Cleaning Cache info: {weather.get_summary_data.cache_info()}")


@patch("src.weather.get_api_data")
@patch("src.weather.get_month_dates")
@patch("src.weather.get_year_dates")
def test_get_summary_data_logic(mock_get_year_dates, mock_get_month_dates, mock_get_api_data):
    """Test get_summary_data logic with mocked dependencies.
    
    Mock data structure simulates EcoWitt API response with:
    - Temperature: min=10, max=20
    - Humidity: min=30, max=50  
    - Wind speed: min=5, max=15
    - Pressure: min=1000, max=1020
    - UVI: min=1, max=3
    - Rainfall: yearly total=100
    """
    # Mocking the dependencies
    mock_get_month_dates.return_value = ("20230101", "20230131")
    mock_get_year_dates.return_value = ("20230101", "20231231")
    # Mock API response structure matching EcoWitt format
    mock_get_api_data.return_value = {
        "data": {
            "outdoor": {"temperature": {"list": {"1": "10", "2": "20"}}, 
                        "humidity": {"list": {"1": "30", "2": "50"}}},
            "wind": {"wind_speed": {"list": {"1": "5", "2": "15"}}},
            "pressure": {"relative": {"list": {"1": "1000", "2": "1020"}}},
            "solar_and_uvi": {"uvi": {"list": {"1": "1", "2": "3"}}},
            "rainfall": {"yearly": {"list": {"1": "100", "2": "200"}}},
        }
    }

    # Call the function
    url = URL_WEATHER_ECOWITT_HISTOY + "&start_date=20230101&end_date=20230131"
    logger.Log.debug(f"*** Calling get_summary_data with URL: \n{url}")
    result = weather.get_summary_data(url)
    logger.Log.debug(f"*** Result: \n{result}")

    # Assertions
    assert "temperature" in result[0]
    assert result[0]["temperature"]["min"] == 10.0
    assert result[0]["temperature"]["max"] == 20.0
    assert "rainfall" in result[0]
    assert result[0]["rainfall"] == 100.0


def test_get_min_max():
    # Test the get_min_max function
    data = {"1": "10", "2": "20", "3": "15"}
    result = weather.get_min_max(data)

    assert result["min"] == 10.0
    assert result["max"] == 20.0


def test_get_summary_empty_data():
    # Test get_summary with empty data
    data = {"data": {}}
    result = weather.get_summary(data)

    assert result["temperature"] == "-"
    assert result["wind"] == "-"
    assert result["humidity"] == "-"
    assert result["pressure"] == "-"
    assert result["uvi"] == "-"
    assert result["rainfall"] == "-"


@patch("src.weather.get_min_max")
def test_get_summary(mock_get_min_max):
    # Test get_summary with valid data
    mock_get_min_max.side_effect = [
        {"min": 10, "max": 20},
        {"min": 5, "max": 15},
        {"min": 30, "max": 50},
        {"min": 1000, "max": 1020},
        {"min": 1, "max": 3},
        {"min": 100, "max": 200},
    ]

    data = {
        "data": {
            "outdoor": {"temperature": {"list": {"1": "10", "2": "20"}}, 
                        "humidity": {"list": {"1": "30", "2": "50"}}},
            "wind": {"wind_speed": {"list": {"1": "5", "2": "15"}}},
            "pressure": {"relative": {"list": {"1": "1000", "2": "1020"}}},
            "solar_and_uvi": {"uvi": {"list": {"1": "1", "2": "3"}}},
            "rainfall": {"yearly": {"list": {"1": "100", "2": "200"}}},
        }
    }

    result = weather.get_summary(data)

    assert result["temperature"]["min"] == 10
    assert result["temperature"]["max"] == 20
    assert result["rainfall"] == 100
