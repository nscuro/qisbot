import unittest
from qisbot import select
from qisbot import select_first


class TestSelect(unittest.TestCase):

    def test_select_positive(self):
        result = select('https://httpbin.org/', '//*[@id="ENDPOINTS"]')
        self.assertTrue(result)
        self.assertEqual(result[0].text, 'ENDPOINTS')

    def test_select_invalid_host(self):
        self.assertIsNone(select('inva://lidpage.com', '//*[@id="hplogo"]'))

    def test_select_invalid_selector(self):
        self.assertIsNone(select('https://httpbin.org/', '?!2145'))

    def test_select_empty_selector(self):
        self.assertIsNone(select('https://httpbin.org/', ''))

    def test_select_no_selector(self):
        self.assertIsNone(select('https://httpbin.org/', None))


class TestSelectFirst(unittest.TestCase):

    def test_select_first_positive(self):
        pass

    def test_select_first_negative(self):
        pass
