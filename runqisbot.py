#!/usr/bin/env python

import argparse

from qisbot.bot import Bot


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default='./qisbot.ini', help='Path to the configuration file')
    parser.add_argument('--database', '-d', type=str, default='./qisbot.db', help='Path to the database file')
    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_arguments()
    bot = Bot(config_path=getattr(arguments, 'config'), database_path=getattr(arguments, 'database'))
