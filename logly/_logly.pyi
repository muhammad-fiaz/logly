"""Logly type stubs.

Provides type annotations for the ``logly`` package.
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

class _Logger:
    """Native Rust logger engine (internal).

    This class wraps the PyO3-based Rust implementation and provides
    low-level logging operations. It is not intended for direct use;
    use :class:`~logly.Logger` instead.
    """

    def __init__(self) -> None: ...
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
    ) -> int: ...
    def remove(self, sink_id: int | None = None) -> None: ...
    def complete(self) -> None: ...
    def enable(self, name: str) -> None: ...
    def disable(self, name: str) -> None: ...
    def log(self, level: str, message: str) -> None: ...
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
    ) -> None: ...
    def trace(self, message: str) -> None: ...
    def debug(self, message: str) -> None: ...
    def info(self, message: str) -> None: ...
    def notice(self, message: str) -> None: ...
    def success(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
    def fail(self, message: str) -> None: ...
    def critical(self, message: str) -> None: ...
    def fatal(self, message: str) -> None: ...

class Logger:
    """Main logger class providing the full logging API.

    Usage::

        from logly import logger

        logger.info("Hello from Logly")
        logger.opt(exception=True).error("Something went wrong")
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
    ) -> int: ...
    def remove(self, handler_id: int | None = None) -> None: ...
    def complete(self) -> None: ...
    def reinstall(self, handler_id: int | None = None) -> None: ...
    def catch(
        self,
        exception: type[BaseException] | tuple[type[BaseException], ...] | None = ...,
        *,
        level: str = ...,
        reraise: bool = ...,
        onerror: Callable[[BaseException], None] | None = ...,
        exclude: type[BaseException] | tuple[type[BaseException], ...] | None = ...,
        default: object = ...,
    ) -> _CatchContext: ...
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
    ) -> Self: ...
    def bind(self, **kwargs: object) -> Self: ...
    def contextualize(self, **kwargs: object) -> Generator[None]: ...
    def patch(self, patcher: Callable[[dict[str, object]], None]) -> Self: ...
    def level(
        self,
        name: str,
        no: int | None = None,
        color: str | None = None,
        icon: str | None = None,
    ) -> tuple[str, int, str | None]: ...
    def enable(self, name: str) -> None: ...
    def disable(self, name: str) -> None: ...
    def configure(
        self,
        *,
        handlers: list[dict[str, object]] | None = None,
        levels: list[dict[str, object]] | None = None,
        extra: dict[str, object] | None = None,
        patcher: Callable[[dict[str, object]], None] | None = None,
        activation: list[tuple[str, bool]] | None = None,
    ) -> None: ...
    def log(
        self, level: str | int, message: object, *args: object, **kwargs: object
    ) -> dict[str, object] | None: ...
    def trace(self, message: object, *args: object, **kwargs: object) -> None: ...
    def debug(self, message: object, *args: object, **kwargs: object) -> None: ...
    def info(self, message: object, *args: object, **kwargs: object) -> None: ...
    def notice(self, message: object, *args: object, **kwargs: object) -> None: ...
    def success(self, message: object, *args: object, **kwargs: object) -> None: ...
    def warning(self, message: object, *args: object, **kwargs: object) -> None: ...
    def warn(self, message: object, *args: object, **kwargs: object) -> None: ...
    def error(self, message: object, *args: object, **kwargs: object) -> None: ...
    def exception(
        self, message: object, *args: object, exc_info: bool = True, **kwargs: object
    ) -> None: ...
    def fail(self, message: object, *args: object, **kwargs: object) -> None: ...
    def critical(self, message: object, *args: object, **kwargs: object) -> None: ...
    def fatal(self, message: object, *args: object, **kwargs: object) -> None: ...
    def audit(self, message: object, *args: object, **kwargs: object) -> None: ...
    def root_dir(self, path: str | Path) -> None: ...
    def parse(
        self,
        path: str | Path,
        pattern: str | re.Pattern[str] | None = None,
        *,
        cast: dict[str, Callable[[str], object]] | None = None,
        chunk: int = 65536,
        encoding: str = "utf-8",
    ) -> Generator[dict[str, object]]: ...
    def __copy__(self) -> Self: ...
    def __deepcopy__(self, memo: dict[int, object]) -> Self: ...
    @property
    def levels(self) -> list[str]: ...

