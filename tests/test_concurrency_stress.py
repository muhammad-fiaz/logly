"""Stress tests: threads, failing sinks, lifecycle idempotency."""

from __future__ import annotations

import threading

from logly import Logger


class TestConcurrencyStress:
    def test_many_threads_failing_sink_isolation(self) -> None:
        """One broken sink must not starve others under threaded load."""
        good: list[str] = []
        lock = threading.Lock()

        def capture(msg: str) -> None:
            with lock:
                good.append(msg)

        def broken(msg: str) -> None:
            raise RuntimeError("sink boom")

        local_logger = Logger()
        good_id = local_logger.add(capture)
        bad_id = local_logger.add(broken)
        barrier = threading.Barrier(8)

        def emit(n: int) -> None:
            barrier.wait()
            for i in range(50):
                local_logger.info(f"thread-{n} msg-{i}")

        threads = [threading.Thread(target=emit, args=(n,)) for n in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)

        local_logger.complete()
        local_logger.remove(bad_id)
        local_logger.remove(good_id)

        assert all(not thread.is_alive() for thread in threads)
        assert len(good) == 400

    def test_repeated_complete_is_safe_remove_missing_raises(self) -> None:
        """complete() is idempotent; removing an unknown sink raises."""
        import pytest

        local_logger = Logger()
        messages: list[str] = []
        sink_id = local_logger.add(messages.append)
        local_logger.info("hello")
        local_logger.complete()
        local_logger.complete()
        local_logger.remove(sink_id)
        with pytest.raises(RuntimeError):
            local_logger.remove(sink_id)
        local_logger.complete()
        assert len(messages) == 1
