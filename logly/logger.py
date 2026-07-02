"""Python convenience facade over the native Logly Rust engine.

This module provides the primary ``Logger`` class that wraps the PyO3-based
``_Logger`` from the Rust backend. All business logic (level resolution,
message rendering, exception text formatting, record construction, patching,
filtering) is handled in Rust. This module provides a Pythonic API on top.

Usage::

    from logly import logger

    logger.info("Hello from Logly")
    logger.opt(exception=True).error("Something went wrong")
    logger.bind(user="alice").info("User logged in")
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import multiprocessing.context
import os
import re
import sys
import threading
import time
import types
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from logly._logly import (
    _Logger,
    format_exception_text,
    inspect_level,
    list_levels,
    register_custom_level,
    render_message,
    resolve_level_name,
)
from logly.models import PrettyJsonConfig

_context: ContextVar[dict[str, object] | None] = ContextVar("logly_context", default=None)
_logly_level_tls: threading.local = threading.local()


@dataclass(frozen=True, slots=True)
class Level:
    """Represents a registered log level.

    Returned by ``logger.level("NAME")``. Contains the level name, numeric
    severity, optional ANSI color, and optional icon/emoji.

    Attributes:
        name: Level name (e.g. ``"INFO"``).
        no: Numeric severity priority.
        color: ANSI color name or ``None``.
        icon: Icon/emoji string or ``None``.

    Example::

        info = logger.level("INFO")
        print(info.name)    # "INFO"
        print(info.no)      # 20
        print(info.color)   # None
        print(info.icon)    # None
    """

    name: str
    no: int
    color: str | None
    icon: str | None = None


def _current_context() -> dict[str, object]:
    """Return a copy of the current context variables.

    Returns:
        A dictionary containing all currently bound context values.
        Returns an empty dict if no context is set.
    """
    return dict(_context.get() or {})


@dataclass
class _Options:
    """Per-call logging options.

    Attributes:
        exception: Exception instance or bool to attach to the log record.
        lazy: Whether to use lazy string evaluation.
        raw: Whether to skip message rendering.
        record: Whether to return the record dict.
        depth: Stack frame depth for caller info capture.
        colors: Whether to enable ANSI color output.
        ansi: Whether to treat message as ANSI-formatted.
        capture: Whether to capture caller file/line/function.
        backtrace: Whether to include backtrace in exception formatting.
        diagnose: Whether to include diagnostic info in exceptions.
    """

    exception: BaseException | bool | None = None
    lazy: bool = False
    raw: bool = False
    record: bool = False
    depth: int = 0
    colors: bool = False
    ansi: bool = False
    capture: bool = True
    backtrace: bool = True
    diagnose: bool = False


class Logger:
    """Python convenience facade over the native Logly engine.

    All business logic (level resolution, message rendering, exception text
    formatting, record construction, patching, filtering) is handled in Rust.
    This class is a thin wrapper that delegates to the PyO3 _Logger.
    """

    _root_dir: Path | None = None

    def __init__(
        self,
        native: _Logger | None = None,
        *,
        name: str = "logly",
        bound: Mapping[str, object] | None = None,
        patchers: tuple[Callable[[dict[str, object]], None], ...] = (),
        options: _Options | None = None,
        sink_configs: dict[int, tuple[object, dict[str, object]]] | None = None,
    ) -> None:
        """Initialize a new Logger instance.

        Args:
            native: Internal Rust logger engine. If ``None``, a new one is created.
            name: Logger name identifier (default: ``"logly"``).
            bound: Initial context key-value pairs to bind.
            patchers: Tuple of callables that mutate record dicts before dispatch.
            options: Default per-call options.
            sink_configs: Existing sink configurations (for cloning).
        """
        self._native = native or _Logger()
        self._name = name
        self._bound = dict(bound or {})
        self._patchers = patchers
        self._options = options or _Options()
        self._start_time = time.time()
        self._async_futures: list[
            tuple[
                concurrent.futures.Future[Any],
                asyncio.AbstractEventLoop,
                bool,
                threading.Thread | None,
            ]
        ] = []
        self._sink_configs: dict[int, tuple[object, dict[str, Any]]] = sink_configs or {}

    def add(
        self,
        sink: object = sys.stderr,
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
        watch: bool = False,
        context: str | multiprocessing.context.BaseContext | None = None,
        catch: bool = True,
        mode: str = "a",
        buffering: int = 1,
        loop: asyncio.AbstractEventLoop | None = None,
        opener: Callable[..., object] | None = None,
        **kwargs: object,
    ) -> int:
        """Add a logging sink.

        The sink can be a file path (str/Path), a file-like object with
        ``.write()``, a callable, a coroutine function, or a ``logging.Handler``.

        Args:
            sink: Destination for log messages. Can be:
                - ``"stderr"`` or ``"stdout"`` for console output
                - A file path string or ``Path`` object
                - Any object with a ``.write()`` method
                - A callable ``Callable[[str], Any]``
                - A coroutine function (async sink)
                - A ``logging.Handler`` instance
            level: Minimum log level for this sink (default ``"DEBUG"``).
            format: Format template string or callable. Uses tokens like
                ``{time}``, ``{level}``, ``{message}``, ``{file}``, ``{line}``,
                ``{function}``, ``{extra[key]}``.
            rotation: Rotation policy. Accepts size strings (``"10 MB"``),
                time strings (``"daily"``, ``"hourly"``), clock strings
                (``"00:00"``), weekday names (``"monday"``), or ``None``.
            retention: Retention policy. Accepts count (``7``), time strings
                (``"30 days"``), or ``None``.
            compression: Compression codec (``"gzip"``, ``"zip"``, ``"bz2"``,
                ``"xz"``, ``"zstd"``, or ``None``).
            enqueue: If ``True``, dispatch through a background worker.
            colorize: ANSI color override. ``None`` = auto-detect,
                ``True`` = force on, ``False`` = force off.
            backtrace: If ``True``, include backtrace on exceptions.
            diagnose: If ``True``, include diagnostic info on exceptions.
            filter: Filter rule. Can be a string (prefix), callable, or
                mapping of extra field values.
            serialize: If ``True``, output as JSON.
            pretty_json: Pretty JSON configuration (``True``, or
                ``PrettyJsonConfig`` instance).
            patch: Callable that mutates the record dict before dispatch.
            encoding: File encoding (default ``"utf-8"``).
            delay: If ``True``, delay file opening until first write.
            watch: If ``True``, reopen the log file if it is deleted or
                replaced (useful with external log rotation tools).
            context: Multiprocessing context for queue-based sinks.
            catch: If ``True``, catch sink errors silently.
            mode: File mode (``"a"`` for append, ``"w"`` for overwrite).
            buffering: File buffering level.
            loop: Event loop for async sinks.
            opener: Custom file opener.

        Returns:
            Integer handler ID for use with :meth:`remove`.

        Example::

            logger.add("app.log", level="INFO", rotation="daily")
            logger.add("stderr", colorize=True)
        """
        _ = (backtrace, diagnose, context, buffering, opener, kwargs)

        if format is None:
            format = (
                "<green>{time:%Y-%m-%d %H:%M:%S}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )

        if colorize is None:
            if sink is sys.stderr or sink == "stderr":
                colorize = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
            elif sink is sys.stdout or sink == "stdout":
                colorize = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
            else:
                colorize = False

        # Detect logging.Handler — wrap it as a callable
        if isinstance(sink, logging.Handler):
            handler = sink
            level_val = getattr(logging, "NOTSET", 0)
            for lvl_name in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
                if hasattr(logging, lvl_name):
                    lvl_int = getattr(logging, lvl_name)
                    if isinstance(lvl_int, int) and lvl_int <= handler.level:
                        level_val = lvl_int
            _ = level_val

            def _handler_sink(message: str) -> None:
                lvl_no = getattr(_logly_level_tls, "level", 0)
                if lvl_no < handler.level:
                    return
                record = logging.LogRecord(
                    name="logly",
                    level=lvl_no,
                    pathname="",
                    lineno=0,
                    msg=message.rstrip("\n"),
                    args=(),
                    exc_info=None,
                )
                handler.emit(record)

            sink = _handler_sink

        # Detect coroutine function — schedule on event loop
        if callable(sink) and asyncio.iscoroutinefunction(sink):
            target_loop = loop
            if target_loop is None:
                try:
                    target_loop = asyncio.get_running_loop()
                except RuntimeError:
                    target_loop = None

            if target_loop is None or not target_loop.is_running():
                _started_loop = True
                if target_loop is None:
                    target_loop = asyncio.new_event_loop()
                _loop_thread = threading.Thread(
                    target=target_loop.run_forever, daemon=True, name="logly-async-sink"
                )
                _loop_thread.start()
            else:
                _started_loop = False
                _loop_thread = None

            _target_loop = target_loop
            _owns = _started_loop
            _original_sink: Callable[[str], Any] = sink
            _loop_thread_ref = _loop_thread if _started_loop else None

            async def _wrapper(message: str) -> None:
                await _original_sink(message)

            def _async_sink(message: str) -> None:
                coro = _wrapper(message)
                future = asyncio.run_coroutine_threadsafe(coro, _target_loop)
                self._async_futures.append((future, _target_loop, _owns, _loop_thread_ref))

            sink = _async_sink

        # Detect Path
        rust_sink = sink
        if isinstance(sink, Path):
            rust_sink = str(sink)
        elif isinstance(sink, str) and not sink.startswith(("stdout", "stderr")):
            sink_path = Path(sink)
            if not sink_path.is_absolute() and Logger._root_dir is not None:
                resolved = Logger._root_dir / sink_path
                resolved.parent.mkdir(parents=True, exist_ok=True)
                rust_sink = str(resolved)
                sink = resolved

        sink_id = self._native.add(
            rust_sink,
            level=str(level),
            format=format,
            colorize=colorize,
            serialize=serialize,
            pretty_json=pretty_json,
            enqueue=enqueue,
            rotation=rotation,
            retention=retention,
            compression=compression,
            delay=delay,
            watch=watch,
            mode=mode,
            encoding=encoding,
            filter=filter,
            patch=patch,
        )

        # Store sink config for reinstall
        self._sink_configs[sink_id] = (
            sink,
            {
                "level": level,
                "format": format,
                "rotation": rotation,
                "retention": retention,
                "compression": compression,
                "enqueue": enqueue,
                "colorize": colorize,
                "backtrace": backtrace,
                "diagnose": diagnose,
                "filter": filter,
                "serialize": serialize,
                "patch": patch,
                "encoding": encoding,
                "delay": delay,
                "context": context,
                "catch": catch,
                "mode": mode,
                "buffering": buffering,
                "loop": loop,
                "opener": opener,
            },
        )

        return sink_id

    def remove(self, handler_id: int | None = None) -> None:
        """Remove a previously added handler.

        Args:
            handler_id: The handler ID returned by :meth:`add`. If ``None``,
                all handlers are removed from this logger.

        Example::

            sink_id = logger.add(sys.stderr)
            logger.remove(sink_id)
        """
        self._native.remove(handler_id)

    def complete(self) -> None:
        """Wait for the end of enqueued messages and asynchronous tasks.

        This method proceeds in two steps: first it waits for all logging
        messages added to handlers with ``enqueue=True`` to be processed,
        then it awaits all coroutine tasks scheduled by async sinks.
        """
        self._native.complete()
        owned_loops: list[tuple[asyncio.AbstractEventLoop, threading.Thread | None]] = []
        seen: set[int] = set()
        for future, loop, owns, thread in list(self._async_futures):
            try:
                future.result()
            except Exception:
                pass
            if owns and id(loop) not in seen:
                seen.add(id(loop))
                owned_loops.append((loop, thread))
        self._async_futures.clear()
        for loop, thread in owned_loops:
            if loop.is_running():
                loop.call_soon_threadsafe(loop.stop)
            if thread is not None:
                thread.join(timeout=5.0)

    def catch(
        self,
        exception: type[BaseException] | tuple[type[BaseException], ...] | None = Exception,
        *,
        level: str = "ERROR",
        reraise: bool = False,
        onerror: Callable[[BaseException], None] | None = None,
        exclude: type[BaseException] | tuple[type[BaseException], ...] | None = None,
        default: object = None,
    ) -> _CatchContext:
        """Return a decorator/context manager that logs caught exceptions.

        Works as both a context manager and a decorator. When an exception
        occurs, it is logged at the specified level and optionally re-raised.

        Args:
            exception: Exception type(s) to catch. If ``None``, catches all
                ``Exception`` subclasses.
            level: Log level for caught exceptions (default ``"ERROR"``).
            reraise: If ``True``, re-raise the exception after logging.
            onerror: Callback invoked with the caught exception.
            exclude: Exception type(s) to skip (re-raise without logging).
            default: Return value when used as decorator and exception occurs.

        Returns:
            A ``_CatchContext`` that works as decorator and context manager.

        Example::

            # As context manager
            with logger.catch():
                risky_operation()

            # As decorator
            @logger.catch(reraise=True)
            def critical_function():
                raise ValueError("Error")
        """
        return _CatchContext(
            self,
            reraise=reraise,
            level=level,
            onerror=onerror,
            exception_type=exception if exception is not None else Exception,
            exclude=exclude,
            default=default,
        )

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
        """Return a logger view with per-call options.

        Args:
            exception: Exception to attach, or ``True`` to capture current exception.
            record: If ``True``, :meth:`log` returns the record dict.
            lazy: If ``True``, defer string formatting until needed.
            colors: If ``True``, enable ANSI color codes in output.
            raw: If ``True``, skip message rendering entirely.
            capture: If ``True``, capture caller file/line/function info.
            depth: Number of additional stack frames to skip for caller info.
            ansi: If ``True``, treat message as ANSI-formatted.
            backtrace: If ``True``, include backtrace in exception output.
            diagnose: If ``True``, include diagnostic info in exceptions.

        Returns:
            A new Logger instance with the specified options applied.

        Example::

            logger.opt(exception=True).error("Something failed")
            record = logger.opt(record=True).info("Return the record")
        """
        clone = self._clone()
        clone._options = _Options(
            exception=exception,
            lazy=lazy,
            raw=raw,
            record=record,
            depth=depth,
            colors=colors or ansi,
            ansi=ansi,
            capture=capture,
            backtrace=backtrace,
            diagnose=diagnose,
        )
        return clone

    def bind(self, **kwargs: object) -> Self:
        """Return a logger view with bound context key-value pairs.

        Bound values are included in all log records emitted by the
        returned logger view.

        Args:
            **kwargs: Key-value pairs to bind to the logger context.

        Returns:
            A new Logger instance with the specified context bound.

        Example::

            user_logger = logger.bind(user="alice", role="admin")
            user_logger.info("User logged in")
            # Output includes: user=alice role=admin
        """
        clone = self._clone()
        clone._bound = {**self._bound, **kwargs}
        return clone

    @contextmanager
    def contextualize(self, **kwargs: object) -> Generator[None, None, None]:
        """Temporarily bind context values for the current thread/task.

        Uses ``contextvars`` so contextualized values are unique to each
        thread and asynchronous task, and are automatically cleaned up
        when the context manager exits.

        Args:
            **kwargs: Key-value pairs to add to the current context.

        Yields:
            ``None``. Context values are available to all log calls within
            this block.

        Example::

            with logger.contextualize(request_id="abc-123"):
                logger.info("Processing request")  # includes request_id
            logger.info("After request")  # request_id is gone
        """
        token = _context.set({**_current_context(), **kwargs})
        try:
            yield
        finally:
            _context.reset(token)

    def root_dir(self, path: str | Path) -> None:
        """Set the default root directory for all file sinks.

        When set, relative file paths passed to ``add()`` are resolved
        relative to this directory.

        Args:
            path: Root directory path. Created if it doesn't exist.
        """
        resolved = Path(path).resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        Logger._root_dir = resolved

    def patch(self, patcher: Callable[[dict[str, object]], None]) -> Self:
        """Return a logger view that applies a patcher to all records.

        The patcher callable receives the record dict and can modify it
        in-place before it is dispatched to sinks.

        Args:
            patcher: A callable that mutates the record dict.

        Returns:
            A new Logger instance with the patcher applied.

        Example::

            def add_service(record):
                record["extra"]["service"] = "my-api"

            patched = logger.patch(add_service)
            patched.info("Hello")  # extra includes service=my-api
        """
        clone = self._clone()
        clone._patchers = (*self._patchers, patcher)
        return clone

    def level(
        self,
        name: str,
        no: int | None = None,
        color: str | None = None,
        icon: str | None = None,
    ) -> Level:
        """Inspect or register a custom log level.

        When called with only ``name``, returns the level's current
        configuration as a :class:`Level` object. When ``no`` is provided,
        registers a new level.

        Args:
            name: Level name (e.g. ``"VERBOSE"``).
            no: Numeric priority. If provided, registers the level.
            color: ANSI color code for the level (e.g. ``"green"``).
            icon: Icon/emoji for the level (e.g. ``"🚀"``).

        Returns:
            :class:`Level` with ``.name``, ``.no``, ``.color``, ``.icon``.

        Example::

            # Register a custom level
            logger.level("SUCCESS_PLUS", no=35, color="green", icon="🚀")

            # Inspect an existing level
            info = logger.level("INFO")
            print(info.name)    # "INFO"
            print(info.no)      # 20
            print(info.color)   # None
            print(info.icon)    # None
        """
        if no is not None:
            register_custom_level(name, no, color, icon)
        name_str, priority, color_opt, icon_opt = inspect_level(name)
        return Level(name=name_str, no=priority, color=color_opt, icon=icon_opt)

    def enable(self, name: str) -> None:
        """Enable log emission for a logger name pattern.

        Args:
            name: Logger name or pattern to enable.

        Example::

            logger.enable("myapp.database")
        """
        self._native.enable(name)

    def disable(self, name: str) -> None:
        """Disable log emission for a logger name pattern.

        Args:
            name: Logger name or pattern to disable.

        Example::

            logger.disable("myapp.debug")
        """
        self._native.disable(name)

    def configure(
        self,
        *,
        handlers: list[dict[str, Any]] | None = None,
        levels: list[dict[str, object]] | None = None,
        extra: dict[str, object] | None = None,
        patcher: Callable[[dict[str, object]], None] | None = None,
        activation: list[tuple[str, bool]] | None = None,
    ) -> None:
        """Replace the current logging configuration.

        All parameters are optional. If ``handlers`` is provided, existing
        handlers are removed and replaced. ``levels`` registers custom levels.
        ``extra`` binds default extra context. ``patcher`` is applied to all
        records. ``activation`` enables/disables loggers by name pattern.

        Args:
            handlers: List of handler config dicts (each with ``sink`` key).
            levels: List of level dicts with ``name``, ``no``, ``color``, ``icon``.
            extra: Default extra context to bind.
            patcher: Callable applied to all records before dispatch.
            activation: List of ``(name, enabled)`` tuples for logger activation.
        """
        if levels is not None:
            for lvl in levels:
                lvl_name = str(lvl.get("name", ""))
                lvl_no = lvl.get("no")
                lvl_color = lvl.get("color")
                lvl_icon = lvl.get("icon")
                if lvl_name and lvl_no is not None:
                    self.level(
                        lvl_name,
                        int(str(lvl_no)),
                        str(lvl_color) if lvl_color else None,
                        str(lvl_icon) if lvl_icon else None,
                    )

        if handlers is not None:
            self.remove()
            for handler in handlers:
                h = dict(handler)
                sink = h.pop("sink", sys.stderr)
                self.add(sink, **h)  # type: ignore[arg-type]

        if extra is not None:
            self._bound.update(extra)

        if patcher is not None:
            self._patchers = (*self._patchers, patcher)

        if activation is not None:
            for name_pattern, active in activation:
                if active:
                    self.enable(name_pattern)
                else:
                    self.disable(name_pattern)

    def reinstall(self, handler_id: int | None = None) -> None:
        """Remove and re-add a handler by its ID.

        This is useful to reset file handlers (e.g., after log rotation).

        Args:
            handler_id: The handler ID to reinstall. If ``None``, all
                handlers are reinstalled.

        Example::

            sink_id = logger.add("app.log")
            logger.reinstall(sink_id)  # Reset the file handler
        """
        if handler_id is not None:
            config = self._sink_configs.get(handler_id)
            self._native.remove(handler_id)
            if config is not None:
                sink, kwargs = config
                new_id = self.add(sink, **kwargs)  # type: ignore[arg-type]
                self._sink_configs.pop(handler_id, None)
                self._sink_configs[new_id] = config
        else:
            all_configs = dict(self._sink_configs)
            self._native.remove()
            self._sink_configs.clear()
            for _old_id, (sink, kwargs) in all_configs.items():
                new_id = self.add(sink, **kwargs)  # type: ignore[arg-type]

    @staticmethod
    def parse(
        path: str | Path,
        pattern: str | re.Pattern[str] | None = None,
        *,
        cast: dict[str, Callable[[str], object]] | None = None,
        chunk: int = 65536,
        encoding: str = "utf-8",
    ) -> Generator[dict[str, object], None, None]:
        """Parse a log file and yield matched records.

        Args:
            path: Path to the log file.
            pattern: Regex pattern with named groups.
            cast: Mapping of group names to casting functions.
            chunk: Read chunk size in bytes.
            encoding: File encoding.

        Yields:
            Dict with matched groups for each line, optionally cast.
        """
        file_path = Path(path)
        if not file_path.exists():
            return
        re_pattern = (
            re.compile(pattern) if isinstance(pattern, str) else pattern or re.compile(r".*")
        )
        with file_path.open("r", encoding=encoding) as f:
            for line in f:
                line = line.rstrip("\n")
                match = re_pattern.search(line)
                if match:
                    result: dict[str, object] = {"message": line, **match.groupdict()}
                    if cast:
                        for key, func in cast.items():
                            if key in result:
                                try:
                                    result[key] = func(str(result[key]))
                                except (ValueError, KeyError):
                                    pass
                    yield result

    def start(self, *args: object, **kwargs: object) -> None:
        """Start logger-managed background processing hooks.

        Queued sinks start their workers when the sink is registered. This
        method accepts application lifecycle hooks for compatibility with
        service startup code and intentionally performs no work when no
        deferred hooks are configured.
        """
        _ = (args, kwargs)

    def stop(self) -> None:
        """Flush sinks and stop logger-managed background workers."""
        self.complete()

    def log(
        self, level: str | int, message: object, *args: object, **kwargs: object
    ) -> dict[str, object] | None:
        """Log a message at a named or numeric level.

        Supports ``str.format()`` style placeholders::

            logger.info("User {} logged in", username)
            logger.info("User {user} logged in", user=username)

        Returns:
            The record dict if ``opt(record=True)`` was used, otherwise None.
        """
        level_name = resolve_level_name(str(level)) if isinstance(level, int) else str(level)

        if self._options.raw:
            rendered = str(message)
        else:
            effective_kwargs = dict(kwargs) if kwargs else {}
            if self._options.record:
                import inspect as _inspect

                frame = _inspect.currentframe()
                caller_file: str | None = None
                caller_line: int | None = None
                caller_func: str | None = None
                caller_module: str | None = None
                if frame is not None and frame.f_back is not None:
                    caller = frame.f_back
                    if caller is not None:
                        caller_file = caller.f_code.co_filename
                        caller_line = caller.f_lineno
                        caller_func = caller.f_code.co_name
                        caller_module = caller.f_code.co_filename
                        if caller_module:
                            caller_module = os.path.splitext(os.path.basename(caller_module))[0]

                record_sub = {
                    "message": str(message),
                    "level": level_name,
                    "name": self._name,
                    "file": caller_file or "",
                    "line": caller_line or 0,
                    "function": caller_func or "",
                    "module": caller_module or "",
                }
                effective_kwargs["record"] = record_sub

            py_args = [a for a in args] if args else None
            py_kwargs = effective_kwargs if effective_kwargs else None
            rendered = render_message(
                str(message),
                py_args,
                py_kwargs,
                lazy=self._options.lazy,
            )

        extra_map: dict[str, object] = {k: v for k, v in self._bound.items()}
        extra_map.update({k: v for k, v in _current_context().items()})

        exc_text = None
        exc_tuple: tuple[object, object, str] | None = None
        if self._options.exception is not None:
            exc_text = format_exception_text(self._options.exception, self._options.backtrace)
            exc_obj = self._options.exception
            if isinstance(exc_obj, BaseException):
                import traceback as _traceback

                exc_tuple = (
                    type(exc_obj),
                    exc_obj,
                    "".join(
                        _traceback.format_exception(type(exc_obj), exc_obj, exc_obj.__traceback__)
                    ),
                )

        file_val: str | None = None
        line_val: int | None = None
        func_val: str | None = None
        module_val: str | None = None

        if self._options.capture:
            import inspect as _inspect

            frame = _inspect.currentframe()
            if frame is not None:
                cap_frame: types.FrameType | None = frame.f_back
                if cap_frame is not None:
                    cap_frame = cap_frame.f_back
                for _ in range(self._options.depth):
                    if cap_frame is not None:
                        cap_frame = cap_frame.f_back
                if cap_frame is not None:
                    file_val = cap_frame.f_code.co_filename
                    line_val = cap_frame.f_lineno
                    func_val = cap_frame.f_code.co_name
                    if file_val:
                        module_val = os.path.splitext(os.path.basename(file_val))[0]

        record_dict: dict[str, object] = {
            "message": rendered,
            "level": level_name,
            "extra": dict(extra_map),
            "name": self._name,
        }
        if file_val:
            record_dict["file"] = file_val
        if line_val is not None:
            record_dict["line"] = line_val
        if func_val:
            record_dict["function"] = func_val
        if module_val:
            record_dict["module"] = module_val
        record_dict["thread"] = threading.current_thread().name
        record_dict["process"] = os.getpid()
        record_dict["exception"] = exc_tuple

        for patcher in self._patchers:
            try:
                patcher(record_dict)
            except Exception:
                pass

        rendered = str(record_dict.get("message", rendered))
        patched_extra = record_dict.get("extra", extra_map)
        if isinstance(patched_extra, dict):
            extra_map = {k: v for k, v in patched_extra.items()}

        # Convert extra values to strings for Rust-side storage
        extra_str_map: dict[str, str] = {k: str(v) for k, v in extra_map.items()}

        _logly_level_tls.level = inspect_level(level_name)[1]

        self._native.log_structured(
            level=level_name,
            message=rendered,
            name=self._name,
            file=file_val,
            line=line_val,
            function=func_val,
            module=module_val,
            thread_name=threading.current_thread().name,
            process_id=os.getpid(),
            extra=extra_str_map,
            exception=exc_text,
            colors=self._options.colors,
        )

        if self._options.record:
            return record_dict
        return None

    def trace(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at TRACE level (most verbose).

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("TRACE", message, *args, **kwargs)

    def debug(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at DEBUG level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("DEBUG", message, *args, **kwargs)

    def info(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at INFO level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("INFO", message, *args, **kwargs)

    def notice(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at NOTICE level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("NOTICE", message, *args, **kwargs)

    def success(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at SUCCESS level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("SUCCESS", message, *args, **kwargs)

    def warning(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at WARNING level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("WARNING", message, *args, **kwargs)

    def warn(self, message: object, *args: object, **kwargs: object) -> None:
        """Alias for :meth:`warning`.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("WARNING", message, *args, **kwargs)

    def error(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at ERROR level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("ERROR", message, *args, **kwargs)

    def exception(
        self,
        message: object,
        *args: object,
        exc_info: bool = True,
        **kwargs: object,
    ) -> None:
        """Log a message at ERROR level with exception info.

        Automatically captures the current exception if one is active.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            exc_info: Whether to include exception info (default ``True``).
            **kwargs: Keyword arguments for format string substitution.
        """
        _ = exc_info
        exc = sys.exc_info()[1]
        if exc is not None:
            self.opt(exception=exc).log("ERROR", message, *args, **kwargs)
        else:
            self.log("ERROR", message, *args, **kwargs)

    def fail(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at FAIL level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("FAIL", message, *args, **kwargs)

    def critical(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at CRITICAL level.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("CRITICAL", message, *args, **kwargs)

    def fatal(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at FATAL level (highest severity).

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("FATAL", message, *args, **kwargs)

    def audit(self, message: object, *args: object, **kwargs: object) -> None:
        """Log a message at AUDIT level.

        AUDIT level is intended for security and compliance logging.

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            **kwargs: Keyword arguments for format string substitution.
        """
        self.log("AUDIT", message, *args, **kwargs)

    @property
    def levels(self) -> list[str]:
        """Return registered level names in severity order."""
        return list_levels()

    def _clone(self) -> Self:
        """Create a shallow copy of this logger instance.

        Returns:
            A new Logger with the same native engine, name, bound context,
            patchers, options, and sink configs.
        """
        clone = type(self)(
            self._native,
            name=self._name,
            bound=self._bound,
            patchers=self._patchers,
            options=self._options,
            sink_configs=self._sink_configs,
        )
        clone._start_time = self._start_time
        return clone

    def __copy__(self) -> Self:
        """Return a shallow copy of this logger.

        Returns:
            A new Logger instance sharing the same native engine.
        """
        return self._clone()

    def __deepcopy__(self, memo: dict[int, object]) -> Self:
        """Return a deep copy of this logger.

        Args:
            memo: Memo dict for deepcopy tracking.

        Returns:
            A new Logger with deeply copied bound context and patchers.
        """
        import copy as _copy

        clone = type(self)(
            self._native,
            name=self._name,
            bound=_copy.deepcopy(self._bound, memo),
            patchers=_copy.deepcopy(self._patchers, memo),
            options=_copy.deepcopy(self._options, memo),
            sink_configs=_copy.deepcopy(self._sink_configs, memo),
        )
        clone._start_time = self._start_time
        memo[id(self)] = clone
        return clone


class _CatchContext:
    """Context manager and decorator for catching and logging exceptions.

    This class is returned by :meth:`Logger.catch` and can be used as
    either a context manager or a function decorator.
    """

    def __init__(
        self,
        logger: Logger,
        *,
        reraise: bool,
        level: str,
        onerror: Callable[[BaseException], None] | None = None,
        exception_type: type[BaseException] | tuple[type[BaseException], ...] = Exception,
        exclude: type[BaseException] | tuple[type[BaseException], ...] | None = None,
        default: object = None,
    ) -> None:
        """Initialize the catch context.

        Args:
            logger: Logger instance to emit caught exceptions to.
            reraise: If ``True``, re-raise the exception after logging.
            level: Log level for the caught exception message.
            onerror: Optional callback invoked with the exception.
            exception_type: Exception type(s) to catch.
            exclude: Exception type(s) to exclude from catching.
            default: Default return value when used as decorator.
        """
        self._logger = logger
        self._reraise = reraise
        self._level = level
        self._onerror = onerror
        self._exception_type = exception_type
        self._exclude = exclude
        self._default = default

    def __enter__(self) -> _CatchContext:
        """Enter the catch context.

        Returns:
            This instance (for use in ``with`` statements).
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Exit the catch context, logging any caught exception.

        Args:
            exc_type: Exception type, or ``None`` if no exception.
            exc: Exception instance, or ``None``.
            tb: Traceback object, or ``None``.

        Returns:
            ``True`` if the exception was caught and suppressed,
            ``False`` otherwise.
        """
        if exc is not None:
            if self._exclude is not None and isinstance(exc, self._exclude):
                return False
            if not isinstance(exc, self._exception_type):
                return False
            if self._onerror is not None:
                self._onerror(exc)
            self._logger.opt(exception=exc).log(
                self._level,
                "An error has been caught",
            )
            return not self._reraise
        return False

    def __call__(self, func: Callable[..., object]) -> Callable[..., object]:
        """Wrap a function as a decorator that catches and logs exceptions.

        Args:
            func: The function to wrap.

        Returns:
            A wrapped function that catches exceptions matching the
            configured criteria.
        """
        import functools

        @functools.wraps(func)
        def wrapper(*args: object, **inner_kwargs: object) -> object:
            with self:
                return func(*args, **inner_kwargs)
            return self._default  # type: ignore[unreachable]

        return wrapper


logger = Logger()

# LOGLY_AUTOINIT support: set LOGLY_AUTOINIT=false to disable pre-configured sink
_autoinit = os.environ.get("LOGLY_AUTOINIT", "true").lower()
if _autoinit not in ("false", "0", "no"):
    logger.add(sys.stderr, level="DEBUG")
