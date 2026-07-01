"""Tests for Gunicorn integration."""

from __future__ import annotations

import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.gunicorn import (
    LoglyWorker,
    _GunicornHandler,
    _resolve_level,
    setup_gunicorn_logging,
)


class TestResolveLevel:
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


class TestGunicornHandler:
    def test_emit_routes_to_logly(self) -> None:
        handler = _GunicornHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.gunicorn.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.return_value.log.assert_called_once()

    def test_emit_with_exception(self) -> None:
        handler = _GunicornHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        with patch("logly.integrations.gunicorn.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            assert mock_logger.opt.call_args[1]["exception"] is not None

    def test_emit_none_record(self) -> None:
        handler = _GunicornHandler()
        handler.emit(None)

    def test_handle_error(self) -> None:
        handler = _GunicornHandler()
        with patch("builtins.print") as mock_print:
            handler.handleError(None)
            mock_print.assert_called_once()

    def test_handle_error_print_exception(self) -> None:
        handler = _GunicornHandler()
        with patch("builtins.print", side_effect=Exception("fail")):
            handler.handleError(None)


class TestSetupGunicornLogging:
    def test_setup_configures_loggers(self) -> None:
        with patch("logly.integrations.gunicorn.logger") as mock_logger:
            mock_logger.add = MagicMock()
            setup_gunicorn_logging(level="INFO")
            assert mock_logger.add.called


class TestLoglyWorker:
    def test_init_import_guard(self) -> None:
        saved = sys.modules.get("gunicorn.workers.sync")
        sys.modules["gunicorn.workers.sync"] = None  # type: ignore[assignment]
        try:
            with pytest.raises(ImportError, match="gunicorn"):
                LoglyWorker()
        finally:
            if saved is not None:
                sys.modules["gunicorn.workers.sync"] = saved
            else:
                sys.modules.pop("gunicorn.workers.sync", None)
