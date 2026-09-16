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
import atexit
import concurrent.futures
import datetime
import inspect
import io
import logging
import os
import re
import sys
import threading
import time
import traceback
import types
import weakref
from collections.abc import AsyncGenerator, Callable, Coroutine, Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Final, Literal, TypeGuard, TypeVar, cast, overload

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
from logly.typing import FilterCallable, FormatterCallable, LevelType, PatchCallable

try:  # Python 3.14 template strings (PEP 750)
    from string.templatelib import Template as _TemplateString
except ImportError:  # pragma: no cover - Python < 3.14
    _TemplateString = None  # type: ignore[assignment,misc]

_CatchT = TypeVar("_CatchT")

_context: ContextVar[dict[str, object] | None] = ContextVar("logly_context", default=None)
_logly_level_tls: threading.local = threading.local()

# Frame names belonging to the logging machinery itself. Stored once so the
# per-call caller-attribution walk does not rebuild the set every time.
_INTERNAL_FRAMES: Final = frozenset(
    {
        "trace",
        "debug",
        "info",
        "notice",
        "success",
        "warning",
        "warn",
        "error",
        "exception",
        "fail",
        "critical",
        "fatal",
        "audit",
        "__exit__",
        "_catch_wrapper",
    }
)

# Loggers owning background (`enqueue=True`) sinks, mapped to the pid that
# created them. A single interpreter-shutdown hook drains them while the
# interpreter is still alive: dropping a live worker during finalization can
# deadlock against interpreter teardown, so every queued record is flushed
# first. Entries vanish automatically when their logger is collected, and
# the map is cleared in fork children (which must configure their own
# sinks; a copied worker has no live thread behind it).
_enqueue_registry: weakref.WeakKeyDictionary[Logger, int] = weakref.WeakKeyDictionary()


def _drain_enqueue_loggers() -> None:
    """Flush every registered background logger exactly once per process."""
    current_pid = os.getpid()
    for log, pid in list(_enqueue_registry.items()):
        if pid != current_pid:
            continue
        try:
            log.complete()
        except Exception:
            pass


atexit.register(_drain_enqueue_loggers)

if hasattr(os, "register_at_fork"):  # Unix only; absent on Windows
    os.register_at_fork(after_in_child=_enqueue_registry.clear)


def _is_async_callable(obj: object) -> bool:
    """Check if an object is an async callable (coroutine function or async callable class).

    This function detects:
    - Regular async functions defined with `async def`
    - Class instances with async `__call__` methods
    - functools.partial objects wrapping async callables

    Args:
        obj: The object to check.

    Returns:
        True if the object is an async callable, False otherwise.

    Example::

        async def async_func(msg: str) -> None:
            pass

        class AsyncCallable:
            async def __call__(self, msg: str) -> None:
                pass

        assert _is_async_callable(async_func)  # True
        assert _is_async_callable(AsyncCallable())  # True
        assert _is_async_callable(lambda msg: None)  # False
    """
    import functools

    # Handle functools.partial
    if isinstance(obj, functools.partial):
        obj = obj.func

    # Check if it's a coroutine function directly
    if inspect.iscoroutinefunction(obj):
        return True

    # Check if it's a callable object with an async __call__ method
    if callable(obj):
        try:
            if inspect.iscoroutinefunction(obj.__call__):
                return True
        except AttributeError:
            pass

    return False


def _is_console_sink(sink: object) -> bool:
    """Return whether ``sink`` addresses a standard console stream."""
    return sink is sys.stderr or sink is sys.stdout or sink in ("stdout", "stderr")


def _is_path_sink(sink: object) -> TypeGuard[str | Path]:
    """Return whether ``sink`` addresses a file path (not console/object)."""
    return isinstance(sink, (str, Path)) and not _is_console_sink(sink)


class _BinaryStreamAdapter:
    """Adapt a binary stream to the text sink protocol.

    Encodes ``str`` messages with the configured encoding before writing.
    Never takes ownership: it has no ``close`` method and never closes the
    wrapped stream, so removing the sink leaves the caller's object usable.
    """

    def __init__(self, stream: io.BufferedIOBase, encoding: str) -> None:
        self._stream = stream
        self._encoding = encoding

    def write(self, message: object) -> None:
        payload: Any = message.encode(self._encoding) if isinstance(message, str) else message
        self._stream.write(payload)

    def flush(self) -> None:
        self._stream.flush()


def _render_template_string(message: object) -> str:
    """Render a PEP 750 template string into plain text.

    Applies each interpolation's conversion (``!s``/``!r``/``!a``) and format
    specification, mirroring template-string semantics without evaluating
    anything beyond what the template already captured.
    """
    template = cast(Any, message)
    strings: tuple[str, ...] = template.strings
    interpolations: tuple[Any, ...] = template.interpolations
    parts: list[str] = [strings[0]]
    for index, interpolation in enumerate(interpolations):
        value: Any = interpolation.value
        conversion = interpolation.conversion
        spec = interpolation.format_spec or ""
        if conversion == "r":
            value = repr(value)
        elif conversion == "a":
            value = ascii(value)
        elif conversion == "s":
            value = str(value)
        parts.append(format(value, spec))
        parts.append(strings[index + 1])
    return "".join(parts)


