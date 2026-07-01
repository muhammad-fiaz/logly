"""Tests for Pydantic integration."""

from __future__ import annotations

import logging
import sys
from unittest.mock import MagicMock, patch

from logly.integrations.pydantic import (
    LoglyFormatter,
    PydanticLogHandler,
    _resolve_level,
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


class TestPydanticLogHandlerInit:
    def test_instantiation(self) -> None:
        handler = PydanticLogHandler()
        assert handler is not None

    def test_is_logging_handler(self) -> None:
        assert issubclass(PydanticLogHandler, logging.Handler)


class TestPydanticLogHandlerEmit:
    def test_emit_routes_to_logly(self) -> None:
        handler = PydanticLogHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.pydantic.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)
            mock_logger.opt.return_value.log.assert_called_once_with("INFO", "hello")

    def test_emit_with_exception(self) -> None:
        handler = PydanticLogHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        with patch("logly.integrations.pydantic.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            assert mock_logger.opt.call_args[1]["exception"] is not None

    def test_emit_exception_info_none(self) -> None:
        handler = PydanticLogHandler()
        record = logging.LogRecord("test", logging.WARNING, "", 0, "warn", (), (None, None, None))
        with patch("logly.integrations.pydantic.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)

    def test_emit_level_fallback_on_resolve_error(self) -> None:
        handler = PydanticLogHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with patch("logly.integrations.pydantic._resolve_level", side_effect=Exception("bad")):
            with patch("logly.integrations.pydantic.logger") as mock_logger:
                mock_logger.opt.return_value.log = MagicMock()
                handler.emit(record)
                mock_logger.opt.return_value.log.assert_called_once_with("INFO", "msg")


class TestHandleError:
    def test_handle_error_prints_to_stderr(self) -> None:
        handler = PydanticLogHandler()
        with patch("builtins.print") as mock_print:
            handler.handleError(None)  # type: ignore[arg-type]
            mock_print.assert_called_once_with("Logly PydanticLogHandler error:", file=sys.stderr)

    def test_handle_error_stderr_none(self) -> None:
        handler = PydanticLogHandler()
        with patch("sys.stderr", None):
            handler.handleError(None)  # type: ignore[arg-type]

    def test_handle_error_print_exception(self) -> None:
        handler = PydanticLogHandler()
        with patch("builtins.print", side_effect=Exception("fail")):
            handler.handleError(None)  # type: ignore[arg-type]


class TestLoglyFormatterInit:
    def test_default_uses_global_logger(self) -> None:
        formatter = LoglyFormatter()
        assert formatter._logger is not None

    def test_custom_logger(self) -> None:
        mock_logger = MagicMock()
        formatter = LoglyFormatter(logly_logger=mock_logger)
        assert formatter._logger is mock_logger


class TestLoglyFormatterFormat:
    def test_format_returns_message(self) -> None:
        formatter = LoglyFormatter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.pydantic.logger"):
            result = formatter.format(record)
        assert result == "hello"

    def test_format_calls_logger(self) -> None:
        mock_logger = MagicMock()
        formatter = LoglyFormatter(logly_logger=mock_logger)
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        formatter.format(record)
        mock_logger.opt.return_value.log.assert_called_once_with("INFO", "hello")

    def test_format_with_exception(self) -> None:
        mock_logger = MagicMock()
        formatter = LoglyFormatter(logly_logger=mock_logger)
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        formatter.format(record)
        assert mock_logger.opt.call_args[1]["exception"] is not None

    def test_format_level_fallback_on_resolve_error(self) -> None:
        mock_logger = MagicMock()
        formatter = LoglyFormatter(logly_logger=mock_logger)
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with patch("logly.integrations.pydantic._resolve_level", side_effect=Exception("bad")):
            result = formatter.format(record)
            mock_logger.opt.return_value.log.assert_called_once_with("INFO", "msg")
        assert result == "msg"
