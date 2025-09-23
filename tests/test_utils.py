import unittest
from unittest.mock import patch
from io import StringIO
import sys
import time
from datetime import datetime, timedelta

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

    # @patch('sys.stdin', StringIO('Writing...\n'))  # Simulate user input
    @patch('sys.stderr', new_callable=StringIO)
    @patch('sys.stdout', new_callable=StringIO)
    def test_convert_date(self, stdout, stderr):
        utils.convert_date("20220101 11:59:00 PM")
        print("Prueba de stdout")
        print(stdout.getvalue())
        print(stderr.getvalue())
        self.assertIn("", stdout.getvalue())

    def test_convert_date_format(self):
        captured_output = redirect_stdout()
        utils.convert_date("20220101 11:59:00", format_date='%Y%m%d %I:%M:%S')
        redirect_reset()
        self.assertIn("", captured_output.getvalue())

    def test_check_cache(self):
        captured_output = redirect_stdout()
        ret = utils.check_cache(minutes=1)
        redirect_reset()
        print(captured_output.getvalue())

    @patch("src.weather.get_summary_data")
    def test_check_cache_expiration(self, mock_get_summary_data):
        # Mock the cache info and simulate expiration
        mock_get_summary_data.cache_info.return_value = "Cache Info Mocked"
        utils.previous_cache = datetime.now() - timedelta(minutes=62)
        captured_output = redirect_stdout()
        utils.check_cache(minutes=1)
        redirect_reset()
        output = captured_output.getvalue()
        self.assertIn("Cleaning cache by expiration", output)

    def test_timed_lru_cache_basic_functionality(self):
        """Test that timed_lru_cache decorator works for basic caching"""
        call_count = 0
        
        @utils.timed_lru_cache(seconds=60)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute the function
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call with same argument should use cache
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increment

    def test_timed_lru_cache_different_args(self):
        """Test that different arguments create separate cache entries"""
        call_count = 0
        
        @utils.timed_lru_cache(seconds=60)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = test_function(5)
        result2 = test_function(10)
        
        self.assertEqual(result1, 10)
        self.assertEqual(result2, 20)
        self.assertEqual(call_count, 2)  # Two different calls

    @patch('src.utils.datetime')
    def test_timed_lru_cache_expiration(self, mock_datetime):
        """Test that cache expires after the specified time"""
        call_count = 0
        
        # Mock initial time
        initial_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = initial_time
        
        @utils.timed_lru_cache(seconds=30)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call within time limit - should use cache
        mock_datetime.utcnow.return_value = initial_time + timedelta(seconds=20)
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)
        
        # Third call after expiration - should execute function again
        mock_datetime.utcnow.return_value = initial_time + timedelta(seconds=35)
        result3 = test_function(5)
        self.assertEqual(result3, 10)
        self.assertEqual(call_count, 2)

    @patch('src.utils.datetime')
    def test_timed_lru_cache_multiple_expirations(self, mock_datetime):
        """Test multiple cache expirations work correctly"""
        call_count = 0
        
        initial_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = initial_time
        
        @utils.timed_lru_cache(seconds=10)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        test_function(5)
        self.assertEqual(call_count, 1)
        
        # Expire cache and call again
        mock_datetime.utcnow.return_value = initial_time + timedelta(seconds=15)
        test_function(5)
        self.assertEqual(call_count, 2)
        
        # Expire cache again and call
        mock_datetime.utcnow.return_value = initial_time + timedelta(seconds=30)
        test_function(5)
        self.assertEqual(call_count, 3)

    def test_timed_lru_cache_maxsize_parameter(self):
        """Test that maxsize parameter is properly handled"""
        call_count = 0
        
        @utils.timed_lru_cache(seconds=60, maxsize=2)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Fill cache with 2 items
        test_function(1)
        test_function(2)
        self.assertEqual(call_count, 2)
        
        # Access cached items
        test_function(1)
        test_function(2)
        self.assertEqual(call_count, 2)
        
        # Add third item, should evict oldest
        test_function(3)
        self.assertEqual(call_count, 3)
        
        # Access first item again, should be recomputed
        test_function(1)
        self.assertEqual(call_count, 4)

    def test_timed_lru_cache_with_kwargs(self):
        """Test that the decorator works with functions that have keyword arguments"""
        call_count = 0
        
        @utils.timed_lru_cache(seconds=60)
        def test_function(x, y=1):
            nonlocal call_count
            call_count += 1
            return x * y
        
        result1 = test_function(5, y=2)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Same call should use cache
        result2 = test_function(5, y=2)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)
        
        # Different kwargs should create new cache entry
        result3 = test_function(5, y=3)
        self.assertEqual(result3, 15)
        self.assertEqual(call_count, 2)

    @patch('src.utils.datetime')
    def test_timed_lru_cache_preserves_function_metadata(self, mock_datetime):
        """Test that the decorator preserves original function metadata"""
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        
        @utils.timed_lru_cache(seconds=60)
        def test_function(x):
            """Test function docstring"""
            return x * 2
        
        self.assertEqual(test_function.__name__, 'test_function')
        self.assertEqual(test_function.__doc__, 'Test function docstring')

    def test_timed_lru_cache_default_parameters(self):
        """Test that default parameters work correctly"""
        call_count = 0
        
        @utils.timed_lru_cache(30)  # Only seconds specified
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Should work with default maxsize
        result = test_function(5)
        self.assertEqual(result, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result = test_function(5)
        self.assertEqual(result, 10)
        self.assertEqual(call_count, 1)



if __name__ == '__main__':
    unittest.main()
