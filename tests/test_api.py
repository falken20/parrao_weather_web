import unittest
from unittest.mock import patch

from src import web
from src import api


class TestApi(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()
        web._request_history.clear()
        # Reset cache before each test
        api._rain_cache["date"] = None
        api._rain_cache["rained_today"] = None

    @patch("src.api.get_api_data")
    def test_rain_today_true(self, mock_get_api_data):
        """Test rain endpoint returns true when daily rainfall is above zero"""
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

    @patch("src.api.get_api_data")
    def test_rain_today_false(self, mock_get_api_data):
        """Test rain endpoint returns false when daily rainfall is zero"""
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
        self.assertEqual(1, len(payload))

    @patch("src.api.get_api_data")
    def test_rain_today_cache(self, mock_get_api_data):
        """Test that rain status is cached for the same day and API not called again"""
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
        self.assertEqual(call_count_after_first, mock_get_api_data.call_count)

    @patch("src.api.get_api_data")
    def test_rain_today_key_error(self, mock_get_api_data):
        """Test rain endpoint handles missing data gracefully"""
        mock_get_api_data.return_value = {'data': {}}

        response = self.app.get("/api/rain-today")
        self.assertEqual(500, response.status_code)
        payload = response.get_json()
        self.assertEqual("Data processing error occurred", payload["error"])

    @patch("src.api.get_api_data")
    @patch("src.api.API_ACCESS_KEY", "secret-token")
    def test_rain_today_requires_api_key_when_enabled(self, mock_get_api_data):
        mock_get_api_data.return_value = {
            'data': {
                'rainfall': {
                    'daily': {'value': '0', 'unit': 'mm'}
                }
            }
        }

        unauthorized = self.app.get("/api/rain-today")
        self.assertEqual(401, unauthorized.status_code)

        authorized = self.app.get("/api/rain-today", headers={"X-API-Key": "secret-token"})
        self.assertEqual(200, authorized.status_code)


if __name__ == "__main__":
    unittest.main()
