"""Tests for SQLAlchemy integration."""

from __future__ import annotations

import logging
import sys
from unittest.mock import MagicMock, patch

from logly.integrations.sqlalchemy import (
    _resolve_level,
    _SQLAlchemyHandler,
    setup_sqlalchemy_logging,
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

    def test_custom_level_falls_back_to_levelname(self) -> None:
        record = logging.LogRecord("test", 25, "", 0, "msg", (), None)
        record.levelname = "CUSTOM"
        assert _resolve_level(record) == "CUSTOM"


class TestSQLAlchemyHandlerInit:
    def test_instantiation(self) -> None:
        handler = _SQLAlchemyHandler()
        assert handler is not None

    def test_is_logging_handler(self) -> None:
        assert issubclass(_SQLAlchemyHandler, logging.Handler)


class TestSQLAlchemyHandlerEmit:
    def test_emit_none_record_is_noop(self) -> None:
        handler = _SQLAlchemyHandler()
        handler.emit(None)

    def test_emit_routes_to_logly(self) -> None:
        handler = _SQLAlchemyHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.sqlalchemy.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)
            mock_logger.opt.return_value.log.assert_called_once_with("INFO", "hello")

    def test_emit_with_exception(self) -> None:
        handler = _SQLAlchemyHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        with patch("logly.integrations.sqlalchemy.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            assert mock_logger.opt.call_args[1]["exception"] is not None

    def test_emit_exception_info_none(self) -> None:
        handler = _SQLAlchemyHandler()
        record = logging.LogRecord("test", logging.WARNING, "", 0, "warn", (), (None, None, None))
        with patch("logly.integrations.sqlalchemy.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)

    def test_emit_level_fallback_on_resolve_error(self) -> None:
        handler = _SQLAlchemyHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with patch(
            "logly.integrations.sqlalchemy._resolve_level",
            side_effect=Exception("bad"),
        ):
            with patch("logly.integrations.sqlalchemy.logger") as mock_logger:
                mock_logger.opt.return_value.log = MagicMock()
                handler.emit(record)
                mock_logger.opt.return_value.log.assert_called_once_with("INFO", "msg")


class TestHandleError:
    def test_handle_error_prints_to_stderr(self) -> None:
        handler = _SQLAlchemyHandler()
        with patch("builtins.print") as mock_print:
            handler.handleError(None)
            mock_print.assert_called_once_with("Logly SQLAlchemy handler error:", file=sys.stderr)

    def test_handle_error_stderr_none(self) -> None:
        handler = _SQLAlchemyHandler()
        with patch("sys.stderr", None):
            handler.handleError(None)

    def test_handle_error_print_exception(self) -> None:
        handler = _SQLAlchemyHandler()
        with patch("builtins.print", side_effect=Exception("fail")):
            handler.handleError(None)


class TestSetupSqlalchemyLogging:
    def test_configures_all_loggers(self) -> None:
        with patch("logly.integrations.sqlalchemy.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.WARNING = logging.WARNING
            setup_sqlalchemy_logging()
            calls = [c[0][0] for c in mock_logging.getLogger.call_args_list]
            for name in ("sqlalchemy", "sqlalchemy.engine", "sqlalchemy.dialects"):
                assert name in calls

    def test_propagate_false(self) -> None:
        with patch("logly.integrations.sqlalchemy.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.WARNING = logging.WARNING
            setup_sqlalchemy_logging()
            logger = mock_logging.getLogger.return_value
            assert logger.propagate is False

    def test_custom_level(self) -> None:
        with patch("logly.integrations.sqlalchemy.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.DEBUG = logging.DEBUG
            mock_logging.WARNING = logging.WARNING
            setup_sqlalchemy_logging(level="DEBUG")
            logger = mock_logging.getLogger.return_value
            logger.setLevel.assert_called_with(logging.DEBUG)

    def test_echo_parameter_ignored(self) -> None:
        with patch("logly.integrations.sqlalchemy.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.WARNING = logging.WARNING
            setup_sqlalchemy_logging(echo=True)
