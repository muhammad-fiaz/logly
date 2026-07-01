"""Tests for Starlette integration."""

from __future__ import annotations

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from logly.integrations.starlette import LoglyMiddleware


class TestLoglyMiddlewareInit:
    def test_init_import_guard(self) -> None:
        saved = sys.modules.get("starlette.middleware.base")
        sys.modules["starlette.middleware.base"] = None  # type: ignore[assignment]
        try:
            with pytest.raises(ImportError, match="starlette"):
                LoglyMiddleware(app=MagicMock())
        finally:
            if saved is not None:
                sys.modules["starlette.middleware.base"] = saved
            else:
                sys.modules.pop("starlette.middleware.base", None)

    def test_init_default(self) -> None:
        mock_base = MagicMock()
        with patch.dict(sys.modules, {"starlette.middleware.base": mock_base}):
            app = MagicMock()
            middleware = LoglyMiddleware(app, level="INFO")
            assert middleware is not None


class TestLoglyMiddlewareCall:
    def test_call_non_http_passthrough(self) -> None:
        mock_base = MagicMock()
        inner = AsyncMock()
        mock_base.BaseHTTPMiddleware.return_value = inner
        with patch.dict(sys.modules, {"starlette.middleware.base": mock_base}):
            app = AsyncMock()
            middleware = LoglyMiddleware(app, level="INFO")
            scope = {"type": "lifespan"}
            receive = AsyncMock()
            send = AsyncMock()
            asyncio.run(middleware(scope, receive, send))
            inner.assert_called_once_with(scope, receive, send)

    def test_call_http_logs_request(self) -> None:
        mock_base = MagicMock()
        inner = AsyncMock()
        mock_base.BaseHTTPMiddleware.return_value = inner
        with patch.dict(sys.modules, {"starlette.middleware.base": mock_base}):
            app = AsyncMock()
            middleware = LoglyMiddleware(app, level="INFO")
            scope = {"type": "http", "method": "GET", "path": "/test"}
            receive = AsyncMock()
            send = AsyncMock()
            asyncio.run(middleware(scope, receive, send))
            inner.assert_called_once_with(scope, receive, send)
