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

    def add(  # pylint: disable=too-many-arguments
        self,
        sink: str,
        *,
        rotation: str | None = ...,
        size_limit: str | None = ...,
        filter_min_level: str | None = ...,
        filter_module: str | None = ...,
        filter_function: str | None = ...,
        async_write: bool = ...,
        buffer_size: int = ...,
        flush_interval: int = ...,
        max_buffered_lines: int = ...,
        date_style: str | None = ...,
        date_enabled: bool = ...,
        retention: int | None = ...,
        format: str | None = ...,  # pylint: disable=redefined-builtin
    ) -> int:
        """Add a logging sink (output destination).

        Args:
            sink: Path to log file or "console" for stdout.
            rotation: Time-based rotation policy ("daily", "hourly", "minutely").
            size_limit: Maximum file size before rotation (e.g., "5KB", "10MB", "1GB").
            filter_min_level: Exact log level for this sink. Only messages with this exact level will be logged.
            filter_module: Only log messages from this module.
            filter_function: Only log messages from this function.
            async_write: Enable background async writing (default: True).
            buffer_size: Buffer size in bytes for async writing (default: 8192).
            flush_interval: Flush interval in milliseconds for async writing (default: 1000).
            max_buffered_lines: Maximum number of buffered lines before blocking (default: 1000).
            date_style: Date format ("rfc3339", "local", "utc").
            date_enabled: Include timestamp in log output (default: False).
            retention: Number of rotated files to keep (older files auto-deleted).
            format: Custom format string with placeholders like "{level}", "{message}", "{time}", "{extra}", or any extra field key. Placeholders are case-insensitive and extra fields not used in the template are automatically appended.

        Returns:
            Handler ID that can be used to remove this sink later.
        """
        ...

    def configure(
        self,
        level: str = ...,
        color: bool = ...,
        level_colors: dict[str, str] | None = ...,
        json: bool = ...,
        pretty_json: bool = ...,
        console: bool = ...,
        show_time: bool = ...,
        show_module: bool = ...,
        show_function: bool = ...,
        console_levels: dict[str, bool] | None = ...,
        time_levels: dict[str, bool] | None = ...,
        color_levels: dict[str, bool] | None = ...,
        storage_levels: dict[str, bool] | None = ...,
    ) -> None:
        """Configure global logger settings.

        Args:
            level: Default minimum log level ("TRACE", "DEBUG", "INFO", "SUCCESS",
                  "WARNING", "ERROR", "CRITICAL").
            color: Enable colored output for console logs.
            level_colors: Dictionary mapping log levels to ANSI color codes or color names.
            json: Output logs in JSON format.
            pretty_json: Format logs as pretty-printed JSON (more readable, higher cost).
            console: Enable console output.
            show_time: Show timestamps in console output.
            show_module: Show module information in console output.
            show_function: Show function information in console output.
            console_levels: Dictionary mapping log levels to console output enable/disable.
            time_levels: Dictionary mapping log levels to time display enable/disable.
            color_levels: Dictionary mapping log levels to color enable/disable.
            storage_levels: Dictionary mapping log levels to file storage enable/disable.
        """
        ...

    def reset(self) -> None:
        """Reset logger configuration to default settings.

        Resets all logger settings to their default values, clearing any
        per-level controls and custom configurations.
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

    def trace(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at TRACE level (most verbose).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def debug(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at DEBUG level.

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def info(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at INFO level (general information).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def success(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at SUCCESS level (successful operations).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def warning(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at WARNING level.

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def error(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at ERROR level.

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def critical(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at CRITICAL level (most severe).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def log(self, level: str, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at a custom or aliased level.

        Args:
            level: Log level name (e.g., "INFO", "ERROR", or a custom alias).
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
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

