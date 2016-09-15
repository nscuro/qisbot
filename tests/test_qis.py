import unittest
from unittest import mock

from lxml import html

from qisbot import qis
from qisbot import scraper


class TestInitialization(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            qis.Qis(None)


class TestIsLoggedIn(unittest.TestCase):
    def setUp(self):
        self.test_scraper = scraper.Scraper()
        self.test_scraper.fetch = mock.MagicMock()  # Don't attempt to fetch anything
        self.qis = qis.Qis('http://doesnt-even-matt.er/', custom_scraper=self.test_scraper)

    def test_no_jsessionid(self):
        self.assertFalse(self.qis.is_logged_in)
        self.assertFalse(self.test_scraper.fetch.called)

    @mock.patch('lxml.etree.strip_tags')
    @mock.patch('qisbot.scraper.Scraper.cookies', new_callable=mock.PropertyMock)
    def test_no_link(self, cookies_mock: mock.PropertyMock, strip_tags_mock: mock.Mock):
        # Provide the JSESSIONID cookie
        cookies_mock.return_value = {'JSESSIONID': None}
        # Return no results when searching for login action link
        self.test_scraper.find_all = mock.MagicMock(return_value=[])
        self.assertFalse(self.qis.is_logged_in)
        self.assertTrue(self.test_scraper.find_all.called)
        self.assertFalse(strip_tags_mock.called)

    @mock.patch('lxml.html.HtmlElement.text', new_callable=mock.PropertyMock)
    @mock.patch('qisbot.scraper.Scraper.cookies', new_callable=mock.PropertyMock)
    def test_logged_in(self, cookies_mock: mock.PropertyMock, element_text_mock: mock.PropertyMock):
        # Provide the JSESSIONID cookie
        cookies_mock.return_value = {'JSESSIONID': None}
        # Return at least one result when searching for login action link
        self.test_scraper.find_all = mock.MagicMock(return_value=[html.HtmlElement()])
        # The login action element's text indicates a logged in session
        element_text_mock.return_value = 'Abmelden'
        self.assertTrue(self.qis.is_logged_in)
        self.assertTrue(element_text_mock.called)

    @mock.patch('lxml.html.HtmlElement.text', new_callable=mock.PropertyMock)
    @mock.patch('qisbot.scraper.Scraper.cookies', new_callable=mock.PropertyMock)
    def test_not_logged_in(self, cookies_mock: mock.PropertyMock, element_text_mock: mock.PropertyMock):
        # Provide the JSESSIONID cookie
        cookies_mock.return_value = {'JSESSIONID': None}
        # Return at least one result when searching for login action link
        self.test_scraper.find_all = mock.MagicMock(return_value=[html.HtmlElement()])
        # The login action element's text indicates a logged in session
        element_text_mock.return_value = 'Login'
        self.assertFalse(self.qis.is_logged_in)
        # Make sure the not-logged-in state was influenced by the link's text
        self.assertTrue(element_text_mock.called)


class TestLogin(unittest.TestCase):
    # TODO
    pass


class TestFetchExamsExtract(unittest.TestCase):
    # TODO
    pass
