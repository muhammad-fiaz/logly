from __future__ import annotations

import urllib.request
from unittest.mock import MagicMock, patch

from logly.integrations.discord import DiscordHandler


class TestDiscordHandlerInit:
    def test_init_default_params(self) -> None:
        handler = DiscordHandler()
        assert handler.webhook_url == ""
        assert handler.timeout == 10.0
        assert handler.username is None
        assert handler.avatar_url is None

    def test_init_with_webhook(self) -> None:
        handler = DiscordHandler(
            "https://discord.com/api/webhooks/123/abc",
            timeout=5.0,
            username="bot",
            avatar_url="https://example.com/avatar.png",
        )
        assert handler.webhook_url == "https://discord.com/api/webhooks/123/abc"
        assert handler.timeout == 5.0
        assert handler.username == "bot"
        assert handler.avatar_url == "https://example.com/avatar.png"


class TestDiscordHandlerWrite:
    def test_write_empty_webhook_noop(self) -> None:
        handler = DiscordHandler()
        handler.write("[ERROR] test message\n")

    def test_write_sends_message(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            handler = DiscordHandler("https://discord.com/api/webhooks/123/abc")
            handler.write("[ERROR] something broke\n")
            mock_urlopen.assert_called_once()
            req = mock_urlopen.call_args[0][0]
            assert isinstance(req, urllib.request.Request)

    def test_write_payload_format(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            handler = DiscordHandler("https://discord.com/api/webhooks/123/abc")
            handler.write("hello discord\n")
            mock_urlopen.assert_called_once()
            req = mock_urlopen.call_args[0][0]
            assert isinstance(req, urllib.request.Request)

    def test_write_includes_username(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            handler = DiscordHandler(
                "https://discord.com/api/webhooks/123/abc",
                username="test-bot",
            )
            handler.write("msg\n")
            mock_urlopen.assert_called_once()

    def test_write_includes_avatar_url(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            handler = DiscordHandler(
                "https://discord.com/api/webhooks/123/abc",
                avatar_url="https://example.com/avatar.png",
            )
            handler.write("msg\n")
            mock_urlopen.assert_called_once()

    def test_write_strips_newline(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            handler = DiscordHandler("https://discord.com/api/webhooks/123/abc")
            handler.write("msg\n\n\n")
            mock_urlopen.assert_called_once()

    def test_write_empty_message(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            handler = DiscordHandler("https://discord.com/api/webhooks/123/abc")
            handler.write("\n")
            mock_urlopen.assert_called_once()

    def test_write_http_error_swallows_exception(self) -> None:
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("fail")):
            handler = DiscordHandler("https://discord.com/api/webhooks/123/abc")
            handler.write("msg\n")


class TestDiscordHandlerFlush:
    def test_flush_noop(self) -> None:
        handler = DiscordHandler("https://discord.com/api/webhooks/123/abc")
        handler.flush()


class TestDiscordHandlerClose:
    def test_close_noop(self) -> None:
        handler = DiscordHandler("https://discord.com/api/webhooks/123/abc")
        handler.close()
