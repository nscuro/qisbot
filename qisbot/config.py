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

    @property
    def notify_on_new(self) -> bool:
        return self.parser.getboolean('NOTIFICATIONS', 'on_new', fallback=False)

    @property
    def notify_on_changed(self) -> bool:
        return self.parser.getboolean('NOTIFICATIONS', 'on_changed', fallback=False)

    @property
    def notify_stdout(self) -> bool:
        return self.parser.getboolean('NOTIFICATIONS', 'stdout', fallback=False)

    @property
    def notify_email(self) -> bool:
        return self.parser.getboolean('NOTIFICATIONS', 'email', fallback=False)

    @property
    def email_notify_host(self) -> str:
        return self.parser.get('EMAIL NOTIFY', 'host')

    @property
    def email_notify_port(self) -> str:
        return self.parser.get('EMAIL NOTIFY', 'port')

    @property
    def email_notify_ssl(self) -> bool:
        return self.parser.getboolean('EMAIL NOTIFY', 'ssl')

    @property
    def email_notify_username(self) -> str:
        return self.parser.get('EMAIL NOTIFY', 'username')

    @property
    def email_notify_password(self) -> str:
        return self.parser.get('EMAIL NOTIFY', 'password')

    @property
    def email_notify_destination(self) -> str:
        return self.parser.get('EMAIL NOTIFY', 'destination')
