"""Logly - A high-performance Rust-powered logging library for Python.

Logly provides a clean, intuitive API with 10 built-in log levels,
multiple sink types, context binding, structured logging,
and integrations for FastAPI, Django, stdlib logging, and Rich.

Usage::

    from logly import logger

    logger.info("Hello from Logly")
    logger.opt(exception=True).error("Something went wrong")

Attributes:
    logger: The default module-level Logger instance.
    Logger: The Logger class for creating custom instances.
    PrettyJsonConfig: Configuration model for pretty-printed JSON output.
    __version__: The current version of the logly package.
"""

from __future__ import annotations

from logly._logly import (
    __version__,
    inspect_level,
    list_levels,
    register_custom_level,
)
from logly.exceptions import (
    CompressionError,
    ConfigError,
    FilterError,
    FormatterError,
    LoglyError,
    RotationError,
    SinkError,
)
from logly.logger import Logger, logger
from logly.models import PrettyJsonConfig

__all__ = [
    "CompressionError",
    "ConfigError",
    "FilterError",
    "FormatterError",
    "Logger",
    "LoglyError",
    "PrettyJsonConfig",
    "RotationError",
    "SinkError",
    "__version__",
    "inspect_level",
    "list_levels",
    "logger",
    "register_custom_level",
]
