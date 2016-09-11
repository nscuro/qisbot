class InvalidSessionError(ValueError):
    """Raised when trying to perform actions that require a login with
    an invalid or expired session.
    """
