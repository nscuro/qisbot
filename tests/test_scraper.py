import unittest
from unittest import mock

import requests
from lxml import html
from lxml.etree import ParseError
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
        self.scraper.allow_redirects = False
        with self.scraper.permit_redirects(True) as permissive_scraper:
            doc = permissive_scraper.fetch('https://httpbin.org/redirect/3')
        self.assertIs(self.scraper.allow_redirects, False)
        self.assertEqual(self.scraper.status, 200)
        self.assertIsInstance(doc, html.HtmlElement)
        self.assertIn('python-requests', str(html.tostring(doc)))

    def test_fetching_disallow_redirects(self):
        """It should be possible to disallow redirects and still fetch & parse a document."""
        self.scraper.allow_redirects = True
        with self.scraper.permit_redirects(False) as dismissive_scraper:
            doc = dismissive_scraper.fetch('https://httpbin.org/redirect/1')
        self.assertIs(self.scraper.allow_redirects, True)
        self.assertEqual(self.scraper.status, 302)
        self.assertIsInstance(doc, html.HtmlElement)
        self.assertIn('redirecting', str(html.tostring(doc)).lower())

    def test_fetching_invalid_url(self):
        """When an invalid URL is passed, a chained ScraperException shall be raised."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.fetch('http://inva.lid/url')
        self.assertIsInstance(context.exception.__cause__, requests.ConnectionError)

    @mock.patch('requests.Session.get')
    def test_fetching_http_error(self, response_mock: mock.Mock):
        """When the server responds with HTTP >= 500, a chained ScraperException shall be raised."""
        dummy_response = requests.Response()
        dummy_response.status_code = 500
        response_mock.return_value = dummy_response
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.fetch('http://does-not-matt.er/')
        self.assertIsInstance(context.exception.__cause__, requests.HTTPError)

    @mock.patch('requests.Session.get')
    def test_fetching_http_not_found(self, response_mock: mock.Mock):
        """When the server responds with HTTP >= 400, a chained ScraperException shall be raised."""
        dummy_response = requests.Response()
        dummy_response.status_code = 401
        response_mock.return_value = dummy_response
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.fetch('http://does-not-matt.er/')
        self.assertIsInstance(context.exception.__cause__, requests.HTTPError)

    @mock.patch('requests.Session.get')
    @mock.patch('requests.Response.content', new_callable=mock.PropertyMock)
    def test_fetching_no_response_content(self, response_content_mock: mock.PropertyMock, session_get_mock: mock.Mock):
        """When the content of a response is empty, a ScraperException shall be raised when attempting to parse it."""
        dummy_response = requests.Response()
        dummy_response.status_code = 200
        session_get_mock.return_value = dummy_response
        # The response's content is empty -> Parsing fails
        response_content_mock.return_value = ''
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.fetch('https://httpbin.org/get')
        self.assertIsInstance(context.exception.__cause__, ParseError)


class TestSelection(unittest.TestCase):
    """Test the scraper's ability to select elements on a HTML document."""

    @classmethod
    def setUpClass(cls):
        cls.valid_html = html_builder.HTML(
            html_builder.HEAD(
                html_builder.TITLE('TEST DOCUMENT')
            ), html_builder.BODY(
                html_builder.H1(html_builder.CLASS('heading-class'), 'TEST HEADING'),
                html_builder.P(html_builder.CLASS('paragraph'), 'This is a nice text.'),
                html_builder.UL(
                    html_builder.LI('TEST ITEM 01'),
                    html_builder.LI('TEST ITEM 02')
                )
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

    def test_number(self):
        """Use an XPath expression that returns a number."""
        result = self.scraper.number('count(//li)', self.valid_html)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 2)

    def test_number_nan(self):
        """When attempting to get a non-number XPath result, a chained ScraperException shall be raised."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.number('//li', self.valid_html)
        self.assertIsInstance(context.exception.__cause__, TypeError)

    def test_text(self):
        """Test selection of string values."""
        result = self.scraper.text('//li/text()', self.valid_html)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn('TEST ITEM 01', result)
        self.assertIn('TEST ITEM 02', result)

    def test_text_empty(self):
        """When no text was found, an empty list shall be returned."""
        result = self.scraper.text('//ul/text()', self.valid_html)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_text_no_text(self):
        """A ScraperException shall be raised when the result is not a list of strings."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.text('//ul/li', self.valid_html)
        self.assertIsInstance(context.exception.__cause__, TypeError)

    def test_find_all(self):
        """Use an XPath expression that returns multiple HTML elements."""
        result = self.scraper.find_all('//li', self.valid_html)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_find_all_no_list(self):
        """When attempting to get a non-HTML-element-list XPath result, a chained ScraperException shall be raised."""
        with self.assertRaises(scraper.ScraperException) as context:
            self.scraper.find_all('count(//li)', self.valid_html)
        self.assertIsInstance(context.exception.__cause__, TypeError)
