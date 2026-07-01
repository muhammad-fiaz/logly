"""Tests for RQ integration."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

from logly.integrations.rq import (
    RQHandler,
    _resolve_level,
    setup_rq_logging,
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


class TestRQHandlerInit:
    def test_instantiation(self) -> None:
        handler = RQHandler()
        assert handler is not None

    def test_is_logging_handler(self) -> None:
        assert issubclass(RQHandler, logging.Handler)


class TestRQHandlerEmit:
    def test_emit_none_record_is_noop(self) -> None:
        handler = RQHandler()
        handler.emit(None)

    def test_emit_routes_to_logly(self) -> None:
        handler = RQHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.rq.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)
            mock_logger.opt.return_value.log.assert_called_once_with("INFO", "hello")

    def test_emit_with_exception(self) -> None:
        handler = RQHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        with patch("logly.integrations.rq.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            assert mock_logger.opt.call_args[1]["exception"] is not None

    def test_emit_exception_info_none(self) -> None:
        handler = RQHandler()
        record = logging.LogRecord("test", logging.WARNING, "", 0, "warn", (), (None, None, None))
        with patch("logly.integrations.rq.logger") as mock_logger:
            mock_logger.opt.return_value.log = MagicMock()
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(exception=None)

    def test_emit_level_fallback_on_resolve_error(self) -> None:
        handler = RQHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with patch("logly.integrations.rq._resolve_level", side_effect=Exception("bad")):
            with patch("logly.integrations.rq.logger") as mock_logger:
                mock_logger.opt.return_value.log = MagicMock()
                handler.emit(record)
                mock_logger.opt.return_value.log.assert_called_once_with("INFO", "msg")

    def test_emit_handles_logger_exception(self) -> None:
        handler = RQHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with patch("logly.integrations.rq.logger") as mock_logger:
            mock_logger.opt.return_value.log.side_effect = Exception("fail")
            handler.emit(record)


class TestHandleError:
    def test_handle_error_writes_to_stderr(self) -> None:
        handler = RQHandler()
        with patch("sys.stderr") as mock_stderr:
            handler.handleError(None)
            mock_stderr.write.assert_called_once_with("Logly RQHandler error:\n")

    def test_handle_error_stderr_none(self) -> None:
        handler = RQHandler()
        with patch("sys.stderr", None):
            handler.handleError(None)

    def test_handle_error_write_exception(self) -> None:
        handler = RQHandler()
        with patch("sys.stderr") as mock_stderr:
            mock_stderr.write.side_effect = Exception("fail")
            handler.handleError(None)


class TestSetupRqLogging:
    def test_configures_rq_logger(self) -> None:
        with patch("logly.integrations.rq.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            setup_rq_logging()
            calls = [c[0][0] for c in mock_logging.getLogger.call_args_list]
            assert "rq" in calls

    def test_configures_rq_worker_logger(self) -> None:
        with patch("logly.integrations.rq.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            setup_rq_logging()
            calls = [c[0][0] for c in mock_logging.getLogger.call_args_list]
            assert "rq.worker" in calls

    def test_propagate_false(self) -> None:
        with patch("logly.integrations.rq.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            setup_rq_logging()
            logger = mock_logging.getLogger.return_value
            assert logger.propagate is False

    def test_custom_level(self) -> None:
        with patch("logly.integrations.rq.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.DEBUG = logging.DEBUG
            mock_logging.INFO = logging.INFO
            setup_rq_logging(level="DEBUG")
            logger = mock_logging.getLogger.return_value
            logger.setLevel.assert_called_with(logging.DEBUG)
