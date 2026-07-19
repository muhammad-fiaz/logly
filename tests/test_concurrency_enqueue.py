"""Tests for enqueue (background worker) mode."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from logly import Logger, logger


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

    def test_complete_does_not_spin_when_worker_drains_immediately(self) -> None:
        """complete() waits for queued work without busy-spinning."""
        messages: list[str] = []
        local_logger = Logger()
        sink_id = local_logger.add(messages.append, enqueue=True)
        for i in range(500):
            local_logger.info(f"queued {i}")

        start = time.monotonic()
        local_logger.complete()
        elapsed = time.monotonic() - start
        local_logger.remove(sink_id)

        assert len(messages) == 500
        assert elapsed < 3.0

    def test_python_object_sink_is_safe_under_parallel_logging(self) -> None:
        """Python sinks do not deadlock when writes release the GIL."""

        class ReleasingSink:
            def __init__(self) -> None:
                self.messages: list[str] = []
                self.lock = threading.Lock()

            def write(self, message: str) -> None:
                # sleep() releases the GIL and reproduces the contested path
                # that previously deadlocked with the dispatcher mutex held.
                time.sleep(0.0001)
                with self.lock:
                    self.messages.append(message)

            def flush(self) -> None:
                pass

        local_logger = Logger()
        sink = ReleasingSink()
        sink_id = local_logger.add(sink, serialize=True)
        start = threading.Barrier(8)

        def emit() -> None:
            start.wait()
            for _ in range(100):
                local_logger.info("parallel record")

        threads = [threading.Thread(target=emit) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        local_logger.complete()
        local_logger.remove(sink_id)

        assert all(not thread.is_alive() for thread in threads)
        assert len(sink.messages) == 800
