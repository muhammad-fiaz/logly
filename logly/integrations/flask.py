"""Flask integration for Logly.

Provides ``LoglyHandler`` and ``LoglyMiddleware`` for Flask applications.

Requires ``flask``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[flask]

    # Option 2: pip
    pip install "logly[flask]"

    # Option 3: uv without extras
    uv add flask

    # Option 4: pip without extras
    pip install flask
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from typing import Any

from logly import logger

try:
    from flask import Flask, g, request

    _has_flask: bool = True
except ImportError:
    Flask = None  # type: ignore[assignment,misc]  # noqa: F811
    g = None  # type: ignore[assignment]  # noqa: F811
    request = None  # type: ignore[assignment]  # noqa: F811
    _has_flask = False

_IMPORT_MSG = (
    "flask is required for Logly Flask integration.\n"
    "Install with one of:\n"
    "  uv add logly[flask]       # recommended\n"
    "  pip install logly[flask]\n"
    "  uv add flask\n"
    "  pip install flask"
)


def _resolve_level(record: logging.LogRecord) -> str:
    """Resolve a Python logging record to a Logly level name.

    Maps Python's 5 standard levels to their Logly equivalents.

    Args:
        record: The Python logging record.

    Returns:
        Logly level name string.
    """
    stdlib_map: dict[int, str] = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }
    return stdlib_map.get(record.levelno, record.levelname.upper())


class LoglyHandler(logging.Handler):
    """Route Flask/stdlib logging records through Logly.

    Usage::

        from flask import Flask
        from logly.integrations.flask import LoglyHandler

        app = Flask(__name__)
        app.logger.handlers = [LoglyHandler()]
    """

    def emit(self, record: logging.LogRecord | None) -> None:
        """Emit a log record through Logly.

        Args:
            record: The log record to emit. If ``None``, this is a no-op.
        """
        if record is None:
            return
        try:
            level = _resolve_level(record)
        except Exception:
            level = record.levelname.upper()

        exc: BaseException | None = None
        if record.exc_info and record.exc_info[1] is not None:
            exc = record.exc_info[1]

        logger.opt(exception=exc).log(level, record.getMessage())

    def handleError(self, record: logging.LogRecord | None) -> None:  # noqa: N802
        """Prevent logging errors from causing recursive failures.

        Args:
            record: The log record that caused the error (unused).
        """
        if sys.stderr is not None:
            try:
                print("Logly LoglyHandler error:", file=sys.stderr)  # noqa: T201
            except Exception:
                pass


def init_app(app: Any, **kwargs: Any) -> None:
    """Initialize Logly on a Flask app.

    Adds request context, error handling, and configures stdlib logging.

    Usage::

        from flask import Flask
        from logly.integrations.flask import init_app

        app = Flask(__name__)
        init_app(app)

    Args:
        app: Flask application instance.
        **kwargs: Additional arguments passed to ``logger.add()``.
    """
    if not _has_flask:
        raise ImportError(_IMPORT_MSG)

    from flask import g as _g
    from flask import request as _request

    @app.before_request
    def _logly_before_request() -> None:
        _g.logly_request_id = str(uuid.uuid4())
        _g.logly_start = time.perf_counter()
        logger.contextualize(
            request_id=_g.logly_request_id,
            method=_request.method,
            path=_request.path,
        )

    @app.after_request
    def _logly_after_request(response: Any) -> Any:
        elapsed_ms = (time.perf_counter() - _g.logly_start) * 1000
        logger.info(
            "{} {} {} {:.1f}ms",
            _request.method,
            _request.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    @app.teardown_request
    def _logly_teardown_request(exc: BaseException | None) -> None:
        if exc is not None:
            logger.exception("request failed: {}", exc)

    # Route Flask logs through Logly
    app.logger.handlers = [LoglyHandler()]
    app.logger.propagate = False
    for name in ("werkzeug", "flask.app"):
        log = logging.getLogger(name)
        log.handlers = [LoglyHandler()]
        log.propagate = False

    logger.add("stderr", level=kwargs.pop("level", "INFO"), **kwargs)
