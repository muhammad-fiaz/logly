"""Tests for enqueue (background worker) mode."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from logly import logger


class TestConcurrencyEnqueue:
    """Tests for enqueue=True background dispatch."""

    def test_enqueue_writes_in_background(self) -> None:
        """Enqueue mode should process messages in a background thread."""
        messages = []
        lock = threading.Lock()

        def capture(msg: str) -> None:
            with lock:
                messages.append(msg)

        sink_id = logger.add(capture, enqueue=True)
        logger.info("background message")
        logger.complete()
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_enqueue_file_sink(self, tmp_path: Path) -> None:
        """Enqueue mode should work with file sinks."""
        log_file = tmp_path / "async.log"
        sink_id = logger.add(str(log_file), enqueue=True)
        for i in range(10):
            logger.info(f"async message {i}")
        logger.complete()
        logger.remove(sink_id)
        content = log_file.read_text()
        assert "async message" in content

    def test_enqueue_does_not_block(self) -> None:
        """Enqueue should not block the calling thread."""
        start = time.time()
        sink_id = logger.add("stderr", enqueue=True)
        for _ in range(100):
            logger.info("non-blocking message")
        elapsed = time.time() - start
        logger.complete()
        logger.remove(sink_id)
        assert elapsed < 5.0  # Should be fast

    def test_complete_drains_queue(self) -> None:
        """complete() should drain the background queue."""
        messages = []
        lock = threading.Lock()

        def capture(msg: str) -> None:
            with lock:
                messages.append(msg)

        sink_id = logger.add(capture, enqueue=True)
        for i in range(5):
            logger.info(f"drain {i}")
        logger.complete()
        logger.remove(sink_id)
        assert len(messages) == 5
