import functools

import tablib
import zope.event

from qisbot import config
from qisbot import persistence
from qisbot import qis
from qisbot import scraper
from qisbot import events
from qisbot import models


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
        self._db_manager = persistence.DatabaseManager(database_path)
        self._scraper = scraper.Scraper()
        self.qis = qis.Qis(base_url=self.config.base_url, custom_scraper=self._scraper)
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
        """Fetch the exams extract from remote.

        New exams will be persisted, existing ones will be compared with their
        already-fetched equivalents and changes will be detected.
        """
        exams_extract = self.qis.exams_extract
        for exam in exams_extract:
            persisted_exam = self._db_manager.fetch_exam(exam.id)
            if persisted_exam:
                changes = models.compare_exams(old=persisted_exam, new=exam)
                if len(changes):
                    zope.event.notify(events.ExamChangedEvent(old_exam=persisted_exam, new_exam=exam, changes=changes))
                    # Persist the changes
                    update_changes = {}
                    for changed_field, values in changes.items():
                        update_changes[changed_field] = values[1]
                    self._db_manager.update_exam(exam.id, update_changes)
                    self._db_manager.commit()
            else:
                self._db_manager.persist_exam(exam)
                zope.event.notify(events.NewExamEvent(exam))

    def exams_extract_dataset(self, force_refresh=False) -> tablib.Dataset:
        """Get the exams extract as tabular dataset.

        Args:
            force_refresh: Refresh exams extract before processing it
        Returns:
            The resulting dataset
        """
        if force_refresh:
            self.refresh_exams_extract()
        exams_extract = self._db_manager.fetch_all_exams()
        dataset = tablib.Dataset()
        dataset.headers = [attr_name for attr_name in models.ExamData.__members__.keys()]
        for exam in exams_extract:
            row = []
            for attr_name in models.ExamData.__members__.keys():
                row.append(getattr(exam, attr_name))
            dataset.append(row)
        return dataset

    def print_exams_extract(self, force_refresh=False) -> ():
        """Print the exams extract as table to stdout.

        Args:
            force_refresh: Refresh exams extract before printing
        """
        print(self.exams_extract_dataset(force_refresh=force_refresh))
