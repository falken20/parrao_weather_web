from timeit import repeat

from src import weather, web


def test_get_summary_data():
    # Test the time for getting data from url using timeit.repeat

    setup_code = "from src import weather, web"
    stmt = "weather.get_summary_data(web.URL_WEATHER_ECOWITT_HISTOY)"
    times = repeat(setup=setup_code, stmt=stmt, repeat=3, number=2)

    print(f"\nExecution params: -Repeat: 3, - Times: 2")
    print(f"Execution times: {times}")
    print(f"Minimum execution time: {min(times)}")
    print(f"Current Cache info: {weather.get_summary_data.cache_info()}")
    
    # cleaning cache
    weather.get_summary_data.cache_clear()
    print(f"Cleaning Cache info: {weather.get_summary_data.cache_info()}")
