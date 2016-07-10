import unittest
from qisbot import select
from qisbot import select_first


class TestSelect(unittest.TestCase):

    def test_select_positive(self):
        result = select('https://google.com/', '//*[@id="hplogo"]')
        self.assertTrue(result)
        self.assertEqual(result[0].get('title'), 'Google')

    def test_select_invalid_host(self):
        self.assertIsNone(select('https://localhost/', '//*[@id="hplogo"]'))

    def test_select_invalid_selector(self):
        self.assertIsNone(select('https://bing.com/', '?!2145'))

    def test_select_empty_selector(self):
        self.assertIsNone(select('https://bing.com/', ''))

    def test_select_no_selector(self):
        self.assertIsNone(select('https://bing.com/', None))


class TestSelectFirst(unittest.TestCase):

    def test_select_first_positive(self):
        pass

    def test_select_first_negative(self):
        pass
