"""FastAPI middleware integration.

Provides ``LoglyMiddleware`` for ASGI applications (FastAPI, Starlette).

Requires ``starlette`` (installed automatically with ``fastapi``).

Install with::

    # Option 1: uv (recommended)
    uv add logly[fastapi]

    # Option 2: pip
    pip install "logly[fastapi]"

    # Option 3: uv without extras
    uv add fastapi starlette

    # Option 4: pip without extras
    pip install fastapi starlette
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any

from logly import logger

_IMPORT_MSG = (
    "starlette is required for LoglyMiddleware.\n"
    "Install with one of:\n"
    "  uv add logly[fastapi]       # recommended\n"
    "  pip install logly[fastapi]\n"
    "  uv add fastapi starlette\n"
    "  pip install fastapi starlette"
)


def _check_starlette() -> None:
    """Verify starlette is available.

    Raises:
        ImportError: If ``starlette`` is not installed.
    """
    try:
        from starlette.middleware.base import BaseHTTPMiddleware  # noqa: F401
    except ImportError:
        raise ImportError(_IMPORT_MSG) from None


class LoglyMiddleware:
    """ASGI middleware that contextualizes each request with metadata.

    Adds ``request_id``, ``method``, ``path``, ``client``, and ``user_agent``
    to the Logly context for the duration of each request.

    Usage::

        from fastapi import FastAPI
        from logly.integrations.fastapi import LoglyMiddleware

        app = FastAPI()
        app.add_middleware(LoglyMiddleware)
    """

    def __init__(self, app: Callable[..., Any], **kwargs: Any) -> None:
        """Initialize the ASGI middleware.

        Args:
            app: The ASGI application to wrap.
            **kwargs: Additional arguments passed to Starlette's
                ``BaseHTTPMiddleware``.
        """
        _check_starlette()
        from starlette.middleware.base import BaseHTTPMiddleware

        self._middleware = BaseHTTPMiddleware(app, **kwargs)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] not in {"http", "websocket"}:
            return await self._middleware(scope, receive, send)

        request_id = str(uuid.uuid4())
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")

        with logger.contextualize(
            request_id=request_id,
            method=method,
            path=path,
        ):
            start = time.perf_counter()
            try:
                await self._middleware(scope, receive, send)
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    "{} {} {:.1f}ms",
                    method,
                    path,
                    elapsed_ms,
                )
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.exception(
                    "{} {} failed {:.1f}ms",
                    method,
                    path,
                    elapsed_ms,
                )
                raise
