import zope.event.classhandler

from qisbot import events


@zope.event.classhandler.handler(events.NewExamEvent)
def on_new_exam_email(event: events.NewExamEvent) -> ():
    pass


@zope.event.classhandler.handler(events.ExamChangedEvent)
def on_exam_changed_email(event: events.ExamChangedEvent) -> ():
    pass
