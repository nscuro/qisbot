import typing
import smtplib
import email.mime.text
from contextlib import contextmanager

import zope.event.classhandler

from qisbot import models
from qisbot import events
from qisbot import config


@contextmanager
def _email_connection(conf: config.QisConfiguration) -> typing.Union[smtplib.SMTP, smtplib.SMTP_SSL]:
    """Open an SMTP connection based on the configuration and close it when leaving the context.

    Args:
        conf: The application's configuration (needed for E-Mail server & login data)
    """
    connection = None
    try:
        if conf.email_notify_ssl:
            connection = smtplib.SMTP_SSL(conf.email_notify_host, conf.email_notify_port)
        else:
            connection = smtplib.SMTP(conf.email_notify_host, conf.email_notify_port)
        connection.login(conf.email_notify_username, conf.email_notify_password)
        yield connection
    finally:
        if connection:
            connection.quit()


@zope.event.classhandler.handler(events.NewExamEvent)
def on_new_exam_email(event: events.NewExamEvent) -> ():
    message_content = """qisbot is excited to inform you that the result of your \"{}\" exam
    has just been published! Here is everything I know about it:\n\n""".format(event.exam.name)
    for attr_name in models.ExamData.__members__.keys():
        attribute = getattr(event.exam, attr_name)
        if attribute and attribute != 'None':
            message_content += '\t- {}: "{}"\n'.format(attr_name, attribute)
    message = email.mime.text.MIMEText(message_content, _subtype='plain')
    message['Subject'] = 'qisbot: The results of your "{}" exam have been published!'
    message['From'] = event.config.email_notify_username
    with _email_connection(event.config) as conn:
        conn.sendmail(event.config.email_notify_username, event.config.email_notify_destination, message.as_string())


@zope.event.classhandler.handler(events.ExamChangedEvent)
def on_exam_changed_email(event: events.ExamChangedEvent) -> ():
    message_content = """qisbot is happy to let you know that your \"{}\" exam was just updated!
        \nThe following changes have been made:\n""".format(event.old_exam.name)
    for changed_attr, values in event.changes.items():
        message_content += '\t- {}: "{}" -> "{}"\n'.format(changed_attr, values[0], values[1])
    message = email.mime.text.MIMEText(message_content, _subtype='plain')
    message['Subject'] = 'qisbot: Your "{}" exam has been updated!'.format(event.old_exam.name)
    message['From'] = event.config.email_notify_username
    with _email_connection(event.config) as conn:
        conn.sendmail(event.config.email_notify_username, event.config.email_notify_destination, message.as_string())
