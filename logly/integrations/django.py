"""Django integration - handler and middleware.

Provides ``LoglyHandler`` (a ``logging.Handler``) and ``LoglyMiddleware``
for Django applications.

Requires ``django``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[django]

    # Option 2: pip
    pip install "logly[django]"

    # Option 3: uv without extras
    uv add django

    # Option 4: pip without extras
    pip install django
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from typing import Any

from logly import logger

try:
    from django.http import HttpRequest, HttpResponse  # pragma: no cover

    _has_django: bool = True
except ImportError:
    HttpRequest = None
    HttpResponse = None
    _has_django = False

_IMPORT_MSG = (  # pragma: no cover
    "django is required for LoglyMiddleware.\n"
    "Install with one of:\n"
    "  uv add logly[django]       # recommended\n"
    "  pip install logly[django]\n"
    "  uv add django\n"
    "  pip install django"
)  # pragma: no cover


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
    """Route Django ``logging`` records through Logly.

    Usage in ``settings.py``::

        LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "logly": {
                    "class": "logly.integrations.django.LoglyHandler",
                    "level": "INFO",
                },
            },
            "root": {
                "handlers": ["logly"],
                "level": "INFO",
            },
        }

    No extra dependencies required beyond Django itself.
    """

    def emit(self, record: logging.LogRecord | None) -> None:
        """Emit a log record.

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

        logger.opt(
            exception=exc,
        ).log(
            level,
            record.getMessage(),
        )

    def handleError(self, record: logging.LogRecord | None) -> None:  # noqa: N802
        """Prevent logging errors from causing recursive failures."""
        if sys.stderr is not None:
            try:
                print("Logly LoglyHandler error:", file=sys.stderr)  # noqa: T201
            except Exception:
                pass


class LoglyMiddleware:
    """Django middleware that contextualizes each request with metadata.

    Adds ``request_id``, ``method``, ``path``, and ``client_ip`` to the
    Logly context for the duration of each request.

    Usage in ``settings.py``::

        MIDDLEWARE = [
            "logly.integrations.django.LoglyMiddleware",
            # ... other middleware
        ]
    """

    def __init__(self, get_response: Any = None) -> None:
        if not _has_django:  # pragma: no cover
            raise ImportError(_IMPORT_MSG)  # pragma: no cover
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        request_id = str(uuid.uuid4())
        client_ip = self._get_client_ip(request)

        with logger.contextualize(
            request_id=request_id,
            method=getattr(request, "method", "UNKNOWN"),
            path=getattr(request, "path", "/"),
            client_ip=client_ip,
        ):
            start = time.perf_counter()
            try:
                response = self.get_response(request)
                elapsed_ms = (time.perf_counter() - start) * 1000
                status = getattr(response, "status_code", 0)
                logger.info(
                    "{} {} {} {:.1f}ms",
                    getattr(request, "method", "?"),
                    getattr(request, "path", "/"),
                    status,
                    elapsed_ms,
                )
                return response
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.exception(
                    "{} {} FAILED {:.1f}ms",
                    getattr(request, "method", "?"),
                    getattr(request, "path", "/"),
                    elapsed_ms,
                )
                raise

    def process_exception(self, request: Any, exception: Any) -> None:
        """Log unhandled exceptions raised during request processing.

        Args:
            request: The Django HTTP request.
            exception: The exception that was raised.
        """
        logger.exception("Unhandled exception: {}", exception)

    @staticmethod
    def _get_client_ip(request: Any) -> str:
        """Extract client IP from request headers.

        Args:
            request: The Django HTTP request.

        Returns:
            Client IP address string.
        """
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return str(x_forwarded).split(",")[0].strip()
        return str(request.META.get("REMOTE_ADDR", "unknown"))
