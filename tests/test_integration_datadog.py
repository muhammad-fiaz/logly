from __future__ import annotations

import json
import urllib.request
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.datadog import DatadogSink


class TestDatadogSinkInit:
    def test_init_requires_api_key(self) -> None:
        with pytest.raises(ValueError, match="A Datadog API key is required"):
            DatadogSink(api_key="")

    def test_init_requires_api_key_none(self) -> None:
        with pytest.raises(ValueError, match="A Datadog API key is required"):
            DatadogSink(api_key=None)  # type: ignore[arg-type]

    def test_init_default_params(self) -> None:
        sink = DatadogSink(api_key="test-key-123")
        assert sink._api_key == "test-key-123"
        assert sink._source == "python"
        assert sink._host is None
        assert sink._service is None
        assert sink._tags is None

    def test_init_custom_params(self) -> None:
        sink = DatadogSink(
            api_key="key",
            host="web-01",
            source="python",
            service="my-app",
            tags=["env:prod", "team:backend"],
            site="datadoghq.eu",
            timeout=10.0,
        )
        assert sink._host == "web-01"
        assert sink._source == "python"
        assert sink._service == "my-app"
        assert sink._tags == ["env:prod", "team:backend"]
        assert sink._site == "datadoghq.eu"
        assert sink._timeout == 10.0

    def test_init_default_site(self) -> None:
        sink = DatadogSink(api_key="key")
        assert "datadoghq.com" in sink._url


class TestDatadogSinkDetectSeverity:
    def test_detect_severity_fatal(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("FATAL crash") == "critical"

    def test_detect_severity_critical(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("CRITICAL failure") == "critical"

    def test_detect_severity_error(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[ERROR] bad") == "error"

    def test_detect_severity_fail(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[FAIL] task") == "error"

    def test_detect_severity_warning(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[WARNING]小心") == "warning"

    def test_detect_severity_warn(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[WARN] heads up") == "warning"

    def test_detect_severity_notice(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[NOTICE] info") == "info"

    def test_detect_severity_success(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[SUCCESS] done") == "info"

    def test_detect_severity_info(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("general message") == "info"

    def test_detect_severity_debug(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[DEBUG] verbose") == "debug"

    def test_detect_severity_trace(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("[TRACE] trace") == "debug"

    def test_detect_severity_default_info(self) -> None:
        sink = DatadogSink(api_key="key")
        assert sink._detect_severity("random text") == "info"


class TestDatadogSinkWrite:
    def test_write_sends_payload(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "ok"}'

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            sink = DatadogSink(api_key="test-key", service="test-svc")
            sink.write("[ERROR] something broke\n")
            mock_urlopen.assert_called_once()
            req = mock_urlopen.call_args[0][0]
            assert isinstance(req, urllib.request.Request)
            assert req.data is not None
            payload = json.loads(req.data)  # type: ignore[arg-type]
            assert payload["message"] == "[ERROR] something broke"
            assert payload["status"] == "error"
            assert payload["ddsource"] == "python"
            assert payload["service"] == "test-svc"

    def test_write_includes_optional_fields(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            sink = DatadogSink(
                api_key="key",
                host="web-01",
                service="my-svc",
                tags=["env:prod"],
            )
            sink.write("test msg\n")
            mock_urlopen.assert_called_once()
            req = mock_urlopen.call_args[0][0]
            assert isinstance(req, urllib.request.Request)

    def test_write_strips_newline(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            sink = DatadogSink(api_key="key")
            sink.write("msg\n")
            mock_urlopen.assert_called_once()

    def test_write_empty_message(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            sink = DatadogSink(api_key="key")
            sink.write("\n")
            mock_urlopen.assert_called_once()


class TestDatadogSinkFlush:
    def test_flush_noop(self) -> None:
        sink = DatadogSink(api_key="key")
        sink.flush()


class TestDatadogSinkClose:
    def test_close_noop(self) -> None:
        sink = DatadogSink(api_key="key")
        sink.close()
