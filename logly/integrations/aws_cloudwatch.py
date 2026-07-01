"""AWS CloudWatch Logs integration for Logly.

Provides ``CloudWatchSink`` that sends log entries to AWS CloudWatch
Logs with batching and automatic flushing.

Requires ``boto3``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[aws]

    # Option 2: pip
    pip install "logly[aws]"

    # Option 3: uv without extras
    uv add boto3

    # Option 4: pip without extras
    pip install boto3
"""

from __future__ import annotations

import importlib.util
import threading
import time
from typing import Any

_IMPORT_MSG = (
    "boto3 is required for Logly AWS CloudWatch Logs integration.\n"
    "Install with one of:\n"
    "  uv add logly[aws]       # recommended\n"
    "  pip install logly[aws]\n"
    "  uv add boto3\n"
    "  pip install boto3"
)


class CloudWatchSink:
    """Send log entries to AWS CloudWatch Logs.

    Batches log events and flushes them to CloudWatch periodically or
    when the batch size is reached. Thread-safe.

    Usage::

        from logly import logger
        from logly.integrations.aws_cloudwatch import CloudWatchSink

        logger.add(
            CloudWatchSink(
                log_group="/app/production",
                log_stream="api-server",
                region="us-east-1",
                batch_size=10000,
                flush_interval=5.0,
            ),
            level="INFO",
        )

    Args:
        log_group: CloudWatch log group name.
        log_stream: CloudWatch log stream name.
        region: AWS region (defaults to boto3 configuration chain).
        aws_access_key_id: AWS access key (defaults to boto3 configuration chain).
        aws_secret_access_key: AWS secret key (defaults to boto3 configuration chain).
        batch_size: Maximum number of events per batch (max 10000).
        flush_interval: Seconds between automatic flushes.
        create_group: Whether to create the log group if it doesn't exist.
        create_stream: Whether to create the log stream if it doesn't exist.

    Raises:
        ImportError: If ``boto3`` is not installed.
    """

    def __init__(
        self,
        log_group: str = "",
        log_stream: str = "",
        *,
        region: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        batch_size: int = 10000,
        flush_interval: float = 5.0,
        create_group: bool = True,
        create_stream: bool = True,
    ) -> None:
        """Initialize the CloudWatch sink.

        Args:
            log_group: CloudWatch log group name.
            log_stream: CloudWatch log stream name.
            region: AWS region.
            aws_access_key_id: AWS access key.
            aws_secret_access_key: AWS secret key.
            batch_size: Maximum events per batch.
            flush_interval: Seconds between flushes.
            create_group: Whether to create the log group.
            create_stream: Whether to create the log stream.

        Raises:
            ImportError: If ``boto3`` is not installed.
        """
        if importlib.util.find_spec("boto3") is None:
            raise ImportError(_IMPORT_MSG)

        import boto3

        kwargs: dict[str, Any] = {}
        if region:
            kwargs["region_name"] = region
        if aws_access_key_id:
            kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            kwargs["aws_secret_access_key"] = aws_secret_access_key

        self._client: Any = boto3.client("logs", **kwargs)
        self.log_group = log_group
        self.log_stream = log_stream
        self.batch_size = min(batch_size, 10000)
        self.flush_interval = flush_interval
        self.create_group = create_group
        self.create_stream = create_stream

        self._buffer: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        self._sequence_token: str | None = None
        self._last_flush = time.monotonic()
        self._initialized = False

        # Start background flush thread
        self._stop_event = threading.Event()
        self._flush_thread = threading.Thread(
            target=self._flush_loop,
            daemon=True,
            name="logly-cloudwatch-flush",
        )
        self._flush_thread.start()

    def _ensure_stream(self) -> None:
        """Ensure the log group and stream exist."""
        if self._initialized:
            return

        if self.create_group:
            try:
                self._client.create_log_group(logGroupName=self.log_group)
            except self._client.exceptions.ResourceAlreadyExistsException:
                pass

        if self.create_stream:
            try:
                self._client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream,
                )
            except self._client.exceptions.ResourceAlreadyExistsException:
                pass

        self._initialized = True

    def _flush_loop(self) -> None:
        """Background thread that flushes the buffer periodically."""
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self.flush_interval)
            self.flush()

    def _do_flush(self) -> None:
        """Flush buffered events to CloudWatch."""
        with self._lock:
            if not self._buffer:
                return
            events = self._buffer[:]
            self._buffer.clear()

        self._ensure_stream()

        # CloudWatch put_log_events accepts max 10,000 events per call
        for i in range(0, len(events), 10000):
            batch = events[i : i + 10000]
            kwargs: dict[str, Any] = {
                "logGroupName": self.log_group,
                "logStreamName": self.log_stream,
                "logEvents": batch,
            }
            if self._sequence_token:
                kwargs["sequenceToken"] = self._sequence_token

            try:
                response = self._client.put_log_events(**kwargs)
                self._sequence_token = response.get("nextSequenceToken")
            except Exception:
                pass

    def write(self, message: str) -> None:
        """Add a log entry to the buffer.

        Args:
            message: The formatted log message to send.
        """
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        event: dict[str, Any] = {
            "timestamp": int(time.time() * 1000),  # CloudWatch uses milliseconds
            "message": strip_ansi(message.rstrip("\n")),
        }

        with self._lock:
            self._buffer.append(event)

        # Auto-flush if buffer is full
        if len(self._buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> None:
        """Flush buffered log entries to CloudWatch."""
        self._do_flush()

    def close(self) -> None:
        """Flush remaining events and shut down the handler."""
        self._stop_event.set()
        if self._flush_thread.is_alive():
            self._flush_thread.join(timeout=5.0)
        self.flush()
