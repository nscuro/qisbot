import functools
import typing

import requests
from lxml import html
from lxml.etree import strip_tags

from qisbot import models
from qisbot import scraper
from qisbot.exceptions import NoSuchElementException
from qisbot.exceptions import QisLoginFailedException
from qisbot.exceptions import QisNotLoggedInException
from qisbot.exceptions import UnexpectedStateException
from qisbot.selectors import Selectors


def requires_login(func):
    """Checks whether or not the current session is logged in before executing a function."""

    @functools.wraps(func)
    def check_login(*args, **kwargs):
        if not isinstance(args[0], Qis):
            raise ValueError('@requires_login only works for Qis instances')
        qis_instance = args[0]  # type: Qis
        if not qis_instance.is_logged_in:
            raise QisNotLoggedInException('This action requires a login')
        return func(*args, **kwargs)

    return check_login


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
            ValueError: When either username or password are missing or the login action was not found
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
        if login_action is None:
            raise ValueError('No login action found')
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

        A handy side-effect is that whenever this check is performed on an already
        logged-in session, the server-side session timeout is being reset due to activity.
        This contributes to keeping a session alive longer.

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

    @requires_login
    def fetch_exams_extract(self) -> typing.List[html.HtmlElement]:
        """Fetch all rows of the exams extract.

        This does not perform any filtering actions.

        Returns:
            A list of all rows containing exam information
        Raises:
            QisNotLoggedInException: When session is not logged in
            UnexpectedStateException: When navigating to exams extract page failed
            NoSuchElementException: When unable to locate exams extract data table
        """
        ee_doc = None  # type: html.HtmlElement
        for _, ee_doc in self._scraper.navigate([Selectors.EXAM_ADMINISTRATION_LINK.value,
                                                 Selectors.EXAMS_EXTRACT_LINK.value,
                                                 Selectors.SHOW_ACCOMPLISHMENTS_LINK.value],
                                                self._base_url):
            pass
        if not self._scraper.number('count(//div[@class = "abstand_pruefinfo"])', document=ee_doc):
            raise UnexpectedStateException('This may be something, but it\'s definitely NOT the exams extract page.')
        # Get the table that contains all the exam data
        exam_data_table = self._scraper.find_all(Selectors.EXAMS_EXTRACT_EXAMS_TABLE.value, document=ee_doc)
        if not len(exam_data_table):
            raise NoSuchElementException('Unable to find table containing exams data')
        return self._scraper.find_all('.//tr', document=exam_data_table[0])

    @property
    def exams_extract(self) -> typing.List[models.Exam]:
        """Get an exams extract.

        Note that this will call fetch_exams_extract every time.

        Returns:
            A list of Exam instances. See models.map_exam for how
            the result of fetch_exams_extract is mapped.
        """
        extract_rows = self.fetch_exams_extract()
        extract = []
        for row in extract_rows:
            try:
                exam = models.map_to_exam(source=row)
            except ValueError:
                # That row was not relevant
                continue
            if not exam:
                continue
            extract.append(exam)
        return extract

    @property
    def base_url(self) -> str:
        return self._base_url

    def __repr__(self) -> str:
        return '{} (base_url={})'.format(self.__class__, self.base_url)
