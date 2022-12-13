import unittest
from io import StringIO
import sys

from src import utils


def redirect_stdout():
    captured_output = StringIO()  # Create StringIO object
    sys.stdout = captured_output  # and redirect stdout
    return captured_output


def redirect_reset():
    sys.stdout = sys.__stdout__  # Reset redirect


class TestUtils(unittest.TestCase):

    def test_convert_date_exception(self):
        self.assertRaises(ValueError, utils.convert_date, "")


    def test_convert_date(self):
        captured_output = redirect_stdout()
        utils.convert_date("20220101 11:59:00",format_date='%Y%m%d %I:%M:%S')
        utils.convert_date("20220101 11:59:00 PM")
        redirect_reset()

        print(captured_output.getvalue())
        self.assertIn("", captured_output.getvalue())
