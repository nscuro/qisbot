import typing

from qisbot import config
from qisbot import models


class BaseEvent(object):
    """Base class for all Events."""

    def __init__(self, configuration: config.QisConfiguration):
        """Initialize a new instance.

        Args:
            configuration: An instance of the application's configuration
        """
        self._config = configuration

    @property
    def config(self):
        return self._config


class NewExamEvent(BaseEvent):
    """Event that notifies about new Exams."""

    def __init__(self, configuration: config.QisConfiguration, exam: models.Exam):
        """Initialize a new instance.

        Args:
            configuration: An instance of the application's configuration
            exam: The new exam
        """
        super().__init__(configuration)
        self.exam = exam


class ExamChangedEvent(BaseEvent):
    """Event that notifies about changes in Exams."""

    def __init__(self, configuration: config.QisConfiguration, old_exam: models.Exam, new_exam: models.Exam,
                 changes: typing.Dict[str, typing.Tuple[str, str]]):
        """Initialize a new instance.

        Args:
            configuration: An instance of the application's configuration
            old_exam: Exam instance containing "old" data
            new_exam: Exam instance containing "new" data
            changes: The actual changes
        """
        super().__init__(configuration)
        self.old_exam = old_exam
        self.new_exam = new_exam
        self.changes = changes
