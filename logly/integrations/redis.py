"""Redis integration for Logly.

Provides ``RedisHandler`` that pushes log entries to Redis lists or streams.

Requires ``redis``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[redis]

    # Option 2: pip
    pip install "logly[redis]"

    # Option 3: uv without extras
    uv add redis

    # Option 4: pip without extras
    pip install redis
"""

from __future__ import annotations

import importlib.util
import json
import time
from typing import Literal

_IMPORT_MSG = (
    "redis is required for Logly Redis integration.\n"
    "Install with one of:\n"
    "  uv add logly[redis]       # recommended\n"
    "  pip install logly[redis]\n"
    "  uv add redis\n"
    "  pip install redis"
)


class RedisHandler:
    """Push log entries to Redis lists or streams.

    Usage::

        from logly import logger
        from logly.integrations.redis import RedisHandler

        handler = RedisHandler(
            "redis://localhost:6379/0",
            key="app:logs",
            mode="list",
        )
        logger.add(handler, level="WARNING")

    Args:
        url: Redis connection URL.
        key: Redis key for log storage.
        mode: Storage mode - ``"list"`` (LPUSH) or ``"stream"`` (XADD).
        timeout: Socket timeout in seconds.
        max_stream_len: Maximum stream length when using stream mode.
    """

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        *,
        key: str = "logly:logs",
        mode: Literal["list", "stream"] = "list",
        timeout: float = 5.0,
        max_stream_len: int = 10000,
    ) -> None:
        """Initialize the Redis handler.

        Args:
            url: Redis connection URL.
            key: Redis key for log storage.
            mode: Storage mode - ``"list"`` (LPUSH) or ``"stream"`` (XADD).
            timeout: Socket timeout in seconds.
            max_stream_len: Maximum stream length when using stream mode.

        Raises:
            ImportError: If ``redis`` is not installed.
        """
        if importlib.util.find_spec("redis") is None:
            raise ImportError(_IMPORT_MSG)

        redis_mod = importlib.import_module("redis")

        self._client = redis_mod.Redis.fromurl(
            url,
            socket_timeout=timeout,
            decode_responses=True,
        )
        self.key = key
        self.mode = mode
        self.max_stream_len = max_stream_len

    def write(self, message: str) -> None:
        """Push one log entry to Redis."""
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        entry = json.dumps(
            {
                "message": strip_ansi(message.rstrip("\n")),
                "timestamp": time.time(),
            }
        )

        if self.mode == "stream":
            self._client.xadd(
                self.key,
                {"message": entry},
                maxlen=self.max_stream_len,
            )
        else:
            self._client.lpush(self.key, entry)
            self._client.ltrim(self.key, 0, self.max_stream_len - 1)

    def flush(self) -> None:
        """No-op for Redis handler."""

    def close(self) -> None:
        """Close the Redis connection."""
        self._client.close()
