import functools

from qisbot import models


class BaseEvent(object):
    """Base class for all Events."""
    pass


class NewExamEvent(BaseEvent):
    """Event that notifies about new Exams."""

    def __init__(self, exam: models.Exam):
        self.exam = exam


class ExamChangedEvent(BaseEvent):
    """Event that notifies about changes in Exams."""

    def __init__(self, old_exam: models.Exam, new_exam: models.Exam):
        self.old_exam = old_exam
        self.new_exam = new_exam


def subscriber_of(event_type: BaseEvent):
    """Restrict the decorated subscriber function to the given Event."""

    def decorator(func):
        @functools.wraps(func)
        def verify_event(*args, **kwargs):
            event = args[0]
            if not isinstance(event, event_type):
                return
            return func(*args, **kwargs)

        return verify_event

    return decorator


@subscriber_of(NewExamEvent)
def on_new_exam_stdout(event: NewExamEvent) -> ():
    """Subscriber to NewExamEvent that prints to stdout."""
    pass


@subscriber_of(ExamChangedEvent)
def on_exam_changed_stdout(event: ExamChangedEvent) -> ():
    """Subscriber of ExamChangedEvent that prints to stdout."""
    pass


@subscriber_of(ExamChangedEvent)
def on_exam_changed_email(event: ExamChangedEvent) -> ():
    """Subscriber to ExamChangedEvent that notifies the user via E-Mail."""
    pass
