import unittest
from qisbot import fetch_source


class TestFetchSource(unittest.TestCase):

    def test_fetch_source_positive(self):
        source = fetch_source('http://brainjar.com/java/host/test.html')
        self.assertIsNotNone(source)
        self.assertIn('<html>', source)

    def test_fetch_source_invalid_url(self):
        self.assertIsNone(fetch_source('https://localhost/'))

    def test_fetch_source_no_url(self):
        self.assertIsNone(fetch_source(None))

    def test_fetch_source_empty_url(self):
        self.assertIsNone(fetch_source(''))
