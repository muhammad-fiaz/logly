"""Tests for Uvicorn integration."""

from __future__ import annotations

import logging
from unittest.mock import patch

from logly.integrations.uvicorn import (
    _UvicornFormatter,
    _UvicornHandler,
    get_log_config,
    setup_uvicorn_logging,
)


class TestSetupUvicornLogging:
    def test_configures_all_loggers(self) -> None:
        with patch("logly.integrations.uvicorn.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            with patch("logly.integrations.uvicorn.logger"):
                setup_uvicorn_logging()
                calls = [c[0][0] for c in mock_logging.getLogger.call_args_list]
                for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
                    assert name in calls

    def test_propagate_false(self) -> None:
        with patch("logly.integrations.uvicorn.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            with patch("logly.integrations.uvicorn.logger"):
                setup_uvicorn_logging()
                logger = mock_logging.getLogger.return_value
                assert logger.propagate is False

    def test_custom_level(self) -> None:
        with patch("logly.integrations.uvicorn.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.DEBUG = logging.DEBUG
            mock_logging.INFO = logging.INFO
            with patch("logly.integrations.uvicorn.logger"):
                setup_uvicorn_logging(level="DEBUG")
                logger = mock_logging.getLogger.return_value
                logger.setLevel.assert_called_with(logging.DEBUG)

    def test_adds_stderr_sink(self) -> None:
        with patch("logly.integrations.uvicorn.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            with patch("logly.integrations.uvicorn.logger") as mock_logger:
                setup_uvicorn_logging()
                mock_logger.add.assert_called_once()


class TestGetLogConfig:
    def test_returns_dict(self) -> None:
        result = get_log_config()
        assert isinstance(result, dict)

    def test_has_version(self) -> None:
        result = get_log_config()
        assert result["version"] == 1

    def test_has_formatters(self) -> None:
        result = get_log_config()
        assert "formatters" in result
        assert "logly" in result["formatters"]

    def test_has_handlers(self) -> None:
        result = get_log_config()
        assert "handlers" in result
        assert "logly" in result["handlers"]

    def test_has_root(self) -> None:
        result = get_log_config()
        assert "root" in result
        assert result["root"]["handlers"] == ["logly"]

    def test_has_loggers(self) -> None:
        result = get_log_config()
        assert "loggers" in result
        for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            assert name in result["loggers"]

    def test_custom_level(self) -> None:
        result = get_log_config(level="DEBUG")
        assert result["root"]["level"] == "DEBUG"
        assert result["handlers"]["logly"]["level"] == "DEBUG"
        for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            assert result["loggers"][name]["level"] == "DEBUG"


class TestUvicornFormatter:
    def test_format_returns_message(self) -> None:
        formatter = _UvicornFormatter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        result = formatter.format(record)
        assert result == "hello"


class TestUvicornHandler:
    def test_emit_routes_to_logly(self) -> None:
        handler = _UvicornHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.uvicorn.logger") as mock_logger:
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(depth=1)
            mock_logger.opt.return_value.log.assert_called_once_with("INFO", "hello")

    def test_emit_handles_exception(self) -> None:
        handler = _UvicornHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
        with patch("logly.integrations.uvicorn.logger") as mock_logger:
            mock_logger.opt.side_effect = Exception("fail")
            handler.emit(record)

    def test_emit_exception_with_exc_info(self) -> None:
        handler = _UvicornHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "err", (), exc_info)
        with patch("logly.integrations.uvicorn.logger") as mock_logger:
            handler.emit(record)
            mock_logger.opt.assert_called_once_with(depth=1)
