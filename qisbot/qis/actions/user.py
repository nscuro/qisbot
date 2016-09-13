import requests
from lxml.etree import strip_tags

from qisbot import scraper
from qisbot.qis import selectors


def is_logged_in(session: requests.Session, login_url: str) -> bool:
    """Determine if the user is logged in the given session.

    Args:
        session: The session to check the login status on
        login_url: URL pointing to the QIS login page
    Returns:
        True when user is logged in, otherwise False
    Raises:
        ValueError: When no login url was given
    """
    if not login_url:
        raise ValueError('No login URL provided')
    if 'JSESSIONID' not in session.cookies.keys():
        # This session can't be logged in without JSESSIONID cookie
        return False
    login_page = scraper.fetch_source(login_url, session=session)
    login_action_link = scraper.select(login_page, selectors.LOGIN_ACTION_LINK)
    if login_action_link is None:
        return False
    strip_tags(login_action_link, 'u')
    link_text = login_action_link.text.replace('"', '').strip().lower()
    if link_text in ('abmelden', 'logout'):
        return True
    return False


def login(login_url: str, username: str, password: str, session: requests.Session = None) -> requests.Session:
    """Perform a login using the given credentials.

    Args:
        login_url: Base URL of the QIS server
        username: The username
        password: The password
        session: Session to use
    Returns:
         A logged in session
    Raises:
        ValueError: When any non-optional parameter is missing
        scraper.ElementNotFoundError: When a web element could not be found
        IOError: When the login failed
    """
    if not login_url:
        raise ValueError('No base url for login given')
    elif not username:
        raise ValueError('No username for login given')
    elif not password:
        raise ValueError('No password for login given')
    if session:
        if is_logged_in(session, login_url):
            return session
        else:
            login_session = session
    else:
        login_session = requests.Session()
    # Collect information needed to POST login data
    login_source = scraper.fetch_source(login_url, session=login_session)
    form_element = scraper.select(login_source, selectors.LOGIN_FORM)
    if form_element is None:
        raise scraper.ElementNotFoundError('No form element found on login page')
    action_url = form_element.get('action')
    if action_url is None:
        raise scraper.ElementNotFoundError('Cannot determine action URL')
    submit_value = form_element.xpath(selectors.LOGIN_FORM_SUBMIT)
    if submit_value is None:
        raise scraper.ElementNotFoundError('Cannot determine submit value')
    # Perform login request
    login_response = login_session.post(action_url, data={
        'username': username,
        'password': password,
        'submit': submit_value
    })
    login_response.raise_for_status()
    if not is_logged_in(login_session, login_url):
        raise IOError('Login as {} failed, please check login credentials'.format(username))
    return login_session
