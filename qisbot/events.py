import typing
import functools

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
    print('[+] New Exam detected: ')
    for attr_name in models.ExamData.__members__.keys():
        attribute = getattr(event.exam, attr_name)
        if attribute and attribute != 'None':
            # Empty fields are omitted
            print('\t{}: {}'.format(attr_name, attribute))


@subscriber_of(NewExamEvent)
def on_new_exam_email(event: NewExamEvent) -> ():
    """Subscriber to NewExamEvent that notifies the user via E-Mail."""
    pass


@subscriber_of(ExamChangedEvent)
def on_exam_changed_stdout(event: ExamChangedEvent) -> ():
    """Subscriber of ExamChangedEvent that prints to stdout."""
    print('[*] Changed Exam detected: ')
    print('\t{} - {}'.format(event.old_exam.id, event.old_exam.name))
    for changed_attr, values in event.changes.items():
        print('\t- {}: {} -> {}'.format(changed_attr, values[0], values[1]))


@subscriber_of(ExamChangedEvent)
def on_exam_changed_email(event: ExamChangedEvent) -> ():
    """Subscriber to ExamChangedEvent that notifies the user via E-Mail."""
    pass
