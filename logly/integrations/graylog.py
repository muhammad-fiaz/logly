"""Graylog GELF integration for Logly.

Provides ``GraylogSink`` that sends log entries in GELF format to
Graylog over TCP or UDP.

No extra dependencies required - uses only the Python standard library.

Install with::

    # Option 1: uv (recommended)
    uv add logly[graylog]

    # Option 2: pip
    pip install "logly[graylog]"

    # Option 3: uv without extras
    uv add graylog

    # Option 4: pip without extras
    pip install graylog
"""

from __future__ import annotations

import json
import platform
import random
import socket
import struct
import time
import zlib
from typing import Any

_IMPORT_MSG = (
    "No extra dependencies required for Logly Graylog integration.\n"
    "Uses only Python standard library modules (socket, json, zlib).\n"
    "Install with one of:\n"
    "  uv add logly       # recommended\n"
    "  pip install logly"
)

_GELF_LEVEL_MAP: dict[str, int] = {
    "TRACE": 7,
    "DEBUG": 7,
    "INFO": 6,
    "NOTICE": 6,
    "SUCCESS": 6,
    "WARNING": 4,
    "ERROR": 3,
    "FAIL": 3,
    "CRITICAL": 2,
    "FATAL": 2,
    "AUDIT": 6,
}


class GraylogSink:
    """Send log entries in GELF format to a Graylog server.

    Formats log entries as GELF (Graylog Extended Log Format) and sends
    them over TCP or UDP. Supports GELF 1.0 and 1.1.

    Usage::

        from logly import logger
        from logly.integrations.graylog import GraylogSink

        logger.add(
            GraylogSink(
                host="localhost",
                port=12201,
                protocol="udp",
                graylog_version="1.1",
            ),
            level="INFO",
        )

    Args:
        host: Graylog server hostname or IP.
        port: Graylog server port.
        protocol: Transport protocol (``"tcp"`` or ``"udp"``).
        graylog_version: GELF version (``"1.0"`` or ``"1.1"``).
        chunk_size: Maximum chunk size in bytes for UDP (default 8192).
        facility: Optional facility name for the GELF message.
        hostname: Override hostname field (defaults to system hostname).
        timeout: Socket timeout in seconds.

    Raises:
        ValueError: If an unsupported protocol or GELF version is specified.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 12201,
        *,
        protocol: str = "udp",
        graylog_version: str = "1.1",
        chunk_size: int = 8192,
        facility: str | None = None,
        hostname: str | None = None,
        timeout: float = 5.0,
    ) -> None:
        """Initialize the Graylog sink.

        Args:
            host: Graylog server hostname or IP.
            port: Graylog server port.
            protocol: Transport protocol (``"tcp"`` or ``"udp"``).
            graylog_version: GELF version (``"1.0"`` or ``"1.1"``).
            chunk_size: Maximum chunk size for UDP.
            facility: Optional facility name.
            hostname: Override hostname.
            timeout: Socket timeout in seconds.

        Raises:
            ValueError: If an unsupported protocol or GELF version is specified.
        """
        if protocol not in ("tcp", "udp"):
            raise ValueError(f"Unsupported protocol: {protocol!r}, use 'tcp' or 'udp'")
        if graylog_version not in ("1.0", "1.1"):
            raise ValueError(f"Unsupported GELF version: {graylog_version!r}")

        self.host = host
        self.port = port
        self.protocol = protocol
        self.graylog_version = graylog_version
        self.chunk_size = chunk_size
        self.facility = facility
        self.hostname_override = hostname
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
        """Send one log entry as GELF to Graylog.

        Args:
            message: The formatted log message to send.
        """
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        hostname = self.hostname_override or platform.node()
        gelf_level = _GELF_LEVEL_MAP.get(self._detect_level(msg), 6)

        event: dict[str, Any] = {
            "version": self.graylog_version,
            "host": hostname,
            "short_message": msg,
            "level": gelf_level,
            "timestamp": time.time(),
        }

        if self.facility:
            event["facility"] = self.facility

        payload = json.dumps(event, default=str).encode("utf-8")

        # Compress for GELF 1.1 unless message is too small
        if self.graylog_version == "1.1" and len(payload) > 100:
            compressed = zlib.compress(payload)
            if len(compressed) < len(payload):
                payload = compressed

        try:
            if self.protocol == "udp" and len(payload) > self.chunk_size:
                self._send_chunked(payload)
            else:
                sock = self._get_socket()
                if self.protocol == "tcp":
                    sock.sendall(payload)
                else:
                    sock.sendto(payload, (self.host, self.port))
        except Exception:
            self._socket = None

    def _send_chunked(self, data: bytes) -> None:
        """Send data as GELF chunks over UDP.

        GELF chunked messages use a 12-byte header followed by the chunk.

        Args:
            data: The complete GELF message bytes.
        """
        sock = self._get_socket()
        message_id = random.getrandbits(64)
        num_chunks = (len(data) + self.chunk_size - 1) // self.chunk_size

        for i in range(num_chunks):
            chunk = data[i * self.chunk_size : (i + 1) * self.chunk_size]
            header = struct.pack(">QBB", message_id, i, num_chunks)
            sock.sendto(header + chunk, (self.host, self.port))

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
        """Flush pending data (no-op for Graylog handler)."""

    def close(self) -> None:
        """Close the socket connection."""
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
