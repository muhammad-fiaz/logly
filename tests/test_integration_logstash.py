"""Tests for Logstash integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestLogstashSinkInit:
    def test_init_defaults(self) -> None:
        from logly.integrations.logstash import LogstashSink

        sink = LogstashSink()
        assert sink.host == "localhost"
        assert sink.port == 5959
        assert sink.protocol == "tcp"
        assert sink.message_type == "logstash"
        assert sink.tags == []
        assert sink.key_prefix == ""
        assert sink.timeout == 5.0

    def test_init_invalid_protocol_raises(self) -> None:
        from logly.integrations.logstash import LogstashSink

        with pytest.raises(ValueError, match="Unsupported protocol"):
            LogstashSink(protocol="http")

    def test_init_custom_params(self) -> None:
        from logly.integrations.logstash import LogstashSink

        sink = LogstashSink(
            "10.0.0.1",
            9599,
            protocol="udp",
            message_type="myapp",
            tags=["prod"],
            key_prefix="app.",
            timeout=3.0,
        )
        assert sink.host == "10.0.0.1"
        assert sink.port == 9599
        assert sink.protocol == "udp"
        assert sink.message_type == "myapp"
        assert sink.tags == ["prod"]
        assert sink.key_prefix == "app."


class TestLogstashDetectLevel:
    def test_detect_fatal(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("FATAL crash") == "CRITICAL"

    def test_detect_critical(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("CRITICAL error") == "CRITICAL"

    def test_detect_error(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("ERROR 500") == "ERROR"

    def test_detect_fail(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("FAIL timeout") == "ERROR"

    def test_detect_warning(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("WARNING slow") == "WARNING"

    def test_detect_warn(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("WARN memory") == "WARNING"

    def test_detect_notice(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("NOTICE scheduled") == "NOTICE"

    def test_detect_success(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("SUCCESS complete") == "SUCCESS"

    def test_detect_debug(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("DEBUG trace") == "DEBUG"

    def test_detect_trace(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("TRACE entry") == "DEBUG"

    def test_detect_info_default(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("started server") == "INFO"

    def test_detect_case_insensitive(self) -> None:
        from logly.integrations.logstash import LogstashSink

        assert LogstashSink._detect_level("error lowercase") == "ERROR"


class TestLogstashSinkWrite:
    @patch("logly.integrations.logstash.socket.socket")
    def test_write_tcp(self, mock_socket_cls: MagicMock) -> None:
        from logly.integrations.logstash import LogstashSink

        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        sink = LogstashSink(protocol="tcp")
        sink.write("test message\n")

        mock_sock.sendall.assert_called_once()

    @patch("logly.integrations.logstash.socket.socket")
    def test_write_udp(self, mock_socket_cls: MagicMock) -> None:
        from logly.integrations.logstash import LogstashSink

        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        sink = LogstashSink(protocol="udp")
        sink.write("test message\n")

        mock_sock.sendto.assert_called_once()

    @patch("logly.integrations.logstash.socket.socket")
    def test_write_exception_resets_socket(self, mock_socket_cls: MagicMock) -> None:
        from logly.integrations.logstash import LogstashSink

        mock_sock = MagicMock()
        mock_sock.sendall.side_effect = ConnectionError("fail")
        mock_socket_cls.return_value = mock_sock

        sink = LogstashSink(protocol="tcp")
        sink.write("msg")
        assert sink._socket is None

    def test_write_empty_message(self) -> None:
        from logly.integrations.logstash import LogstashSink

        with patch("logly.integrations.logstash.socket.socket") as mock_cls:
            mock_sock = MagicMock()
            mock_cls.return_value = mock_sock

            sink = LogstashSink(protocol="tcp")
            sink.write("")
            mock_sock.sendall.assert_called_once()


class TestLogstashSinkFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.logstash import LogstashSink

        sink = LogstashSink()
        sink.flush()

    def test_close_clears_socket(self) -> None:
        from logly.integrations.logstash import LogstashSink

        sink = LogstashSink()
        mock_sock = MagicMock()
        sink._socket = mock_sock
        sink.close()
        mock_sock.close.assert_called_once()
        assert sink._socket is None

    def test_close_no_socket(self) -> None:
        from logly.integrations.logstash import LogstashSink

        sink = LogstashSink()
        sink.close()  # should not raise
