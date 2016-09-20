from qisbot import events
from qisbot.notifies import subscriber_of


@subscriber_of(events.NewExamEvent)
def on_new_exam_email(event: events.NewExamEvent) -> ():
    pass


@subscriber_of(events.ExamChangedEvent)
def on_exam_changed_email(event: events.ExamChangedEvent) -> ():
    pass
