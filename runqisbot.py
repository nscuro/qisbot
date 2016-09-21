#!/usr/bin/env python

import sys
import argparse

from qisbot.bot import Bot
from qisbot.notifies.email import test_connection


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default='./qisbot.ini', help='Path to the configuration file')
    parser.add_argument('--database', '-d', type=str, default='./qisbot.db', help='Path to the database file')
    parser.add_argument('--print', '-p', default=False, action='store_true',
                        help='Print the exams extract as table')
    parser.add_argument('--force-refresh', '-f', default=False, action='store_true',
                        help='Force a refresh of exams extract')
    parser.add_argument('--test-email', default=False, action='store_true', help='Test the email configuration')
    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_arguments()
    bot = Bot(config_path=getattr(arguments, 'config'), database_path=getattr(arguments, 'database'))
    if getattr(arguments, 'test_email'):
        if test_connection(bot.config):
            print('[*] I was able to perform a login using the provided E-Mail configuration.')
            sys.exit(0)
        else:
            print('[x] I wasn\'t able to login using the provided E-Mail configuration.')
            sys.exit(2)
    if getattr(arguments, 'force_refresh'):
        # This will just perform any actions provided by subscribers of new/changed exam events
        bot.refresh_exams_extract()
    if getattr(arguments, 'print'):
        bot.print_exams_extract(force_refresh=getattr(arguments, 'force_refresh'))
