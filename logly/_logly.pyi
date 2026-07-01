"""Logly type stubs.

Provides type annotations for the ``logly`` package. Logly is a
Rust-powered, high-performance logging library for Python with structured
sinks, custom levels, rotation, compression, and telemetry integrations.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable, Generator, Mapping
from pathlib import Path
from types import TracebackType
from typing import Any

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from logly.models import PrettyJsonConfig

__version__: str
"""Current version of the logly package."""

class _Logger:
    """Native Rust logger engine (internal).

    This class wraps the PyO3-based Rust implementation and provides
    low-level logging operations. It is not intended for direct use;
    use :class:`~logly.Logger` instead.

    The engine manages sink dispatch, level filtering, format rendering,
    and record construction entirely in Rust for maximum performance.
    """

    def __init__(self) -> None:
        """Initialize a new native Rust logger engine."""
        ...
    def add(
        self,
        sink: Any,
        *,
        level: str = "INFO",
        format: str | Callable[[dict[str, Any]], str] = "{level} | {message}",
        colorize: bool | None = None,
        serialize: bool = False,
        pretty_json: bool | PrettyJsonConfig | None = None,
        enqueue: bool = False,
        rotation: Any | None = None,
        retention: Any | None = None,
        compression: Any | None = None,
        delay: bool = False,
        watch: bool = False,
        mode: str = "a",
        encoding: str = "utf-8",
        filter: Any | None = None,
        patch: Any | None = None,
    ) -> int:
        """Add a sink to the native engine.

        Args:
            sink: The sink target (file path, callable, or sink object).
            level: Minimum log level for this sink.
            format: Format template string or callable formatter.
            colorize: Whether to colorize output. ``None`` auto-detects.
            serialize: Whether to output JSON instead of plain text.
            pretty_json: Whether to pretty-print JSON output.
            enqueue: Whether to use background queue for async dispatch.
            rotation: Rotation policy (size, time, clock, or weekday).
            retention: Retention policy (count or time-based).
            compression: Compression codec for rotated files.
            delay: Whether to delay file creation until first log.
            watch: Whether to watch for file changes.
            mode: File open mode (``"a"`` for append, ``"w"`` for overwrite).
            encoding: File encoding (default ``"utf-8"``).
            filter: Filter callable or mapping for selective logging.
            patch: Patcher callable to modify records before dispatch.

        Returns:
            Integer sink ID for later removal.
        """
        ...
    def remove(self, sink_id: int | None = None) -> None:
        """Remove a sink or all sinks from the engine.

        Args:
            sink_id: The sink ID to remove. If ``None``, removes all sinks.
        """
        ...
    def complete(self) -> None:
        """Wait for all enqueued messages to be processed.

        Blocks until the background worker queue is drained. Should be
        called before process exit when using ``enqueue=True`` sinks.
        """
        ...
    def enable(self, name: str) -> None:
        """Enable logging for a logger name pattern.

        Args:
            name: Logger name prefix to enable (e.g. ``"app"``).
        """
        ...
    def disable(self, name: str) -> None:
        """Disable logging for a logger name pattern.

        Args:
            name: Logger name prefix to disable (e.g. ``"app"``).
        """
        ...
    def log(self, level: str, message: str) -> None:
        """Log a message at a named level.

        Args:
            level: Level name (e.g. ``"INFO"``, ``"ERROR"``).
            message: The log message text.
        """
        ...
    def log_structured(
        self,
        level: str,
        message: str,
        *,
        name: str | None = None,
        file: str | None = None,
        line: int | None = None,
        function: str | None = None,
        module: str | None = None,
        thread_name: str | None = None,
        process_id: int | None = None,
        extra: dict[str, str] | None = None,
        exception: str | None = None,
        colors: bool = False,
    ) -> None:
        """Log a structured message with full record metadata.

        Args:
            level: Level name (e.g. ``"INFO"``).
            message: The log message text.
            name: Logger name.
            file: Source file path.
            line: Source line number.
            function: Source function name.
            module: Source module name.
            thread_name: Thread name.
            process_id: Process ID.
            extra: Additional key-value pairs to attach.
            exception: Formatted exception text.
            colors: Whether to apply ANSI color codes.
        """
        ...
    def trace(self, message: str) -> None:
        """Log at TRACE level (priority 5).

        Args:
            message: The log message text.
        """
        ...
    def debug(self, message: str) -> None:
        """Log at DEBUG level (priority 10).

        Args:
            message: The log message text.
        """
        ...
    def info(self, message: str) -> None:
        """Log at INFO level (priority 20).

        Args:
            message: The log message text.
        """
        ...
    def notice(self, message: str) -> None:
        """Log at NOTICE level (priority 25).

        Args:
            message: The log message text.
        """
        ...
    def success(self, message: str) -> None:
        """Log at SUCCESS level (priority 30).

        Args:
            message: The log message text.
        """
        ...
    def warning(self, message: str) -> None:
        """Log at WARNING level (priority 40).

        Args:
            message: The log message text.
        """
        ...
    def error(self, message: str) -> None:
        """Log at ERROR level (priority 50).

        Args:
            message: The log message text.
        """
        ...
    def fail(self, message: str) -> None:
        """Log at FAIL level (priority 55).

        Args:
            message: The log message text.
        """
        ...
    def critical(self, message: str) -> None:
        """Log at CRITICAL level (priority 60).

        Args:
            message: The log message text.
        """
        ...
    def fatal(self, message: str) -> None:
        """Log at FATAL level (priority 70).

        Args:
            message: The log message text.
        """
        ...
    def audit(self, message: str) -> None:
        """Log at AUDIT level (custom, must be registered first).

        Args:
            message: The log message text.
        """
        ...

class Logger:
    """Main logger class providing the full logging API.

    Logly's Logger wraps a native Rust engine and adds Python-level
    features like context binding, patching, exception catching, and
    per-call options.

    Usage::

        from logly import logger

        logger.info("Hello from Logly")
        logger.opt(exception=True).error("Something went wrong")

    Args:
        native: Optional pre-existing Rust engine. Creates a new one if ``None``.
        name: Logger name for identification and filtering.
        bound: Pre-bound context key-value pairs.
        patchers: Tuple of patcher callables applied to each record.
        options: Per-call options (opt) state.
        sink_configs: Sink configurations for reinstall support.
    """

    def __init__(
        self,
        native: _Logger | None = None,
        *,
        name: str = "logly",
        bound: Mapping[str, object] | None = None,
        patchers: tuple[Callable[[dict[str, object]], None], ...] = (),
        options: Any | None = None,
        sink_configs: dict[int, tuple[object, dict[str, object]]] | None = None,
    ) -> None: ...
    def add(
        self,
        sink: object = "stderr",
        *,
        level: str | int = "DEBUG",
        format: str | Callable[[dict[str, object]], str] | None = None,
        rotation: str | int | object | None = None,
        retention: int | str | object | None = None,
        compression: str | object | None = None,
        enqueue: bool = False,
        colorize: bool | None = None,
        backtrace: bool = True,
        diagnose: bool = False,
        filter: str | Callable[[dict[str, object]], bool] | Mapping[str, str | bool] | None = None,
        serialize: bool = False,
        pretty_json: bool | PrettyJsonConfig | None = None,
        patch: Callable[[dict[str, object]], None] | None = None,
        encoding: str = "utf-8",
        delay: bool = False,
        context: str | Any | None = None,
        catch: bool = True,
        mode: str = "a",
        buffering: int = 1,
        loop: Any | None = None,
        opener: Callable[..., object] | None = None,
        **kwargs: object,
    ) -> int:
        """Add a logging sink.

        Sinks are destinations where log records are dispatched. Multiple
        sinks can be active simultaneously, each with independent level
        filtering, formatting, and rotation settings.

        Args:
            sink: Destination for log records. Supported types:
                - ``str``: File path (e.g. ``"app.log"``)
                - ``"stdout"`` / ``"stderr"``: Console output
                - ``Callable[[str], None]``: Custom callback
                - ``logging.Handler``: Python logging handler
            level: Minimum log level. Records below this level are discarded.
                Accepts level names (``"INFO"``) or numeric values (``20``).
            format: Format template (``"{level} | {message}"``) or callable
                that receives a record dict and returns a formatted string.
            rotation: File rotation policy. Examples:
                - ``"10 MB"``: Rotate when file exceeds 10 megabytes
                - ``"daily"``: Rotate at midnight each day
                - ``"00:00"``: Rotate at specific clock time
                - ``"monday"``: Rotate on specific weekday
            retention: How many rotated files to keep. Examples:
                - ``7``: Keep last 7 rotated files
                - ``"30 days"``: Keep files from last 30 days
            compression: Compression codec for rotated files.
                Supported: ``"gzip"``, ``"zip"``, ``"bz2"``, ``"xz"``, ``"zstd"``
            enqueue: Use background queue for non-blocking writes.
            colorize: Force colorized output. ``None`` auto-detects TTY.
            backtrace: Include backtrace in exception formatting.
            diagnose: Include variable values in exception formatting.
            filter: Filter records before dispatch. Can be:
                - ``Callable[[dict], bool]``: Returns ``True`` to accept
                - ``Mapping[str, str]``: Required key-value pairs in record
            serialize: Output records as JSON lines instead of formatted text.
            pretty_json: Pretty-print JSON with configurable options.
            patch: Callable to modify record dict before dispatch.
            encoding: File encoding for file-based sinks.
            delay: Delay file creation until first log message.
            context: Context object for async sinks.
            catch: Catch and log sink errors instead of raising.
            mode: File open mode. ``"a"`` (default) appends, ``"w"`` overwrites.
            buffering: File buffering (1 = line-buffered, 0 = unbuffered).
            loop: Event loop for async coroutine sinks.
            opener: Custom file opener callable.
            **kwargs: Additional sink-specific options.

        Returns:
            Integer sink ID for use with :meth:`remove` or :meth:`reinstall`.

        Example::

            logger.add("app.log", rotation="10 MB", retention="7 days")
            logger.add(sys.stderr, level="WARNING", colorize=True)
        """
        ...
    def remove(self, handler_id: int | None = None) -> None:
        """Remove a sink by ID or remove all sinks.

        Args:
            handler_id: The sink ID returned by :meth:`add`. If ``None``,
                removes all sinks from this logger.

        Example::

            sink_id = logger.add("app.log")
            logger.remove(sink_id)
        """
        ...
    def complete(self) -> None:
        """Wait for all enqueued messages to be processed.

        Should be called before process exit when using ``enqueue=True``
        sinks to ensure all pending messages are flushed.
        """
        ...
    def reinstall(self, handler_id: int | None = None) -> None:
        """Remove and re-add a sink with its original configuration.

        Useful for reopening file handles after external rotation.

        Args:
            handler_id: The sink ID to reinstall. If ``None``, reinstalls all.
        """
        ...
    def catch(
        self,
        exception: type[BaseException] | tuple[type[BaseException], ...] | None = ...,
        *,
        level: str = ...,
        reraise: bool = ...,
        onerror: Callable[[BaseException], None] | None = ...,
        exclude: type[BaseException] | tuple[type[BaseException], ...] | None = ...,
        default: object = ...,
    ) -> _CatchContext:
        """Create an exception catching context manager or decorator.

        When used as a context manager, catches exceptions matching the
        specified types and logs them. When used as a decorator, wraps
        a function to catch exceptions.

        Args:
            exception: Exception type(s) to catch. ``None`` catches all.
            level: Log level for the caught exception.
            reraise: Re-raise the exception after logging.
            onerror: Callback invoked with the caught exception.
            exclude: Exception type(s) to re-raise without logging.
            default: Return value when exception is caught (decorator mode).

        Returns:
            A :class:`_CatchContext` usable as context manager or decorator.

        Example::

            # As context manager
            with logger.catch():
                risky_operation()

            # As decorator
            @logger.catch(onerror=lambda e: print(f"Failed: {e}"))
            def my_func():
                risky_operation()
        """
        ...
    def opt(
        self,
        *,
        exception: BaseException | bool | None = None,
        record: bool = False,
        lazy: bool = False,
        colors: bool = False,
        raw: bool = False,
        capture: bool = True,
        depth: int = 0,
        ansi: bool = False,
        backtrace: bool = True,
        diagnose: bool = False,
    ) -> Self:
        """Set per-call logging options.

        Returns a clone of the logger with the specified options applied
        to the next log call. Options are not persisted.

        Args:
            exception: Format and attach exception info to the log record.
                Pass ``True`` to auto-capture current exception, or an
                explicit exception instance.
            record: Return the record dict from :meth:`log` instead of ``None``.
            lazy: Defer message formatting until the message is actually
                dispatched to a sink. Use with lambda arguments.
            colors: Enable Rich-style ``<color>`` markup in messages.
            raw: Skip format string interpolation, log message as-is.
            capture: Capture source file, line, and function information.
                Disable for slightly faster logging.
            depth: Number of stack frames to skip when capturing source.
                Use ``1`` in a wrapper function to report the caller's location.
            ansi: Interpret ANSI escape codes in the message.
            backtrace: Include backtrace in exception formatting.
            diagnose: Include variable values in exception formatting.

        Returns:
            A cloned logger with the specified options.

        Example::

            logger.opt(record=True).info("Returns record dict")
            logger.opt(lazy=True).debug("Result: {}", lambda: expensive())
            logger.opt(exception=True).error("Failed")
        """
        ...
    def bind(self, **kwargs: object) -> Self:
        """Bind key-value pairs to the logger context.

        Bound values appear in all subsequent log records from this
        logger and its children.

        Args:
            **kwargs: Key-value pairs to attach to log records.

        Returns:
            A new logger with the bound context.

        Example::

            user_log = logger.bind(user_id="12345", request_id="abc")
            user_log.info("User logged in")
            # Output includes: user_id=12345 request_id=abc
        """
        ...
    def contextualize(self, **kwargs: object) -> Generator[None]:
        """Context manager for temporary context binding.

        Unlike :meth:`bind`, contextualized values are scoped to the
        ``with`` block and automatically removed when the block exits.
        Thread-safe via ``contextvars``.

        Args:
            **kwargs: Key-value pairs to attach temporarily.

        Yields:
            ``None`` (used as context manager).

        Example::

            with logger.contextualize(request_id="req-123"):
                logger.info("Processing request")
                # request_id is attached to this log
            logger.info("After request")
            # request_id is NOT attached
        """
        ...
    def patch(self, patcher: Callable[[dict[str, object]], None]) -> Self:
        """Add a patcher callable to modify log records.

        Patchers are called for each log record before dispatch, allowing
        dynamic modification of record fields.

        Args:
            patcher: Callable that receives a mutable record dict.

        Returns:
            A new logger with the patcher applied.

        Example::

            def add_hostname(record: dict) -> None:
                record["extra"]["hostname"] = socket.gethostname()

            patched = logger.patch(add_hostname)
        """
        ...
    def level(
        self,
        name: str,
        no: int | None = None,
        color: str | None = None,
        icon: str | None = None,
    ) -> tuple[str, int, str | None]:
        """Inspect or register a custom log level.

        When called with only ``name``, returns the current configuration.
        When called with ``no``, registers a new level.

        Args:
            name: Level name to inspect or register (e.g. ``"VERBOSE"``).
            no: Numeric priority for new levels. Lower = more verbose.
            color: ANSI color code for the level (e.g. ``"red"``, ``"#ff0000"``).
            icon: Icon character for the level.

        Returns:
            Tuple of ``(name, numeric_priority, color_or_none)``.

        Example::

            # Inspect existing level
            name, pri, color = logger.level("INFO")

            # Register custom level
            logger.level("VERBOSE", no=5, color="cyan")
        """
        ...
    def enable(self, name: str) -> None:
        """Enable logging for a logger name pattern.

        Args:
            name: Logger name prefix to enable (e.g. ``"app"``).

        Example::

            logger.disable("app")
            logger.enable("app")  # Re-enable
        """
        ...
    def disable(self, name: str) -> None:
        """Disable logging for a logger name pattern.

        All log calls with this name prefix are silently discarded.

        Args:
            name: Logger name prefix to disable (e.g. ``"app"``).

        Example::

            logger.disable("app")  # All "app.*" logs are silenced
        """
        ...
    def configure(
        self,
        *,
        handlers: list[dict[str, object]] | None = None,
        levels: list[dict[str, object]] | None = None,
        extra: dict[str, object] | None = None,
        patcher: Callable[[dict[str, object]], None] | None = None,
        activation: list[tuple[str, bool]] | None = None,
    ) -> None:
        """Bulk-configure the logger, replacing existing settings.

        Args:
            handlers: List of sink configurations (same format as :meth:`add`).
            levels: List of level definitions (name, priority, color).
            extra: Default extra context for all records.
            patcher: Global patcher callable applied to all records.
            activation: List of ``(name, enabled)`` tuples for enable/disable.

        Example::

            logger.configure(
                handlers=[
                    {"sink": "app.log", "level": "INFO", "rotation": "daily"},
                    {"sink": sys.stderr, "level": "WARNING"},
                ],
                extra={"env": "production"},
            )
        """
        ...
    def log(
        self, level: str | int, message: object, *args: object, **kwargs: object
    ) -> dict[str, object] | None:
        """Log a message at a named or numeric level.

        Supports ``str.format()`` style placeholders::

            logger.info("User {} logged in", username)
            logger.info("User {user} logged in", user=username)

        Args:
            level: Level name (``"INFO"``) or numeric priority (``20``).
            message: Format string or pre-formatted message.
            *args: Positional arguments for ``str.format()``.
            **kwargs: Keyword arguments for ``str.format()``.

        Returns:
            The record dict if ``opt(record=True)`` was used, otherwise ``None``.
        """
        ...
    def trace(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at TRACE level (priority 5).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def debug(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at DEBUG level (priority 10).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def info(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at INFO level (priority 20).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def notice(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at NOTICE level (priority 25).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def success(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at SUCCESS level (priority 30).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def warning(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at WARNING level (priority 40).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def warn(self, message: object, *args: object, **kwargs: object) -> None:
        """Alias for :meth:`warning`.

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def error(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at ERROR level (priority 50).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def exception(
        self, message: object, *args: object, exc_info: bool = True, **kwargs: object
    ) -> None:
        """Log at ERROR level with exception info attached.

        Automatically captures the current exception if one is active.

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            exc_info: Whether to include exception info (default ``True``).
            **kwargs: Keyword format arguments.
        """
        ...
    def fail(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at FAIL level (priority 55).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def critical(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at CRITICAL level (priority 60).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def fatal(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at FATAL level (priority 70).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def audit(self, message: object, *args: object, **kwargs: object) -> None:
        """Log at AUDIT level (custom, must be registered first).

        Args:
            message: Format string or message.
            *args: Positional format arguments.
            **kwargs: Keyword format arguments.
        """
        ...
    def root_dir(self, path: str | Path) -> None:
        """Set the default root directory for relative file paths.

        When ``add("logs/app.log")`` is called after setting root_dir,
        the file path is resolved relative to this directory.

        Args:
            path: Root directory path.

        Example::

            logger.root_dir("/var/log/myapp")
            logger.add("app.log")  # Writes to /var/log/myapp/app.log
        """
        ...
    def parse(
        self,
        path: str | Path,
        pattern: str | re.Pattern[str] | None = None,
        *,
        cast: dict[str, Callable[[str], object]] | None = None,
        chunk: int = 65536,
        encoding: str = "utf-8",
    ) -> Generator[dict[str, object]]:
        """Parse a log file and yield record dicts.

        Args:
            path: Path to the log file.
            pattern: Regex pattern with named groups. Defaults to parsing
                ``"LEVEL | MESSAGE"`` format.
            cast: Dictionary mapping group names to type cast functions.
            chunk: Read chunk size in bytes (default 65536).
            encoding: File encoding (default ``"utf-8"``).

        Yields:
            Record dicts with matched groups as keys.

        Example::

            for record in logger.parse("app.log"):
                print(record["level"], record["message"])
        """
        ...
    def __copy__(self) -> Self:
        """Create a shallow copy sharing the same Rust engine."""
        ...
    def __deepcopy__(self, memo: dict[int, object]) -> Self:
        """Create a deep copy with an independent Rust engine."""
        ...
    def start(self, *args: object, **kwargs: object) -> None:
        """Start logger-managed background processing hooks.

        This method accepts application lifecycle hooks for compatibility
        with service startup code.
        """
        ...
    def stop(self) -> None:
        """Flush sinks and stop logger-managed background workers."""
        ...
    @property
    def levels(self) -> list[str]:
        """List of all registered level names in severity order.

        Returns:
            Level name strings sorted by priority.
        """
        ...

class _CatchContext:
    """Context manager and decorator for exception catching.

    Created by :meth:`Logger.catch`. Can be used as either a context
    manager or a function decorator.

    Example::

        # As context manager
        with logger.catch():
            risky_operation()

        # As decorator
        @logger.catch()
        def my_func():
            risky_operation()
    """

    def __enter__(self) -> _CatchContext:
        """Enter the exception catching context."""
        ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Exit the exception catching context.

        Args:
            exc_type: Exception type if an exception occurred.
            exc: Exception instance if an exception occurred.
            tb: Traceback object if an exception occurred.

        Returns:
            ``True`` if the exception was caught and handled.
        """
        ...
    def __call__(self, func: Callable[..., object]) -> Callable[..., object]:
        """Wrap a function as an exception-catching decorator.

        Args:
            func: The function to wrap.

        Returns:
            A wrapped function that catches exceptions.
        """
        ...

class HttpJsonSink:
    """HTTP JSON sink for sending logs to HTTP endpoints.

    Posts log records as JSON to a specified HTTP endpoint. Useful for
    log aggregation services like Loki, Elasticsearch, or custom APIs.

    Usage::

        from logly import logger
        from logly._logly import HttpJsonSink

        logger.add(HttpJsonSink(url="http://localhost:3100/loki/api/v1/push"))

    Args:
        url: HTTP endpoint URL to post logs to.
        method: HTTP method (default ``"POST"``).
        headers: List of ``(name, value)`` header tuples.
        timeout: Request timeout in seconds (default ``30``).
    """

    def __init__(
        self,
        url: str,
        *,
        method: str = "POST",
        headers: list[tuple[str, str]] | None = None,
        timeout: int = 30,
    ) -> None: ...
    def write(self, line: str) -> None:
        """Write a formatted log line to the HTTP endpoint.

        Args:
            line: The formatted log line to send.
        """
        ...
    def flush(self) -> None:
        """Flush any pending writes."""
        ...

class TcpSink:
    """TCP sink for sending logs over TCP connections.

    Maintains a persistent TCP connection and sends log lines delimited
    by a configurable separator.

    Usage::

        from logly import logger
        from logly._logly import TcpSink

        logger.add(TcpSink(host="127.0.0.1", port=514))

    Args:
        host: Remote host address (default ``"127.0.0.1"``).
        port: Remote port number (default ``514``).
        delimiter: Line delimiter (default ``"\\n"``).
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 514, delimiter: str = "\n") -> None: ...
    def connect(self) -> None:
        """Establish the TCP connection."""
        ...
    def write(self, line: str) -> None:
        """Write a formatted log line over TCP.

        Args:
            line: The formatted log line to send.
        """
        ...
    def flush(self) -> None:
        """Flush any pending writes."""
        ...

class UdpSink:
    """UDP sink for sending logs over UDP.

    Sends each log line as a separate UDP datagram. Suitable for
    high-throughput logging where occasional packet loss is acceptable.

    Usage::

        from logly import logger
        from logly._logly import UdpSink

        logger.add(UdpSink(host="127.0.0.1", port=514))

    Args:
        host: Remote host address (default ``"127.0.0.1"``).
        port: Remote port number (default ``514``).
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 514) -> None: ...
    def write(self, line: str) -> None:
        """Write a formatted log line over UDP.

        Args:
            line: The formatted log line to send.
        """
        ...

class SyslogSink:
    """Syslog sink for sending logs to syslog servers.

    Supports both RFC 3164 (BSD) and RFC 5424 (modern) formats over
    TCP or UDP transport.

    Usage::

        from logly import logger
        from logly._logly import SyslogSink

        logger.add(SyslogSink(host="127.0.0.1", port=514))

    Args:
        host: Syslog server address (default ``"127.0.0.1"``).
        port: Syslog server port (default ``514``).
        facility: Syslog facility (default ``"USER"``). Common values:
            ``"KERN"``, ``"USER"``, ``"MAIL"``, ``"DAEMON"``, ``"AUTH"``,
            ``"SYSLOG"``, ``"LPR"``, ``"NEWS"``, ``"UUCP"``, ``"CRON"``,
            ``"LOCAL0"``-``"LOCAL7"``
        transport: Transport protocol (default ``"UDP"``). Use ``"TCP"`` for
            reliable delivery.
        format: Syslog format (default ``"RFC3164"``). Use ``"RFC5424"`` for
            the modern format.
        process_name: Process name for syslog identification.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 514,
        facility: str = "USER",
        transport: str = "UDP",
        format: str = "RFC3164",
        process_name: str = "logly",
    ) -> None: ...
    def write(self, line: str) -> None:
        """Write a formatted log line to the syslog server.

        Args:
            line: The formatted log line to send.
        """
        ...
    def flush(self) -> None:
        """Flush any pending writes."""
        ...

def register_custom_level(name: str, priority: int, color: str | None = None) -> str:
    """Register a custom log level.

    Args:
        name: Level name (e.g. ``"VERBOSE"``).
        priority: Numeric priority (lower = more verbose).
        color: Optional ANSI color code (e.g. ``"red"``, ``"#ff0000"``).

    Returns:
        The registered level name.

    Example::

        register_custom_level("VERBOSE", 5, "cyan")
        logger.log("VERBOSE", "Detailed info")
    """
    ...

def inspect_level(name: str) -> tuple[str, int, str | None]:
    """Inspect a log level's configuration.

    Args:
        name: Level name to inspect.

    Returns:
        Tuple of ``(name, numeric_priority, color_or_none)``.

    Example::

        name, pri, color = inspect_level("INFO")
        # ("INFO", 20, "green")
    """
    ...

def list_levels() -> list[str]:
    """List all registered level names in severity order.

    Returns:
        List of level name strings.

    Example::

        levels = list_levels()
        # ["TRACE", "DEBUG", "INFO", "NOTICE", "SUCCESS", ...]
    """
    ...

def unsupported(name: str) -> None:
    """Mark a feature as unsupported.

    Args:
        name: Feature name.
    """
    ...

def parse_rotation_str(value: str) -> str:
    """Parse a rotation string into a normalized value.

    Args:
        value: Rotation string (e.g. ``"10 MB"``).

    Returns:
        Normalized rotation value.

    Example::

        parse_rotation_str("10 MB")  # "10485760"
        parse_rotation_str("daily")  # "daily"
    """
    ...

def parse_retention_str(value: str) -> str:
    """Parse a retention string into a normalized value.

    Args:
        value: Retention string (e.g. ``"30 days"``).

    Returns:
        Normalized retention value.

    Example::

        parse_retention_str("30 days")  # "2592000"
    """
    ...

def parse_compression_str(value: str) -> str:
    """Parse a compression string into a normalized codec name.

    Args:
        value: Compression string (e.g. ``"gzip"``).

    Returns:
        Normalized codec name.

    Example::

        parse_compression_str("gz")  # "gzip"
    """
    ...

def resolve_level_name(value: str) -> str:
    """Resolve a level name or number to its canonical name.

    Args:
        value: Level name or numeric string.

    Returns:
        Canonical level name.

    Example::

        resolve_level_name("20")  # "INFO"
        resolve_level_name("info")  # "INFO"
    """
    ...

def format_exception_text(exc: Any, backtrace: bool = False) -> str | None:
    """Format an exception as a text string.

    Args:
        exc: Exception instance.
        backtrace: Whether to include full backtrace with variable values.

    Returns:
        Formatted exception text, or ``None`` if formatting fails.

    Example::

        try:
            1 / 0
        except Exception as e:
            text = format_exception_text(e)
    """
    ...

def render_message(
    message: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    lazy: bool = False,
) -> str:
    """Render a log message with format arguments.

    Args:
        message: Format string with ``{}`` or ``{name}`` placeholders.
        args: Positional format arguments.
        kwargs: Keyword format arguments.
        lazy: Whether to defer formatting.

    Returns:
        Rendered message string.

    Example::

        render_message("Hello {}", ["world"])  # "Hello world"
        render_message("User {name}", kwargs={"name": "alice"})  # "User alice"
    """
    ...

def strip_rich_tags(text: str) -> str:
    """Strip Rich-style ``<tag>`` and ``</tag>`` markup from a string.

    Removes HTML-like tags such as ``<bold>``, ``<red>``, ``</green>``, etc.,
    returning plain text without ANSI escape codes. Useful when you need
    clean text for file output or external services.

    Args:
        text: String that may contain Rich-style markup tags.

    Returns:
        The string with all ``<tag>`` and ``</tag>`` sequences removed.

    Example::

        strip_rich_tags("<bold>Hello</bold> <red>World</red>")
        # Returns: "Hello World"
    """
    ...

def paint_themed(text: str, level_name: str, colorize: bool = True) -> str:
    """Apply theme-aware coloring based on a logical level name.

    Maps a level name (e.g. ``"success"``, ``"error"``) to the appropriate
    ANSI color based on the built-in theme.

    Args:
        text: The text to colorize.
        level_name: Logical level name (e.g. ``"success"``, ``"error"``).
        colorize: Whether to emit ANSI codes. If ``False``, returns text unchanged.

    Returns:
        The text wrapped in ANSI color codes, or plain text if ``colorize=False``.

    Example::

        paint_themed("Done!", "success", colorize=True)
        # Returns: "\\033[32mDone!\\033[0m" (green text)
    """
    ...

def colorize(text: str, color: str, colorize: bool = True) -> str:
    """Colorize text with a named ANSI color.

    Wraps the given text in ANSI escape codes for the specified color.
    If ``colorize`` is ``False``, returns the text unchanged.

    Args:
        text: The text to colorize.
        color: ANSI color name (e.g. ``"red"``, ``"bold_blue"``, ``"green"``).
        colorize: Whether to emit ANSI codes.

    Returns:
        The text wrapped in ANSI color codes, or plain text if ``colorize=False``.

    Example::

        colorize("Error!", "red", colorize=True)
        # Returns: "\\033[31mError!\\033[0m"
    """
    ...

logger: Logger
"""Default module-level logger instance.

Pre-configured with a stderr sink at DEBUG level when ``LOGLY_AUTOINIT``
is not set to ``false``.
"""
