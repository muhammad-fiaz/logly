"""Slack integration for Logly.

Provides ``SlackHandler`` that sends log entries to Slack webhooks.

No extra dependencies required - uses ``urllib.request`` from the
Python standard library.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any


class SlackHandler:
    """Send log entries to a Slack webhook.

    Usage::

        from logly import logger
        from logly.integrations.slack import SlackHandler

        handler = SlackHandler(
            "https://hooks.slack.com/services/...",
            channel="#logs",
            username="Logly Bot",
        )
        logger.add(handler, level="WARNING")

    Args:
        webhook_url: Slack incoming webhook URL.
        channel: Channel override for the webhook.
        username: Username override for the webhook.
        icon_emoji: Emoji override for the webhook icon.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        webhook_url: str = "",
        *,
        channel: str | None = None,
        username: str | None = None,
        icon_emoji: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize the Slack handler.

        Args:
            webhook_url: Slack incoming webhook URL.
            channel: Channel override for the webhook.
            username: Username override for the webhook.
            icon_emoji: Emoji override for the webhook icon.
            timeout: HTTP request timeout in seconds.
        """
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji
        self.timeout = timeout

    def write(self, message: str) -> None:
        """Send one log message to Slack."""
        if not self.webhook_url:
            return

        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        payload: dict[str, Any] = {
            "text": strip_ansi(message.rstrip("\n")),
        }
        if self.channel:
            payload["channel"] = self.channel
        if self.username:
            payload["username"] = self.username
        if self.icon_emoji:
            payload["icon_emoji"] = self.icon_emoji

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout
            ) as response:  # pragma: no cover
                response.read()
        except Exception:
            pass

    def flush(self) -> None:
        """No-op for Slack handler."""

    def close(self) -> None:
        """No-op for Slack handler."""