def _validate_sink_args(
    sink: object,
    *,
    level: LevelType,
    format: str | FormatterCallable | None,
    rotation: str | int | object | None,
    retention: int | str | object | None,
    compression: str | object | None,
    mode: str,
    buffering: int,
    opener: Callable[..., object] | None,
    encoding: str,
    delay: bool,
    watch: bool,
    context: str | object | None,
) -> None:
    """Validate one sink configuration without side effects.

    Raises:
        ValueError: For invalid option values or unsupported combinations
            (e.g. rotation on a non-file sink).
        TypeError: For options of the wrong type.

    Used by :meth:`Logger.add` and :meth:`Logger.configure` (which validates
    every handler before mutating active state).
    """
    from logly._logly import (
        parse_compression_str,
        parse_retention_str,
        parse_rotation_str,
    )

    if isinstance(level, bool) or not isinstance(level, (str, int)):
        raise TypeError(f"level must be a level name or priority, got {level!r}")
    if isinstance(level, int):
        resolve_level_name(str(level))
    else:
        inspect_level(level)

    if mode not in ("a", "w"):
        raise ValueError(f'mode must be "a" or "w", got {mode!r}')

    if format is not None and not isinstance(format, str) and not callable(format):
        raise TypeError("format must be a template string, a callable, or None")

    if isinstance(buffering, bool) or not isinstance(buffering, int):
        raise TypeError(f"buffering must be an int, got {buffering!r}")
    if opener is not None and not callable(opener):
        raise TypeError("opener must be a callable or None")
    if not isinstance(encoding, str):
        raise TypeError(f"encoding must be a string, got {encoding!r}")

    if context is not None:
        raise TypeError(
            "context must be None: cross-process queue sinks are not supported; "
            "spawn child processes that configure their own Logger instead "
            "(see the concurrency guide)"
        )

    if rotation is not None:
        if isinstance(rotation, bool):
            raise TypeError(f"invalid rotation policy: {rotation!r}")
        elif isinstance(rotation, str):
            parse_rotation_str(rotation)
        elif isinstance(rotation, int):
            if rotation < 0:
                raise ValueError(f"rotation byte size must be >= 0, got {rotation}")
        elif callable(rotation):
            pass
        elif hasattr(rotation, "kind"):
            kind = rotation.kind
            if kind not in ("never", "size", "interval", "clock", "weekday", "callable"):
                raise ValueError(f"unknown rotation policy kind: {kind!r}")
            if kind == "callable" and not callable(getattr(rotation, "value", None)):
                raise ValueError("callable rotation policy value must be callable")
        else:
            raise TypeError(f"invalid rotation policy: {rotation!r}")

    if retention is not None:
        if isinstance(retention, bool):
            raise TypeError(f"invalid retention policy: {retention!r}")
        elif isinstance(retention, str):
            parse_retention_str(retention)
        elif isinstance(retention, int):
            if retention < 0:
                raise ValueError(f"retention count must be >= 0, got {retention}")
        elif hasattr(retention, "count") or hasattr(retention, "seconds"):
            pass
        else:
            raise TypeError(f"invalid retention policy: {retention!r}")

    if compression is not None:
        if isinstance(compression, str):
            parse_compression_str(compression)
        elif hasattr(compression, "codec"):
            parse_compression_str(str(compression.codec))
        else:
            raise TypeError(f"invalid compression codec: {compression!r}")

    if _is_path_sink(sink) and (opener is not None or buffering != 1 or encoding != "utf-8"):
        # Such sinks are opened in Python (see Logger.add), which cannot
        # rotate, retain, compress, delay, or watch.
        if (
            rotation is not None
            or retention is not None
            or compression is not None
            or delay
            or watch
        ):
            raise ValueError(
                "opener, buffering, and encoding require a plain file sink "
                "without rotation, retention, compression, delay, or watch"
            )

    if not _is_path_sink(sink):
        if (
            not _is_console_sink(sink)
            and not callable(sink)
            and not hasattr(sink, "write")
            and not isinstance(sink, logging.Handler)
        ):
            raise TypeError(
                "sink must be a file path, console stream name, text/binary stream, "
                f"callable, coroutine, or logging handler, got {type(sink).__name__!r}"
            )
        if rotation is not None or retention is not None or compression is not None:
            raise ValueError("rotation, retention, and compression require a file path sink")
        if delay or watch:
            raise ValueError("delay and watch require a file path sink")
        if opener is not None:
            raise ValueError("opener requires a file path sink")
        if buffering != 1 or encoding != "utf-8":
            if not isinstance(sink, (io.RawIOBase, io.BufferedIOBase)):
                raise ValueError(
                    "buffering and encoding only apply to file path and binary stream sinks"
                )
            if buffering != 1:
                raise ValueError("buffering must be 1 for binary stream sinks")


