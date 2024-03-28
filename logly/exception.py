"""
Logly: A ready to go logging utility.

Copyright (c) 2023 Muhammad Fiaz

This file is part of Logly.

Logly is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published by
the Open Source Initiative.

You should have received a copy of the MIT License
along with Logly. If not, see <https://opensource.org/licenses/MIT>.
"""

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
