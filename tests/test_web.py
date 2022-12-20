import unittest

from src import web


class TestWeb(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

    def test_home(self):
        ret = self.app.get("/")
        # It is necessary convert to byte the str
        self.assertIn(b"<html", ret.data)
        self.assertIn(b'Cercedilla Weather', ret.data)

    def test_contact(self):
        ret = self.app.get("/contact")
        # It is necessary convert to byte the str
        self.assertIn(b"<html", ret.data)

    def test_portfolio(self):
        ret = self.app.get("/portfolio")
        # It is necessary convert to byte the str
        self.assertIn(b"<html", ret.data)
