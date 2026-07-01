"""Tests for Seq integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestSeqSinkInit:
    def test_init_requires_url(self) -> None:
        from logly.integrations.seq import SeqSink

        with pytest.raises(ValueError, match="Seq server URL is required"):
            SeqSink(server_url="")

    def test_init_defaults(self) -> None:
        from logly.integrations.seq import SeqSink

        sink = SeqSink("http://localhost:5341")
        assert sink._server_url == "http://localhost:5341"
        assert sink._api_key is None
        assert sink._event_template == {}
        assert sink._timeout == 5.0

    def test_init_custom_params(self) -> None:
        from logly.integrations.seq import SeqSink

        sink = SeqSink(
            "http://seq:5341",
            api_key="key123",
            event_template={"app": "web"},
            timeout=10.0,
        )
        assert sink._server_url == "http://seq:5341"
        assert sink._api_key == "key123"
        assert sink._event_template == {"app": "web"}
        assert sink._timeout == 10.0

    def test_init_strips_trailing_slash(self) -> None:
        from logly.integrations.seq import SeqSink

        sink = SeqSink("http://seq:5341/")
        assert sink._server_url == "http://seq:5341"


class TestSeqDetectSeverity:
    def test_detect_trace(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("TRACE entry") == "Debug"

    def test_detect_debug(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("DEBUG var") == "Debug"

    def test_detect_info(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("INFO started") == "Information"

    def test_detect_notice(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("NOTICE loaded") == "Information"

    def test_detect_success(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("SUCCESS done") == "Information"

    def test_detect_warning(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("WARNING low") == "Warning"

    def test_detect_error(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("ERROR 500") == "Error"

    def test_detect_fail(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("FAIL timeout") == "Error"

    def test_detect_critical(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("CRITICAL outage") == "Fatal"

    def test_detect_fatal(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("FATAL crash") == "Fatal"

    def test_detect_audit(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("AUDIT login") == "Information"

    def test_detect_no_match_default(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("just a message") == "Information"

    def test_detect_case_insensitive(self) -> None:
        from logly.integrations.seq import SeqSink

        assert SeqSink._detect_severity("error lowercase") == "Error"


class TestSeqSinkWrite:
    @patch("logly.integrations.seq.urllib.request.urlopen")
    def test_write_sends_event(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.seq import SeqSink

        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        sink = SeqSink("http://localhost:5341")
        sink.write("test log\n")

        mock_urlopen.assert_called_once()

    @patch("logly.integrations.seq.urllib.request.urlopen")
    def test_write_includes_api_key(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.seq import SeqSink

        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        sink = SeqSink("http://localhost:5341", api_key="key123")
        sink.write("msg")

        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert request.get_header("X-seq-apikey") == "key123"

    def test_write_empty_message(self) -> None:
        from logly.integrations.seq import SeqSink

        with patch("logly.integrations.seq.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b""
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            sink = SeqSink("http://localhost:5341")
            sink.write("")
            mock_urlopen.assert_called_once()

    @patch("logly.integrations.seq.urllib.request.urlopen")
    def test_write_exception_swallows(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.seq import SeqSink

        mock_urlopen.side_effect = ConnectionError("fail")

        sink = SeqSink("http://localhost:5341")
        sink.write("msg")  # should not raise


class TestSeqSinkFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.seq import SeqSink

        sink = SeqSink("http://localhost:5341")
        sink.flush()

    def test_close_noop(self) -> None:
        from logly.integrations.seq import SeqSink

        sink = SeqSink("http://localhost:5341")
        sink.close()
