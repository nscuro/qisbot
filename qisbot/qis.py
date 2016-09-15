import enum

import requests
from lxml import html
from lxml.etree import strip_tags

from qisbot import scraper
from qisbot.exceptions import NoSuchElementException
from qisbot.exceptions import QisLoginFailedException


class Selectors(enum.Enum):
    LOGIN_ACTION_LINK = '//*[@id="wrapper"]/div[3]/a[2]'


class Qis(object):
    def __init__(self, base_url: str, custom_scraper: scraper.Scraper = None):
        """Initialize a new QIS session.

        Args:
            base_url: The QIS' base url (usually that of the login page)
            custom_scraper: A custom scraper instance
        Raises:
            ValueError: When no base url was provided
        """
        if not base_url:
            raise ValueError('No base url provided')
        self._base_url = base_url
        self._scraper = custom_scraper or scraper.Scraper()

    def login(self, username: str, password: str) -> ():
        """Perform a login.

        Args:
            username: The username (the student's e-mail)
            password: The password
        Raises:
            ValueError: When either username or password are missing
            NoSuchElementException: When unable to locate elements on login form
            QisLoginFailedException: When the login failed
        """
        if self.is_logged_in:
            return
        if not username or not password:
            raise ValueError('Username or password missing')
        base_doc = self._scraper.fetch(self.base_url)
        if not len(base_doc.forms):
            raise NoSuchElementException('Unable to locate the login form')
        # Determine where to post the login request to
        login_form = base_doc.forms[0]  # type: html.FormElement
        login_action = login_form.action
        # The submit button has a name & value, thus has to be posted too
        login_submit_value = None  # type: str
        for form_field in login_form.fields.keys():
            if form_field == 'submit':
                login_submit_value = login_form.fields[form_field]
                break
        if login_submit_value is None:
            raise NoSuchElementException('Unable to determine login submit value')
        # POST the login request
        try:
            login_response = self._scraper.session.post(login_action, data={
                'username': username,
                'password': password,
                'submit': login_submit_value
            })
            login_response.raise_for_status()
        except requests.RequestException as ex:
            raise QisLoginFailedException('Login failed due to unexpected server response') from ex
        if not self.is_logged_in:
            raise QisLoginFailedException('Login not successful. Possibly invalid credentials')

    @property
    def is_logged_in(self) -> bool:
        """Determine whether or not the current session is logged in.

        This is accomplished by opening the base_url and looking for options
        to logout. If none is found, the session is considered to be not logged in.

        Returns:
            True when logged in, otherwise False
        """
        if 'JSESSIONID' not in self._scraper.cookies.keys():
            # This is the first time the page is being visited, can't possibly be logged in
            return False
        document = self._scraper.fetch(self.base_url)
        login_action_link = self._scraper.find_all(Selectors.LOGIN_ACTION_LINK.value, document)
        if not len(login_action_link):
            return False
        # Strip down the link's horrible text format
        login_status = login_action_link[0]
        strip_tags(login_status, 'u')
        login_status = login_status.text.replace('"', '').strip().lower()
        if login_status in ('logout', 'abmelden'):
            return True
        return False

    @property
    def base_url(self) -> str:
        return self._base_url
