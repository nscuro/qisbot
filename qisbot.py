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

import os
import sys
import json
import logging
import requests
import argparse
from lxml import html
from tabulate import tabulate
from collections import OrderedDict
from lxml.etree import XPathEvalError


# User credentials
QIS_USERNAME = os.environ.get('QIS_USER') or None
QIS_PASSWORD = os.environ.get('QIS_PASS') or None

# Static urls
QIS_URL_BASE = 'https://qis.fh-kiel.de/qisserver'
QIS_URL_LOGIN = QIS_URL_BASE + '/rds?state=user&type=1&category=auth.login'
QIS_URL_INITIAL = QIS_URL_BASE + '/rds?state=user&type=0'

# XPath selectors
SELECTOR_EXAM_MANAGEMENT_LINK = '//a[contains(text(), "Prüfungsverwaltung")]/@href'
SELECTOR_GRADE_OVERVIEW_LINK = '//a[contains(text(), "Notenspiegel")]/@href'
SELECTOR_GRADE_OVERVIEW_GRADUATION_LINK = '//a[contains(@title, "Leistungen anzeigen")]/@href'
SELECTOR_GRADES_TABLE = '//form/table[2]'
SELECTOR_GRADES_TABLE_CELLS = './/*[@class = "tabelle1_alignleft" or @class = "tabelle1_aligncenter" ' \
                              'or @class = "tabelle1_alignright"]'

# Index-based mapping of grade information
GRADE_MAPPING = [
    'exam_id',
    'exam_title',
    'exam_vert',
    'exam_ruling',
    'attempt',
    'rejection',
    'semester',
    'appointment',
    'grade',
    'points',
    'ects',
    'status',
    'approved'
]


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
    except (requests.ConnectionError, requests.HTTPError):
        logging.error('Something went wrong while fetching the initial session ID')
        return None
    else:
        return session


def login(user=None, password=None):
    """Login as the configured user.

    :type user: str
    :type password: str
    :rtype (requests.Session, bool, str)
    """
    if user is None:
        logging.warning('No username specified, falling back to QIS_USERNAME')
        user = QIS_USERNAME
    if password is None:
        logging.warning('No password specified, falling back to QIS_PASSWORD')
        password = QIS_PASSWORD
    session = determine_session_id(requests.Session())
    if session is None:
        logging.error('Cannot authenticate without initial session ID')
        return None, False, None
    logging.debug('Attempting login...')
    try:
        response = session.post(QIS_URL_LOGIN, data={
            'username': user,
            'password': password,
            'submit': 'Ok'
        })
        response.raise_for_status()
    except requests.RequestException as err:
        logging.error('Authentication failed: {0}'.format(err))
        session, redirect_url = None
    else:
        redirect_url = response.url if response.status_code == requests.codes.ok else None
        logging.info('Successfully logged in as ' + user)
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
    :rtype html.HtmlElement
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


def map_grade_row(row):
    """Maps the cell content of a given table row.

    :type row: html.HtmlElement
    :rtype (dict)
    """
    row_cells = row.xpath(SELECTOR_GRADES_TABLE_CELLS)
    if len(row_cells) < 1:
        return None
    return {
        key: value for (key, value) in map(
            lambda x: (GRADE_MAPPING[row_cells.index(x)], x.text_content().strip() if x.text != '&nbsp' else None),
            row_cells
        )
    }


def parse_grades(source):
    """Parse grades from page source.

    :type source: str
    :rtype (list)
    """
    if source is None:
        logging.error('Cannot parse grades: No grade overview page source')
        return False
    logging.debug('Parsing grades from page source')
    grade_tree = html.fromstring(source)
    try:
        grades_table = grade_tree.xpath(SELECTOR_GRADES_TABLE)
    except XPathEvalError as eval_err:
        logging.error('Cannot parse grades: {0}'.format(eval_err))
        return None
    if grades_table is None or len(grades_table) < 1:
        logging.error('Cannot parse grades: Unable to locate grades table')
        return None
    parsed_grades = list(
        filter(
            lambda x: x is not None and x.get('grade') != '',
            map(map_grade_row, grades_table[0].xpath('.//tr'))
        )
    )
    logging.info('Successfully parsed {0} grades'.format(len(parsed_grades)))
    return parsed_grades


