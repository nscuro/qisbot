import unittest

from requests import RequestException

from qisbot import scraper


class TestFetchSource(unittest.TestCase):
    def test_fetch_source_success(self):
        source = scraper.fetch_source('https://httpbin.org/get')
        self.assertIsNotNone(source)

    def test_fetch_source_none_url(self):
        with self.assertRaises(ValueError):
            scraper.fetch_source(None)

    def test_fetch_source_blank_url(self):
        with self.assertRaises(ValueError):
            scraper.fetch_source(' ')

    def test_fetch_source_http_redirect(self):
        source = scraper.fetch_source('https://httpbin.org/absolute-redirect/1')
        self.assertIn('python-requests', source, '')

    def test_fetch_source_http_status_error(self):
        with self.assertRaises(RequestException):
            scraper.fetch_source('https://httpbin.org/status/400')
            scraper.fetch_source('https://httpbin.org/status/500')


class TestSelect(unittest.TestCase):
    source_valid = """
    <body>
        <h1 class='testclass'>testtitle</h1>
        <ul>
            <li>testitem 1</li>
            <li>testitem 2</li>
            <li>testitem 3</li>
        </ul>
    </body>
    """

    def test_select_all_success(self):
        selected = scraper.select_all(self.source_valid, '//ul/li')
        self.assertIs(len(selected), 3)
        for element in selected:
            self.assertIn('testitem', element.text)

    def test_select_all_success_single(self):
        selected = scraper.select_all(self.source_valid, '//*[@class = "testclass"]')
        self.assertIs(len(selected), 1)

    def test_select_all_invalid_source(self):
        with self.assertRaises(scraper.ScraperError) as context:
            scraper.select_all('<<<<', '')  # XPath not relevant in this scenario
        self.assertIn('malformed html', str(context.exception).lower())

    def test_select_all_invalid_xpath(self):
        with self.assertRaises(scraper.ScraperError) as context:
            scraper.select_all(self.source_valid, 'damn_invalid_xpath!241?#')
        self.assertIn('not a valid xpath expression', str(context.exception).lower())

    def test_select_success(self):
        selected = scraper.select(self.source_valid, '//li[text() = "testitem 1"]')
        self.assertIsNotNone(selected)
        self.assertEqual(selected.text, 'testitem 1')
