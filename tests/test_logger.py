from io import StringIO
import sys
from src import logger
import pytest


def redirect_stdout():
    captured_output = StringIO()  # Create StringIO object
    sys.stdout = captured_output  # and redirect stdout
    return captured_output


def redirect_reset():
    sys.stdout = sys.__stdout__  # Reset redirect


def test_debug():
    logger.LEVEL_LOG = "['DEBUG']"
    trace = "Test Debug"

    captured_output = redirect_stdout()
    logger.Log.debug(trace)
    redirect_reset()

    assert trace in captured_output.getvalue()


def test_debug_no_trace():
    logger.LEVEL_LOG = "[]"
    trace = "Test Debug"

    captured_output = redirect_stdout()
    logger.Log.debug(trace)
    redirect_reset()

    assert trace not in captured_output.getvalue()


def test_info():
    logger.LEVEL_LOG = "['INFO']"
    trace = "Test Info"

    captured_output = redirect_stdout()
    logger.Log.info(trace)
    redirect_reset()

    assert trace in captured_output.getvalue()


def test_info_no_trace():
    logger.LEVEL_LOG = "[]"
    trace = "Test Info"

    captured_output = redirect_stdout()
    logger.Log.info(trace)
    redirect_reset()

    assert trace not in captured_output.getvalue()


def test_warning():
    logger.LEVEL_LOG = "['WARNING']"
    trace = "Test Warning"

    captured_output = redirect_stdout()
    logger.Log.warning(trace)
    redirect_reset()

    assert trace in captured_output.getvalue()


def test_warning_no_trace():
    logger.LEVEL_LOG = "[]"
    trace = "Test Warning"

    captured_output = redirect_stdout()
    logger.Log.warning(trace)
    redirect_reset()

    assert trace not in captured_output.getvalue()


def test_error():
    logger.LEVEL_LOG = "['ERROR']"
    trace = "Test Error"

    try:
        raise(Exception)

    except Exception as err:
        captured_output = redirect_stdout()
        logger.Log.error(trace, err, sys)
        redirect_reset()

        assert trace in captured_output.getvalue()


def test_error_no_trace():
    logger.LEVEL_LOG = "[]"
    trace = "Test Error"

    try:
        raise(Exception)

    except Exception as err:
        captured_output = redirect_stdout()
        logger.Log.error(trace, err, sys)
        redirect_reset()

        assert trace not in captured_output.getvalue()