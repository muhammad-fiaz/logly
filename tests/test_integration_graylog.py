"""Tests for Graylog GELF integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestGraylogSinkInit:
    def test_init_defaults(self) -> None:
        from logly.integrations.graylog import GraylogSink

        sink = GraylogSink()
        assert sink.host == "localhost"
        assert sink.port == 12201
        assert sink.protocol == "udp"
        assert sink.graylog_version == "1.1"
        assert sink.chunk_size == 8192
        assert sink.facility is None
        assert sink.hostname_override is None
        assert sink.timeout == 5.0

    def test_init_invalid_protocol_raises(self) -> None:
        from logly.integrations.graylog import GraylogSink

        with pytest.raises(ValueError, match="Unsupported protocol"):
            GraylogSink(protocol="http")

    def test_init_invalid_gelf_version_raises(self) -> None:
        from logly.integrations.graylog import GraylogSink

        with pytest.raises(ValueError, match="Unsupported GELF version"):
            GraylogSink(graylog_version="2.0")

    def test_init_tcp(self) -> None:
        from logly.integrations.graylog import GraylogSink

        sink = GraylogSink(protocol="tcp")
        assert sink.protocol == "tcp"

    def test_init_custom_params(self) -> None:
        from logly.integrations.graylog import GraylogSink

        sink = GraylogSink(
            "10.0.0.1",
            9200,
            protocol="tcp",
            graylog_version="1.0",
            chunk_size=4096,
            facility="myapp",
            hostname="web01",
            timeout=3.0,
        )
        assert sink.host == "10.0.0.1"
        assert sink.port == 9200
        assert sink.facility == "myapp"
        assert sink.hostname_override == "web01"


class TestGraylogDetectLevel:
    def test_detect_fatal(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("FATAL error occurred") == "CRITICAL"

    def test_detect_critical(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("CRITICAL failure") == "CRITICAL"

    def test_detect_error(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("ERROR in module") == "ERROR"

    def test_detect_fail(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("FAIL to connect") == "ERROR"

    def test_detect_warning(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("WARNING low disk") == "WARNING"

    def test_detect_warn(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("WARN deprecated") == "WARNING"

    def test_detect_notice(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("NOTICE config loaded") == "NOTICE"

    def test_detect_success(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("SUCCESS deployed") == "SUCCESS"

    def test_detect_debug(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("DEBUG var x") == "DEBUG"

    def test_detect_trace(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("TRACE entry") == "DEBUG"

    def test_detect_info_default(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("server started") == "INFO"

    def test_detect_case_insensitive(self) -> None:
        from logly.integrations.graylog import GraylogSink

        assert GraylogSink._detect_level("error lowercase") == "ERROR"


class TestGraylogSinkWrite:
    @patch("logly.integrations.graylog.socket.socket")
    def test_write_udp(self, mock_socket_cls: MagicMock) -> None:
        from logly.integrations.graylog import GraylogSink

        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        sink = GraylogSink(protocol="udp")
        sink.write("test message\n")

        mock_sock.sendto.assert_called_once()

    def test_write_empty_message(self) -> None:
        from logly.integrations.graylog import GraylogSink

        with patch("logly.integrations.graylog.socket.socket") as mock_cls:
            mock_sock = MagicMock()
            mock_cls.return_value = mock_sock

            sink = GraylogSink(protocol="udp")
            sink.write("")
            mock_sock.sendto.assert_called_once()


class TestGraylogSinkFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.graylog import GraylogSink

        sink = GraylogSink()
        sink.flush()

    def test_close_clears_socket(self) -> None:
        from logly.integrations.graylog import GraylogSink

        sink = GraylogSink()
        mock_sock = MagicMock()
        sink._socket = mock_sock
        sink.close()
        mock_sock.close.assert_called_once()
        assert sink._socket is None

    def test_close_no_socket(self) -> None:
        from logly.integrations.graylog import GraylogSink

        sink = GraylogSink()
        sink.close()  # should not raise
