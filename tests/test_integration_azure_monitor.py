"""Tests for Azure Monitor integration."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

_orig_find_spec = __import__("importlib.util", fromlist=["find_spec"]).find_spec


def _safe_find_spec(name: str, *args: object, **kwargs: object):  # type: ignore[no-untyped-def]
    try:
        return _orig_find_spec(name, *args, **kwargs)
    except (ModuleNotFoundError, ValueError):
        return None


_safe_find_spec.__doc__ = _orig_find_spec.__doc__


def _import_mod():  # type: ignore[no-untyped-def]
    with patch("importlib.util.find_spec", side_effect=_safe_find_spec):
        if "logly.integrations.azure_monitor" in sys.modules:
            del sys.modules["logly.integrations.azure_monitor"]
        from logly.integrations import azure_monitor as _m

        return _m


_mod = _import_mod()


class TestAzureMonitorSinkInit:
    def test_init_import_guard(self) -> None:
        with patch.object(_mod, "_has_otel", False):
            with pytest.raises(ImportError, match="opentelemetry"):
                _mod.AzureMonitorSink(connection_string="InstrumentationKey=abc")

    def test_init_import_guard_no_azure(self) -> None:
        with patch.object(_mod, "_has_otel", True):
            with patch.object(_mod, "_has_azure_monitor", False):
                with pytest.raises(ImportError, match="opentelemetry"):
                    _mod.AzureMonitorSink(connection_string="InstrumentationKey=abc")

    def test_detect_severity_fatal(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("FATAL crash") == "FATAL"

    def test_detect_severity_critical(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("CRITICAL failure") == "FATAL"

    def test_detect_severity_error(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[ERROR] bad") == "ERROR"

    def test_detect_severity_fail(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[FAIL] task") == "ERROR"

    def test_detect_severity_warning(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[WARNING] heads up") == "WARN"

    def test_detect_severity_notice(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[NOTICE] info") == "INFO"

    def test_detect_severity_success(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[SUCCESS] done") == "INFO"

    def test_detect_severity_info(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[INFO] general") == "INFO"

    def test_detect_severity_debug(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[DEBUG] detail") == "TRACE"

    def test_detect_severity_trace(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("[TRACE] trace") == "TRACE"

    def test_detect_severity_unknown(self) -> None:
        assert _mod.AzureMonitorSink._detect_severity("random message") == "INFO"


class TestAzureMonitorSinkWrite:
    def test_write_emits_log(self) -> None:
        mock_logger = MagicMock()
        sink = object.__new__(_mod.AzureMonitorSink)
        sink._logger = mock_logger

        sink.write("[INFO] hello azure\n")
        mock_logger.emit.assert_called_once()

    def test_write_strips_newline(self) -> None:
        mock_logger = MagicMock()
        sink = object.__new__(_mod.AzureMonitorSink)
        sink._logger = mock_logger

        sink.write("msg\n")
        call_kwargs = mock_logger.emit.call_args[1]
        assert call_kwargs["body"] == "msg"


class TestAzureMonitorSinkFlush:
    def test_flush_calls_provider(self) -> None:
        mock_provider = MagicMock()
        sink = object.__new__(_mod.AzureMonitorSink)
        sink._provider = mock_provider
        sink.flush()
        mock_provider.force_flush.assert_called_once()


class TestAzureMonitorSinkClose:
    def test_close_calls_shutdown(self) -> None:
        mock_provider = MagicMock()
        sink = object.__new__(_mod.AzureMonitorSink)
        sink._provider = mock_provider
        sink.close()
        mock_provider.shutdown.assert_called_once()
