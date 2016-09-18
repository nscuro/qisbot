import typing
import configparser


class QisConfiguration(object):
    def __init__(self, config_path: str):
        if not config_path:
            raise ValueError('Path to configuration file must not be None or empty')
        self.parser = self.load(config_path)

    @staticmethod
    def load(config_path: str) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        with open(config_path, 'r') as config_file:
            parser.read_file(config_file)
        return parser

    @property
    def base_url(self) -> typing.Optional[str]:
        return self.parser.get('QIS', 'baseUrl')

    @property
    def username(self) -> typing.Optional[str]:
        return self.parser.get('QIS', 'username')

    @property
    def password(self) -> typing.Optional[str]:
        return self.parser.get('QIS', 'password')
