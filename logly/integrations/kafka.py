"""Kafka integration for Logly.

Provides ``KafkaHandler`` that publishes log entries to Kafka topics.

Requires ``confluent-kafka``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[kafka]

    # Option 2: pip
    pip install "logly[kafka]"

    # Option 3: uv without extras
    uv add confluent-kafka

    # Option 4: pip without extras
    pip install confluent-kafka
"""

from __future__ import annotations

import importlib.util
import json
import time

_IMPORT_MSG = (  # pragma: no cover
    "confluent-kafka is required for Logly Kafka integration.\n"
    "Install with one of:\n"
    "  uv add logly[kafka]       # recommended\n"
    "  pip install logly[kafka]\n"
    "  uv add confluent-kafka\n"
    "  pip install confluent-kafka"
)  # pragma: no cover


class KafkaHandler:
    """Publish log entries to a Kafka topic.

    Usage::

        from logly import logger
        from logly.integrations.kafka import KafkaHandler

        handler = KafkaHandler(
            "localhost:9092",
            topic="app-logs",
            client_id="logly-producer",
        )
        logger.add(handler, level="WARNING")

    Args:
        bootstrap_servers: Comma-separated list of broker addresses.
        topic: Kafka topic to publish log messages to.
        client_id: Client identifier for the Kafka producer.
        acks: Acknowledgment mode (``"all"``, ``"1"``, ``"0"``).
        timeout: Delivery timeout in seconds.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        *,
        topic: str = "logly-logs",
        client_id: str = "logly-producer",
        acks: str = "1",
        timeout: float = 5.0,
    ) -> None:
        """Initialize the Kafka handler.

        Args:
            bootstrap_servers: Comma-separated list of broker addresses.
            topic: Kafka topic to publish log messages to.
            client_id: Client identifier for the Kafka producer.
            acks: Acknowledgment mode (``"all"``, ``"1"``, ``"0"``).
            timeout: Delivery timeout in seconds.

        Raises:
            ImportError: If ``confluent-kafka`` is not installed.
        """
        if importlib.util.find_spec("confluent_kafka") is None:  # pragma: no cover
            raise ImportError(_IMPORT_MSG)  # pragma: no cover

        from confluent_kafka import (
            Producer,  # type: ignore[import-untyped]  # noqa: PLC0415  # pragma: no cover
        )

        self._producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "client.id": client_id,
                "acks": acks,
                "message.timeout.ms": int(timeout * 1000),
            }
        )
        self.topic = topic

    def write(self, message: str) -> None:
        """Produce one log message to Kafka."""
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        payload = json.dumps(
            {
                "message": strip_ansi(message.rstrip("\n")),
                "timestamp": time.time(),
            }
        ).encode("utf-8")

        self._producer.produce(self.topic, value=payload)  # pragma: no cover
        self._producer.poll(0)  # pragma: no cover

    def flush(self) -> None:
        """Flush pending messages to Kafka."""
        self._producer.flush(timeout=5.0)  # pragma: no cover

    def close(self) -> None:
        """Flush and close the Kafka producer."""
        self._producer.flush(timeout=5.0)  # pragma: no cover
