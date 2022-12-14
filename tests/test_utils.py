import unittest
from unittest.mock import patch
from io import StringIO
import sys

from src import utils
from src import logger


def redirect_stdout():
    captured_output = StringIO()  # Create StringIO object
    sys.stdout = captured_output  # and redirect stdout
    return captured_output


def redirect_reset():
    sys.stdout = sys.__stdout__  # Reset redirect


class TestUtils(unittest.TestCase):

    def test_convert_date_exception(self):
        self.assertRaises(ValueError, utils.convert_date, "")

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('sys.stdin', StringIO('Writing...\n'))  # Simulate user input
    def test_convert_date(self, stdout, stderr):
        utils.convert_date("20220101 11:59:00 PM")

        print(stdout.getvalue())
        print(stderr.getvalue())
        self.assertIn("", stdout.getvalue())

    def test_convert_date_format(self):
        captured_output = redirect_stdout()
        utils.convert_date("20220101 11:59:00", format_date='%Y%m%d %I:%M:%S')
        redirect_reset()

        print("***", captured_output.getvalue())
        self.assertIn("", captured_output.getvalue())

    def test_check_cache(self):
        ret = utils.check_cache(minutes=1)
        print(f"*** {ret}")


if __name__ == '__main__':
    unittest.main()
