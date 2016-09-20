import zope.event.classhandler

from qisbot import models
from qisbot import events


@zope.event.classhandler.handler(events.NewExamEvent)
def on_new_exam_stdout(event: events.NewExamEvent) -> ():
    """Subscriber to NewExamEvent that prints to stdout."""
    print('[+] New Exam detected: ')
    for attr_name in models.ExamData.__members__.keys():
        attribute = getattr(event.exam, attr_name)
        if attribute and attribute != 'None':
            # Empty fields are omitted
            print('\t{}: {}'.format(attr_name, attribute))


@zope.event.classhandler.handler(events.ExamChangedEvent)
def on_exam_changed_stdout(event: events.ExamChangedEvent) -> ():
    """Subscriber of ExamChangedEvent that prints to stdout."""
    print('[*] Changed Exam detected: ')
    print('\t{} - {}'.format(event.old_exam.id, event.old_exam.name))
    for changed_attr, values in event.changes.items():
        print('\t- {}: {} -> {}'.format(changed_attr, values[0], values[1]))
