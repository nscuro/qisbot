import unittest

import requests
from lxml import html
from lxml.html import builder as html_builder

from qisbot import scraper


class TestFetching(unittest.TestCase):
    """Test the scraper's ability to fetch & parse a web page's content."""

    def setUp(self):
        self.scraper = scraper.Scraper()

    def test_fetching_success(self):
        """Positive case: Result is of type html.HtmlElement as was successfully parsed."""
        doc = self.scraper.fetch('https://httpbin.org/get')
        self.assertEqual(self.scraper.status, 200)
        self.assertTrue(isinstance(doc, html.HtmlElement), 'Unexpected type of fetch result')
        self.assertIn('python-requests', str(html.tostring(doc)), 'Cannot verify fetched document content')

    def test_fetching_redirect(self):
        """Redirects shall be performed before the document is parsed."""
        doc = self.scraper.fetch('https://httpbin.org/redirect/3')
        self.assertEqual(self.scraper.status, 200)
        self.assertIsInstance(doc, html.HtmlElement)
        self.assertIn('python-requests', str(html.tostring(doc)))

    def test_fetching_disallow_redirects(self):
        """It should be possible to disallow redirects and still fetch & parse a document."""
        self.scraper.allow_redirects = False
        doc = self.scraper.fetch('https://httpbin.org/redirect/1')
        self.assertEqual(self.scraper.status, 302)
        self.assertIsInstance(doc, html.HtmlElement)
        self.assertIn('redirecting', str(html.tostring(doc)).lower())

    def test_fetching_invalid_url(self):
        """When an invalid URL is passed, a chained ScraperException shall be raised."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.fetch('http://inva.lid/url')
        self.assertIsInstance(context.exception.__cause__, requests.ConnectionError)

    def test_fetching_http_error(self):
        """When the server responds with HTTP >= 500, a chained ScraperException shall be raised."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.fetch('https://httpbin.org/status/500')
        self.assertIsInstance(context.exception.__cause__, requests.HTTPError)

    def test_fetching_http_notfound(self):
        """When the server responds with HTTP >= 400, a chained ScraperException shall be raised."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.fetch('https://httpbin.org/status/404')
        self.assertIsInstance(context.exception.__cause__, requests.HTTPError)


class TestSelection(unittest.TestCase):
    """Test the scraper's ability to select elements on a HTML document."""

    @classmethod
    def setUpClass(cls):
        cls.valid_html = html_builder.HTML(
            html_builder.HEAD(
                html_builder.TITLE('TEST DOCUMENT')
            ), html_builder.BODY(
                html_builder.H1(html_builder.CLASS('heading-class'), 'TEST HEADING'),
                html_builder.P(html_builder.CLASS('paragraph'), 'This is a nice text.')
            )
        )
        # TODO: Invalid HTML

    def setUp(self):
        self.scraper = scraper.Scraper()

    def test_check(self):
        """Use an XPath expression that returns a boolean."""
        result = self.scraper.check('//h1/@class = "heading-class"', document=self.valid_html)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_check_no_bool(self):
        """When attempting to check a non-boolean expression, a chained ScraperException shall be raised."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.check('//h1', document=self.valid_html)
        self.assertIsInstance(context.exception.__cause__, TypeError)
