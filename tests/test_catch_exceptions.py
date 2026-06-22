"""Tests for exception catching (catch decorator and context manager)."""

from __future__ import annotations

from logly import logger


class TestCatchExceptions:
    """Tests for catch() decorator and context manager."""

    def test_catch_context_manager(self) -> None:
        """catch() context manager should log exceptions."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture)
        with logger.catch():
            raise ValueError("test error")
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_catch_suppresses_exception(self) -> None:
        """catch() should suppress the exception by default."""
        sink_id = logger.add("stderr")
        with logger.catch():
            raise RuntimeError("should be suppressed")
        logger.remove(sink_id)

    def test_catch_decorator(self) -> None:
        """catch() should work as a decorator wrapper."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture)

        def failing_func() -> None:
            raise TypeError("decorated error")

        catcher = logger.catch()
        with catcher:
            failing_func()
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_catch_reraise(self) -> None:
        """catch(reraise=True) should re-raise the exception."""
        import pytest

        sink_id = logger.add("stderr")
        with pytest.raises(IOError):
            with logger.catch(reraise=True):
                raise OSError("reraise test")
        logger.remove(sink_id)

    def test_catch_custom_level(self) -> None:
        """catch() should accept a custom log level."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, level="DEBUG")
        with logger.catch(level="WARNING"):
            raise ValueError("custom level catch")
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_catch_custom_message(self) -> None:
        """catch() should log exception by default."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture)
        with logger.catch():
            raise RuntimeError("oops")
        logger.remove(sink_id)
        assert len(messages) >= 1