def detect_changes(grades_old, grades_new):
    """Detect changes in two list of grades.

    Note that no changes will be detected if grades_new contains
    less elements than grades_old. As deletion of grades should be
    very unlikely, this does not really matter, should be noted though.

    :type grades_old: list
    :type grades_new: list
    :rtype (list)
    """
    return list(filter(lambda x: x not in grades_old, grades_new)) + \
        list(filter(lambda x: x not in grades_new, grades_old))


def export_json(grades, destination):
    """Export a grade dictionary as JSON file.

    :type grades: list
    :type destination: str
    :rtype (bool)
    """
    if os.path.exists(destination):
        logging.warning('File "{0}" already exists and will be overwritten'.format(destination))
    if os.path.exists(destination) and not os.access(destination, os.W_OK):
        logging.error('Cannot export grades to "{0}": No write permission'.format(destination))
        return False
    logging.debug('Exporting grades to "{0}"'.format(destination))
    with open(destination, 'w') as dest_file:
        json.dump(grades, dest_file, indent=True)
    logging.info('Successfully exported grades to "{0}"'.format(destination))
    return True


def import_json(source):
    """Import grades data from a given JSON file.

    :type source: str
    :rtype (list)
    """
    if not os.path.exists(source):
        logging.error('Cannot import "{0}": File does not exist'.format(source))
        return None
    elif not os.access(source, os.R_OK):
        logging.error('Cannot import "{0}": No read permission'.format(source))
        return None
    logging.debug('Importing grades from "{0}"'.format(source))
    with open(source, 'r') as source_file:
        grades = json.load(source_file)
    return grades


def tabulate_grades(grades):
    """Present grade data in a fancy table.

    :type grades: list
    :rtype (str)
    """
    if grades is None:
        logging.warning('Cannot tabulate grades: No grade data')
        return None
    table = OrderedDict()
    table.update(list(map(lambda key: (key, list(map(lambda grade: grade.get(key), grades))), GRADE_MAPPING)))
    table = OrderedDict((key, values) for (key, values) in table.items() if None not in values and '' not in values)
    return tabulate(table, headers='keys', tablefmt='fancy_grid')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--username', '-u', help='The username', type=str)
    argparser.add_argument('--password', '-p', help='The password', type=str)
    argparser.add_argument('--export', '-e', help='Export grades to JSON file', type=str)
    argparser.add_argument('--compare', '-c', help='Compare fetched grades with JSON file', type=str)
    argparser.add_argument('--tabulate', '-t', action='store_true', help='Display grades in a table')
    argparser.add_argument('--debug', '-d', action='store_true', help='Show debug messages')
    args = argparser.parse_args()
    if (not QIS_USERNAME or not QIS_PASSWORD) and (not args.username or not args.password):
        argparser.print_help()
        sys.exit(2)
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG if args.debug else logging.ERROR)
    bot_session, logged_in, red_url = login(args.username, args.password)
    if not logged_in:
        logging.error('Login as {user} failed'.format(user=args.username or QIS_USERNAME))
        sys.exit(1)
    fetched_grades = parse_grades(fetch_grade_overview(bot_session, red_url))
    if args.export:
        if not export_json(fetched_grades, args.export):
            sys.exit(1)
    elif args.compare:
        old_grades = import_json(args.compare)
        if old_grades is None:
            logging.error('Unable to compare grades: Importing old grades failed')
            sys.exit(1)
        compare_result = detect_changes(old_grades, fetched_grades)
        if len(compare_result) < 1:
            print('No new grades found. Here are your current grades:\n')
            print(tabulate_grades(fetched_grades) if args.tabulate else fetched_grades)
            sys.exit(0)
        else:
            print(tabulate_grades(compare_result) if args.tabulate else compare_result)
            sys.exit(0)
    else:
        print(tabulate_grades(fetched_grades) if args.tabulate else fetched_grades)
