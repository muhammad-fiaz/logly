class LoglyException(Exception):
    """
    Base exception class for Logly. All specific Logly exceptions should inherit from this class.
    """
    def __init__(self, message):
        """
        Initialize a LoglyException.

        Parameters:
        - message (str): The error message.
        """
        super().__init__(message)


class FilePathNotFoundException(LoglyException):
    """
    Exception raised when the specified file path is not found.
    """
    pass


class FileCreationError(LoglyException):
    """
    Exception raised when there is an error creating or writing to the log file.
    """
    pass


class FileAccessError(LoglyException):
    """
    Exception raised when there is an error accessing the log file.
    """
    pass


class InvalidConfigError(LoglyException):
    """
    Exception raised for invalid Logly configuration.
    """
    pass


class InvalidLogLevelError(LoglyException):
    """
    Exception raised when an invalid log level is provided.
    """
    pass
