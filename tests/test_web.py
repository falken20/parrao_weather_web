import unittest
from unittest.mock import patch
import logging

logging.basicConfig(level=logging.DEBUG)

from src import web


class TestWeb(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

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

    @patch("src.web.get_api_data")
    def test_rain_today_true(self, mock_get_api_data):
        """Test rain endpoint returns true when daily rainfall is above zero"""
        # Reset cache to ensure fresh call
        from src.web import _rain_cache
        _rain_cache["date"] = None
        _rain_cache["rained_today"] = None
        
        mock_get_api_data.return_value = {
            'data': {
                'rainfall': {
                    'daily': {'value': '1.5', 'unit': 'mm'}
                }
            }
        }

        response = self.app.get("/api/rain-today")
        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual(True, payload["rained_today"])
        # Verify only rained_today field is in response
        self.assertEqual(1, len(payload))

    @patch("src.web.get_api_data")
    def test_rain_today_false(self, mock_get_api_data):
        """Test rain endpoint returns false when daily rainfall is zero"""
        # Reset cache to ensure fresh call
        from src.web import _rain_cache
        _rain_cache["date"] = None
        _rain_cache["rained_today"] = None
        
        mock_get_api_data.return_value = {
            'data': {
                'rainfall': {
                    'daily': {'value': '0', 'unit': 'mm'}
                }
            }
        }

        response = self.app.get("/api/rain-today")
        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual(False, payload["rained_today"])
        # Verify only rained_today field is in response
        self.assertEqual(1, len(payload))

    @patch("src.web.get_api_data")
    def test_rain_today_cache(self, mock_get_api_data):
        """Test that rain status is cached for the same day and API not called again"""
        # Reset cache
        from src.web import _rain_cache
        _rain_cache["date"] = None
        _rain_cache["rained_today"] = None
        
        mock_get_api_data.return_value = {
            'data': {
                'rainfall': {
                    'daily': {'value': '2.0', 'unit': 'mm'}
                }
            }
        }

        # First call should hit API
        response1 = self.app.get("/api/rain-today")
        self.assertEqual(200, response1.status_code)
        self.assertEqual(True, response1.get_json()["rained_today"])
        call_count_after_first = mock_get_api_data.call_count

        # Second call should use cache and not call API again
        response2 = self.app.get("/api/rain-today")
        self.assertEqual(200, response2.status_code)
        self.assertEqual(True, response2.get_json()["rained_today"])
        # Verify API was not called again
        self.assertEqual(call_count_after_first, mock_get_api_data.call_count)

    @patch("src.web.get_api_data")
    def test_rain_today_key_error(self, mock_get_api_data):
        """Test rain endpoint handles missing data gracefully"""
        # Reset cache
        from src.web import _rain_cache
        _rain_cache["date"] = None
        _rain_cache["rained_today"] = None
        
        mock_get_api_data.return_value = {'data': {}}

        response = self.app.get("/api/rain-today")
        self.assertEqual(500, response.status_code)
        payload = response.get_json()
        self.assertEqual("Data processing error occurred", payload["error"])

if __name__ == "__main__":
    unittest.main()