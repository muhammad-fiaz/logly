"""Tests for propagate integration."""

from __future__ import annotations

import logging
from unittest.mock import patch


class TestPropagateHandlerInit:
    def test_init_defaults(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        handler = PropagateHandler()
        assert handler._logger.name == "logly"
        assert handler.level == logging.NOTSET

    def test_init_custom_name(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        handler = PropagateHandler(name="myapp")
        assert handler._logger.name == "myapp"

    def test_init_custom_level(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        handler = PropagateHandler(level=logging.WARNING)
        assert handler.level == logging.WARNING


class TestPropagateHandlerWriteLevelDetection:
    def test_write_debug(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[DEBUG] something happened")
            mock_log.assert_called_once_with(logging.DEBUG, "[DEBUG] something happened")

    def test_write_trace_maps_to_debug(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[TRACE] entry")
            mock_log.assert_called_once_with(logging.DEBUG, "[TRACE] entry")

    def test_write_info(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("server started")
            mock_log.assert_called_once_with(logging.INFO, "server started")

    def test_write_notice_maps_to_info(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[NOTICE] config loaded")
            mock_log.assert_called_once_with(logging.INFO, "[NOTICE] config loaded")

    def test_write_success_maps_to_info(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[SUCCESS] deployed")
            mock_log.assert_called_once_with(logging.INFO, "[SUCCESS] deployed")

    def test_write_warning(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[WARNING] low disk")
            mock_log.assert_called_once_with(logging.WARNING, "[WARNING] low disk")

    def test_write_warn_maps_to_warning(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[WARN] deprecated")
            mock_log.assert_called_once_with(logging.WARNING, "[WARN] deprecated")

    def test_write_error(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[ERROR] 500")
            mock_log.assert_called_once_with(logging.ERROR, "[ERROR] 500")

    def test_write_fail_maps_to_error(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[FAIL] timeout")
            mock_log.assert_called_once_with(logging.ERROR, "[FAIL] timeout")

    def test_write_critical(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[CRITICAL] outage")
            mock_log.assert_called_once_with(logging.CRITICAL, "[CRITICAL] outage")

    def test_write_fatal_maps_to_critical(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("[FATAL] crash")
            mock_log.assert_called_once_with(logging.CRITICAL, "[FATAL] crash")

    def test_write_strips_trailing_whitespace(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        with patch.object(logging.Logger, "log") as mock_log:
            handler = PropagateHandler()
            handler.write("msg  \n")
            mock_log.assert_called_once_with(logging.INFO, "msg")


class TestPropagateHandlerFlush:
    def test_flush_noop(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        handler = PropagateHandler()
        handler.flush()  # should not raise


class TestPropagateHandlerEmit:
    def test_emit_noop(self) -> None:
        from logly.integrations.propagate import PropagateHandler

        handler = PropagateHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        handler.emit(record)  # should not raise
