from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.opentelemetry import OTelLogSink


class TestOTelLogSinkInit:
    def test_init_import_guard(self) -> None:
        saved = sys.modules.get("opentelemetry.sdk._logs")
        saved_resource = sys.modules.get("opentelemetry.sdk.resources")
        sys.modules["opentelemetry.sdk._logs"] = None
        sys.modules["opentelemetry.sdk.resources"] = None
        try:
            with pytest.raises(ImportError, match="opentelemetry-api and opentelemetry-sdk"):
                OTelLogSink(service_name="test")
        finally:
            if saved is not None:
                sys.modules["opentelemetry.sdk._logs"] = saved
            else:
                sys.modules.pop("opentelemetry.sdk._logs", None)
            if saved_resource is not None:
                sys.modules["opentelemetry.sdk.resources"] = saved_resource
            else:
                sys.modules.pop("opentelemetry.sdk.resources", None)

    def test_init_creates_provider(self) -> None:
        mock_sdk = MagicMock()
        mock_resources = MagicMock()
        mock_resources.SERVICE_NAME = "service.name"
        mock_resource = MagicMock()
        mock_resources.Resource.create.return_value = mock_resource
        mock_provider = MagicMock()
        mock_sdk.LoggerProvider.return_value = mock_provider
        mock_otel_logger = MagicMock()
        mock_provider.get_logger.return_value = mock_otel_logger

        with patch.dict(
            sys.modules,
            {
                "opentelemetry.sdk._logs": mock_sdk,
                "opentelemetry.sdk.resources": mock_resources,
            },
        ):
            sink = OTelLogSink(service_name="my-service")
            assert sink._service_name == "my-service"
            assert sink._otel_logger is mock_otel_logger


class TestOTelLogSinkResolveSeverity:
    def test_resolve_severity_fatal(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("FATAL error occurred") == 21

    def test_resolve_severity_critical(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("CRITICAL failure") == 21

    def test_resolve_severity_error(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[ERROR] something") == 17

    def test_resolve_severity_fail(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[FAIL] task failed") == 17

    def test_resolve_severity_warning(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[WARNING] heads up") == 13

    def test_resolve_severity_notice(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[NOTICE] info") == 9

    def test_resolve_severity_success(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[SUCCESS] done") == 9

    def test_resolve_severity_info(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[INFO] general") == 9

    def test_resolve_severity_debug(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[DEBUG] detail") == 5

    def test_resolve_severity_trace(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("[TRACE] trace") == 1

    def test_resolve_severity_unknown_defaults_to_info(self) -> None:
        mock_severity = MagicMock()
        mock_severity.FATAL.value = 21
        mock_severity.ERROR.value = 17
        mock_severity.WARN.value = 13
        mock_severity.INFO.value = 9
        mock_severity.DEBUG.value = 5
        mock_severity.TRACE.value = 1
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity
        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            assert OTelLogSink._resolve_severity("random message") == 9

    def test_resolve_severity_import_error_returns_info(self) -> None:
        with patch.dict(sys.modules, {"opentelemetry._logs": None}):
            assert OTelLogSink._resolve_severity("anything") == 9


class TestOTelLogSinkWrite:
    def test_write_emits_to_otel_logger(self) -> None:
        mock_otel_logger = MagicMock()
        mock_severity = MagicMock()
        mock_severity.INFO.value = 9
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity

        sink = object.__new__(OTelLogSink)
        sink._otel_logger = mock_otel_logger

        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            sink.write("[INFO] hello otel\n")
            mock_otel_logger.emit.assert_called_once()

    def test_write_strips_newline(self) -> None:
        mock_otel_logger = MagicMock()
        mock_severity = MagicMock()
        mock_severity.INFO.value = 9
        mock_logs = MagicMock()
        mock_logs.SeverityNumber = mock_severity

        sink = object.__new__(OTelLogSink)
        sink._otel_logger = mock_otel_logger

        with patch.dict(sys.modules, {"opentelemetry._logs": mock_logs}):
            sink.write("msg\n")
            call_kwargs = mock_otel_logger.emit.call_args[1]
            assert call_kwargs["body"] == "msg"


class TestOTelLogSinkFlush:
    def test_flush_calls_provider(self) -> None:
        mock_provider = MagicMock()
        sink = object.__new__(OTelLogSink)
        sink._provider = mock_provider
        sink.flush()
        mock_provider.force_flush.assert_called_once()


class TestOTelLogSinkClose:
    def test_close_calls_shutdown(self) -> None:
        mock_provider = MagicMock()
        sink = object.__new__(OTelLogSink)
        sink._provider = mock_provider
        sink.close()
        mock_provider.shutdown.assert_called_once()