@dataclass(frozen=True, slots=True)
class Level:
    """Represents a registered log level.

    Returned by ``logger.level("NAME")``. Contains the level name, numeric
    severity, optional ANSI color, and optional icon/emoji.

    Levels compare by numeric severity (``no``), with the name as a
    deterministic tiebreak, so ``logger.level("DEBUG") < logger.level("ERROR")``.

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

    def _severity_key(self) -> tuple[int, str]:
        return (self.no, self.name)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self._severity_key() < other._severity_key()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self._severity_key() <= other._severity_key()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self._severity_key() > other._severity_key()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self._severity_key() >= other._severity_key()


def _current_context() -> dict[str, object]:
    """Return a copy of the current context variables.

    Returns:
        A dictionary containing all currently bound context values.
        Returns an empty dict if no context is set.
    """
    return dict(_context.get() or {})


def _diagnose_suffix(exc: BaseException, *, max_frames: int = 16, max_vars: int = 12) -> str | None:
    """Build a bounded diagnostic suffix listing frame locals per traceback frame.

    Every value is rendered with a guarded, truncated ``repr`` so exotic
    objects cannot break or bloat logging. Returns ``None`` when no frame
    information is available.
    """
    lines: list[str] = ["--- Diagnostic context ---"]
    tb = exc.__traceback__
    count = 0
    while tb is not None and count < max_frames:
        frame = tb.tb_frame
        try:
            items = list(frame.f_locals.items())[:max_vars]
            rendered_vars = ", ".join(
                f"{key}={_safe_repr(value)}" for key, value in items if not key.startswith("__")
            )
        except Exception:
            rendered_vars = "<unavailable>"
        lines.append(
            f"{frame.f_code.co_filename}:{tb.tb_lineno} in {frame.f_code.co_name}"
            + (f" | {rendered_vars}" if rendered_vars else "")
        )
        count += 1
        tb = tb.tb_next
    return "\n".join(lines) if count else None


def _safe_repr(value: object, limit: int = 200) -> str:
    """Return a truncated ``repr`` that never raises."""
    try:
        text = repr(value)
    except Exception:
        return "<unrepresentable>"
    if len(text) > limit:
        return text[:limit] + "…"
    return text


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
        patchers: tuple[PatchCallable, ...] = (),
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
        # Mirror of the native engine's disabled-name set. Consulted first
        # in log() so disabled logging returns without any formatting,
        # frame inspection, or FFI crossing. The native engine remains the
        # source of truth for direct _native users.
        self._disabled: set[str] = set()
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
        level: LevelType = "DEBUG",
        format: str | FormatterCallable | None = None,
        rotation: str | int | object | None = None,
        retention: int | str | object | None = None,
        compression: str | object | None = None,
        enqueue: bool = False,
        colorize: bool | None = None,
        backtrace: bool = True,
        diagnose: bool = False,
        filter: str | FilterCallable | Mapping[str, str | bool] | None = None,
        serialize: bool = False,
        pretty_json: bool | PrettyJsonConfig | None = None,
        patch: PatchCallable | None = None,
        encoding: str = "utf-8",
        delay: bool = False,
        watch: bool = False,
        context: None = None,
        catch: bool = True,
        mode: str = "a",
        buffering: int = 1,
        loop: asyncio.AbstractEventLoop | None = None,
        opener: Callable[..., object] | None = None,
        **kwargs: object,
    ) -> int:
        """Add a logging sink.

        The sink can be a file path (str/Path), a text or binary stream with
        ``.write()`` (binary streams are adapted with ``encoding``), a
        callable, a coroutine function, or a ``logging.Handler``.

        Args:
            sink: Destination for log messages. Can be:
                - ``"stderr"`` or ``"stdout"`` for console output
                - A file path string or ``Path`` object
                - A text stream with a ``.write()`` method
                - A binary stream (adapted to text using ``encoding``)
                - A callable ``Callable[[str], Any]``
                - A coroutine function (async sink)
                - A ``logging.Handler`` instance
            level: Minimum log level for this sink (default ``"DEBUG"``).
                Accepts level names (``"INFO"``) or numeric priorities
                (``20``), resolved exactly like :meth:`log` levels.
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
            backtrace: Accepted for compatibility; exception detail is
                controlled per message via ``opt(exception=..., backtrace=...)``.
            diagnose: Accepted for compatibility; reserved for per-message
                diagnostic detail via ``opt(exception=..., diagnose=...)``.
            filter: Filter rule. Can be a string (prefix), callable, or
                mapping of extra field values.
            serialize: If ``True``, output as JSON.
            pretty_json: Pretty JSON configuration (``True``, or
                ``PrettyJsonConfig`` instance).
            patch: Callable that mutates the record dict before dispatch.
            encoding: File encoding (default ``"utf-8"``). A non-default
                encoding (or ``opener``/``buffering``) opens the file in
                Python instead of natively, so it cannot be combined with
                ``rotation``, ``retention``, ``compression``, ``delay``, or
                ``watch``.
            delay: If ``True``, delay file opening until first write.
            watch: If ``True``, reopen the log file if it is deleted or
                replaced (useful with external log rotation tools).
            context: Must be ``None``. Cross-process queue sinks are not
                supported; spawn child processes that configure their own
                ``Logger`` instead (see the concurrency guide).
            catch: If ``True``, catch sink errors silently.
            mode: File mode (``"a"`` for append, ``"w"`` for overwrite).
            buffering: File buffering level. Non-default values require a
                file path sink without rotation and friends (see
                ``encoding``).
            loop: Event loop for async sinks.
            opener: Custom file opener ``Callable[[str, int], int]``. Only
                valid with a file path sink without rotation and friends
                (see ``encoding``).

        Returns:
            Integer handler ID for use with :meth:`remove`.

        Raises:
            ValueError: For invalid option values or unsupported
                combinations (e.g. rotation on a non-file sink, an unknown
                ``mode``, or ``opener`` with rotation).
            TypeError: For options of the wrong type.

        Example::

            logger.add("app.log", level="INFO", rotation="daily")
            logger.add("stderr", colorize=True)
        """
        _ = (backtrace, diagnose, kwargs)
        # `backtrace`/`diagnose` are accepted for compatibility; exception
        # detail is controlled per message via ``opt(exception=...,
        # backtrace=..., diagnose=...)``.
        _validate_sink_args(
            sink,
            level=level,
            format=format,
            rotation=rotation,
            retention=retention,
            compression=compression,
            mode=mode,
            buffering=buffering,
            opener=opener,
            encoding=encoding,
            delay=delay,
            watch=watch,
            context=context,
        )
        # Integer levels resolve exactly like names; the native engine only
        # resolves level names.
        level_name = resolve_level_name(str(level)) if isinstance(level, int) else level

        if format is None:
            format = (
                "<green>{time:%Y-%m-%d %H:%M:%S}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{filename}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
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

            # Marker read by log() to decide whether the per-record numeric
            # level must be published for handler filtering.
            _handler_sink._logly_captures_level = True  # type: ignore[attr-defined]
            sink = _handler_sink

        # Detect coroutine function or async callable — schedule on event loop
        if callable(sink) and _is_async_callable(sink):
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
                result = _original_sink(message)
                # If the result is awaitable, await it
                if hasattr(result, "__await__"):
                    await result  # type: ignore[misc]

            def _async_sink(message: str) -> None:
                coro = _wrapper(message)
                future = asyncio.run_coroutine_threadsafe(coro, _target_loop)
                self._async_futures.append((future, _target_loop, _owns, _loop_thread_ref))

            sink = _async_sink

        # Detect binary streams — adapt them to text with the requested
        # encoding so no message is silently dropped.
        if (
            not _is_console_sink(sink)
            and not _is_path_sink(sink)
            and hasattr(sink, "write")
            and not callable(sink)
        ):
            if isinstance(sink, io.RawIOBase):
                sink = _BinaryStreamAdapter(io.BufferedWriter(sink), encoding)
            elif isinstance(sink, io.BufferedIOBase):
                sink = _BinaryStreamAdapter(sink, encoding)

        # Detect Path
        rust_sink = sink
        reinstall_sink: object = sink
        if isinstance(sink, Path):
            rust_sink = str(sink)
        elif isinstance(sink, str) and sink not in ("stdout", "stderr"):
            sink_path = Path(sink)
            if not sink_path.is_absolute() and Logger._root_dir is not None:
                resolved = Logger._root_dir / sink_path
                resolved.parent.mkdir(parents=True, exist_ok=True)
                rust_sink = str(resolved)
                sink = resolved

        # A custom opener, non-default buffering, or non-UTF-8 encoding
        # cannot be honored by the native file sink, so open the file here
        # in Python and dispatch to it as a stream sink. Rotation and
        # friends require the native file sink (enforced above).
        if _is_path_sink(sink) and (opener is not None or buffering != 1 or encoding != "utf-8"):
            target: Path = Path(sink) if isinstance(sink, str) else sink
            if not target.is_absolute() and Logger._root_dir is not None:
                target = Logger._root_dir / target
            target.parent.mkdir(parents=True, exist_ok=True)
            mode_char: Literal["w", "a"] = "w" if mode == "w" else "a"
            file_opener = cast("Callable[[str, int], int] | None", opener)
            sink = open(
                target,
                mode_char,
                encoding=encoding,
                buffering=buffering,
                opener=file_opener,
                # Raw newlines, exactly like the native file sink: formatted
                # records already end with "\n" and must not gain "\r".
                newline="\n",
            )
            rust_sink = sink
            reinstall_sink = str(target)

        sink_id = self._native.add(
            rust_sink,
            level=level_name,
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

        if enqueue:
            # Ensure background queues are drained during interpreter
            # shutdown even if the application never calls complete().
            _enqueue_registry[self] = os.getpid()

        # Store sink config for reinstall
        self._sink_configs[sink_id] = (
            reinstall_sink,
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
        # Keep the Python-side mirror in sync so exception-visibility checks
        # (see log()) only consider still-active sinks.
        if handler_id is None:
            self._sink_configs.clear()
        else:
            self._sink_configs.pop(handler_id, None)

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

    def flush(self) -> None:
        """Flush all sinks, ensuring buffered records are written.

        Equivalent to :meth:`complete`: drains ``enqueue=True`` background
        queues and awaits pending async-sink tasks. Safe to call multiple
        times.

        Example::

            logger.add("app.log", enqueue=True)
            logger.info("hello")
            logger.flush()
        """
        self.complete()

    def catch(
        self,
        exception: type[BaseException] | tuple[type[BaseException], ...] | None = Exception,
        *,
        level: str = "ERROR",
        reraise: bool = False,
        onerror: Callable[[BaseException], None] | None = None,
        exclude: type[BaseException] | tuple[type[BaseException], ...] | None = None,
        default: object = None,
        message: str | None = None,
    ) -> _CatchContext:
        """Return a decorator/context manager that logs caught exceptions.

        Works as a context manager, an async context manager, and a decorator
        (sync, async, generator, and async-generator functions). When an
        exception occurs, it is logged at the specified level and optionally
        re-raised.

        Args:
            exception: Exception type(s) to catch. If ``None``, catches all
                ``Exception`` subclasses.
            level: Log level for caught exceptions (default ``"ERROR"``).
            reraise: If ``True``, re-raise the exception after logging.
            onerror: Callback invoked with the caught exception.
            exclude: Exception type(s) to skip (re-raise without logging).
            default: Return value when used as decorator and exception occurs.
            message: Custom message logged with the caught exception
                (default ``"An error has been caught"``).

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
            message=message,
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

    def patch(self, patcher: PatchCallable) -> Self:
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
        """Enable log emission for a logger name.

        Names match exactly: enabling ``"myapp"`` re-enables only loggers
        named exactly ``"myapp"``.

        Args:
            name: Logger name to enable.

        Example::

            logger.enable("myapp.database")
        """
        self._native.enable(name)
        self._disabled.discard(name)

    def disable(self, name: str) -> None:
        """Disable log emission for a logger name.

        Names match exactly: disabling ``"myapp"`` silences only loggers
        named exactly ``"myapp"``. Disabled names skip formatting and
        dispatch entirely in :meth:`log`, and are also enforced by the
        native engine, so a disabled log call performs no formatting,
        frame inspection, FFI crossing, or sink dispatch.

        Args:
            name: Logger name to disable.

        Example::

            logger.disable("myapp.debug")
        """
        self._native.disable(name)
        self._disabled.add(name)

    def configure(
        self,
        *,
        handlers: list[dict[str, Any]] | None = None,
        levels: list[dict[str, object]] | None = None,
        extra: dict[str, object] | None = None,
        patcher: PatchCallable | None = None,
        activation: list[tuple[str, bool]] | None = None,
    ) -> None:
        """Update the current logging configuration.

        All parameters are optional. If ``handlers`` is provided, existing
        handlers are removed and replaced. ``levels`` registers custom levels.
        ``extra`` is merged into the bound default extra context.
        ``patcher`` is appended to the record patchers.
        ``activation`` enables/disables loggers by exact logger name.

        Every handler is validated before any active sink is touched, so a
        bad handler configuration raises without destroying the sinks that
        are already installed.

        Args:
            handlers: List of handler config dicts (each with ``sink`` key).
            levels: List of level dicts with ``name``, ``no``, ``color``, ``icon``.
            extra: Default extra context to bind.
            patcher: Callable applied to all records before dispatch.
            activation: List of ``(name, enabled)`` tuples for logger activation.

        Raises:
            ValueError: If any handler configuration is invalid.
            TypeError: If any handler option has the wrong type.
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
            prepared: list[tuple[object, dict[str, Any]]] = []
            for handler in handlers:
                h = dict(handler)
                sink = h.pop("sink", sys.stderr)
                _validate_sink_args(
                    sink,
                    level=h.get("level", "DEBUG"),
                    format=h.get("format"),
                    rotation=h.get("rotation"),
                    retention=h.get("retention"),
                    compression=h.get("compression"),
                    mode=h.get("mode", "a"),
                    buffering=h.get("buffering", 1),
                    opener=h.get("opener"),
                    encoding=h.get("encoding", "utf-8"),
                    delay=h.get("delay", False),
                    watch=h.get("watch", False),
                    context=h.get("context"),
                )
                prepared.append((sink, h))
            self.remove()
            for sink, h in prepared:
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
            config = self._sink_configs.pop(handler_id, None)
            try:
                self._native.remove(handler_id)
            except Exception:
                pass
            if config is not None:
                sink, kwargs = config
                self.add(sink, **kwargs)  # type: ignore[arg-type]
        else:
            all_configs = dict(self._sink_configs)
            self._native.remove()
            self._sink_configs.clear()
            for _old_id, (sink, kwargs) in all_configs.items():
                self.add(sink, **kwargs)  # type: ignore[arg-type]

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
        # Read in `chunk`-sized blocks so large files don't require
        # line-buffered iteration; lines split across blocks are rejoined
        # via the pending buffer before matching.
        read_size = chunk if isinstance(chunk, int) and chunk > 0 else 65536
        with file_path.open("r", encoding=encoding) as f:
            pending = ""
            while True:
                block = f.read(read_size)
                if not block:
                    break
                pending += block
                *complete, pending = pending.split("\n")
                for line in complete:
                    match = re_pattern.search(line)
                    if match:
                        result: dict[str, object] = {"message": line, **match.groupdict()}
                        if cast:
                            for key, func in cast.items():
                                if key in result:
                                    try:
                                        result[key] = func(str(result[key]))
                                    except (ValueError, KeyError, TypeError):
                                        pass
                        yield result
            if pending:
                match = re_pattern.search(pending)
                if match:
                    result = {"message": pending, **match.groupdict()}
                    if cast:
                        for key, func in cast.items():
                            if key in result:
                                try:
                                    result[key] = func(str(result[key]))
                                except (ValueError, KeyError, TypeError):
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
        self, level: LevelType, message: object, *args: object, **kwargs: object
    ) -> dict[str, object] | None:
        """Log a message at a named or numeric level.

        Supports ``str.format()`` style placeholders::

            logger.info("User {} logged in", username)
            logger.info("User {user} logged in", user=username)

        On Python 3.14+, template strings (``t"..."``) are rendered
        natively, honoring each interpolation's conversion and format
        specification. A template string cannot be combined with additional
        ``*args``/``**kwargs``.

        Returns:
            The record dict if ``opt(record=True)`` was used, otherwise None.
        """
        # Fast path for disabled loggers: return before level resolution,
        # message rendering, frame inspection, or any FFI crossing.
        if self._name in self._disabled:
            return None
        level_name = resolve_level_name(str(level)) if isinstance(level, int) else str(level)

        template_type: Any = _TemplateString
        if (
            template_type is not None
            and isinstance(message, template_type)
            and not self._options.raw
        ):
            if args or kwargs:
                raise ValueError(
                    "template string messages cannot be combined with format arguments"
                )
            rendered = _render_template_string(message)
        else:
            message_str = str(message)
            if self._options.raw:
                rendered = message_str
            else:
                # Only build the `{record}` template variable when the message
                # can actually reference it; the frame walk below is skipped
                # otherwise.
                if self._options.record and "record" in message_str:
                    frame = inspect.currentframe()
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
                        "message": message_str,
                        "level": level_name,
                        "name": self._name,
                        "file": caller_file or "",
                        "line": caller_line or 0,
                        "function": caller_func or "",
                        "module": caller_module or "",
                    }
                    effective_kwargs: dict[str, object] = {**kwargs, "record": record_sub}
                else:
                    effective_kwargs = dict(kwargs) if kwargs else {}

                rendered = render_message(
                    message_str,
                    args if args else None,
                    effective_kwargs if effective_kwargs else None,
                    lazy=self._options.lazy,
                )

        if self._bound:
            extra_map: dict[str, object] = {**self._bound, **_current_context()}
        else:
            extra_map = _current_context()

        exc_text: str | None = None
        exc_tuple: tuple[object, object, str] | None = None
        exc_opt: BaseException | bool | None = self._options.exception
        # opt(exception=True) captures the currently handled exception.
        # When no exception is active, no exception text is attached
        # (instead of emitting a literal "exception=True" placeholder).
        if exc_opt is True:
            active_exc = sys.exc_info()[1]
            exc_opt = active_exc if active_exc is not None else None
        if exc_opt is not None and exc_opt is not False:
            # The traceback is rendered once here and reused: the native
            # formatter would produce the identical text via its own
            # traceback call, and the record tuple needs it too. The tuple
            # itself is only built when something can observe it (patchers
            # or opt(record=True)).
            if isinstance(exc_opt, BaseException):
                tb_text = "".join(
                    traceback.format_exception(type(exc_opt), exc_opt, exc_opt.__traceback__)
                )
                if self._patchers or self._options.record:
                    exc_tuple = (type(exc_opt), exc_opt, tb_text)
                if self._options.backtrace:
                    exc_text = tb_text
                else:
                    exc_text = format_exception_text(exc_opt, False)
                if self._options.diagnose and exc_opt.__traceback__ is not None:
                    diag = _diagnose_suffix(exc_opt)
                    if diag:
                        exc_text = f"{exc_text.rstrip()}\n{diag}" if exc_text else diag
            else:
                exc_text = format_exception_text(exc_opt, self._options.backtrace)
                # Guard against the legacy native placeholder for bare `True`
                # (no active exception). It carries no traceback and must never
                # be appended to the dispatched message.
                if exc_text == "exception=True":
                    exc_text = None

        file_val: str | None = None
        line_val: int | None = None
        func_val: str | None = None
        module_val: str | None = None

        if self._options.capture:
            frame = inspect.currentframe()
            if frame is not None:
                cap_frame: types.FrameType | None = frame.f_back
                while cap_frame is not None and cap_frame.f_code.co_name in _INTERNAL_FRAMES:
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

        # Capture thread/process identity once and reuse for both the
        # returned record dict and the native dispatch below.
        thread_name = threading.current_thread().name
        process_id = os.getpid()
        if self._patchers or self._options.record:
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
            record_dict["thread"] = thread_name
            record_dict["process"] = process_id
            record_dict["exception"] = exc_tuple
            record_dict["elapsed"] = datetime.timedelta(
                seconds=max(0.0, time.time() - self._start_time)
            )

            for patcher in self._patchers:
                try:
                    patcher(record_dict)
                except Exception:
                    pass

            rendered = str(record_dict.get("message", rendered))
            patched_extra = record_dict.get("extra", extra_map)
            if isinstance(patched_extra, dict):
                extra_map = {k: v for k, v in patched_extra.items()}
            patched_file = record_dict.get("file", file_val)
            if isinstance(patched_file, Path):
                patched_file = str(patched_file)
            if isinstance(patched_file, str) and patched_file:
                file_val = patched_file
            patched_line = record_dict.get("line", line_val)
            if isinstance(patched_line, bool):
                pass
            elif isinstance(patched_line, int) and patched_line >= 0:
                line_val = patched_line
            patched_func = record_dict.get("function", func_val)
            if isinstance(patched_func, str) and patched_func:
                func_val = patched_func
            patched_module = record_dict.get("module", module_val)
            if isinstance(patched_module, str) and patched_module:
                module_val = patched_module
            patched_thread = record_dict.get("thread", thread_name)
            if isinstance(patched_thread, str) and patched_thread:
                thread_name = patched_thread
            patched_process = record_dict.get("process", process_id)
            if isinstance(patched_process, bool):
                pass
            elif isinstance(patched_process, int) and patched_process >= 0:
                process_id = patched_process

        # Ensure the traceback is visible even when the sink format does not
        # contain an `{exception}` token (e.g. the default format). The native
        # `exception` field is still populated so `{exception}` templates and
        # JSON serializers keep working. To avoid duplicating the traceback
        # for sinks that already render `{exception}` (or serialize as JSON),
        # only fold it into the message when at least one known sink would
        # otherwise drop it. The future Rust-side auto-append additionally
        # skips text already present in the message (see
        # TemplateFormatter::format).
        if exc_text:
            stripped = exc_text.strip()
            if stripped and stripped != "exception=True" and stripped not in rendered:
                needs_fallback = True
                if self._sink_configs:
                    needs_fallback = False
                    for _sink, cfg in self._sink_configs.values():
                        fmt = cfg.get("format")
                        serialize = bool(cfg.get("serialize"))
                        if serialize:
                            continue
                        if isinstance(fmt, str):
                            if "{exception" not in fmt:
                                needs_fallback = True
                                break
                        else:
                            # Callable format or None (default template without
                            # `{exception}`): conservatively assume it drops
                            # the traceback so it stays visible.
                            needs_fallback = True
                            break
                if needs_fallback:
                    # Strip trailing newlines: sinks add exactly one newline,
                    # so keeping the native trailing `\n` would blank-line
                    # console/file outputs (writeln) while remaining harmless
                    # for callback sinks (which dedupe trailing newlines).
                    exc_clean = exc_text.rstrip("\n")
                    rendered = f"{rendered}\n{exc_clean}" if rendered else exc_clean

        # Convert extra values to strings for Rust-side storage
        extra_str_map: dict[str, str] = {k: str(v) for k, v in extra_map.items()}

        # The numeric level is consumed only by stdlib-handler sinks via
        # thread-local state; skip the registry lookup when no such sink
        # is installed.
        if any(
            getattr(sink, "_logly_captures_level", False) for sink, _ in self._sink_configs.values()
        ):
            _logly_level_tls.level = inspect_level(level_name)[1]

        self._native.log_structured(
            level=level_name,
            message=rendered,
            name=self._name,
            file=file_val,
            line=line_val,
            function=func_val,
            module=module_val,
            thread_name=thread_name,
            process_id=process_id,
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

        Automatically captures the current exception if one is active,
        including its full traceback (equivalent to
        ``logger.opt(exception=True).error(...)``).

        Args:
            message: Log message (supports ``str.format()`` placeholders).
            *args: Positional arguments for format string substitution.
            exc_info: Whether to include exception info (default ``True``).
                When ``False``, logs a plain ERROR message without traceback.
            **kwargs: Keyword arguments for format string substitution.
        """
        if self._name in self._disabled:
            return
        if not exc_info:
            self.log("ERROR", message, *args, **kwargs)
            return
        exc = sys.exc_info()[1]
        if exc is not None:
            view = self._clone()
            view._options = _Options(
                exception=exc,
                lazy=self._options.lazy,
                raw=self._options.raw,
                record=self._options.record,
                depth=self._options.depth,
                colors=self._options.colors,
                ansi=self._options.ansi,
                capture=self._options.capture,
                backtrace=self._options.backtrace,
                diagnose=self._options.diagnose,
            )
            view.log("ERROR", message, *args, **kwargs)
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
            sink_configs=dict(self._sink_configs),
        )
        clone._start_time = self._start_time
        clone._disabled = set(self._disabled)
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
        clone._disabled = set(self._disabled)
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
        message: str | None = None,
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
            message: Custom message logged with the caught exception.
        """
        self._logger = logger
        self._reraise = reraise
        self._level = level
        self._onerror = onerror
        self._exception_type = exception_type
        self._exclude = exclude
        self._default = default
        self._message = message if message is not None else "An error has been caught"

    def _matches(self, exc: BaseException) -> bool:
        """Return whether ``exc`` should be caught and logged."""
        if self._exclude is not None and isinstance(exc, self._exclude):
            return False
        return isinstance(exc, self._exception_type)

    def _log_and_handle(self, exc: BaseException) -> None:
        """Log ``exc`` first, then invoke ``onerror``.

        Logging precedes the callback so the original exception and its
        traceback are preserved even when ``onerror`` is NoReturn (e.g.
        ``sys.exit``) or itself raises.
        """
        try:
            self._logger.opt(exception=exc).log(self._level, self._message)
        finally:
            if self._onerror is not None:
                self._onerror(exc)

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
        if exc is not None and self._matches(exc):
            self._log_and_handle(exc)
            return not self._reraise
        return False

    async def __aenter__(self) -> _CatchContext:
        """Enter the exception catching context asynchronously.

        Returns:
            This instance (for use in ``async with`` statements).
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Exit the async catching context, logging any caught exception.

        Args:
            exc_type: Exception type if an exception occurred.
            exc: Exception instance if an exception occurred.
            tb: Traceback object if an exception occurred.

        Returns:
            ``True`` if the exception was caught and handled.
        """
        _ = tb
        if exc is not None and self._matches(exc):
            self._log_and_handle(exc)
            return not self._reraise
        return False

    @overload
    def __call__(
        self, func: Callable[..., Coroutine[Any, Any, _CatchT]]
    ) -> Callable[..., Coroutine[Any, Any, _CatchT | None]]: ...
    @overload
    def __call__(
        self, func: Callable[..., AsyncGenerator[_CatchT, None]]
    ) -> Callable[..., AsyncGenerator[_CatchT, None]]: ...
    @overload
    def __call__(
        self, func: Callable[..., Generator[_CatchT, None, None]]
    ) -> Callable[..., Generator[_CatchT, None, None]]: ...
    @overload
    def __call__(self, func: Callable[..., _CatchT]) -> Callable[..., _CatchT | None]: ...
    def __call__(self, func: Callable[..., object]) -> Callable[..., object]:
        """Wrap a function as a decorator that catches and logs exceptions.

        Supports synchronous functions, asynchronous functions, generators,
        and asynchronous generators. For generators, exceptions raised while
        iterating are caught; a caught exception ends iteration (the
        ``default`` value only applies to plain and async functions, since a
        default cannot be yielded without altering the data stream).

        Args:
            func: The function to wrap.

        Returns:
            A wrapped function that catches exceptions matching the
            configured criteria.
        """
        import functools

        if inspect.isasyncgenfunction(func):

            @functools.wraps(func)
            async def _catch_async_gen_wrapper(*args: object, **inner_kwargs: object) -> Any:
                try:
                    async for item in func(*args, **inner_kwargs):
                        yield item
                except BaseException as exc:
                    if self._matches(exc):
                        self._log_and_handle(exc)
                        if self._reraise:
                            raise
                        return
                    raise

            return _catch_async_gen_wrapper  # type: ignore[return-value]

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def _catch_async_wrapper(*args: object, **inner_kwargs: object) -> object:
                try:
                    return await func(*args, **inner_kwargs)
                except BaseException as exc:
                    if self._matches(exc):
                        self._log_and_handle(exc)
                        if self._reraise:
                            raise
                        return self._default
                    raise

            return _catch_async_wrapper

        if inspect.isgeneratorfunction(func):

            @functools.wraps(func)
            def _catch_gen_wrapper(*args: object, **inner_kwargs: object) -> Any:
                try:
                    yield from func(*args, **inner_kwargs)
                except BaseException as exc:
                    if self._matches(exc):
                        self._log_and_handle(exc)
                        if self._reraise:
                            raise
                        return
                    raise

            return _catch_gen_wrapper

        @functools.wraps(func)
        def _catch_wrapper(*args: object, **inner_kwargs: object) -> object:
            with self:
                return func(*args, **inner_kwargs)
            return self._default  # type: ignore[unreachable]

        return _catch_wrapper


def _env_flag(name: str) -> bool | None:
    """Parse a boolean environment variable.

    Returns ``True``/``False`` for recognized values and ``None`` when the
    variable is unset or unrecognized.
    """
    raw = os.environ.get(name)
    if raw is None:
        return None
    normalized = raw.strip().lower()
    if normalized in ("1", "true", "yes", "on"):
        return True
    if normalized in ("0", "false", "no", "off"):
        return False
    return None


logger = Logger()

# Environment configuration for the pre-configured stderr sink (see the
# environment-variables guide). Everything is defensive: an unrecognized
# value falls back to the default so a typo can never break interpreter
# startup by failing the import.
_autoinit = os.environ.get("LOGLY_AUTOINIT", "true").lower()
if _autoinit not in ("false", "0", "no"):
    try:
        logger.add(
            sys.stderr,
            level=os.environ.get("LOGLY_LEVEL", "DEBUG"),
            format=os.environ.get("LOGLY_FORMAT"),
            colorize=_env_flag("LOGLY_COLORIZE"),
            serialize=_env_flag("LOGLY_SERIALIZE") or False,
        )
    except ValueError:
        logger.add(sys.stderr, level="DEBUG")
