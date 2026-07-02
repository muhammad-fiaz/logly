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
    HttpJsonSink,
    SyslogSink,
    TcpSink,
    UdpSink,
    __version__,
    colorize,
    format_exception_text,
    inspect_level,
    list_levels,
    paint_themed,
    parse_compression_str,
    parse_retention_str,
    parse_rotation_str,
    register_custom_level,
    render_message,
    resolve_level_name,
    strip_rich_tags,
    unsupported,
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
from logly.logger import Level, Logger, logger
from logly.models import PrettyJsonConfig

__all__ = [
    "CompressionError",
    "ConfigError",
    "FilterError",
    "FormatterError",
    "HttpJsonSink",
    "Level",
    "Logger",
    "LoglyError",
    "PrettyJsonConfig",
    "RotationError",
    "SinkError",
    "SyslogSink",
    "TcpSink",
    "UdpSink",
    "__version__",
    "colorize",
    "format_exception_text",
    "inspect_level",
    "list_levels",
    "logger",
    "paint_themed",
    "parse_compression_str",
    "parse_retention_str",
    "parse_rotation_str",
    "register_custom_level",
    "render_message",
    "resolve_level_name",
    "strip_rich_tags",
    "unsupported",
]
