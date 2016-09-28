import logging
import functools


def failsafe_notify(func):
    """Prevents exceptions during notify execution to crash the application.

    Occurring exceptions are logged as errors.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            logging.error(ex)

    return wrapper


from qisbot.notifies.email import *
from qisbot.notifies.stdout import *
