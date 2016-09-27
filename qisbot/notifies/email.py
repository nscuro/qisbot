import random
import typing
import smtplib
import email.mime.text
from contextlib import contextmanager

import zope.event.classhandler

from qisbot import models
from qisbot import events
from qisbot import config

_emotions = [
    'happy',
    'pumped',
    'excited',
    'thrilled',
    'pleased'
]

_actions = [
    'inform you',
    'let you know',
]

_new_exam_message = ('qisbot is {emotion} to {action} that the result of your "{exam}" exam '
                     'has just been published.\nYou may want to check it out yourself, but I '
                     'can show you what I know about it:\n')
_updated_exam_message = ('qisbot is {emotion} to {action} that your "{exam}" exam has just\n'
                         'been updated! I noticed the following changes:\n')


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
    """Notify the user about a newly published exam result via E-Mail."""
    if not event.config.notify_email:
        return
    message_content = _new_exam_message.format(emotion=random.choice(_emotions), action=random.choice(_actions),
                                               exam=event.exam.name)
    for attr_name in models.ExamData.__members__.keys():
        attribute = getattr(event.exam, attr_name)
        if attribute and attribute != 'None':
            message_content += '\t- {}: "{}"\n'.format(attr_name, attribute)
    message = email.mime.text.MIMEText(message_content, _subtype='plain')
    message['Subject'] = 'qisbot: The results of your "{}" exam have been published!'.format(event.exam.name)
    message['From'] = event.config.email_notify_username
    with _email_connection(event.config) as conn:
        conn.sendmail(event.config.email_notify_username, event.config.email_notify_destination, message.as_string())


@zope.event.classhandler.handler(events.ExamChangedEvent)
def on_exam_changed_email(event: events.ExamChangedEvent) -> ():
    """Notify the user about an updated exam result via E-Mail."""
    if not event.config.notify_email:
        return
    message_content = _updated_exam_message.format(emotion=random.choice(_emotions), action=random.choice(_actions),
                                                   exam=event.old_exam.name)
    for changed_attr, values in event.changes.items():
        message_content += '\t- {}: "{}" -> "{}"\n'.format(changed_attr, values[0], values[1])
    message = email.mime.text.MIMEText(message_content, _subtype='plain')
    message['Subject'] = 'qisbot: Your "{}" exam has been updated!'.format(event.old_exam.name)
    message['From'] = event.config.email_notify_username
    with _email_connection(event.config) as conn:
        conn.sendmail(event.config.email_notify_username, event.config.email_notify_destination, message.as_string())


def test_connection(conf: config.QisConfiguration, print_exception=False) -> bool:
    """Test the given E-Mail configuration by performing a login with it.

    Args:
        conf: The configuration containing connection & login data
        print_exception: Write the exception to stdout when one occurs
    Returns:
        False when the data is invalid, otherwise True
    """
    try:
        with _email_connection(conf):
            pass
        return True
    except Exception as ex:
        if print_exception:
            print(ex)
        return False
