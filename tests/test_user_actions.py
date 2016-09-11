import unittest
from unittest import mock

from lxml.html import HtmlElement
from requests import Session

from qisbot import scraper
from qisbot.qis import user


class TestUserIsLoggedIn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = Session()
        cls.session.cookies = dict(JSESSIONID='test')

    def setUp(self):
        self.patcher_fetch_source = mock.patch('qisbot.scraper.fetch_source', mock.Mock(return_value='test'))
        self.fetch_source_mock = self.patcher_fetch_source.start()

    def test_no_login_url(self):
        with self.assertRaises(ValueError) as context:
            user.is_logged_in(None, '')
        self.assertIn('no login url provided', str(context.exception).lower())

    def test_no_sessionid(self):
        self.assertFalse(user.is_logged_in(Session(), 'test'))

    def test_no_action_link(self):
        scraper.select = mock.Mock(return_value=None)
        self.assertFalse(user.is_logged_in(self.session, 'test'))

    @mock.patch('qisbot.scraper.select')
    def test_already_logged_out(self, mock_func):
        login_action_element = HtmlElement()
        login_action_element.text = 'login"  '
        mock_func.return_value = login_action_element
        self.assertFalse(user.is_logged_in(self.session, 'test'))

    @mock.patch('qisbot.scraper.select')
    def test_logged_in(self, mock_func):
        login_action_element = HtmlElement()
        login_action_element.text = ' Logout"  '
        mock_func.return_value = login_action_element
        self.assertTrue(user.is_logged_in(self.session, 'test'))

    def tearDown(self):
        self.patcher_fetch_source.stop()
