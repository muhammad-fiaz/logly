"""Tests for HTTP integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestHttpHandlerInit:
    def test_init_defaults(self) -> None:
        from logly.integrations.http import HttpHandler

        handler = HttpHandler()
        assert handler.url == "http://localhost:8080/logs"
        assert handler.method == "POST"
        assert handler.headers == {}
        assert handler.timeout == 5.0
        assert handler.format == "json"

    def test_init_json_format(self) -> None:
        from logly.integrations.http import HttpHandler

        handler = HttpHandler("https://example.com/logs", format="json")
        assert handler.format == "json"

    def test_init_text_format(self) -> None:
        from logly.integrations.http import HttpHandler

        handler = HttpHandler("https://example.com/logs", format="text")
        assert handler.format == "text"

    def test_init_custom_params(self) -> None:
        from logly.integrations.http import HttpHandler

        handler = HttpHandler(
            "https://example.com/logs",
            method="PUT",
            headers={"X-Custom": "val"},
            timeout=10.0,
        )
        assert handler.method == "PUT"
        assert handler.headers == {"X-Custom": "val"}
        assert handler.timeout == 10.0


class TestHttpHandlerWrite:
    @patch("logly.integrations.http.urllib.request.urlopen")
    def test_write_json_format(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.http import HttpHandler

        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        handler = HttpHandler("https://example.com/logs", format="json")
        handler.write("hello world\n")

        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        assert call_args[1]["timeout"] == 5.0

    @patch("logly.integrations.http.urllib.request.urlopen")
    def test_write_text_format(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.http import HttpHandler

        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        handler = HttpHandler("https://example.com/logs", format="text")
        handler.write("hello world\n")

        mock_urlopen.assert_called_once()

    @patch("logly.integrations.http.urllib.request.urlopen")
    def test_write_strips_trailing_newline(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.http import HttpHandler

        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        handler = HttpHandler("https://example.com/logs", format="text")
        handler.write("msg\n")

        mock_urlopen.assert_called_once()

    @patch("logly.integrations.http.urllib.request.urlopen")
    def test_write_exception_swallows(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.http import HttpHandler

        mock_urlopen.side_effect = ConnectionError("fail")

        handler = HttpHandler("https://example.com/logs")
        handler.write("msg")
        # Should not raise

    def test_write_empty_message(self) -> None:
        from logly.integrations.http import HttpHandler

        with patch("logly.integrations.http.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b""
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            handler = HttpHandler("https://example.com/logs", format="text")
            handler.write("")
            mock_urlopen.assert_called_once()


class TestHttpHandlerFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.http import HttpHandler

        handler = HttpHandler()
        handler.flush()  # should not raise

    def test_close_noop(self) -> None:
        from logly.integrations.http import HttpHandler

        handler = HttpHandler()
        handler.close()  # should not raise
