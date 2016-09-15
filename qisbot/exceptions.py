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
    """ """
    pass


class UnexpectedStateException(BaseException):
    """ """
    pass
