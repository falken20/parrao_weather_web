import unittest
from unittest.mock import patch
import logging
from collections import deque

logging.basicConfig(level=logging.DEBUG)

from src import web


class TestWeb(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()
        web._request_history.clear()

    @patch("src.web.get_summary_data")
    @patch("src.web.get_api_data")
    def test_home(self, mock_get_api_data, mock_get_summary_data):
        """Test that home page loads successfully"""
        # Mock API responses with complete structure matching EcoWitt API
        def side_effect_get_api_data(url):
            if 'sunrise-sunset' in url:
                return {'results': {'sunrise': '7:00:00 AM', 'sunset': '6:00:00 PM'}}
            elif 'ecowitt' in url:
                return {
                    'data': {
                        'outdoor': {
                            'temperature': {'value': '10', 'unit': '°C'},
                            'humidity': {'value': '50', 'unit': '%'}
                        },
                        'rainfall': {
                            '1_hour': {'value': '0', 'unit': 'mm'},
                            'daily': {'value': '1.5', 'unit': 'mm'},
                            'monthly': {'value': '25.0', 'unit': 'mm'},
                            'yearly': {'value': '500.0', 'unit': 'mm'}
                        },
                        'wind': {
                            'wind_speed': {'value': '5.0', 'unit': 'km/h'}
                        },
                        'pressure': {
                            'relative': {'value': '1013.0', 'unit': 'hPa'}
                        },
                        'solar_and_uvi': {
                            'uvi': {'value': '3', 'unit': ''}
                        }
                    }
                }
            else:
                return {'observations': [{'metric': {'temp': 10, 'tempLow': 5, 'tempHigh': 15}}]}
        
        mock_get_api_data.side_effect = side_effect_get_api_data
        # Mock summary data as tuple with proper structure
        mock_get_summary_data.return_value = (
            {'temperature': {'min': 5, 'max': 15}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0},
            {'temperature': {'min': 0, 'max': 20}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 100.0}
        )
        
        response = self.app.get("/")
        self.assertEqual(200, response.status_code)
        # Verify response contains HTML
        self.assertTrue(len(response.data) > 0)
        self.assertIn(b'html', response.data.lower())

    @patch("src.web.get_api_data")
    def test_home_key_error(self, mock_get_api_data):
        """Test that KeyError is handled gracefully with appropriate error message"""
        # Simulate a KeyError in get_api_data
        mock_get_api_data.side_effect = KeyError("Test KeyError")
        response = self.app.get("/")
        self.assertEqual(500, response.status_code)
        self.assertIn(b"Data processing error occurred", response.data)
        # Verify error template is rendered
        self.assertIn(b"error", response.data.lower())

    @patch("src.web.get_api_data")
    def test_home_value_error(self, mock_get_api_data):
        """Test that ValueError is handled gracefully with maintenance message"""
        # Simulate a ValueError in get_api_data
        mock_get_api_data.side_effect = ValueError("Test ValueError")
        response = self.app.get("/")
        self.assertEqual(500, response.status_code)
        self.assertIn(b"Website under maintenance", response.data)
        # Verify error template is used
        self.assertIn(b"error", response.data.lower())

    @patch("src.web.get_api_data")
    def test_home_generic_exception(self, mock_get_api_data):
        """Test that generic exceptions are handled with maintenance message"""
        # Simulate a generic Exception in get_api_data
        mock_get_api_data.side_effect = Exception("Test Generic Exception")
        response = self.app.get("/")
        self.assertEqual(500, response.status_code)
        self.assertIn(b"Website under maintenance", response.data)
        # Verify error response is properly formatted
        self.assertTrue(len(response.data) > 0)

    @patch("src.web.get_summary_data")
    @patch("src.web.get_api_data")
    def test_home_route_alias(self, mock_get_api_data, mock_get_summary_data):
        """Test that /home route works as alias for root"""
        # Mock API responses with complete structure
        def side_effect_get_api_data(url):
            if 'sunrise-sunset' in url:
                return {'results': {'sunrise': '7:00:00 AM', 'sunset': '6:00:00 PM'}}
            elif 'ecowitt' in url:
                return {
                    'data': {
                        'outdoor': {
                            'temperature': {'value': '10', 'unit': '°C'},
                            'humidity': {'value': '50', 'unit': '%'}
                        },
                        'rainfall': {
                            '1_hour': {'value': '0', 'unit': 'mm'},
                            'daily': {'value': '1.5', 'unit': 'mm'},
                            'monthly': {'value': '25.0', 'unit': 'mm'},
                            'yearly': {'value': '500.0', 'unit': 'mm'}
                        },
                        'wind': {
                            'wind_speed': {'value': '5.0', 'unit': 'km/h'}
                        },
                        'pressure': {
                            'relative': {'value': '1013.0', 'unit': 'hPa'}
                        },
                        'solar_and_uvi': {
                            'uvi': {'value': '3', 'unit': ''}
                        }
                    }
                }
            else:
                return {'observations': [{'metric': {'temp': 10, 'tempLow': 5, 'tempHigh': 15}}]}
        
        mock_get_api_data.side_effect = side_effect_get_api_data
        mock_get_summary_data.return_value = (
            {'temperature': {'min': 5, 'max': 15}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0},
            {'temperature': {'min': 0, 'max': 20}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 100.0}
        )
        
        response = self.app.get("/home")
        self.assertEqual(200, response.status_code)
        # Both routes should return similar content
        root_response = self.app.get("/")
        self.assertEqual(root_response.status_code, response.status_code)

    @patch("src.web.get_summary_data")
    @patch("src.web.get_api_data")
    def test_security_headers_present(self, mock_get_api_data, mock_get_summary_data):
        def side_effect_get_api_data(url):
            if 'sunrise-sunset' in url:
                return {'results': {'sunrise': '7:00:00 AM', 'sunset': '6:00:00 PM'}}
            elif 'ecowitt' in url:
                return {
                    'data': {
                        'outdoor': {'temperature': {'value': '10'}, 'humidity': {'value': '50'}},
                        'rainfall': {
                            '1_hour': {'value': '0.0', 'unit': 'mm'},
                            'daily': {'value': '0.0', 'unit': 'mm'},
                            'monthly': {'value': '0.0', 'unit': 'mm'},
                            'yearly': {'value': '0.0', 'unit': 'mm'}
                        },
                        'wind': {'wind_speed': {'value': '0.0'}},
                        'pressure': {'relative': {'value': '1013.0'}},
                        'solar_and_uvi': {'uvi': {'value': '0'}},
                    }
                }
            return {'observations': [{'metric': {'temp': 10, 'tempLow': 5, 'tempHigh': 15}}]}

        mock_get_api_data.side_effect = side_effect_get_api_data
        mock_get_summary_data.return_value = (
            {'temperature': {'min': 5, 'max': 15}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0},
            {'temperature': {'min': 0, 'max': 20}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0}
        )

        response = self.app.get("/")
        self.assertEqual(200, response.status_code)
        self.assertEqual('nosniff', response.headers.get('X-Content-Type-Options'))
        self.assertEqual('DENY', response.headers.get('X-Frame-Options'))
        self.assertIsNotNone(response.headers.get('Content-Security-Policy'))

    @patch("src.web.get_summary_data")
    @patch("src.web.get_api_data")
    def test_security_headers_hsts_in_production(self, mock_get_api_data, mock_get_summary_data):
        """HSTS header should be present when production mode flag is enabled."""
        def side_effect_get_api_data(url):
            if 'sunrise-sunset' in url:
                return {'results': {'sunrise': '7:00:00 AM', 'sunset': '6:00:00 PM'}}
            elif 'ecowitt' in url:
                return {
                    'data': {
                        'outdoor': {'temperature': {'value': '10'}, 'humidity': {'value': '50'}},
                        'rainfall': {
                            '1_hour': {'value': '0.0', 'unit': 'mm'},
                            'daily': {'value': '0.0', 'unit': 'mm'},
                            'monthly': {'value': '0.0', 'unit': 'mm'},
                            'yearly': {'value': '0.0', 'unit': 'mm'}
                        },
                        'wind': {'wind_speed': {'value': '0.0'}},
                        'pressure': {'relative': {'value': '1013.0'}},
                        'solar_and_uvi': {'uvi': {'value': '0'}},
                    }
                }
            return {'observations': [{'metric': {'temp': 10, 'tempLow': 5, 'tempHigh': 15}}]}

        mock_get_api_data.side_effect = side_effect_get_api_data
        mock_get_summary_data.return_value = (
            {'temperature': {'min': 5, 'max': 15}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0},
            {'temperature': {'min': 0, 'max': 20}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0}
        )

        with patch("src.web._is_production", True):
            response = self.app.get("/")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            'max-age=31536000; includeSubDomains',
            response.headers.get('Strict-Transport-Security')
        )

    def test_method_not_allowed_by_request_policy(self):
        """POST is blocked globally by before_request policy."""
        response = self.app.post("/")
        self.assertEqual(405, response.status_code)
        self.assertEqual({"error": "Method not allowed"}, response.get_json())

    def test_static_request_passes_policy(self):
        """Static endpoint should bypass business request throttling path."""
        response = self.app.get("/static/main.css")
        self.assertEqual(200, response.status_code)

    @patch("src.web.get_summary_data")
    @patch("src.web.get_api_data")
    def test_rate_limit_returns_429(self, mock_get_api_data, mock_get_summary_data):
        """Second request should be rejected when limit is set to 1 request per window."""
        def side_effect_get_api_data(url):
            if 'sunrise-sunset' in url:
                return {'results': {'sunrise': '7:00:00 AM', 'sunset': '6:00:00 PM'}}
            elif 'ecowitt' in url:
                return {
                    'data': {
                        'outdoor': {'temperature': {'value': '10'}, 'humidity': {'value': '50'}},
                        'rainfall': {
                            '1_hour': {'value': '0.0', 'unit': 'mm'},
                            'daily': {'value': '0.0', 'unit': 'mm'},
                            'monthly': {'value': '0.0', 'unit': 'mm'},
                            'yearly': {'value': '0.0', 'unit': 'mm'}
                        },
                        'wind': {'wind_speed': {'value': '0.0'}},
                        'pressure': {'relative': {'value': '1013.0'}},
                        'solar_and_uvi': {'uvi': {'value': '0'}},
                    }
                }
            return {'observations': [{'metric': {'temp': 10, 'tempLow': 5, 'tempHigh': 15}}]}

        mock_get_api_data.side_effect = side_effect_get_api_data
        mock_get_summary_data.return_value = (
            {'temperature': {'min': 5, 'max': 15}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0},
            {'temperature': {'min': 0, 'max': 20}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0}
        )

        original_limit = web._RATE_LIMITS["/"]
        try:
            web._RATE_LIMITS["/"] = (1, 60)
            first = self.app.get("/")
            second = self.app.get("/")
        finally:
            web._RATE_LIMITS["/"] = original_limit

        self.assertEqual(200, first.status_code)
        self.assertEqual(429, second.status_code)
        self.assertEqual({"error": "Too many requests"}, second.get_json())

    @patch("src.web.get_summary_data")
    @patch("src.web.get_api_data")
    @patch("src.web.time", return_value=200.0)
    def test_rate_limit_discards_expired_timestamps(self, _mock_time, mock_get_api_data, mock_get_summary_data):
        """Expired timestamps in request history must be removed before evaluating limits."""
        def side_effect_get_api_data(url):
            if 'sunrise-sunset' in url:
                return {'results': {'sunrise': '7:00:00 AM', 'sunset': '6:00:00 PM'}}
            elif 'ecowitt' in url:
                return {
                    'data': {
                        'outdoor': {'temperature': {'value': '10'}, 'humidity': {'value': '50'}},
                        'rainfall': {
                            '1_hour': {'value': '0.0', 'unit': 'mm'},
                            'daily': {'value': '0.0', 'unit': 'mm'},
                            'monthly': {'value': '0.0', 'unit': 'mm'},
                            'yearly': {'value': '0.0', 'unit': 'mm'}
                        },
                        'wind': {'wind_speed': {'value': '0.0'}},
                        'pressure': {'relative': {'value': '1013.0'}},
                        'solar_and_uvi': {'uvi': {'value': '0'}},
                    }
                }
            return {'observations': [{'metric': {'temp': 10, 'tempLow': 5, 'tempHigh': 15}}]}

        mock_get_api_data.side_effect = side_effect_get_api_data
        mock_get_summary_data.return_value = (
            {'temperature': {'min': 5, 'max': 15}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0},
            {'temperature': {'min': 0, 'max': 20}, 'wind': '-', 'humidity': '-', 'pressure': '-', 'uvi': '-', 'rainfall': 0.0}
        )

        original_limit = web._RATE_LIMITS["/"]
        key = ("127.0.0.1", "/")
        try:
            web._RATE_LIMITS["/"] = (1, 60)
            web._request_history[key] = deque([100.0])
            response = self.app.get("/")
        finally:
            web._RATE_LIMITS["/"] = original_limit

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(web._request_history[key]))
        self.assertEqual(200.0, web._request_history[key][0])

    def test_transform_sun_time_missing_results_raises_key_error(self):
        with self.assertRaises(KeyError):
            web.transform_sun_time({}, "20260101")

    def test_transform_sun_time_missing_sunrise_or_sunset_raises_key_error(self):
        with self.assertRaises(KeyError):
            web.transform_sun_time({"results": {"sunrise": "7:00:00 AM"}}, "20260101")

if __name__ == "__main__":
    unittest.main()