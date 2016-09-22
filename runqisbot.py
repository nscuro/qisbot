#!/usr/bin/env python

import sys
import os.path
import logging
import logging.config
import argparse

from qisbot.bot import Bot
from qisbot.notifies.email import test_connection

_root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default=os.path.join(_root_path, 'qisbot.ini'),
                        help='Path to the configuration file')
    parser.add_argument('--database', '-d', type=str, default=os.path.join(_root_path, 'qisbot.db'),
                        help='Path to the database file')
    parser.add_argument('--print', '-p', default=False, action='store_true',
                        help='Print the exams extract as table')
    parser.add_argument('--force-refresh', '-f', default=False, action='store_true',
                        help='Force a refresh of exams extract')
    parser.add_argument('--test-email', default=False, action='store_true', help='Test the email configuration')
    parser.add_argument('--log-config', type=str, default=os.path.join(_root_path, 'logging.ini'),
                        help='Path to the logging configuration file')
    return parser.parse_args()


def setup_logging(args: argparse.Namespace):
    config_path = getattr(args, 'log_config')
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path)
        logging.info('Logging configuration loaded from {}'.format(config_path))
    else:
        logfile_path = os.path.join(_root_path, 'qisbot.log')
        logging.basicConfig(filename=logfile_path, level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        logging.info('Using basic logging configuration. Logging to {}'.format(logfile_path))


if __name__ == '__main__':
    arguments = parse_arguments()
    bot = Bot(config_path=getattr(arguments, 'config'), database_path=getattr(arguments, 'database'))
    setup_logging(arguments)
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
