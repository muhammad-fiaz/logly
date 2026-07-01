"""Tests for APScheduler integration."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

from logly.integrations.apscheduler import (
    APSchedulerHandler,
    _resolve_level,
    setup_apscheduler_logging,
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

    def test_custom_level(self) -> None:
        record = logging.LogRecord("test", 25, "", 0, "msg", (), None)
        record.levelname = "CUSTOM"
        assert _resolve_level(record) == "CUSTOM"

    def test_unknown_level_falls_back_to_levelname(self) -> None:
        record = logging.LogRecord("test", 999, "", 0, "msg", (), None)
        record.levelname = "UNKNOWN"
        assert _resolve_level(record) == "UNKNOWN"


class TestAPSchedulerHandlerInit:
    def test_instantiation(self) -> None:
        handler = APSchedulerHandler()
        assert handler is not None

    def test_is_logging_handler(self) -> None:
        assert issubclass(APSchedulerHandler, logging.Handler)


class TestAPSchedulerHandlerEmit:
    def test_emit_none_record_is_noop(self) -> None:
        handler = APSchedulerHandler()
        handler.emit(None)

    def test_emit_routes_to_logly(self) -> None:
        handler = APSchedulerHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.apscheduler.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)
            mock_logger.opt.return_value.log.assert_called_once_with("INFO", "hello")

    def test_emit_with_exception(self) -> None:
        handler = APSchedulerHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        with patch("logly.integrations.apscheduler.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            assert mock_logger.opt.call_args[1]["exception"] is not None

    def test_emit_exception_info_none(self) -> None:
        handler = APSchedulerHandler()
        record = logging.LogRecord("test", logging.WARNING, "", 0, "warn", (), (None, None, None))
        with patch("logly.integrations.apscheduler.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)

    def test_emit_exception_with_none_type(self) -> None:
        handler = APSchedulerHandler()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), (None, None, None))
        with patch("logly.integrations.apscheduler.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)

    def test_emit_handles_logger_exception(self) -> None:
        handler = APSchedulerHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with patch("logly.integrations.apscheduler.logger") as mock_logger:
            mock_logger.opt.return_value.log.side_effect = Exception("fail")
            handler.emit(record)

    def test_emit_level_fallback_on_resolve_error(self) -> None:
        handler = APSchedulerHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with patch("logly.integrations.apscheduler._resolve_level", side_effect=Exception("bad")):
            with patch("logly.integrations.apscheduler.logger") as mock_logger:
                mock_logger.opt.return_value.log = MagicMock()
                handler.emit(record)
                mock_logger.opt.return_value.log.assert_called_once_with("INFO", "msg")


class TestHandleError:
    def test_handle_error_writes_to_stderr(self) -> None:
        handler = APSchedulerHandler()
        with patch("sys.stderr") as mock_stderr:
            handler.handleError(None)
            mock_stderr.write.assert_called_once_with("Logly APSchedulerHandler error:\n")

    def test_handle_error_stderr_none(self) -> None:
        handler = APSchedulerHandler()
        with patch("sys.stderr", None):
            handler.handleError(None)

    def test_handle_error_write_exception(self) -> None:
        handler = APSchedulerHandler()
        with patch("sys.stderr") as mock_stderr:
            mock_stderr.write.side_effect = Exception("fail")
            handler.handleError(None)


class TestSetupApschedulerLogging:
    def test_configures_root_logger(self) -> None:
        mock_logger = MagicMock()
        mock_logger.handlers = []
        with patch("logging.getLogger", return_value=mock_logger):
            setup_apscheduler_logging()
            mock_logger.setLevel.assert_called()
            assert mock_logger.propagate is False
