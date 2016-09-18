import functools

import zope.event

from qisbot import config
from qisbot import persistence
from qisbot import qis
from qisbot import scraper
from qisbot import events


def ensure_login(func):
    """Make sure to be logged in before performing a given action."""

    @functools.wraps(func)
    def login(*args, **kwargs):
        bot = args[0]  # type: Bot
        if not isinstance(bot, Bot):
            raise TypeError('@ensure_login only works for Bot instances')
        if not bot.qis.is_logged_in:
            bot.qis.login(bot.config.username, bot.config.password)
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
        self._register_event_subscribers()

    def _register_event_subscribers(self):
        """Register event subscribers based on the configuration given."""
        if self.config.notify_on_new:
            if self.config.notify_stdout:
                zope.event.subscribers.append(events.on_new_exam_stdout)
            if self.config.notify_email:
                pass
        if self.config.notify_on_changed:
            if self.config.notify_stdout:
                zope.event.subscribers.append(events.on_exam_changed_stdout)
            if self.config.notify_email:
                zope.event.subscribers.append(events.on_exam_changed_email)

    @ensure_login
    def refresh_exams_extract(self) -> ():
        """Fetch the exams extract from remote and persist it.

        TODO: Detect changes and notify the user.
        """
        exams_extract = self.qis.exams_extract
        for exam in exams_extract:
            persisted_exam = self.db_manager.fetch_exam(exam.id)
            if persisted_exam:
                # TODO: Detect changes
                pass
            else:
                self.db_manager.persist_exam(exam)
