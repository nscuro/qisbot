import unittest
from unittest import mock

import requests
from lxml import html
from lxml.html import builder as html_builder

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
    @classmethod
    def setUpClass(cls):
        cls.username = 'username'
        cls.password = 'password'
        cls.login_html = html_builder.HTML(
            html_builder.BODY(
                html_builder.FORM(
                    html_builder.ATTR({
                        'action': 'http://testacti.on/'
                    }),
                    html_builder.INPUT(html_builder.ATTR({
                        'name': 'submit',
                        'value': 'submitMe!'
                    }))
                )
            )
        )

    def setUp(self):
        self.test_scraper = scraper.Scraper()
        self.qis = qis.Qis('http://doesnt-even-matt.er/', custom_scraper=self.test_scraper)
        # Have a non-logged-in session as default prerequisite
        self.is_logged_in_patch = mock.patch('qisbot.qis.Qis.is_logged_in', new_callable=mock.PropertyMock)
        self.is_logged_in_mock = self.is_logged_in_patch.start()
        self.is_logged_in_mock.return_value = False

    def test_already_logged_in(self):
        self.is_logged_in_mock.return_value = True
        self.test_scraper.fetch = mock.MagicMock()
        self.qis.login(None, None)  # Values don't matter at this point
        self.assertFalse(self.test_scraper.fetch.called)

    def test_missing_credentials(self):
        with self.assertRaises(ValueError):
            self.qis.login(None, None)

    def test_missing_username(self):
        with self.assertRaises(ValueError):
            self.qis.login(None, self.password)

    def test_missing_password(self):
        with self.assertRaises(ValueError):
            self.qis.login(self.username, None)

    def test_no_login_form(self):
        self.test_scraper.fetch = mock.MagicMock(return_value=html.HtmlElement())
        with self.assertRaises(qis.NoSuchElementException):
            self.qis.login(self.username, self.password)

    def test_no_login_action(self):
        no_action_html = html_builder.BODY(html_builder.FORM())
        self.test_scraper.fetch = mock.MagicMock(return_value=no_action_html)
        with self.assertRaises(ValueError) as context:
            self.qis.login(self.username, self.password)
        self.assertIn('login action', str(context.exception))

    def test_no_submit_value(self):
        no_submit_value_html = html_builder.BODY(html_builder.FORM(html_builder.ATTR({
            'action': 'non-empty'
        })))
        self.test_scraper.fetch = mock.MagicMock(return_value=no_submit_value_html)
        with self.assertRaises(qis.NoSuchElementException) as context:
            self.qis.login(self.username, self.password)
        self.assertIn('submit value', str(context.exception))

    @mock.patch('requests.Session.post')
    def test_http_error(self, post_mock: mock.Mock):
        response = requests.Response()
        response.status_code = 500
        post_mock.return_value = response
        self.test_scraper.fetch = mock.MagicMock(return_value=self.login_html)
        with self.assertRaises(qis.QisLoginFailedException) as context:
            self.qis.login(self.username, self.password)
        self.assertIsInstance(context.exception.__cause__, requests.HTTPError)

    @mock.patch('requests.Session.post')
    def test_http_notfound(self, post_mock: mock.Mock):
        response = requests.Response()
        response.status_code = 400
        post_mock.return_value = response
        self.test_scraper.fetch = mock.MagicMock(return_value=self.login_html)
        with self.assertRaises(qis.QisLoginFailedException) as context:
            self.qis.login(self.username, self.password)
        self.assertIsInstance(context.exception.__cause__, requests.HTTPError)

    @mock.patch('requests.Session.post')
    def test_login_failed(self, post_mock: mock.Mock):
        self.test_scraper.fetch = mock.MagicMock(return_value=self.login_html)
        response = requests.Response()
        response.status_code = 200
        post_mock.return_value = response
        self.is_logged_in_mock.side_effect = [False, False]
        with self.assertRaises(qis.QisLoginFailedException) as context:
            self.qis.login(self.username, self.password)
        self.assertIs(context.exception.__cause__, None)

    def tearDown(self):
        self.is_logged_in_patch.stop()


class TestFetchExamsExtract(unittest.TestCase):
    # TODO
    pass
