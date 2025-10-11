"""Logly: A high-performance, structured logging library for Python.

Logly provides a simple and efficient logging API with a Rust backend for optimal performance.
It supports structured logging, file output, asynchronous processing, and flexible configuration
to meet the needs of modern Python applications.

**Recent Fixes:**
- Jupyter/Colab notebook support: Logs now display correctly in notebooks.
  See: https://github.com/muhammad-fiaz/logly/issues/76
- File retention: Fixed to properly limit total log files with size_limit.
  See: https://github.com/muhammad-fiaz/logly/issues/77

Example:
    >>> from logly import logger
    >>> logger.configure(level="INFO")
    >>> logger.info("Application started", version="1.0.0")
    >>> logger.error("Database connection failed", error_code=500)
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import ContextDecorator, contextmanager
from typing import TypedDict

from logly._logly import PyLogger, __version__
from logly._logly import logger as _rust_logger


class SearchResult(TypedDict):
    """Result of a log search operation."""

    line: int
    content: str
    match: str
    context_before: list[str] | None
    context_after: list[str] | None


class _LoggerProxy:  # pylint: disable=too-many-public-methods
    """Python proxy class that provides a Loguru-compatible API while delegating to the Rust backend.

    This class maintains API compatibility with popular logging libraries while leveraging
    the high-performance Rust implementation for optimal logging performance.
    """

    def __init__(
        self,
        inner: PyLogger | None = None,
        *,
        auto_update_check: bool = True,
        auto_configure: bool = True,
        internal_debug: bool = False,
        debug_log_path: str | None = None,
    ) -> None:
        """Initialize the logger proxy with a PyLogger instance.

        Args:
            inner: The underlying PyLogger instance from the Rust backend. If None,
                  a new PyLogger will be created with the specified parameters.
            auto_update_check: Enable automatic version checking (default: True).
                              Only used when inner=None.
            auto_configure: Automatically configure with defaults for immediate use (default: True).
                          This ensures users can start logging immediately without calling configure().
            internal_debug: Enable internal debug logging for troubleshooting (default: False).
                           When enabled, all logly operations are logged to a debug file.
            debug_log_path: Path to store internal debug logs (default: "logly_debug.log").
                           Only used when internal_debug=True.
        """
        self._inner: PyLogger
        # bound context values attached to this proxy
        self._bound: dict[str, object] = {}
        # enabled/disabled switch
        self._enabled: bool = True
        # custom level name mappings
        self._levels: dict[str, str] = {}
        # track if we auto-created a console sink (for cleanup when auto_sink=False)
        self._auto_created_console_sink: int | None = None
        # internal debug settings (stored for later use)
        self._internal_debug: bool = internal_debug
        self._debug_log_path: str | None = debug_log_path

        # If no inner logger provided, create one
        if inner is None:
            try:
                # Try with new parameters (requires rebuilt Rust binary)
                self._inner = PyLogger(
                    auto_update_check=auto_update_check,
                    internal_debug=internal_debug,
                    debug_log_path=debug_log_path,
                )
            except TypeError:
                # Fall back to old signature if Rust binary hasn't been rebuilt
                self._inner = PyLogger(auto_update_check=auto_update_check)
        else:
            self._inner = inner

        # At this point, self._inner is guaranteed to be a PyLogger
        assert self._inner is not None

        # Auto-configure on initialization so users can log immediately
        # This creates the default console sink (auto_sink=True by default)
        if auto_configure:
            self.configure()

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

        **Fixed Issues:**
        - Retention now works correctly with size_limit to limit total log files.
          See: https://github.com/muhammad-fiaz/logly/issues/77

        Args:
            sink: Path to log file or "console" for stdout. Defaults to console.
            rotation: Time-based rotation policy. Options: "daily", "hourly", "minutely".
            size_limit: Size-based rotation limit. Supports case-insensitive formats:
                       - Bytes: "100" (number only), "100B", "100b"
                       - Kilobytes: "5KB", "5kb", "5K", "5k"
                       - Megabytes: "10MB", "10mb", "10M", "10m"
                       - Gigabytes: "1GB", "1gb", "1G", "1g"
                       - Terabytes: "2TB", "2tb", "2T", "2t"
            retention: Number of rotated files to keep (including current). Older files are deleted.
                      Works with both rotation and size_limit policies.
            filter_min_level: Minimum log level for this sink. Options: "TRACE", "DEBUG",
                            "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL", "FAIL".
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
        color_callback: Callable[[str, str], str] | None = None,
        auto_sink: bool = True,
        auto_sink_levels: dict[str, str | dict[str, object]] | None = None,
    ) -> None:
        """Configure global logger settings.

        Args:
            level: Default minimum log level. Options: "TRACE", "DEBUG", "INFO",
                  "SUCCESS", "WARNING", "ERROR", "CRITICAL", "FAIL".
            color: Enable colored output for console logs. When enabled without
                  custom level_colors, default colors are applied:
                  - TRACE: Cyan
                  - DEBUG: Blue
                  - INFO: White
                  - SUCCESS: Green
                  - WARNING: Yellow
                  - ERROR: Red
                  - CRITICAL: Bright Red
                  - FAIL: Magenta
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
            console: Enable all logging output globally (default: True). When set to False,
                    disables ALL logging across all sinks (console and file), similar to logger.disable().
                    This provides a global kill-switch for logging output.
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
            auto_sink: Automatically create a console sink if no sinks exist (default: True).
                      When True and no sinks have been added, a console sink is created automatically.
                      This ensures logs are displayed even if you forget to add sinks.
                      Set to False if you want full manual control over sinks.
                      WARNING: If auto_sink=True and you later try to add a console sink manually,
                      you'll receive a warning about duplicate console sinks.
            auto_sink_levels: **NEW in v0.1.5**: Automatically create sinks for different log levels.
                             Maps level names to file paths (str) or configuration dicts.
                             Each sink automatically filters logs by the specified level and above.
                             Simple: {"INFO": "logs/info.log"}
                             Advanced: {"INFO": {"path": "logs/info.log", "rotation": "daily"}}
                             Supports all logger.add() options in dict form.
                             Set to None to disable automatic level-based sink creation.

        Example:
            >>> from logly import logger
            >>> # Configure with colored INFO level and auto console sink
            >>> logger.configure(level="INFO", color=True)
            >>> logger.info("Logs appear in console automatically!")
            >>>
            >>> # Configure without auto sink (manual sink management)
            >>> logger.configure(level="DEBUG", auto_sink=False)
            >>> logger.add("app.log")  # Must manually add sinks
            >>> logger.info("This goes to file only")
            >>>
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
            >>> # Configure with auto-sink levels (NEW in v0.1.5)
            >>> logger.configure(
            ...     level="DEBUG",
            ...     auto_sink_levels={
            ...         "DEBUG": "logs/debug.log",
            ...         "INFO": "logs/info.log",
            ...         "ERROR": "logs/error.log",
            ...     }
            ... )
            >>> # Advanced auto-sink configuration
            >>> logger.configure(
            ...     level="INFO",
            ...     auto_sink_levels={
            ...         "INFO": {
            ...             "path": "logs/info.log",
            ...             "rotation": "daily",
            ...             "retention": 7,
            ...         },
            ...         "ERROR": {
            ...             "path": "logs/errors.json",
            ...             "json": True,
            ...             "async_write": True,
            ...         },
            ...     }
            ... )
        """
        # Set global enabled state based on console parameter
        self._enabled = console

        # auto_sink_levels validation and processing is handled in Rust
        # The Rust layer will validate levels, paths, and configuration
        # and automatically create the appropriate sinks

        # If auto_sink=False is explicitly passed, remove any auto-created console sink
        # This allows users to have full manual control over sinks
        if not auto_sink and self._auto_created_console_sink is not None:
            try:
                self.remove(self._auto_created_console_sink)
                self._auto_created_console_sink = None
            except (ValueError, KeyError, RuntimeError):
                # Sink might have already been removed, that's OK
                pass

        # Track if this configure() call will auto-create a console sink
        # so we can remove it later if user calls configure(auto_sink=False)
        sinks_before = len(self.list_sinks())

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
            auto_sink=auto_sink,
            auto_sink_levels=auto_sink_levels,
        )

        # Track the auto-created console sink ID if one was just created
        if auto_sink and sinks_before == 0 and len(self.list_sinks()) == 1:
            # A sink was auto-created, track it
            sinks = self.list_sinks()
            if sinks:
                self._auto_created_console_sink = sinks[0]

    def reset(self) -> None:
        """Reset logger configuration to default settings.

        Resets all logger settings to their default values, clearing any
        per-level controls and custom configurations.

        Example:
            >>> from logly import logger
            >>> logger.configure(level="DEBUG", console_levels={"INFO": False})
            >>> logger.reset()  # Back to defaults
        """
        self._enabled = True  # Reset global enabled flag to default
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

    def remove_all(self) -> int:
        """Remove all logging sinks.

        Clears all registered sinks (console and file outputs). This is useful
        for cleanup or when you want to reconfigure all logging outputs.

        Returns:
            The number of sinks that were removed.

        Example:
            >>> from logly import logger
            >>> logger.add("app.log")
            >>> logger.add("error.log")
            >>> logger.add("debug.log")
            >>> count = logger.remove_all()
            >>> print(f"Removed {count} sinks")  # Output: Removed 3 sinks
            >>> # Now you can add new sinks with fresh configuration
            >>> logger.add("new_app.log")
        """
        return self._inner.remove_all()

    def sink_count(self) -> int:
        """Get the number of active sinks.

        Returns the count of all registered sinks (file and console outputs).
        This is useful for monitoring and debugging logging configuration.

        Returns:
            The number of active sinks.

        Example:
            >>> from logly import logger
            >>> logger.add("app.log")
            >>> logger.add("error.log")
            >>> count = logger.sink_count()
            >>> print(f"Active sinks: {count}")  # Output: Active sinks: 2
        """
        return self._inner.sink_count()

    def list_sinks(self) -> list[int]:
        """List all active sink handler IDs.

        Returns a list of handler IDs for all registered sinks. These IDs can
        be used with remove() to selectively remove sinks.

        Returns:
            List of handler IDs (as integers).

        Example:
            >>> from logly import logger
            >>> id1 = logger.add("app.log")
            >>> id2 = logger.add("error.log")
            >>> ids = logger.list_sinks()
            >>> print(f"Sink IDs: {ids}")  # Output: Sink IDs: [1, 2]
            >>> logger.remove(ids[0])  # Remove first sink
        """
        return self._inner.list_sinks()

    def sink_info(self, handler_id: int) -> dict[str, str] | None:
        """Get detailed information about a specific sink.

        Returns a dictionary with sink configuration details including path,
        rotation policy, compression, async settings, and format options.

        Args:
            handler_id: Handler ID returned by add().

        Returns:
            Dictionary with sink information, or None if handler ID not found.

        Example:
            >>> from logly import logger
            >>> id = logger.add("app.log", rotation="daily", async_mode=True)
            >>> info = logger.sink_info(id)
            >>> print(info["path"])  # Output: app.log
            >>> print(info["rotation"])  # Output: daily
            >>> print(info["async_write"])  # Output: true
        """
        return self._inner.sink_info(handler_id)

    def all_sinks_info(self) -> list[dict[str, str]]:
        """Get information about all active sinks.

        Returns a list of dictionaries containing configuration details for
        all registered sinks. This is useful for debugging and monitoring.

        Returns:
            List of sink information dictionaries.

        Example:
            >>> from logly import logger
            >>> logger.add("app.log", rotation="daily")
            >>> logger.add("error.log", rotation="10MB", json=True)
            >>> sinks = logger.all_sinks_info()
            >>> for sink in sinks:
            ...     print(f"{sink['path']}: rotation={sink['rotation']}, json={sink['json']}")
            # Output:
            # app.log: rotation=daily, json=false
            # error.log: rotation=10485760B, json=true
        """
        return self._inner.all_sinks_info()

    def delete(self, handler_id: int) -> bool:
        """Delete the log file for a specific sink.

        This removes only the log file, not the sink configuration. The sink
        remains active and will create a new file when the next log is written.

        Args:
            handler_id: Handler ID of the sink whose log file should be deleted.

        Returns:
            True if the file was successfully deleted, False otherwise.

        Example:
            >>> from logly import logger
            >>> id = logger.add("app.log")
            >>> logger.info("Some logs")
            >>> # Delete the log file but keep the sink active
            >>> success = logger.delete(id)
            >>> print(f"File deleted: {success}")  # Output: File deleted: True
            >>> # Sink is still active, new logs will create a new file
            >>> logger.info("This creates a new app.log file")
        """
        return self._inner.delete(handler_id)

    def delete_all(self) -> int:
        """Delete all log files from all sinks.

        This removes all log files but keeps sink configurations active.
        All sinks will create new files when the next log is written.

        Returns:
            The number of files successfully deleted.

        Example:
            >>> from logly import logger
            >>> logger.add("app.log")
            >>> logger.add("error.log")
            >>> logger.add("debug.log")
            >>> logger.info("Writing to all sinks")
            >>> # Delete all log files
            >>> count = logger.delete_all()
            >>> print(f"Deleted {count} files")  # Output: Deleted 3 files
            >>> # All sinks still active, will create new files on next log
            >>> logger.info("Creates new files")
        """
        return self._inner.delete_all()

    def clear(self) -> None:
        """Clear the console display.

        This is a platform-specific operation that clears the terminal screen.
        On Windows, it executes 'cls'. On Unix-like systems, it uses ANSI escape codes.

        Note:
            This only clears the console display. It does not delete any log files
            or affect sink configurations.

        Example:
            >>> from logly import logger
            >>> logger.info("Some messages")
            >>> logger.info("More messages")
            >>> # Clear the console display
            >>> logger.clear()
            >>> # Console is now cleared, but log files are intact
        """
        self._inner.clear()

    def read(self, handler_id: int) -> str | None:
        """Read log content from a specific sink's file.

        This reads and returns the entire content of the log file associated
        with the specified sink. The file is not modified or deleted.

        Args:
            handler_id: Handler ID of the sink whose log file should be read.

        Returns:
            The log file content as a string, or None if the file doesn't exist
            or the handler ID is invalid.

        Example:
            >>> from logly import logger
            >>> id = logger.add("app.log")
            >>> logger.info("First message")
            >>> logger.info("Second message")
            >>> # Read the log content
            >>> content = logger.read(id)
            >>> if content:
            ...     print(f"Log content:\\n{content}")
            >>> # File is still intact after reading
        """
        return self._inner.read(handler_id)

    def read_all(self) -> dict[int, str]:
        """Read log content from all sinks.

        This reads and returns the content of all log files from all active sinks.
        Files are not modified or deleted.

        Returns:
            Dictionary mapping handler IDs to their log file contents.
            Only includes sinks with existing log files.

        Example:
            >>> from logly import logger
            >>> id1 = logger.add("app.log")
            >>> id2 = logger.add("error.log")
            >>> logger.info("Message to both")
            >>> # Read all logs
            >>> all_logs = logger.read_all()
            >>> for sink_id, content in all_logs.items():
            ...     print(f"Sink {sink_id}:\\n{content}")
            >>> # All files are still intact after reading
        """
        return self._inner.read_all()

    def file_size(self, handler_id: int) -> int | None:
        """Get the file size of a specific sink's log file in bytes.

        Returns the size of the log file associated with the given sink ID.
        Returns None if the sink doesn't exist, is not a file sink, or the file
        doesn't exist yet.

        Args:
            handler_id: The unique identifier of the sink (returned by add()).

        Returns:
            File size in bytes, or None if not found.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log")
            >>> logger.info("Hello world!")
            >>> size = logger.file_size(sink_id)
            >>> if size:
            ...     print(f"Log file is {size} bytes")
            Log file is 42 bytes
        """
        return self._inner.file_size(handler_id)

    def file_metadata(self, handler_id: int) -> dict[str, str] | None:
        """Get detailed metadata for a specific sink's log file.

        Returns a dictionary with comprehensive file information including:
        - size: File size in bytes
        - created: Creation timestamp (ISO 8601 format)
        - modified: Last modified timestamp (ISO 8601 format)
        - path: Full file path

        Args:
            handler_id: The unique identifier of the sink (returned by add()).

        Returns:
            Dictionary with file metadata, or None if sink/file doesn't exist.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log")
            >>> logger.info("Test message")
            >>> metadata = logger.file_metadata(sink_id)
            >>> if metadata:
            ...     print(f"Size: {metadata['size']} bytes")
            ...     print(f"Created: {metadata['created']}")
            ...     print(f"Modified: {metadata['modified']}")
            ...     print(f"Path: {metadata['path']}")
        """
        return self._inner.file_metadata(handler_id)

    def read_lines(self, handler_id: int, start: int, end: int) -> str | None:
        """Read specific lines from a sink's log file.

        Allows reading a specific range of lines rather than the entire file.
        Line numbers are 1-indexed. Supports negative indices to count from the end:
        - start=-10 means "start from 10th line from the end"
        - end=-1 means "end at last line"

        Args:
            handler_id: The unique identifier of the sink (returned by add()).
            start: Starting line number (1-indexed, negative for end-relative).
            end: Ending line number (inclusive, negative for end-relative).

        Returns:
            Selected lines joined with newlines, or None if sink/file doesn't exist.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log")
            >>> for i in range(20):
            ...     logger.info(f"Message {i}")
            >>>
            >>> # Read first 5 lines
            >>> lines = logger.read_lines(sink_id, 1, 5)
            >>>
            >>> # Read last 3 lines
            >>> lines = logger.read_lines(sink_id, -3, -1)
            >>>
            >>> # Read lines 10-15
            >>> lines = logger.read_lines(sink_id, 10, 15)
        """
        return self._inner.read_lines(handler_id, start, end)

    def line_count(self, handler_id: int) -> int | None:
        """Count the number of lines in a sink's log file.

        Returns the total number of lines in the log file for the given sink.
        Useful for paginating through large log files.

        Args:
            handler_id: The unique identifier of the sink (returned by add()).

        Returns:
            Number of lines in the file, or None if sink/file doesn't exist.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log")
            >>> logger.info("Line 1")
            >>> logger.info("Line 2")
            >>> logger.info("Line 3")
            >>>
            >>> count = logger.line_count(sink_id)
            >>> print(f"Log has {count} lines")
            Log has 3 lines
        """
        return self._inner.line_count(handler_id)

    def read_json(self, handler_id: int, pretty: bool = False) -> str | None:
        """Read and parse JSON log file.

        Reads a JSON-formatted log file and returns it as a string.
        Supports both JSON array format and newline-delimited JSON (NDJSON).

        For NDJSON files (each line is a separate JSON object), this method will
        automatically collect all objects into a single JSON array.

        Args:
            handler_id: The unique identifier of the sink (returned by add()).
            pretty: If True, returns pretty-printed JSON with indentation.

        Returns:
            JSON string (pretty or compact), or None if sink/file doesn't exist.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log", format="json")
            >>> logger.info("Test message", user="alice", action="login")
            >>>
            >>> # Get compact JSON
            >>> json_logs = logger.read_json(sink_id)
            >>> print(json_logs)
            [{"level":"INFO","message":"Test message","user":"alice","action":"login"}]
            >>>
            >>> # Get pretty-printed JSON
            >>> pretty_logs = logger.read_json(sink_id, pretty=True)
            >>> print(pretty_logs)
            [
              {
                "level": "INFO",
                "message": "Test message",
                "user": "alice",
                "action": "login"
              }
            ]
        """
        return self._inner.read_json(handler_id, pretty)

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
        """Augment log record with caller information from the call stack.

        Uses Python's inspect module to automatically add caller context information
        to log records, including module name, function name, filename, and line number.
        This information is only added if not already present in the kwargs.

        Args:
            kwargs: Dictionary of context fields to potentially augment with caller info.

        Returns:
            The kwargs dictionary with caller information added if available.

        Note:
            This method inspects the call stack to find the actual logging call site.
            It gracefully handles any inspection failures by returning the original kwargs.
        """
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

    def fail(self, message: str, /, *args: object, **kwargs: object) -> None:
        """Log a message at FAIL level (operation failures).

        Use this for operation failures that are distinct from errors.
        Displayed with magenta color by default to distinguish from ERROR.

        Args:
            message: The log message, optionally with % formatting placeholders.
            *args: Arguments for % string formatting.
            **kwargs: Additional context fields to attach to the log record.

        Example:
            >>> from logly import logger
            >>> logger.fail("Authentication failed", user="alice", attempts=3)
        """
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        merged = self._augment_with_callsite(merged)
        msg = message % args if args else message
        self._inner.fail(msg, **merged)

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
        # Skip auto_configure for bound loggers (they share the same Rust backend)
        new = _LoggerProxy(self._inner, auto_configure=False)
        new._bound = {**self._bound, **kwargs}
        new._enabled = self._enabled
        new._levels = dict(self._levels)
        new._auto_created_console_sink = self._auto_created_console_sink
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
        if not self._enabled:
            return

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

    def enable_sink(self, sink_id: int) -> bool:
        """Enable a specific sink by its handler ID.

        When a sink is enabled, log messages will be written to it.
        Sinks are enabled by default when created.

        Args:
            sink_id: The handler ID of the sink to enable.

        Returns:
            True if the sink was found and enabled, False if not found.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log")
            >>> logger.disable_sink(sink_id)
            >>> logger.info("Not logged to file")  # Sink disabled
            >>> logger.enable_sink(sink_id)
            >>> logger.info("Logged to file")  # Sink re-enabled
        """
        if sink_id < 0:
            return False
        return self._inner.enable_sink(sink_id)

    def disable_sink(self, sink_id: int) -> bool:
        """Disable a specific sink by its handler ID.

        When a sink is disabled, log messages will not be written to it,
        but the sink remains registered and can be re-enabled later.

        Args:
            sink_id: The handler ID of the sink to disable.

        Returns:
            True if the sink was found and disabled, False if not found.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log")
            >>> logger.disable_sink(sink_id)
            >>> logger.info("Not logged to file")  # Sink disabled
            >>> logger.enable_sink(sink_id)
            >>> logger.info("Now logged to file")  # Sink re-enabled
        """
        if sink_id < 0:
            return False
        return self._inner.disable_sink(sink_id)

    def is_sink_enabled(self, sink_id: int) -> bool | None:
        """Check if a specific sink is enabled.

        Args:
            sink_id: The handler ID of the sink to check.

        Returns:
            True if enabled, False if disabled, None if not found.

        Example:
            >>> from logly import logger
            >>> sink_id = logger.add("app.log")
            >>> logger.is_sink_enabled(sink_id)  # Returns True
            >>> logger.disable_sink(sink_id)
            >>> logger.is_sink_enabled(sink_id)  # Returns False
        """
        if sink_id < 0:
            return None
        return self._inner.is_sink_enabled(sink_id)

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
            List of dicts with "line", "content", "match" keys.
            None if sink not found. Empty list if no matches.

        Example:
            >>> results = logger.search_log(sink_id, "error")
            >>> results = logger.search_log(sink_id, r"\\d+", use_regex=True)
        """
        if sink_id < 0:
            return None

        return self._inner.search_log(
            sink_id,
            search_string,
            case_sensitive=case_sensitive,
            first_only=first_only,
            use_regex=use_regex,
            start_line=start_line,
            end_line=end_line,
            max_results=max_results,
            context_before=context_before,
            context_after=context_after,
            level_filter=level_filter,
            invert_match=invert_match,
        )

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

    def __call__(
        self,
        auto_update_check: bool = True,
        auto_configure: bool = True,
        internal_debug: bool = False,
        debug_log_path: str | None = None,
    ) -> _LoggerProxy:
        """Create a new logger instance with custom initialization options.

        Args:
            auto_update_check: Enable automatic version checking on startup. Defaults to True.
            auto_configure: Automatically configure with defaults for immediate use (default: True).
                          This ensures users can start logging immediately without calling configure().
            internal_debug: Enable internal debug logging for troubleshooting (default: False).
                           When enabled, all logly operations are logged to a debug file.
            debug_log_path: Path to store internal debug logs (default: "logly_debug.log").
                           Only used when internal_debug=True.

        Returns:
            A new _LoggerProxy instance with the specified configuration.

        Example:
            >>> from logly import logger
            >>> # Create logger with auto-update checks (default)
            >>> default_logger = logger()
            >>>
            >>> # Create logger without auto-update checks
            >>> custom_logger = logger(auto_update_check=False)
            >>> custom_logger.configure(level="INFO")
            >>>
            >>> # Create logger with internal debugging enabled
            >>> debug_logger = logger(internal_debug=True, debug_log_path="my_debug.log")
            >>> debug_logger.info("This operation will be logged internally")
        """
        try:
            # Try with new parameters (requires rebuilt Rust binary)
            new_py_logger = PyLogger(
                auto_update_check=auto_update_check,
                internal_debug=internal_debug,
                debug_log_path=debug_log_path,
            )
        except TypeError:
            # Fall back to old signature if Rust binary hasn't been rebuilt
            new_py_logger = PyLogger(auto_update_check=auto_update_check)

        # New loggers get auto-configured for immediate use
        return _LoggerProxy(
            new_py_logger,
            auto_configure=auto_configure,
            internal_debug=internal_debug,
            debug_log_path=debug_log_path,
        )


logger = _LoggerProxy(inner=_rust_logger)

__all__ = [
    "PyLogger",
    "__version__",
    "logger",
]


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
    if name in ("logger", "__version__", "PyLogger"):
        # Return the actual attributes for explicit access
        return globals()[name]
    # For any other attribute access, delegate to the logger instance
    return getattr(logger, name)
