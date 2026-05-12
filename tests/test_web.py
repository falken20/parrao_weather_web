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

if __name__ == "__main__":
    unittest.main()