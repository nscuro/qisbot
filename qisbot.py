#!/usr/bin/env python

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import logging
import requests
from lxml import html
from os import environ
from lxml.etree import XPathEvalError


# User credentials
QIS_USERNAME = environ.get('QIS_USER') or None
QIS_PASSWORD = environ.get('QIS_PASS') or None

# Static urls
QIS_URL_BASE = 'https://qis.fh-kiel.de/qisserver'
QIS_URL_LOGIN = QIS_URL_BASE + '/rds?state=user&type=1&category=auth.login'
QIS_URL_INITIAL = QIS_URL_BASE + '/rds?state=user&type=0'

# XPath selectors
SELECTOR_EXAM_MANAGEMENT_LINK = '//a[contains(text(), "Prüfungsverwaltung")]/@href'
SELECTOR_GRADE_OVERVIEW_LINK = '//a[contains(text(), "Notenspiegel")]/@href'
SELECTOR_GRADE_OVERVIEW_GRADUATION_LINK = '//a[contains(@title, "Leistungen anzeigen")]/@href'
SELECTOR_GRADES_STUDENT_INFO = '//table[contains(@summary, "Liste der Stammdaten des Studierenden")]'
SELECTOR_GRADES_TABLE = '//*[@id="wrapper"]/div[6]/div[2]/form/table[2]/tbody'

# Application settings
LOGGING_LEVEL = logging.DEBUG


def determine_session_id(session, from_url=None):
    """Determine the session ID by crunching the cookie of a given URL.

    :type session requests.Session
    :type from_url: str
    :rtype (requests.Session)

    :param session Session instance to use
    :param from_url Url to visit
    :return The session when successful, else None
    """
    try:
        initial_response = session.get(from_url or QIS_URL_INITIAL)
        initial_response.raise_for_status()
    except (ConnectionError, requests.HTTPError) as err:
        logging.error('Something went wrong while fetching the initial session ID')
        return None
    else:
        return session


def login():
    """Login as the configured user.

    :rtype (requests.Session, bool, str)
    """
    session = determine_session_id(requests.Session())
    if session is None:
        logging.error('Cannot authenticate without initial session ID')
        return None, False, None
    logging.debug('Attempting login...')
    try:
        response = session.post(QIS_URL_LOGIN, data={
            'username': QIS_USERNAME,
            'password': QIS_PASSWORD,
            'submit': 'Ok'
        })
        response.raise_for_status()
    except requests.RequestException as err:
        logging.error('Authentication failed: {0}'.format(err))
        session, redirect_url = None
    else:
        redirect_url = response.url if response.status_code == requests.codes.ok else None
        logging.info('Successfully logged in as ' + QIS_USERNAME)
    return (
        session,
        True if session else False,
        redirect_url
    )


def fetch_source(url, session=None):
    """Fetch the source of a given web page.

    :type url: str
    :type session: requests.Session
    :rtype (str)
    """
    if url is None:
        logging.warning('Cannot fetch page source: Invalid url')
        return None
    logging.debug('Fetching source from "{0}"'.format(url))
    try:
        response = session.get(url) if session is not None else requests.get(url)
        response.raise_for_status()
    except requests.RequestException as err:
        logging.error('Fetching source from "{0}" failed: {1}'.format(url, err))
        return None
    else:
        if response.status_code != requests.codes.ok:
            logging.warning('Fetching source of "{0}" returned HTTP {1} instead of {2}'.format(
                url, response.status_code, requests.codes.ok
            ))
    return response.text


def select(url, xpath, session=None):
    """Select an element on a given site via xpath.

    :type url: str
    :type xpath: str
    :type session: requests.Session
    :rtype (list)
    """
    if url is None or len(url) < 1:
        logging.warning('Cannot select "{0}" on {1}: Invalid URL'.format(xpath, url))
        return None
    try:
        response = session.get(url) if session is not None else requests.get(url)
        response.raise_for_status()
    except requests.RequestException as err:
        logging.error('Cannot select "{0}" on {1}: {2}'.format(xpath, url, err))
        return None
    else:
        response_source = response.text
    try:
        selected = html.fromstring(response_source).xpath(xpath)
    except (TypeError, XPathEvalError) as select_err:
        logging.error('Selection of "{0}" on {1} failed: {2}'.format(xpath, url, select_err))
        selected = None
    if selected is None or len(selected) < 1:
        logging.warning('No match for "{0}" on {1}'.format(xpath, url))
        return None
    return selected


def select_first(url, xpath, session=None):
    """Select the first element that matches the xpath on a given site.

    :type url: str
    :type xpath: str
    :type session: requests.Session
    """
    result = select(url, xpath, session)
    return result[0] if result else None


def fetch_grade_overview(session, base_url):
    """Fetch the source of the grade overview page.

    :type session: requests.Session
    :type base_url: str
    :rtype (str)
    """
    if base_url is None or QIS_URL_BASE not in base_url:
        logging.error('Unable to fetch grade overview: invalid base url')
        return None
    grade_overview_url = \
        select_first(
            select_first(
                select_first(base_url, SELECTOR_EXAM_MANAGEMENT_LINK, session),
                SELECTOR_GRADE_OVERVIEW_LINK, session),
            SELECTOR_GRADE_OVERVIEW_GRADUATION_LINK,
            session)
    logging.debug('Grade overview URL: ' + grade_overview_url)
    return fetch_source(grade_overview_url, session)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=LOGGING_LEVEL)
    bot_session, logged_in, red_url = login()
    if not logged_in:
        logging.error('Login as {user} failed'.format(user=QIS_USERNAME))
        sys.exit(1)
    grade_overview = fetch_grade_overview(bot_session, red_url)
