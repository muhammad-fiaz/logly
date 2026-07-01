"""RabbitMQ integration for Logly.

Provides ``RabbitMQHandler`` that publishes log entries to RabbitMQ queues.

Requires ``pika``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[rabbitmq]

    # Option 2: pip
    pip install "logly[rabbitmq]"

    # Option 3: uv without extras
    uv add pika

    # Option 4: pip without extras
    pip install pika
"""

from __future__ import annotations

import importlib.util
import json
import time
from typing import Any

_IMPORT_MSG = (  # pragma: no cover
    "pika is required for Logly RabbitMQ integration.\n"
    "Install with one of:\n"
    "  uv add logly[rabbitmq]       # recommended\n"
    "  pip install logly[rabbitmq]\n"
    "  uv add pika\n"
    "  pip install pika"
)  # pragma: no cover


class RabbitMQHandler:
    """Publish log entries to a RabbitMQ queue.

    Usage::

        from logly import logger
        from logly.integrations.rabbitmq import RabbitMQHandler

        handler = RabbitMQHandler(
            "amqp://guest:guest@localhost:5672/",
            queue="app-logs",
        )
        logger.add(handler, level="WARNING")

    Args:
        url: RabbitMQ connection URL.
        queue: Queue name to publish messages to.
        exchange: Exchange name (empty string for default exchange).
        routing_key: Routing key for message routing.
        durable: Whether the queue/exchange should survive restarts.
        timeout: Connection timeout in seconds.
    """

    def __init__(
        self,
        url: str = "amqp://guest:guest@localhost:5672/",
        *,
        queue: str = "logly-logs",
        exchange: str = "",
        routing_key: str | None = None,
        durable: bool = True,
        timeout: float = 5.0,
    ) -> None:
        """Initialize the RabbitMQ handler.

        Args:
            url: RabbitMQ connection URL.
            queue: Queue name to publish messages to.
            exchange: Exchange name (empty string for default exchange).
            routing_key: Routing key for message routing.
            durable: Whether the queue/exchange should survive restarts.
            timeout: Connection timeout in seconds.

        Raises:
            ImportError: If ``pika`` is not installed.
        """
        if importlib.util.find_spec("pika") is None:  # pragma: no cover
            raise ImportError(_IMPORT_MSG)  # pragma: no cover

        self._url = url
        self._queue = queue
        self._exchange = exchange
        self._routing_key = routing_key or queue
        self._durable = durable
        self._timeout = timeout
        self._connection: Any = None
        self._channel: Any = None

    def _ensure_connection(self) -> Any:
        """Ensure a connection and channel exist."""
        if self._channel is not None and self._channel.is_open:
            return self._channel

        import pika as _pika  # noqa: PLC0415  # pragma: no cover

        params = _pika.URLParameters(self._url)
        params.socket_timeout = self._timeout
        self._connection = _pika.BlockingConnection(params)  # pragma: no cover
        self._channel = self._connection.channel()  # pragma: no cover
        self._channel.queue_declare(queue=self._queue, durable=self._durable)  # pragma: no cover
        return self._channel

    def write(self, message: str) -> None:
        """Publish one log message to RabbitMQ."""
        import pika as _pika  # noqa: PLC0415  # pragma: no cover

        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        try:
            channel = self._ensure_connection()
            payload = json.dumps(
                {
                    "message": strip_ansi(message.rstrip("\n")),
                    "timestamp": time.time(),
                }
            )
            channel.basic_publish(  # pragma: no cover
                exchange=self._exchange,
                routing_key=self._routing_key,
                body=payload.encode("utf-8"),
                properties=_pika.BasicProperties(
                    delivery_mode=2 if self._durable else 1,
                    content_type="application/json",
                ),
            )
        except Exception:
            self._channel = None
            self._connection = None

    def flush(self) -> None:
        """No-op for RabbitMQ handler."""

    def close(self) -> None:
        """Close the RabbitMQ connection."""
        try:
            if self._channel and self._channel.is_open:
                self._channel.close()  # pragma: no cover
            if self._connection and self._connection.is_open:
                self._connection.close()  # pragma: no cover
        except Exception:
            pass
        finally:
            self._channel = None
            self._connection = None
