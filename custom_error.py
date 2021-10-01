# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class DateError(Error):
    """
    """
    def __init__(self, message):
        # Call Exception.__init__(message)
        # to use the same Message header as the parent class
        super().__init__(message)
