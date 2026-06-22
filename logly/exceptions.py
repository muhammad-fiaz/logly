"""Exception classes for the Logly logging library.

All Logly-specific exceptions inherit from :class:`LoglyError`, making it
easy to catch any Logly-related error with a single ``except`` clause.

Exception Hierarchy::

    LoglyError
    ├── SinkError
    │   ├── RotationError
    │   └── CompressionError
    ├── FormatterError
    ├── FilterError
    └── ConfigError
"""

from __future__ import annotations


class LoglyError(Exception):
    """Base class for all Logly Python exceptions.

    All Logly-specific exceptions inherit from this class, allowing
    users to catch any Logly error with ``except LoglyError``.
    """


class SinkError(LoglyError):
    """Raised when a sink cannot be configured or written.

    This exception is raised when there is an error communicating with
    a log sink (e.g., network failure, file system error).
    """


class FormatterError(LoglyError):
    """Raised when record formatting fails.

    This exception is raised when a custom formatter callable raises
    an error or returns an unexpected type.
    """


class FilterError(LoglyError):
    """Raised when a filter cannot be evaluated.

    This exception is raised when a custom filter callable raises
    an error during log record filtering.
    """


class ConfigError(LoglyError):
    """Raised when configuration validation fails.

    This exception is raised when invalid configuration options are
    provided to the logger or sink setup functions.
    """


class RotationError(SinkError):
    """Raised when file rotation fails.

    This exception is raised when the logger cannot rotate a log file
    (e.g., disk full, permission denied).
    """


class CompressionError(SinkError):
    """Raised when rotated file compression fails.

    This exception is raised when the logger cannot compress a rotated
    log file (e.g., compression library not available).
    """