class _CatchContext:
    """Context manager and decorator for exception catching."""

    def __enter__(self) -> _CatchContext: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool: ...
    def __call__(self, func: Callable[..., object]) -> Callable[..., object]: ...

class HttpJsonSink:
    """HTTP JSON sink for sending logs to HTTP endpoints.

    Usage::

        from logly import logger
        from logly.network import HttpJsonSink

        logger.add(HttpJsonSink(url="http://localhost:3100/loki/api/v1/push"))
    """

    def __init__(
        self,
        url: str,
        *,
        method: str = "POST",
        headers: list[tuple[str, str]] | None = None,
        timeout: int = 30,
    ) -> None: ...
    def write(self, line: str) -> None: ...
    def flush(self) -> None: ...

class TcpSink:
    """TCP sink for sending logs over TCP.

    Usage::

        from logly import logger
        from logly.network import TcpSink

        logger.add(TcpSink(host="127.0.0.1", port=514))
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 514, delimiter: str = "\n") -> None: ...
    def connect(self) -> None: ...
    def write(self, line: str) -> None: ...
    def flush(self) -> None: ...

class UdpSink:
    """UDP sink for sending logs over UDP.

    Usage::

        from logly import logger
        from logly.network import UdpSink

        logger.add(UdpSink(host="127.0.0.1", port=514))
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 514) -> None: ...
    def write(self, line: str) -> None: ...

class SyslogSink:
    """Syslog sink for sending logs to syslog servers.

    Usage::

        from logly import logger
        from logly.network import SyslogSink

        logger.add(SyslogSink(host="127.0.0.1", port=514))
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
    def write(self, line: str) -> None: ...
    def flush(self) -> None: ...

def register_custom_level(name: str, priority: int, color: str | None = None) -> str:
    """Register a custom log level.

    Args:
        name: Level name (e.g. ``"VERBOSE"``).
        priority: Numeric priority (lower = more verbose).
        color: Optional ANSI color code.

    Returns:
        The registered level name.
    """
    ...

def inspect_level(name: str) -> tuple[str, int, str | None]:
    """Inspect a log level's configuration.

    Args:
        name: Level name to inspect.

    Returns:
        Tuple of ``(name, numeric_priority, color_or_none)``.
    """
    ...

def list_levels() -> list[str]:
    """List all registered level names in severity order.

    Returns:
        List of level name strings.
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
    """
    ...

def parse_retention_str(value: str) -> str:
    """Parse a retention string into a normalized value.

    Args:
        value: Retention string (e.g. ``"30 days"``).

    Returns:
        Normalized retention value.
    """
    ...

def parse_compression_str(value: str) -> str:
    """Parse a compression string into a normalized codec name.

    Args:
        value: Compression string (e.g. ``"gzip"``).

    Returns:
        Normalized codec name.
    """
    ...

def resolve_level_name(value: str) -> str:
    """Resolve a level name or number to its canonical name.

    Args:
        value: Level name or numeric string.

    Returns:
        Canonical level name.
    """
    ...

def format_exception_text(exc: Any, backtrace: bool = False) -> str | None:
    """Format an exception as a text string.

    Args:
        exc: Exception instance or bool.
        backtrace: Whether to include full backtrace.

    Returns:
        Formatted exception text, or ``None``.
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
        message: Format string.
        args: Positional format arguments.
        kwargs: Keyword format arguments.
        lazy: Whether to defer formatting.

    Returns:
        Rendered message string.
    """
    ...

logger: Logger
"""Default module-level logger instance."""
