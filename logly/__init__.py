"""Logly: A high-performance, structured logging library for Python.

Logly provides a simple and efficient logging API with a Rust backend for optimal performance.
It supports structured logging, file output, asynchronous processing, and flexible configuration
to meet the needs of modern Python applications.


Example:
    >>> from logly import logger
    >>> logger.configure(level="INFO")
    >>> logger.info("Application started", version="1.0.0")
    >>> logger.error("Database connection failed", error_code=500)
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import ContextDecorator, contextmanager

from logly._logly import PyLogger, __version__
from logly._logly import logger as _rust_logger


class _LoggerProxy:  # pylint: disable=too-many-public-methods
    """Python proxy class that provides a Loguru-compatible API while delegating to the Rust backend.

    This class maintains API compatibility with popular logging libraries while leveraging
    the high-performance Rust implementation for optimal logging performance.
    """

    def __init__(self, inner: PyLogger) -> None:
        self._inner = inner
        # bound context values attached to this proxy
        self._bound: dict[str, object] = {}
        # enabled/disabled switch
        self._enabled: bool = True
        # custom level name mappings
        self._levels: dict[str, str] = {}

    # configuration and sinks
    def add(  # pylint: disable=too-many-arguments
        self,
        sink: str | None = None,
        *,
        rotation: str | None = None,
        size_limit: str | None = None,
        retention: int | None = None,
        filter_min_level: str | None = None,
        filter_module: str | None = None,
        filter_function: str | None = None,
        async_write: bool = True,
        buffer_size: int = 8192,
        flush_interval: int = 100,
        max_buffered_lines: int = 1000,
        date_style: str | None = None,
        date_enabled: bool = False,
        format: str | None = None,
        json: bool = False,
    ) -> int:
        """Add a logging sink (output destination).

        Args:
            sink: Path to log file or "console" for stdout. Defaults to console.
            rotation: Time-based rotation policy. Options: "daily", "hourly", "minutely".
            size_limit: Size-based rotation limit (e.g., "5KB", "10MB", "1GB").
            retention: Number of rotated files to keep. Older files are deleted.
            filter_min_level: Minimum log level for this sink. Options: "TRACE", "DEBUG",
                            "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL".
            filter_module: Only log messages from this module name.
            filter_function: Only log messages from this function name.
            async_write: Enable asynchronous writing for better performance (default: True).
            buffer_size: Buffer size in bytes for async writing (default: 8192).
            flush_interval: Flush interval in milliseconds for async writing (default: 1000).
            max_buffered_lines: Maximum number of buffered lines before blocking (default: 1000).
            date_style: Date format style. Options: "rfc3339", "local", "utc".
            date_enabled: Enable timestamp in log output (default: False for console).
            format: Custom format string for this sink with placeholders like {time}, {level}, {message}, {module}, {function}, {filename}, {lineno}, or any extra field key. Placeholders are case-insensitive.
            json: Format logs as JSON for this sink (default: False).

        Returns:
            Handler ID that can be used to remove this sink later.

        Example:
            >>> from logly import logger
            >>> # Add console sink
            >>> logger.add("console")
            >>> # Add file sink with daily rotation
            >>> logger.add("app.log", rotation="daily", retention=7)
            >>> # Add file sink with size-based rotation
            >>> logger.add("app.log", size_limit="10MB", retention=5)
            >>> # Add filtered sink for errors only
            >>> logger.add("errors.log", filter_min_level="ERROR")
            >>> # Add sink with custom format including caller info
            >>> logger.add("console", format="{time} [{level}] {message} at {filename}:{lineno}")
        """
        if not sink or sink == "console":
            return self._inner.add(
                "console",
                rotation=rotation,
                size_limit=size_limit,
                retention=retention,
                filter_min_level=filter_min_level,
                filter_module=filter_module,
                filter_function=filter_function,
                async_write=async_write,
                buffer_size=buffer_size,
                flush_interval=flush_interval,
                max_buffered_lines=max_buffered_lines,
                date_style=date_style,
                date_enabled=date_enabled,
                format=format,
                json=json,
            )
        return self._inner.add(
            sink,
            rotation=rotation,
            size_limit=size_limit,
            retention=retention,
            filter_min_level=filter_min_level,
            filter_module=filter_module,
            filter_function=filter_function,
            async_write=async_write,
            buffer_size=buffer_size,
            flush_interval=flush_interval,
            max_buffered_lines=max_buffered_lines,
            date_style=date_style,
            date_enabled=date_enabled,
            format=format,
            json=json,
        )

    def configure(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        level: str = "INFO",
        color: bool = True,
        level_colors: dict[str, str] | None = None,
        json: bool = False,
        pretty_json: bool = False,
        console: bool = True,
        show_time: bool = True,
        show_module: bool = True,
        show_function: bool = True,
        show_filename: bool = False,
        show_lineno: bool = False,
        console_levels: dict[str, bool] | None = None,
        time_levels: dict[str, bool] | None = None,
        color_levels: dict[str, bool] | None = None,
        storage_levels: dict[str, bool] | None = None,
        color_callback: Callable | None = None,
    ) -> None:
        """Configure global logger settings.

        Args:
            level: Default minimum log level. Options: "TRACE", "DEBUG", "INFO",
                  "SUCCESS", "WARNING", "ERROR", "CRITICAL".
            color: Enable colored output for console logs (default: True). When False,
                  disables all coloring. When True, uses built-in ANSI colors or custom
                  color callback if provided.
            level_colors: Dictionary mapping log levels to ANSI color codes or color names.
                         If None, uses default colors. Supports both ANSI codes and color names:
                         ANSI codes: "30" (Black), "31" (Red), "32" (Green), "33" (Yellow),
                                   "34" (Blue), "35" (Magenta), "36" (Cyan), "37" (White)
                         Color names: "BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA",
                                    "CYAN", "WHITE", "BRIGHT_BLACK", "BRIGHT_RED", etc.
            json: Output logs in JSON format (default: False).
            pretty_json: Output logs in pretty-printed JSON format (default: False).
            console: Enable console output (default: True).
            show_time: Show timestamps in console output (default: True).
            show_module: Show module information in console output (default: True).
            show_function: Show function information in console output (default: True).
            show_filename: Show filename information in console output (default: False).
            show_lineno: Show line number information in console output (default: False).
            console_levels: Dictionary mapping log levels to console output enable/disable.
                           If None, uses global console setting.
            time_levels: Dictionary mapping log levels to time display enable/disable.
                        If None, uses global show_time setting.
            color_levels: Dictionary mapping log levels to color enable/disable.
                         If None, uses global color setting.
            storage_levels: Dictionary mapping log levels to file storage enable/disable.
                           If None, uses global setting (always enabled).
            color_callback: Custom color formatting function with signature (level: str, text: str) -> str.
                           If provided, this function is used instead of built-in ANSI coloring.
                           Allows integration with external color libraries like Rich, colorama, etc.
                           When provided, level_colors parameter is ignored.

        Example:
            >>> from logly import logger
            >>> # Configure with colored INFO level
            >>> logger.configure(level="INFO", color=True)
            >>> # Configure with JSON output
            >>> logger.configure(level="DEBUG", json=True)
            >>> # Configure with custom colors using color names
            >>> colors = {
            ...     "INFO": "GREEN",
            ...     "WARNING": "YELLOW",
            ...     "ERROR": "RED"
            ... }
            >>> logger.configure(level="INFO", level_colors=colors)
            >>> # Configure without timestamps
            >>> logger.configure(level="INFO", show_time=False)
            >>> # Configure without module and function info
            >>> logger.configure(level="INFO", show_module=False, show_function=False)
            >>> # Configure per-level console output
            >>> logger.configure(console_levels={"DEBUG": True, "INFO": False, "WARN": True})
            >>> # Configure per-level time display
            >>> logger.configure(time_levels={"DEBUG": True, "INFO": False})
            >>> # Configure with custom color callback for external library integration
            >>> def custom_color(level, text):
            ...     # Example using ANSI colors
            ...     colors = {"INFO": "\033[32m", "ERROR": "\033[31m"}
            ...     reset = "\033[0m"
            ...     return f"{colors.get(level, '')}{text}{reset}"
            >>> logger.configure(level="INFO", color_callback=custom_color)
        """
        self._inner.configure(
            level=level,
            color=color,
            level_colors=level_colors,
            json=json,
            pretty_json=pretty_json,
            console=console,
            show_time=show_time,
            show_module=show_module,
            show_function=show_function,
            show_filename=show_filename,
            show_lineno=show_lineno,
            console_levels=console_levels,
            time_levels=time_levels,
            color_levels=color_levels,
            storage_levels=storage_levels,
            color_callback=color_callback,
        )

    def reset(self) -> None:
        """Reset logger configuration to default settings.

        Resets all logger settings to their default values, clearing any
        per-level controls and custom configurations.

        Example:
            >>> from logly import logger
            >>> logger.configure(level="DEBUG", console_levels={"INFO": False})
            >>> logger.reset()  # Back to defaults
        """
        self._inner.reset()

    def remove(self, handler_id: int) -> bool:
        """Remove a logging sink by its handler ID.

        Args:
            handler_id: The ID returned by add() when the sink was created.

        Returns:
            True if the sink was successfully removed, False otherwise.

        Example:
            >>> from logly import logger
            >>> handler = logger.add("app.log")
            >>> # Later, remove the sink
            >>> logger.remove(handler)
        """
        return self._inner.remove(handler_id)

    # enable / disable
    def enable(self) -> None:
        """Enable logging for this logger instance.

        When disabled, all log messages are silently ignored.

        Example:
            >>> from logly import logger
            >>> logger.disable()
            >>> logger.info("This won't be logged")
            >>> logger.enable()
            >>> logger.info("This will be logged")
        """
        self._enabled = True

    def disable(self) -> None:
        """Disable logging for this logger instance.

        When disabled, all log messages are silently ignored without
        any performance overhead from formatting or serialization.

        Example:
            >>> from logly import logger
            >>> logger.disable()
            >>> logger.info("This won't be logged")
        """
        self._enabled = False

    # logging methods with kwargs as context key-values
    def _augment_with_callsite(self, kwargs: dict[str, object]) -> dict[str, object]:
        try:
            import inspect  # pylint: disable=import-outside-toplevel

            frame = inspect.currentframe()
            # go back two frames: current -> _augment -> caller method wrapper
            if frame and frame.f_back and frame.f_back.f_back:
                caller = frame.f_back.f_back
                module = caller.f_globals.get("__name__", "?")
                function = caller.f_code.co_name
                filename = caller.f_code.co_filename
                lineno = caller.f_lineno
                if "module" not in kwargs:
                    kwargs["module"] = module
                if "function" not in kwargs:
                    kwargs["function"] = function
                if "filename" not in kwargs:
                    kwargs["filename"] = filename
                if "lineno" not in kwargs:
                    kwargs["lineno"] = lineno
        except Exception:  # pylint: disable=broad-exception-caught
            # Introspection can fail for various reasons, catch all exceptions
            pass
        return kwargs

    def trace(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at TRACE level (most verbose).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.trace("Detailed trace info", request_id="abc123")
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.trace(msg, **merged)

    def debug(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at DEBUG level.

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.debug("Processing item %s", item_id, user="alice")
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.debug(msg, **merged)

    def info(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at INFO level (general information).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.info("User logged in", user_id=42)
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.info(msg, **merged)

    def success(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at SUCCESS level (successful operations).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.success("Payment processed", amount=100.50)
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.success(msg, **merged)

    def warning(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at WARNING level.

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.warning("Rate limit approaching", current=95, limit=100)
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.warning(msg, **merged)

    def error(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at ERROR level.

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.error("Database connection failed", db="postgres")
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.error(msg, **merged)

    def critical(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at CRITICAL level (most severe).

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.critical("System shutdown imminent", reason="out_of_memory")
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.critical(msg, **merged)

    def log(self, level: str, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at a custom or aliased level.

        Args:
            level: Log level name (e.g., "INFO", "ERROR", or a custom alias).
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.level("NOTICE", "INFO")  # Create alias
            >>> logger.log("NOTICE", "Custom level message")
        """
        if not self._enabled:
            return
        # allow aliasing custom levels
        lvl = self._levels.get(level, level)
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.log(lvl, msg, **merged)

    def complete(self) -> None:
        """Flush all pending log messages and ensure they are written.

        This method should be called before application shutdown to ensure
        all buffered logs (especially from async sinks) are persisted.

        Example:
            >>> from logly import logger
            >>> logger.info("Final log message")
            >>> logger.complete()  # Ensure all logs are written
        """
        self._inner.complete()

    # context binding similar to loguru: returns a new proxy with additional bound context
    def bind(self, **kwargs: object) -> _LoggerProxy:
        """Create a new logger instance with additional context fields bound.

        Bound context fields are automatically attached to all log messages
        from this logger instance, providing a thread-safe way to add context.

        Args:
            **kwargs: Key-value pairs to bind as context fields.

        Returns:
            A new _LoggerProxy instance with the additional context bound.

        Example:
            >>> from logly import logger
            >>> # Create logger with request context
            >>> request_logger = logger.bind(request_id="abc123", user="alice")
            >>> request_logger.info("Processing request")  # Includes request_id and user
            >>> # Original logger is unchanged
            >>> logger.info("Other message")  # No request context
        """
        new = _LoggerProxy(self._inner)
        new._bound = {**self._bound, **kwargs}
        new._enabled = self._enabled
        new._levels = dict(self._levels)
        return new

    # context manager to temporarily attach values

    @contextmanager
    def contextualize(self, **kwargs):
        """Context manager to temporarily attach context fields.

        Unlike bind(), contextualize() modifies the current logger instance
        within a context block, automatically restoring original state on exit.

        Args:
            **kwargs: Key-value pairs to temporarily attach as context fields.

        Yields:
            None

        Example:
            >>> from logly import logger
            >>> logger.info("Before")  # No context
            >>> with logger.contextualize(request_id="xyz789"):
            ...     logger.info("During")  # Includes request_id
            >>> logger.info("After")  # No context again
        """
        old = dict(self._bound)
        try:
            self._bound.update(kwargs)
            yield
        finally:
            self._bound = old

    # exception logging convenience
    def exception(self, message: str = "", /, **kwargs: object) -> None:
        """Log an exception with traceback at ERROR level.

        Automatically captures the current exception traceback and logs it.
        Must be called from within an exception handler.

        Args:
            message: Optional message prefix before the traceback.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> try:
            ...     1 / 0
            ... except ZeroDivisionError:
            ...     logger.exception("Math error occurred")
        """
        import traceback  # pylint: disable=import-outside-toplevel

        tb = traceback.format_exc()
        full = (message + "\n" + tb).strip() if message else tb
        merged = {**self._bound, **kwargs}
        self._inner.error(full, **merged)

    # catch decorator/context manager: logs exceptions; if reraise=True, re-raises
    def catch(self, *, reraise: bool = False) -> ContextDecorator:
        """Decorator or context manager to automatically log exceptions.

        Can be used as a decorator on functions or as a context manager.
        By default, catches and logs exceptions without re-raising them.

        Args:
            reraise: If True, re-raise the exception after logging (default: False).

        Returns:
            A context manager/decorator that catches and logs exceptions.

        Example:
            >>> from logly import logger
            >>> # As a context manager
            >>> with logger.catch():
            ...     risky_operation()
            >>>
            >>> # As a decorator
            >>> @logger.catch(reraise=True)
            ... def my_function():
            ...     potentially_failing_code()
        """
        proxy = self

        class _Catch(ContextDecorator):
            def __enter__(self):
                return None

            def __exit__(self, exc_type, exc, tb):
                if exc is None:
                    return False
                import traceback  # pylint: disable=import-outside-toplevel

                msg = traceback.format_exception(exc_type, exc, tb)
                proxy._inner.error("".join(msg), **proxy._bound)
                return not reraise

        return _Catch()

    # register alias or custom level mapping to an existing level name
    def level(self, name: str, mapped_to: str) -> None:
        """Register a custom level name as an alias to an existing level.

        Allows creating custom level names that map to built-in levels.
        Use with the log() method to log at custom levels.

        Args:
            name: The custom level name/alias to create.
            mapped_to: The existing level to map to ("TRACE", "DEBUG", "INFO",
                      "SUCCESS", "WARNING", "ERROR", "CRITICAL").

        Example:
            >>> from logly import logger
            >>> # Create custom level aliases
            >>> logger.level("NOTICE", "INFO")
            >>> logger.level("FATAL", "CRITICAL")
            >>> # Use custom levels
            >>> logger.log("NOTICE", "This is a notice")
            >>> logger.log("FATAL", "Fatal error occurred")
        """
        self._levels[name] = mapped_to

    # callback functionality for async log processing
    def add_callback(self, callback: object) -> int:
        """Register a callback function to be invoked for every log message.

        The callback executes asynchronously in a background thread, allowing
        real-time log processing without impacting application performance.

        Args:
            callback: A callable that accepts a dictionary containing log record data.
                     The dictionary includes: timestamp, level, message, and any
                     additional fields from bind(), contextualize(), or kwargs.

        Returns:
            int: A unique callback ID that can be used to remove the callback later.

        Example:
            >>> from logly import logger
            >>> # Define a callback for error alerting
            >>> def alert_on_error(record):
            ...     if record.get("level") == "ERROR":
            ...         send_alert(f"Error: {record['message']}")
            >>>
            >>> # Register the callback
            >>> callback_id = logger.add_callback(alert_on_error)
            >>>
            >>> # Log an error - callback executes asynchronously
            >>> logger.error("Database connection failed", retry_count=3)
            >>>
            >>> # Remove callback when done
            >>> logger.remove_callback(callback_id)
            >>>
            >>> # Ensure all callbacks complete before exit
            >>> logger.complete()

        Notes:
            - Callbacks run in background threads (zero blocking)
            - Multiple callbacks can be registered
            - Exceptions in callbacks are silently caught to prevent disruption
            - Always call logger.complete() before program exit to ensure callbacks finish
        """
        return self._inner.add_callback(callback)

    def remove_callback(self, callback_id: int) -> bool:
        """Remove a previously registered callback using its ID.

        Args:
            callback_id: The ID returned by add_callback() when the callback was registered.

        Returns:
            bool: True if the callback was successfully removed, False if not found.

        Example:
            >>> from logly import logger
            >>> # Register a callback
            >>> callback_id = logger.add_callback(my_callback)
            >>>
            >>> # Later, remove it
            >>> success = logger.remove_callback(callback_id)
            >>> print(f"Callback removed: {success}")
        """
        return self._inner.remove_callback(callback_id)


logger = _LoggerProxy(_rust_logger)

__all__ = [
    "PyLogger",
    "__version__",
    "logger",
]
