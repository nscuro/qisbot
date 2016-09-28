class ScraperException(IOError):
    """Raised when the Scraper class encounters an (internal) error."""
    pass


class NoSuchElementException(LookupError):
    """Raised when trying to access an element that was not found."""
    pass


class QisLoginFailedException(IOError):
    """Raised when logging in to the QIS system failed."""
    pass


class QisNotLoggedInException(BaseException):
    """Raised when trying to perform an action that requires a login without
    being logged in.
    """
    pass


class UnexpectedStateException(BaseException):
    """Raised when trying to perform an action which prerequisite is not satisfied."""
    pass


class PersistenceException(IOError):
    """Raised when a database related process or action failed."""
    pass
