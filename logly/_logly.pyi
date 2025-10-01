"""Type stubs for the logly Rust extension module.

This module provides the core logging functionality implemented in Rust,
offering high-performance asynchronous logging with a Loguru-like API.
"""

from __future__ import annotations

__version__: str
"""The version string of the logly library."""

class PyLogger:
    """High-performance logger implemented in Rust with asynchronous writing.

    This class provides the core logging functionality with support for
    multiple sinks, log levels, structured logging, and async I/O for
    optimal performance.
    """

    def __init__(self) -> None:
        """Initialize a new PyLogger instance.

        Creates a logger with default configuration (INFO level, colored console output).
        """
        ...

    def add(
        self,
        sink: str,
        *,
        rotation: str | None = ...,
        size_limit: str | None = ...,
        filter_min_level: str | None = ...,
        filter_module: str | None = ...,
        filter_function: str | None = ...,
        async_write: bool = ...,
        date_style: str | None = ...,
        date_enabled: bool = ...,
        retention: int | None = ...,
    ) -> int:
        """Add a logging sink (output destination).

        Args:
            sink: Path to log file or "console" for stdout.
            rotation: Time-based rotation policy ("daily", "hourly", "minutely").
            size_limit: Maximum file size before rotation (e.g., "5KB", "10MB", "1GB").
            filter_min_level: Minimum log level for this sink (e.g., "INFO", "ERROR").
            filter_module: Only log messages from this module.
            filter_function: Only log messages from this function.
            async_write: Enable background async writing (default: True).
            date_style: Date format ("rfc3339", "local", "utc").
            date_enabled: Include timestamp in log output (default: False).
            retention: Number of rotated files to keep (older files auto-deleted).

        Returns:
            Handler ID that can be used to remove this sink later.
        """
        ...

    def configure(
        self,
        level: str = ...,
        color: bool = ...,
        json: bool = ...,
        pretty_json: bool = ...,
    ) -> None:
        """Configure global logger settings.

        Args:
            level: Default minimum log level ("TRACE", "DEBUG", "INFO", "SUCCESS",
                  "WARNING", "ERROR", "CRITICAL").
            color: Enable colored output for console logs.
            json: Output logs in JSON format.
            pretty_json: Format logs as pretty-printed JSON (more readable, higher cost).
        """
        ...

    def remove(self, handler_id: int) -> bool:
        """Remove a logging sink by its handler ID.

        Args:
            handler_id: The ID returned by add() when the sink was created.

        Returns:
            True if the sink was successfully removed, False otherwise.
        """
        ...

    def trace(self, message: str, /, **kwargs) -> None:
        """Log a message at TRACE level (most verbose).

        Args:
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def debug(self, message: str, /, **kwargs) -> None:
        """Log a message at DEBUG level.

        Args:
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def info(self, message: str, /, **kwargs) -> None:
        """Log a message at INFO level (general information).

        Args:
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def success(self, message: str, /, **kwargs) -> None:
        """Log a message at SUCCESS level (successful operations).

        Args:
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def warning(self, message: str, /, **kwargs) -> None:
        """Log a message at WARNING level.

        Args:
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def error(self, message: str, /, **kwargs) -> None:
        """Log a message at ERROR level.

        Args:
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def critical(self, message: str, /, **kwargs) -> None:
        """Log a message at CRITICAL level (most severe).

        Args:
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def log(self, level: str, message: str, /, **kwargs) -> None:
        """Log a message at a custom or aliased level.

        Args:
            level: Log level name (e.g., "INFO", "ERROR", or a custom alias).
            message: The log message.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def complete(self) -> None:
        """Flush all pending log messages and ensure they are written.

        This method should be called before application shutdown to ensure
        all buffered logs (especially from async sinks) are persisted.
        """
        ...

    def add_callback(self, callback: object) -> int:
        """Register a callback function to be invoked on every log message.

        The callback will be executed asynchronously in a background thread,
        ensuring zero impact on application performance.

        Args:
            callback: A callable that accepts a single dict argument containing
                     log record information (timestamp, level, message, and fields).

        Returns:
            Callback ID (integer) that can be used with remove_callback().

        Note:
            Callbacks execute in background threads and are thread-safe.
            If a callback raises an exception, it will be silently caught.
        """
        ...

    def remove_callback(self, callback_id: int) -> bool:
        """Remove a previously registered callback by its ID.

        Args:
            callback_id: The ID returned by add_callback() when registering.

        Returns:
            True if the callback was successfully removed, False otherwise.
        """
        ...

logger: PyLogger
"""The global PyLogger instance used by the logly library.

This is the main logger instance that provides the core logging functionality.
Use this instance directly or wrap it with _LoggerProxy for additional features."""
