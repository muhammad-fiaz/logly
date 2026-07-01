"""Tests for Flask integration."""

from __future__ import annotations

import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.flask import (
    LoglyHandler,
    _resolve_level,
    init_app,
)


class TestFlaskResolveLevel:
    def test_debug(self) -> None:
        record = logging.LogRecord("test", logging.DEBUG, "", 0, "msg", (), None)
        assert _resolve_level(record) == "DEBUG"

    def test_info(self) -> None:
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        assert _resolve_level(record) == "INFO"

    def test_warning(self) -> None:
        record = logging.LogRecord("test", logging.WARNING, "", 0, "msg", (), None)
        assert _resolve_level(record) == "WARNING"

    def test_error(self) -> None:
        record = logging.LogRecord("test", logging.ERROR, "", 0, "msg", (), None)
        assert _resolve_level(record) == "ERROR"

    def test_critical(self) -> None:
        record = logging.LogRecord("test", logging.CRITICAL, "", 0, "msg", (), None)
        assert _resolve_level(record) == "CRITICAL"


class TestFlaskLoglyHandler:
    def test_emit_routes_to_logly(self) -> None:
        handler = LoglyHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.flask.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.return_value.log.assert_called_once()

    def test_emit_with_exception(self) -> None:
        handler = LoglyHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        with patch("logly.integrations.flask.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            assert mock_logger.opt.call_args[1]["exception"] is not None

    def test_emit_none_record(self) -> None:
        handler = LoglyHandler()
        handler.emit(None)

    def test_handle_error(self) -> None:
        handler = LoglyHandler()
        with patch("builtins.print") as mock_print:
            handler.handleError(None)
            mock_print.assert_called_once()

    def test_handle_error_print_exception(self) -> None:
        handler = LoglyHandler()
        with patch("builtins.print", side_effect=Exception("fail")):
            handler.handleError(None)


class TestFlaskInitApp:
    def test_init_app_requires_flask(self) -> None:
        with patch("logly.integrations.flask._has_flask", False):
            with pytest.raises(ImportError, match="Flask"):
                init_app(MagicMock())

    def test_init_app_registers_hooks(self) -> None:
        mock_app = MagicMock()
        mock_app.before_request = MagicMock(side_effect=lambda f: f)
        mock_app.after_request = MagicMock(side_effect=lambda f: f)
        mock_app.teardown_request = MagicMock(side_effect=lambda f: f)
        with patch("logly.integrations.flask._has_flask", True):
            with patch("logly.integrations.flask.logger") as mock_logger:
                mock_logger.add = MagicMock()
                init_app(mock_app, level="DEBUG")
                mock_app.before_request.assert_called()
                mock_app.after_request.assert_called()
                mock_app.teardown_request.assert_called()
