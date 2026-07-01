"""Logstash integration for Logly.

Provides ``LogstashSink`` that sends log entries as JSON to Logstash
over TCP or UDP.

No extra dependencies required - uses only the Python standard library.

Install with::

    # Option 1: uv (recommended)
    uv add logly[logstash]

    # Option 2: pip
    pip install "logly[logstash]"

    # Option 3: uv without extras
    uv add logstash

    # Option 4: pip without extras
    pip install logstash
"""

from __future__ import annotations

import json
import socket
import time
from typing import Any

_IMPORT_MSG = (
    "No extra dependencies required for Logly Logstash integration.\n"
    "Uses only Python standard library modules (socket, json).\n"
    "Install with one of:\n"
    "  uv add logly       # recommended\n"
    "  pip install logly"
)


class LogstashSink:
    """Send log entries as JSON to a Logstash instance.

    Formats log entries as JSON in the Logstash event format and sends
    them over TCP or UDP.

    Usage::

        from logly import logger
        from logly.integrations.logstash import LogstashSink

        logger.add(
            LogstashSink(
                host="localhost",
                port=5959,
                protocol="tcp",
                message_type="logstash",
                tags=["app", "production"],
            ),
            level="INFO",
        )

    Args:
        host: Logstash server hostname or IP.
        port: Logstash server port.
        protocol: Transport protocol (``"tcp"`` or ``"udp"``).
        message_type: Logstash message type field.
        tags: Optional list of tags to add to each event.
        key_prefix: Optional prefix for all field names.
        timeout: Socket timeout in seconds.

    Raises:
        ValueError: If an unsupported protocol is specified.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5959,
        *,
        protocol: str = "tcp",
        message_type: str = "logstash",
        tags: list[str] | None = None,
        key_prefix: str = "",
        timeout: float = 5.0,
    ) -> None:
        """Initialize the Logstash sink.

        Args:
            host: Logstash server hostname or IP.
            port: Logstash server port.
            protocol: Transport protocol (``"tcp"`` or ``"udp"``).
            message_type: Logstash message type field.
            tags: Optional list of tags.
            key_prefix: Optional prefix for field names.
            timeout: Socket timeout in seconds.

        Raises:
            ValueError: If an unsupported protocol is specified.
        """
        if protocol not in ("tcp", "udp"):
            raise ValueError(f"Unsupported protocol: {protocol!r}, use 'tcp' or 'udp'")

        self.host = host
        self.port = port
        self.protocol = protocol
        self.message_type = message_type
        self.tags = tags or []
        self.key_prefix = key_prefix
        self.timeout = timeout
        self._socket: socket.socket | None = None

    def _get_socket(self) -> socket.socket:
        """Get or create the socket connection.

        Returns:
            A connected socket instance.
        """
        if self._socket is None:
            sock_type = socket.SOCK_STREAM if self.protocol == "tcp" else socket.SOCK_DGRAM
            self._socket = socket.socket(socket.AF_INET, sock_type)
            self._socket.settimeout(self.timeout)
            if self.protocol == "tcp":
                self._socket.connect((self.host, self.port))
        return self._socket

    def write(self, message: str) -> None:
        """Send one log entry as JSON to Logstash.

        Args:
            message: The formatted log message to send.
        """
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        event: dict[str, Any] = {
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.", time.gmtime()) + "000Z",
            "@version": "1",
            "message": msg,
            "level": self._detect_level(msg),
        }

        if self.message_type:
            event["type"] = self.message_type

        if self.tags:
            event["tags"] = self.tags

        if self.key_prefix:
            prefixed: dict[str, Any] = {}
            for key, value in event.items():
                prefixed[f"{self.key_prefix}{key}"] = value
            event = prefixed

        payload = json.dumps(event, default=str)

        try:
            if self.protocol == "tcp":
                data = (payload + "\n").encode("utf-8")
                sock = self._get_socket()
                sock.sendall(data)
            else:
                data = payload.encode("utf-8")
                sock = self._get_socket()
                sock.sendto(data, (self.host, self.port))
        except Exception:
            self._socket = None

    @staticmethod
    def _detect_level(message: str) -> str:
        """Detect log level from message content.

        Args:
            message: The log message string.

        Returns:
            Level name string.
        """
        upper = message.upper()
        if "FATAL" in upper or "CRITICAL" in upper:
            return "CRITICAL"
        if "ERROR" in upper or "FAIL" in upper:
            return "ERROR"
        if "WARNING" in upper or "WARN" in upper:
            return "WARNING"
        if "NOTICE" in upper:
            return "NOTICE"
        if "SUCCESS" in upper:
            return "SUCCESS"
        if "DEBUG" in upper or "TRACE" in upper:
            return "DEBUG"
        return "INFO"

    def flush(self) -> None:
        """Flush pending data (no-op for Logstash handler)."""

    def close(self) -> None:
        """Close the socket connection."""
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
