"""Tests for Google Cloud Logging integration."""

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
        if "logly.integrations.google_cloud_logging" in sys.modules:
            del sys.modules["logly.integrations.google_cloud_logging"]
        from logly.integrations import google_cloud_logging as _m

        return _m


_mod = _import_mod()


class TestGoogleCloudLoggingSinkInit:
    def test_init_import_guard(self) -> None:
        with patch.object(_mod, "_has_google_cloud_logging", False):
            with pytest.raises(ImportError, match="google-cloud-logging"):
                _mod.GoogleCloudLoggingSink(project_id="test")


class TestGoogleCloudLoggingSinkDetectSeverity:
    def test_fatal(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("FATAL crash") == "CRITICAL"

    def test_critical(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("CRITICAL failure") == "CRITICAL"

    def test_error(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[ERROR] bad") == "ERROR"

    def test_fail(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[FAIL] task") == "ERROR"

    def test_warning(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[WARNING] heads up") == "WARNING"

    def test_notice(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[NOTICE] info") == "INFO"

    def test_success(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[SUCCESS] done") == "INFO"

    def test_info(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[INFO] general") == "INFO"

    def test_debug(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[DEBUG] detail") == "DEBUG"

    def test_trace(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("[TRACE] trace") == "DEBUG"

    def test_unknown(self) -> None:
        assert _mod.GoogleCloudLoggingSink._detect_severity("random message") == "INFO"


class TestGoogleCloudLoggingSinkWrite:
    def test_write_sends_struct(self) -> None:
        mock_logger = MagicMock()
        sink = object.__new__(_mod.GoogleCloudLoggingSink)
        sink._gcl_logger = mock_logger

        sink.write("[INFO] hello gcloud\n")
        mock_logger.log_struct.assert_called_once()


class TestGoogleCloudLoggingSinkFlush:
    def test_flush_noop(self) -> None:
        sink = object.__new__(_mod.GoogleCloudLoggingSink)
        sink.flush()


class TestGoogleCloudLoggingSinkClose:
    def test_close_calls_client_close(self) -> None:
        mock_client = MagicMock()
        sink = object.__new__(_mod.GoogleCloudLoggingSink)
        sink._client = mock_client
        sink.close()
        mock_client.close.assert_called_once()
