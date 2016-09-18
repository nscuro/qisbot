import functools

from qisbot import config
from qisbot import persistence
from qisbot import qis
from qisbot import scraper


def ensure_login(func):
    """Make sure to be logged in before performing a given action."""

    @functools.wraps(func)
    def login(*args, **kwargs):
        self = args[0]  # type: Bot
        if not isinstance(self, Bot):
            raise TypeError('@ensure_login only works for Bot instances')
        if not self.qis.is_logged_in:
            self.qis.login(self.config.username, self.config.password)
        return func(*args, **kwargs)

    return login


class Bot(object):
    def __init__(self, config_path: str, database_path: str):
        """Initialize a new Bot instance.

        Args:
            config_path: Path to the configuration file to use
            database_path: Path to the database file to use
        Raises:
            ValueError: When config path or database path were not provided
        """
        if not config_path:
            raise ValueError('config_path must not be None or empty')
        elif not database_path:
            raise ValueError('database_path must not be None or empty')
        self.config = config.QisConfiguration(config_path)
        self.db_manager = persistence.DatabaseManager(database_path)
        self.scraper = scraper.Scraper()
        self.qis = qis.Qis(base_url=self.config.base_url, custom_scraper=self.scraper)

    @ensure_login
    def refresh_exams_extract(self):
        exams_extract = self.qis.exams_extract
        for exam in exams_extract:
            # TODO Compare before inserting
            self.db_manager.insert_exam(exam)
