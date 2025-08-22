from logly._logly import PyLogger, __version__, logger as _rust_logger


class _LoggerProxy:
    """Thin Python proxy to keep surface close to Loguru while delegating to Rust.

    For MVP we forward methods; advanced features will be added incrementally.
    """

    def __init__(self, inner: PyLogger) -> None:
        self._inner = inner
        # bound context values attached to this proxy
        self._bound: dict[str, object] = {}
        # enabled/disabled switch
        self._enabled: bool = True
        # local options stored by opt()
        self._options: dict[str, object] = {}
        # custom level name mappings
        self._levels: dict[str, str] = {}

    # configuration and sinks
    def add(self, sink: str | None = None, *, rotation: str | None = None) -> int:
        if not sink or sink == "console":
            return self._inner.add("console")
        return self._inner.add(sink, rotation=rotation)

    def configure(self, level: str = "INFO", color: bool = True, json: bool = False) -> None:
        self._inner.configure(level=level, color=color, json=json)

    def remove(self, handler_id: int) -> bool:
        return self._inner.remove(handler_id)

    # enable / disable
    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    # logging methods with kwargs as context key-values
    def trace(self, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.trace(msg, **merged)

    def debug(self, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.debug(msg, **merged)

    def info(self, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.info(msg, **merged)

    def success(self, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.success(msg, **merged)

    def warning(self, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.warning(msg, **merged)

    def error(self, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.error(msg, **merged)

    def critical(self, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.critical(msg, **merged)

    def log(self, level: str, message: str, /, *args, **kwargs):
        if not self._enabled:
            return
        # allow aliasing custom levels
        lvl = self._levels.get(level, level)
        merged = {**self._bound, **kwargs}
        msg = message % args if args else message
        self._inner.log(lvl, msg, **merged)

    def complete(self) -> None:
        self._inner.complete()

    # context binding similar to loguru: returns a new proxy with additional bound context
    def bind(self, **kwargs) -> "_LoggerProxy":
        new = _LoggerProxy(self._inner)
        new._bound = {**self._bound, **kwargs}
        new._enabled = self._enabled
        new._options = dict(self._options)
        new._levels = dict(self._levels)
        return new

    # context manager to temporarily attach values
    from contextlib import contextmanager

    @contextmanager
    def contextualize(self, **kwargs):
        old = dict(self._bound)
        try:
            self._bound.update(kwargs)
            yield
        finally:
            self._bound = old

    # exception logging convenience
    def exception(self, message: str = "", /, **kwargs) -> None:
        import traceback

        tb = traceback.format_exc()
        full = (message + "\n" + tb).strip() if message else tb
        merged = {**self._bound, **kwargs}
        self._inner.error(full, **merged)

    # catch decorator/context manager: logs exceptions; if reraise=True, re-raises
    def catch(self, *, reraise: bool = False):
        from contextlib import ContextDecorator

        proxy = self

        class _Catch(ContextDecorator):
            def __enter__(self_inner):
                return None

            def __exit__(self_inner, exc_type, exc, tb):
                if exc is None:
                    return False
                import traceback

                msg = traceback.format_exception(exc_type, exc, tb)
                proxy._inner.error("".join(msg), **proxy._bound)
                return False if reraise else True

        return _Catch()

    # options / opt stub (store options locally)
    def opt(self, **options) -> "_LoggerProxy":
        new = _LoggerProxy(self._inner)
        new._bound = dict(self._bound)
        new._options = {**self._options, **options}
        new._enabled = self._enabled
        new._levels = dict(self._levels)
        return new

    # register alias or custom level mapping to an existing level name
    def level(self, name: str, mapped_to: str) -> None:
        self._levels[name] = mapped_to


logger = _LoggerProxy(_rust_logger)

__all__ = ["__version__", "logger"]
