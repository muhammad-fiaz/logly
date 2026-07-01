"""Tests for Slack integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestSlackHandlerInit:
    def test_init_defaults(self) -> None:
        from logly.integrations.slack import SlackHandler

        handler = SlackHandler()
        assert handler.webhook_url == ""
        assert handler.channel is None
        assert handler.username is None
        assert handler.icon_emoji is None
        assert handler.timeout == 10.0

    def test_init_custom_params(self) -> None:
        from logly.integrations.slack import SlackHandler

        handler = SlackHandler(
            "https://hooks.slack.com/services/xxx",
            channel="#logs",
            username="Bot",
            icon_emoji=":robot_face:",
            timeout=5.0,
        )
        assert handler.webhook_url == "https://hooks.slack.com/services/xxx"
        assert handler.channel == "#logs"
        assert handler.username == "Bot"
        assert handler.icon_emoji == ":robot_face:"
        assert handler.timeout == 5.0


class TestSlackHandlerWrite:
    def test_write_empty_webhook_noop(self) -> None:
        from logly.integrations.slack import SlackHandler

        handler = SlackHandler(webhook_url="")
        handler.write("should not send")
        # No exception, no network call

    @patch("logly.integrations.slack.urllib.request.urlopen")
    def test_write_sends_payload(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.slack import SlackHandler

        mock_response = MagicMock()
        mock_response.read.return_value = b"ok"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        handler = SlackHandler("https://hooks.slack.com/services/xxx")
        handler.write("test message\n")

        mock_urlopen.assert_called_once()

    @patch("logly.integrations.slack.urllib.request.urlopen")
    def test_write_includes_channel(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.slack import SlackHandler

        mock_response = MagicMock()
        mock_response.read.return_value = b"ok"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        handler = SlackHandler("https://hooks.slack.com/services/xxx", channel="#dev")
        handler.write("msg")
        mock_urlopen.assert_called_once()

    @patch("logly.integrations.slack.urllib.request.urlopen")
    def test_write_exception_swallows(self, mock_urlopen: MagicMock) -> None:
        from logly.integrations.slack import SlackHandler

        mock_urlopen.side_effect = ConnectionError("fail")
        handler = SlackHandler("https://hooks.slack.com/services/xxx")
        handler.write("msg")
        # Should not raise

    def test_write_empty_message(self) -> None:
        from logly.integrations.slack import SlackHandler

        with patch("logly.integrations.slack.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b""
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            handler = SlackHandler("https://hooks.slack.com/services/xxx")
            handler.write("")
            mock_urlopen.assert_called_once()


class TestSlackHandlerFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.slack import SlackHandler

        handler = SlackHandler()
        handler.flush()

    def test_close_noop(self) -> None:
        from logly.integrations.slack import SlackHandler

        handler = SlackHandler()
        handler.close()
