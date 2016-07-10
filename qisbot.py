#!/usr/bin/env python

import logging
import requests
from lxml import html
from os import environ


QIS_USERNAME = environ.get('QIS_USER') or None
QIS_PASSWORD = environ.get('QIS_PASS') or None

QIS_URL_BASE = 'https://qis.fh-kiel.de/qisserver'
QIS_URL_LOGIN = QIS_URL_BASE + '/rds?state=user&type=1&category=auth.login'
QIS_URL_INITIAL = QIS_URL_BASE + '/rds?state=user&type=0'
QIS_COOKIE_SESSIONID = 'JSESSIONID'

LOGGING_LEVEL = logging.DEBUG


def determine_session_id(from_url=None):
    """Determine the session ID by crunching the cookie of a given URL.

    :type from_url: str
    :rtype str
    """
    try:
        initial_response = requests.get(from_url or QIS_URL_INITIAL)
        initial_response.raise_for_status()
    except (ConnectionError, requests.HTTPError) as err:
        logging.error('Something went wrong while fetching the initial session ID')
        return None
    else:
        return initial_response.cookies.get(QIS_COOKIE_SESSIONID)


def login(session_id=None):
    """Login as the configured user.

    :type session_id: str
    :rtype (str, bool, str)
    """
    session_id = session_id or determine_session_id()
    if session_id is None:
        logging.error('Cannot attempt login without initial session ID')
        return None, False, None
    logging.debug('Attempting login with session ID ' + session_id)
    try:
        response = requests.post(QIS_URL_LOGIN, data={
            'username': QIS_USERNAME,
            'password': QIS_PASSWORD,
            'submit': 'Ok'
        }, cookies={QIS_COOKIE_SESSIONID: session_id}, allow_redirects=False)
        response.raise_for_status()
    except (ConnectionError, requests.HTTPError) as err:
        logging.error('Failed to authenticate: ' + err.message)
        session_id, redirect_url = None
    else:
        session_id = response.cookies.get(QIS_COOKIE_SESSIONID)
        redirect_url = response.url if response.status_code == requests.codes.found else None
    return (
        session_id,
        True if session_id else False,
        redirect_url
    )


if __name__ == '__main__':
    logging.basicConfig(filename='qisbot.log', level=LOGGING_LEVEL)
    session, logged_in, red_url = login()
