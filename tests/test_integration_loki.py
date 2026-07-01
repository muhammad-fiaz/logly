"""Tests for Loki integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestLokiSinkInit:
    def test_init_defaults(self) -> None:
        from logly.integrations.loki import LokiSink

        sink = LokiSink()
        assert sink.endpoint == "http://localhost:3100/loki/api/v1/push"
        assert sink.labels == {"app": "logly"}
        assert sink.timeout == 5.0
        assert sink._auth is None

    def test_init_custom_params(self) -> None:
        from logly.integrations.loki import LokiSink

        sink = LokiSink(
            "http://loki:3100/push",
            labels={"env": "prod", "app": "web"},
            timeout=10.0,
        )
        assert sink.endpoint == "http://loki:3100/push"
        assert sink.labels == {"env": "prod", "app": "web"}
        assert sink.timeout == 10.0

    def test_init_with_auth(self) -> None:
        from logly.integrations.loki import LokiSink

        sink = LokiSink("http://localhost:3100/push", username="user", password="pass")
        assert sink._auth is not None

    def test_init_auth_without_both_no_auth(self) -> None:
        from logly.integrations.loki import LokiSink

        sink = LokiSink("http://localhost:3100/push", username="user")
        assert sink._auth is None


class TestLokiSinkWrite:
    @patch("logly.integrations.loki.urllib.request.urlopen")
    def test_write_sends_payload(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.loki import LokiSink

        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        sink = LokiSink("http://localhost:3100/push")
        sink.write("test log entry\n")

        mock_urlopen.assert_called_once()

    @patch("logly.integrations.loki.urllib.request.urlopen")
    def test_write_strips_newline(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.loki import LokiSink

        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        sink = LokiSink("http://localhost:3100/push")
        sink.write("msg\n")
        mock_urlopen.assert_called_once()

    def test_write_empty_message(self) -> None:
        from logly.integrations.loki import LokiSink

        with patch("logly.integrations.loki.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b""
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            sink = LokiSink("http://localhost:3100/push")
            sink.write("")
            mock_urlopen.assert_called_once()

    @patch("logly.integrations.loki.urllib.request.urlopen")
    def test_write_exception_propagates(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.loki import LokiSink

        mock_urlopen.side_effect = ConnectionError("fail")

        sink = LokiSink("http://localhost:3100/push")
        with pytest.raises(ConnectionError):
            sink.write("msg")


class TestLokiSinkFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.loki import LokiSink

        sink = LokiSink()
        sink.flush()

    def test_close_noop(self) -> None:
        from logly.integrations.loki import LokiSink

        sink = LokiSink()
        sink.close()
