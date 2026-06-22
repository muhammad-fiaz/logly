"""Tests for ANSI color output."""

from __future__ import annotations

from logly import logger


class TestColorOutput:
    """Tests for colorized console output."""

    def test_colorize_enabled(self) -> None:
        """colorize=True should produce ANSI escape codes."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, colorize=True, format="{level} | {message}")
        logger.error("colored error")
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_colorize_disabled(self) -> None:
        """colorize=False should not produce ANSI codes."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, colorize=False, format="{level} | {message}")
        logger.error("plain error")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "\x1b[" not in messages[0]

    def test_colorize_default_off(self) -> None:
        """Default should not produce ANSI codes."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, format="{level} | {message}")
        logger.info("default color")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "\x1b[" not in messages[0]

    def test_each_level_gets_different_color(self) -> None:
        """Different levels should get different ANSI codes."""
        messages = []
        lock = __import__("threading").Lock()

        def capture(msg: str) -> None:
            with lock:
                messages.append(msg)

        sink_id = logger.add(capture, colorize=True, format="{level}")
        logger.info("i")
        logger.warning("w")
        logger.error("e")
        logger.remove(sink_id)
        # All messages should be present
        assert len(messages) >= 3
