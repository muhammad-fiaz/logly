from __future__ import annotations

from collections.abc import Callable, Generator
from typing import TypedDict

__version__: str
"""The version string of the logly library."""

class SearchResult(TypedDict):
    """Result of a log search operation."""

    line: int
    content: str
    match: str
    context_before: list[str] | None
    context_after: list[str] | None

class PyLogger:
    """High-performance logger implemented in Rust with asynchronous writing.

    This class provides the core logging functionality with support for
    multiple sinks, log levels, structured logging, and async I/O for
    optimal performance.
    """

    def __init__(self, auto_update_check: bool = True) -> None:
        """Initialize a new PyLogger instance.

        Args:
            auto_update_check: Enable automatic version checking on startup. Defaults to True.

        Creates a logger with default configuration (INFO level, colored console output).
        """
        ...

    def add(  # pylint: disable=too-many-arguments
        self,
        sink: str | None,
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
        json: bool = ...,
    ) -> int:
        """Add a logging sink (output destination).

        Args:
            sink: Path to log file or "console" for stdout.
            rotation: Time-based rotation policy ("daily", "hourly", "minutely").
            size_limit: Maximum file size before rotation (e.g., "5KB", "10MB", "1GB").
            filter_min_level: Exact log level for this sink ("TRACE", "DEBUG", "INFO",
                            "SUCCESS", "WARNING", "ERROR", "CRITICAL", "FAIL").
                            Only messages with this exact level will be logged.
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
            json: Enable JSON output format (default: False).

        Returns:
            Handler ID that can be used to remove this sink later.
        """
        ...

    def configure(
        self,
        level: str | None = ...,
        color: bool = ...,
        level_colors: dict[str, str] | None = ...,
        json: bool = ...,
        pretty_json: bool = ...,
        console: bool = ...,
        show_time: bool = ...,
        show_module: bool = ...,
        show_function: bool = ...,
        show_filename: bool = ...,
        show_lineno: bool = ...,
        console_levels: dict[str, bool] | None = ...,
        time_levels: dict[str, bool] | None = ...,
        color_levels: dict[str, bool] | None = ...,
        storage_levels: dict[str, bool] | None = ...,
        color_callback: Callable[[str, str], str] | None = ...,
        auto_sink: bool = ...,
        auto_sink_levels: dict[str, str | dict[str, object]] | None = ...,
    ) -> None:
        """Configure global logger settings.

        Args:
            level: Default minimum log level ("TRACE", "DEBUG", "INFO", "SUCCESS",
                  "WARNING", "ERROR", "CRITICAL", "FAIL").
            color: Enable colored output for console logs. When enabled without
                  custom level_colors, default colors are applied:
                  - TRACE: Cyan, DEBUG: Blue, INFO: White, SUCCESS: Green,
                  - WARNING: Yellow, ERROR: Red, CRITICAL: Bright Red, FAIL: Magenta.
            level_colors: Dictionary mapping log levels to ANSI color codes or color names.
                         When not provided and color=True, default colors are used.
            json: Output logs in JSON format.
            pretty_json: Format logs as pretty-printed JSON (more readable, higher cost).
            console: Enable console output.
            show_time: Show timestamps in console output.
            show_module: Show module information in console output.
            show_function: Show function information in console output.
            show_filename: Show filename information in console output.
            show_lineno: Show line number information in console output.
            console_levels: Dictionary mapping log levels to console output enable/disable.
            time_levels: Dictionary mapping log levels to time display enable/disable.
            color_levels: Dictionary mapping log levels to color enable/disable.
            storage_levels: Dictionary mapping log levels to file storage enable/disable.
            color_callback: Custom color formatting function with signature (level: str, text: str) -> str.
                           If provided, this function is used instead of built-in ANSI coloring.
                           Allows integration with external color libraries like Rich, colorama, etc.
                           When provided, level_colors parameter is ignored.
            auto_sink: Automatically create a console sink if no sinks exist (default: True).
                      When True and no sinks have been added, a console sink is created automatically.
                      Set to False if you want full manual control over sinks.
            auto_sink_levels: Dictionary mapping log levels to file paths or configuration dicts.
                             Automatically creates file sinks for specified levels without manual logger.add() calls.
                             Keys are level names ("DEBUG", "INFO", etc.), values can be:
                             - str: Simple file path (e.g., "logs/debug.log")
                             - dict: Advanced config with rotation, retention, json, etc.
                             Example: {"DEBUG": "logs/debug.log", "ERROR": {"path": "logs/error.log", "rotation": "daily"}}
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

    def remove_all(self) -> int:
        """Remove all logging sinks.

        Clears all registered sinks (console and file outputs). This is useful
        for cleanup or when you want to reconfigure all logging outputs.

        Returns:
            The number of sinks that were removed.
        """
        ...

    def sink_count(self) -> int:
        """Get the number of active sinks.

        Returns the count of all registered sinks (file and console outputs).

        Returns:
            The number of active sinks.
        """
        ...

    def list_sinks(self) -> list[int]:
        """List all active sink handler IDs.

        Returns a list of handler IDs for all registered sinks.

        Returns:
            List of handler IDs (as integers).
        """
        ...

    def sink_info(self, handler_id: int) -> dict[str, str] | None:
        """Get detailed information about a specific sink.

        Args:
            handler_id: Handler ID returned by add().

        Returns:
            Dictionary with sink information, or None if handler ID not found.
        """
        ...

    def all_sinks_info(self) -> list[dict[str, str]]:
        """Get information about all active sinks.

        Returns:
            List of sink information dictionaries.
        """
        ...

    def delete(self, handler_id: int) -> bool:
        """Delete the log file for a specific sink.

        Args:
            handler_id: Handler ID of the sink whose log file should be deleted.

        Returns:
            True if the file was successfully deleted, False otherwise.
        """
        ...

    def delete_all(self) -> int:
        """Delete all log files from all sinks.

        Returns:
            The number of files successfully deleted.
        """
        ...

    def clear(self) -> None:
        """Clear the console display.

        This is a platform-specific operation that clears the terminal screen.
        """
        ...

    def read(self, handler_id: int) -> str | None:
        """Read log content from a specific sink's file.

        Args:
            handler_id: Handler ID of the sink whose log file should be read.

        Returns:
            The log file content as a string, or None if the file doesn't exist.
        """
        ...

    def read_all(self) -> dict[int, str]:
        """Read log content from all sinks.

        Returns:
            Dictionary mapping handler IDs to their log file contents.
        """
        ...

    def file_size(self, handler_id: int) -> int | None:
        """Get the file size of a specific sink's log file in bytes.

        Args:
            handler_id: The unique identifier of the sink.

        Returns:
            File size in bytes, or None if not found.
        """
        ...

    def file_metadata(self, handler_id: int) -> dict[str, str] | None:
        """Get detailed metadata for a specific sink's log file.

        Args:
            handler_id: The unique identifier of the sink.

        Returns:
            Dictionary with file metadata (size, created, modified, path), or None.
        """
        ...

    def read_lines(self, handler_id: int, start: int, end: int) -> str | None:
        """Read specific lines from a sink's log file.

        Args:
            handler_id: The unique identifier of the sink.
            start: Starting line number (1-indexed, negative for end-relative).
            end: Ending line number (inclusive, negative for end-relative).

        Returns:
            Selected lines joined with newlines, or None if not found.
        """
        ...

    def line_count(self, handler_id: int) -> int | None:
        """Count the number of lines in a sink's log file.

        Args:
            handler_id: The unique identifier of the sink.

        Returns:
            Number of lines, or None if not found.
        """
        ...

    def read_json(self, handler_id: int, pretty: bool = False) -> str | None:
        """Read and parse JSON log file.

        Args:
            handler_id: The unique identifier of the sink.
            pretty: If True, returns pretty-printed JSON.

        Returns:
            JSON string, or None if not found.
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

    def fail(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at FAIL level (operation failures).

        Use this for operation failures that are distinct from errors.
        Displayed with magenta color by default to distinguish from ERROR.

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

    def _log_with_stdout(self, level: str, msg: str, stdout: object, **kwargs: object) -> None:
        """Log a message directly to a specific stdout object (for testing).

        This is an internal method used for testing color callbacks and other
        output formatting functionality.

        Args:
            level: Log level string
            msg: Log message
            stdout: Python stdout object to write to
            **kwargs: Additional context fields
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

    def enable(self) -> None:
        """Enable logging for this logger instance.

        When disabled, all log messages are silently ignored.
        """
        ...

    def disable(self) -> None:
        """Disable logging for this logger instance.

        When disabled, all log messages are silently ignored without
        any performance overhead from formatting or serialization.
        """
        ...

    def level(self, name: str, mapped_to: str) -> None:
        """Register a custom level name as an alias to an existing level.

        Allows creating custom level names that map to built-in levels.
        Use with the log() method to log at custom levels.

        Args:
            name: The custom level name/alias to create.
            mapped_to: The existing level to map to ("TRACE", "DEBUG", "INFO",
                      "SUCCESS", "WARNING", "ERROR", "CRITICAL").
        """
        ...

    def bind(self, **kwargs: object) -> PyLogger:
        """Create a new logger instance with additional context fields bound.

        Bound context fields are automatically attached to all log messages
        from this logger instance, providing a thread-safe way to add context.

        Args:
            **kwargs: Key-value pairs to bind as context fields.

        Returns:
            A new logger instance with the additional context bound.
        """
        ...

    def contextualize(self, **kwargs: object) -> Generator[None, None, None]:
        """Context manager to temporarily attach context fields.

        Unlike bind(), contextualize() modifies the current logger instance
        within a context block, automatically restoring original state on exit.

        Args:
            **kwargs: Key-value pairs to temporarily attach as context fields.

        Yields:
            None
        """
        ...

    def exception(self, message: str = "", /, **kwargs: object) -> None:
        """Log an exception with traceback at ERROR level.

        Automatically captures the current exception traceback and logs it.
        Must be called from within an exception handler.

        Args:
            message: Optional message prefix before the traceback.
            **kwargs: Additional context fields to attach to the log record.
        """
        ...

    def catch(
        self, *, reraise: bool = False
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator or context manager to automatically log exceptions.

        Can be used as a decorator on functions or as a context manager.
        By default, catches and logs exceptions without re-raising them.

        Args:
            reraise: If True, re-raise the exception after logging (default: False).

        Returns:
            A context manager/decorator that catches and logs exceptions.
        """
        ...

    def _reset_for_tests(self) -> None:
        """Reset internal state for testing purposes.

        WARNING: This is for internal testing only and should not be used
        in production code. It does not reset the global tracing subscriber.
        """
        ...

    def enable_sink(self, sink_id: int) -> bool:
        """Enable a specific sink by its handler ID.

        When a sink is enabled, log messages will be written to it.
        Sinks are enabled by default when created.

        Args:
            sink_id: The handler ID of the sink to enable.

        Returns:
            True if the sink was found and enabled, False if not found.

        Example:
            >>> sink_id = logger.add("app.log")
            >>> logger.disable_sink(sink_id)
            >>> logger.info("Not logged")  # Sink disabled
            >>> logger.enable_sink(sink_id)
            >>> logger.info("Logged")  # Sink re-enabled
        """
        ...

    def disable_sink(self, sink_id: int) -> bool:
        """Disable a specific sink by its handler ID.

        When a sink is disabled, log messages will not be written to it,
        but the sink remains registered and can be re-enabled later.

        Args:
            sink_id: The handler ID of the sink to disable.

        Returns:
            True if the sink was found and disabled, False if not found.

        Example:
            >>> sink_id = logger.add("app.log")
            >>> logger.disable_sink(sink_id)
            >>> logger.info("Not logged")  # Sink disabled
        """
        ...

    def is_sink_enabled(self, sink_id: int) -> bool | None:
        """Check if a specific sink is enabled.

        Args:
            sink_id: The handler ID of the sink to check.

        Returns:
            True if enabled, False if disabled, None if not found.

        Example:
            >>> sink_id = logger.add("app.log")
            >>> logger.is_sink_enabled(sink_id)  # Returns True
            >>> logger.disable_sink(sink_id)
            >>> logger.is_sink_enabled(sink_id)  # Returns False
        """
        ...

    def search_log(
        self,
        sink_id: int,
        search_string: str,
        *,
        first_only: bool = False,
        case_sensitive: bool = False,
        use_regex: bool = False,
        start_line: int | None = None,
        end_line: int | None = None,
        max_results: int | None = None,
        context_before: int | None = None,
        context_after: int | None = None,
        level_filter: str | None = None,
        invert_match: bool = False,
    ) -> list[SearchResult] | None:
        """Search a sink's log file for a pattern (Rust-powered).

        All search operations are performed by the high-performance Rust backend.

        Args:
            sink_id: Handler ID of the sink whose log file to search.
            search_string: String or regex pattern to search for.
            first_only: Return only first match (default: False).
            case_sensitive: Perform case-sensitive search (default: False).
            use_regex: Treat search_string as regex (default: False).
            start_line: Start from this line number (1-indexed).
            end_line: Stop at this line number (inclusive).
            max_results: Maximum number of results.
            context_before: Lines to include before match.
            context_after: Lines to include after match.
            level_filter: Only search lines with this log level.
            invert_match: Return lines that DON'T match.

        Returns:
            List of dicts with "line", "content", "match" keys,
            plus optional "context_before" and "context_after".
            None if sink not found. Empty list if no matches.

        Example:
            >>> results = logger.search_log(sink_id, "error")
            >>> regex_results = logger.search_log(sink_id, r"error:\\s+\\d+", use_regex=True)
            >>> context_results = logger.search_log(sink_id, "crash", context_before=2, context_after=2)
        """
        ...

    def __call__(self, auto_update_check: bool = True) -> PyLogger:
        """Create a new logger instance with custom initialization options.

        Args:
            auto_update_check: Enable automatic version checking on startup. Defaults to True.

        Returns:
            A new PyLogger instance with the specified configuration.

        Example:
            >>> from logly import logger
            >>> # Create logger with auto-update checks (default)
            >>> default_logger = logger()
            >>>
            >>> # Create logger without auto-update checks
            >>> custom_logger = logger(auto_update_check=False)
            >>> custom_logger.configure(level="INFO")
        """
        ...

logger: PyLogger

def __getattr__(name: str) -> object:
    """Redirect module attribute access to the logger instance for convenience.

    This allows users to do:
        import logly as logger
        logger.info("message")

    Or:
        import logly
        logly.info("message")

    Instead of:
        from logly import logger
        logger.info("message")
    """
    ...
