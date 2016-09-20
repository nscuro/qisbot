import typing

from qisbot import models


class BaseEvent(object):
    """Base class for all Events."""
    pass


class NewExamEvent(BaseEvent):
    """Event that notifies about new Exams."""

    def __init__(self, exam: models.Exam):
        """Initialize a new instance.

        Args:
            exam: The new exam
        """
        self.exam = exam


class ExamChangedEvent(BaseEvent):
    """Event that notifies about changes in Exams."""

    def __init__(self, old_exam: models.Exam, new_exam: models.Exam, changes: typing.Dict[str, typing.Tuple[str, str]]):
        """Initialize a new instance.

        Args:
            old_exam: Exam instance containing "old" data
            new_exam: Exam instance containing "new" data
            changes: The actual changes
        """
        self.old_exam = old_exam
        self.new_exam = new_exam
        self.changes = changes
