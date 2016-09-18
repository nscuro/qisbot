#!/usr/bin/env python

import argparse

from qisbot.bot import Bot


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default='./qisbot.ini', help='Path to the configuration file')
    parser.add_argument('--database', '-d', type=str, default='./qisbot.db', help='Path to the database file')
    parser.add_argument('--print', '-p', default=False, action='store_true',
                        help='Print the exams extract as table')
    parser.add_argument('--force-refresh', '-f', default=False, action='store_true',
                        help='Force a refresh of exams extract')
    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_arguments()
    bot = Bot(config_path=getattr(arguments, 'config'), database_path=getattr(arguments, 'database'))
    if getattr(arguments, 'print'):
        bot.print_exams_extract(force_refresh=getattr(arguments, 'force_refresh'))
    elif getattr(arguments, 'force_refresh'):
        # This will just perform any actions provided by subscribers of new/changed exam events
        bot.refresh_exams_extract()

