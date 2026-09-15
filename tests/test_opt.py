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

    def test_opt_diagnose_includes_frame_locals(self) -> None:
        """opt(diagnose=True) should append frame local variables."""
        from logly import Logger

        local_logger = Logger()
        messages: list[str] = []
        sink_id = local_logger.add(
            lambda m: messages.append(m), level="DEBUG", format="{level}:{message}"
        )
        try:
            secret_token = "tok-12345"  # noqa: F841
            _ = 1 / 0
        except ZeroDivisionError:
            local_logger.opt(exception=True, diagnose=True).error("diagnosed")
        local_logger.remove(sink_id)
        assert len(messages) == 1
        assert "ZeroDivisionError" in messages[0]
        assert "Diagnostic context" in messages[0]
        assert "secret_token" in messages[0]
        assert "tok-12345" in messages[0]

    def test_opt_diagnose_false_omits_locals(self) -> None:
        """Without diagnose, frame locals must not be attached."""
        from logly import Logger

        local_logger = Logger()
        messages: list[str] = []
        sink_id = local_logger.add(
            lambda m: messages.append(m), level="DEBUG", format="{level}:{message}"
        )
        try:
            secret_token = "tok-12345"  # noqa: F841
            _ = 1 / 0
        except ZeroDivisionError:
            local_logger.opt(exception=True).error("plain")
        local_logger.remove(sink_id)
        assert len(messages) == 1
        assert "Diagnostic context" not in messages[0]
        assert "tok-12345" not in messages[0]
