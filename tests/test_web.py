import unittest

from src import web


class TestWeb(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

    def test_home(self):
        response = self.app.get("/")
        self.assertEqual(200, response.status_code)


