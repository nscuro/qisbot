import functools

from qisbot import events


def subscriber_of(event_type: events.BaseEvent):
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


from qisbot.notifies.email import *
from qisbot.notifies.stdout import *
