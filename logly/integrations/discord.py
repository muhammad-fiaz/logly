"""Discord integration for Logly.

Provides ``DiscordHandler`` that sends log entries to Discord webhooks.

No extra dependencies required - uses ``urllib.request`` from the
Python standard library.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any


class DiscordHandler:
    """Send log entries to a Discord webhook.

    Usage::

        from logly import logger
        from logly.integrations.discord import DiscordHandler

        handler = DiscordHandler(
            "https://discord.com/api/webhooks/...",
            level="WARNING",
        )
        logger.add(handler, level="WARNING")

    Args:
        webhook_url: Discord webhook URL.
        timeout: HTTP request timeout in seconds.
        username: Override webhook username.
        avatar_url: Override webhook avatar URL.
    """

    def __init__(
        self,
        webhook_url: str = "",
        *,
        timeout: float = 10.0,
        username: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        """Initialize the Discord handler.

        Args:
            webhook_url: Discord webhook URL.
            timeout: HTTP request timeout in seconds.
            username: Override webhook username.
            avatar_url: Override webhook avatar URL.
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.username = username
        self.avatar_url = avatar_url

    def write(self, message: str) -> None:
        """Send one log message to Discord."""
        if not self.webhook_url:
            return

        payload: dict[str, Any] = {"content": message.rstrip("\n")}
        if self.username:
            payload["username"] = self.username
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response.read()
        except Exception:
            pass

    def flush(self) -> None:
        """No-op for Discord handler."""

    def close(self) -> None:
        """No-op for Discord handler."""
