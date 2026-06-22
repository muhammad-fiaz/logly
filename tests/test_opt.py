"""Tests for opt() per-call option overrides."""

from __future__ import annotations

from logly import logger


class TestOpt:
    """Tests for opt() method."""

    def test_opt_exception(self) -> None:
        """opt(exception=True) should capture exception info."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture)
        logger.opt(exception=True).info("with exception flag")
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_opt_lazy_evaluation(self) -> None:
        """opt(lazy=True) should defer callable evaluation."""
        call_count = 0

        def expensive() -> str:
            nonlocal call_count
            call_count += 1
            return "expensive result"

        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, level="WARNING")
        # This should NOT evaluate the callable because level is filtered
        logger.opt(lazy=True).info(expensive)
        logger.remove(sink_id)
        assert call_count == 0

    def test_opt_lazy_evaluation_when_emitted(self) -> None:
        """opt(lazy=True) should evaluate callables when emitted."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        def lazy_value() -> str:
            return "lazy result"

        sink_id = logger.add(capture)
        logger.opt(lazy=True).info("value: {}", lazy_value)
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "lazy result" in messages[0]
