from timeit import repeat

from src import weather, web


def test_get_summary_data():
    # Test the time for getting data from url using timeit.repeat

    setup_code = "from src import weather, web"
    stmt = "weather.get_summary_data(web.URL_WEATHER_ECOWITT_HISTOY)"
    times = repeat(setup=setup_code, stmt=stmt, repeat=3, number=2)

    print(f"\nMinimum execution time: {min(times)}\n{times}")
