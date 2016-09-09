import unittest
from unittest import mock
from requests import Session
from lxml.html import HtmlElement

from qisbot import scraper
from qisbot.qis import user


class TestUserIsLoggedIn(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = Session()
        cls.session.cookies = dict(JSESSIONID='test')
        scraper.fetch_source = mock.Mock(return_value='test')

    def test_no_login_url(self):
        with self.assertRaises(ValueError) as context:
            user.is_logged_in(None, '')
        self.assertIn('no login url provided', str(context.exception).lower())

    def test_no_sessionid(self):
        self.assertFalse(user.is_logged_in(Session(), 'test'))

    def test_no_action_link(self):
        scraper.select = mock.Mock(return_value=None)
        self.assertFalse(user.is_logged_in(self.session, 'test'))

    def test_already_logged_out(self):
        login_action_element = HtmlElement()
        login_action_element.text = 'login"  '
        scraper.select = mock.Mock(return_value=login_action_element)
        self.assertFalse(user.is_logged_in(self.session, 'test'))

    def test_logged_in(self):
        login_action_element = HtmlElement()
        login_action_element.text = ' Logout"  '
        scraper.select = mock.Mock(return_value=login_action_element)
        self.assertTrue(user.is_logged_in(self.session, 'test'))
