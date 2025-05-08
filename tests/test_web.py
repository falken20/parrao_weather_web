import unittest
from unittest.mock import patch

from src import web


class TestWeb(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

    def test_home(self):
        response = self.app.get("/")
        self.assertEqual(200, response.status_code)

    @patch("src.web.get_api_data")
    def test_home_key_error(self, mock_get_api_data):
        # Simulate a KeyError in get_api_data
        mock_get_api_data.side_effect = KeyError("Test KeyError")
        response = self.app.get("/")
        self.assertEqual(500, response.status_code)
        self.assertIn(b"Data processing error occurred", response.data)

    @patch("src.web.get_api_data")
    def test_home_value_error(self, mock_get_api_data):
        # Simulate a ValueError in get_api_data
        mock_get_api_data.side_effect = ValueError("Test ValueError")
        response = self.app.get("/")
        self.assertEqual(500, response.status_code)
        self.assertIn(b"Website under maintenance", response.data)

    @patch("src.web.get_api_data")
    def test_home_generic_exception(self, mock_get_api_data):
        # Simulate a generic Exception in get_api_data
        mock_get_api_data.side_effect = Exception("Test Generic Exception")
        response = self.app.get("/")
        self.assertEqual(500, response.status_code)
        self.assertIn(b"Website under maintenance", response.data)

if __name__ == "__main__":
    unittest.main()