from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.sentry import _SENTRY_LEVEL_MAP, SentrySink


class TestSentrySinkInit:
    def test_init_import_guard(self) -> None:
        saved = sys.modules.get("sentry_sdk")
        sys.modules["sentry_sdk"] = None
        try:
            with pytest.raises(ImportError, match="sentry-sdk is required"):
                SentrySink(dsn="https://fake@sentry.io/1")
        finally:
            if saved is not None:
                sys.modules["sentry_sdk"] = saved
            else:
                sys.modules.pop("sentry_sdk", None)

    def test_init_with_dsn(self) -> None:
        mock_sdk = MagicMock()
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            SentrySink(dsn="https://key@sentry.io/1")
            mock_sdk.init.assert_called_once_with(dsn="https://key@sentry.io/1")

    def test_init_without_dsn(self) -> None:
        mock_sdk = MagicMock()
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            SentrySink()
            mock_sdk.init.assert_called_once_with()

    def test_init_with_all_params(self) -> None:
        mock_sdk = MagicMock()
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            sink = SentrySink(
                dsn="https://key@sentry.io/1",
                environment="prod",
                release="1.0.0",
                level="ERROR",
            )
            mock_sdk.init.assert_called_once_with(
                dsn="https://key@sentry.io/1",
                environment="prod",
                release="1.0.0",
            )
            assert sink._level == "ERROR"


class TestSentryLevelMap:
    def test_all_logly_levels_mapped(self) -> None:
        expected_levels = [
            "TRACE",
            "DEBUG",
            "INFO",
            "NOTICE",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "FAIL",
            "CRITICAL",
            "FATAL",
            "AUDIT",
        ]
        for level in expected_levels:
            assert level in _SENTRY_LEVEL_MAP

    def test_trace_maps_to_debug(self) -> None:
        assert _SENTRY_LEVEL_MAP["TRACE"] == "debug"

    def test_debug_maps_to_debug(self) -> None:
        assert _SENTRY_LEVEL_MAP["DEBUG"] == "debug"

    def test_info_maps_to_info(self) -> None:
        assert _SENTRY_LEVEL_MAP["INFO"] == "info"

    def test_notice_maps_to_info(self) -> None:
        assert _SENTRY_LEVEL_MAP["NOTICE"] == "info"

    def test_success_maps_to_info(self) -> None:
        assert _SENTRY_LEVEL_MAP["SUCCESS"] == "info"

    def test_warning_maps_to_warning(self) -> None:
        assert _SENTRY_LEVEL_MAP["WARNING"] == "warning"

    def test_error_maps_to_error(self) -> None:
        assert _SENTRY_LEVEL_MAP["ERROR"] == "error"

    def test_fail_maps_to_error(self) -> None:
        assert _SENTRY_LEVEL_MAP["FAIL"] == "error"

    def test_critical_maps_to_fatal(self) -> None:
        assert _SENTRY_LEVEL_MAP["CRITICAL"] == "fatal"

    def test_fatal_maps_to_fatal(self) -> None:
        assert _SENTRY_LEVEL_MAP["FATAL"] == "fatal"

    def test_audit_maps_to_info(self) -> None:
        assert _SENTRY_LEVEL_MAP["AUDIT"] == "info"


class TestSentrySinkWrite:
    def _make_sink(self, level: str = "WARNING") -> SentrySink:
        mock_sdk = MagicMock()
        mock_sdk.new_scope.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_sdk.new_scope.return_value.__exit__ = MagicMock(return_value=False)
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            sink = SentrySink(dsn="https://key@sentry.io/1", level=level)
        return sink

    def test_write_sends_above_threshold(self) -> None:
        mock_sdk = MagicMock()
        scope = MagicMock()
        mock_sdk.new_scope.return_value.__enter__ = MagicMock(return_value=scope)
        mock_sdk.new_scope.return_value.__exit__ = MagicMock(return_value=False)
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            sink = SentrySink(dsn="https://key@sentry.io/1", level="WARNING")
            sink.write("[WARNING] something broke\n")
            mock_sdk.capture_message.assert_called_once()

    def test_write_skips_below_threshold(self) -> None:
        mock_sdk = MagicMock()
        scope = MagicMock()
        mock_sdk.new_scope.return_value.__enter__ = MagicMock(return_value=scope)
        mock_sdk.new_scope.return_value.__exit__ = MagicMock(return_value=False)
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            sink = SentrySink(dsn="https://key@sentry.io/1", level="ERROR")
            sink.write("[DEBUG] verbose output\n")
            mock_sdk.capture_message.assert_not_called()

    def test_write_empty_message_at_info_level(self) -> None:
        mock_sdk = MagicMock()
        scope = MagicMock()
        mock_sdk.new_scope.return_value.__enter__ = MagicMock(return_value=scope)
        mock_sdk.new_scope.return_value.__exit__ = MagicMock(return_value=False)
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            sink = SentrySink(dsn="https://key@sentry.io/1", level="INFO")
            sink.write("\n")
            mock_sdk.capture_message.assert_called_once()

    def test_write_import_error_returns(self) -> None:
        with patch.dict(sys.modules, {"sentry_sdk": None}):
            sink = object.__new__(SentrySink)
            sink._level = "WARNING"
            sink.write("[ERROR] test\n")


class TestSentrySinkFlush:
    def test_flush_calls_sentry_flush(self) -> None:
        mock_sdk = MagicMock()
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            sink = object.__new__(SentrySink)
            sink._level = "WARNING"
            sink.flush()
            mock_sdk.flush.assert_called_once()

    def test_flush_import_error_noop(self) -> None:
        with patch.dict(sys.modules, {"sentry_sdk": None}):
            sink = object.__new__(SentrySink)
            sink._level = "WARNING"
            sink.flush()


class TestSentrySinkClose:
    def test_close_calls_flush(self) -> None:
        mock_sdk = MagicMock()
        with patch.dict(sys.modules, {"sentry_sdk": mock_sdk}):
            sink = object.__new__(SentrySink)
            sink._level = "WARNING"
            sink.close()
            mock_sdk.flush.assert_called_once()
