"""Tests for structlog integration."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.structlog import (
    LoglyRenderer,
    _check_structlog,
    logly_processor,
)


class TestCheckStructlog:
    def test_raises_when_structlog_missing(self) -> None:
        with patch.dict(sys.modules, {"structlog": None}):
            with pytest.raises(ImportError, match="structlog is required"):
                _check_structlog()

    def test_does_not_raise_when_structlog_present(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            _check_structlog()


class TestLoglyProcessor:
    def test_returns_list(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            result = logly_processor()
            assert isinstance(result, list)

    def test_includes_merge_contextvars(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            result = logly_processor()
            assert mock_structlog.contextvars.merge_contextvars in result

    def test_includes_add_log_level(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            result = logly_processor()
            assert mock_structlog.processors.add_log_level in result

    def test_includes_timestamper(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            result = logly_processor()
            assert mock_structlog.processors.TimeStamper.return_value in result

    def test_logger_name_bound(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            with patch("logly.integrations.structlog.logger") as mock_logger:
                mock_logger.bind.return_value = mock_logger
                processors = logly_processor(logger_name="myapp")
                sink = processors[-1]
                sink("myapp", "info", {"event": "hello"})
                mock_logger.bind.assert_called()

    def test_kwargs_ignored(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            result = logly_processor(wrapper_class="foo", extra="bar")
            assert isinstance(result, list)


class TestLoglyRenderer:
    def test_instantiation(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            renderer = LoglyRenderer()
            assert renderer is not None

    def test_instantiation_with_level(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            renderer = LoglyRenderer(level="DEBUG")
            assert renderer._level == "DEBUG"

    def test_instantiation_raises_without_structlog(self) -> None:
        with patch.dict(sys.modules, {"structlog": None}):
            with pytest.raises(ImportError, match="structlog is required"):
                LoglyRenderer()

    def test_call_routes_to_logly(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            with patch("logly.integrations.structlog.logger") as mock_logger:
                mock_logger.bind.return_value = mock_logger
                renderer = LoglyRenderer()
                renderer(None, "info", {"event": "hello"})
                mock_logger.log.assert_called_once_with("INFO", "hello")

    def test_call_with_extra_fields(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            with patch("logly.integrations.structlog.logger") as mock_logger:
                mock_logger.bind.return_value = mock_logger
                renderer = LoglyRenderer()
                renderer(None, "info", {"event": "hello", "key": "value"})
                mock_logger.bind.assert_called_once_with(key="value")

    def test_call_with_logger_name_and_extra(self) -> None:
        mock_structlog = MagicMock()
        with patch.dict(sys.modules, {"structlog": mock_structlog}):
            with patch("logly.integrations.structlog.logger") as mock_logger:
                mock_logger.bind.return_value = mock_logger
                renderer = LoglyRenderer()
                renderer("myapp", "info", {"event": "hello", "key": "value"})
                mock_logger.bind.assert_called_once_with(key="value")
                mock_logger.bind.return_value.log.assert_called_once_with("INFO", "hello")
