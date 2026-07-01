"""Tests for ANSI color output."""

from __future__ import annotations

from logly import Logger, logger


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


def test_custom_level_rgb_color_output() -> None:
    messages: list[str] = []
    local_logger = Logger()

    local_logger.level("ORANGE_RGB", no=33, color="rgb(255, 128, 0)")
    sink_id = local_logger.add(
        messages.append, level="TRACE", colorize=True, format="{level}:{message}"
    )
    local_logger.log("ORANGE_RGB", "custom color")
    local_logger.remove(sink_id)

    assert messages
    assert "\x1b[38;2;255;128;0m" in messages[0]


def test_custom_level_raw_ansi_color_output() -> None:
    messages: list[str] = []
    local_logger = Logger()

    local_logger.level("RAW_GREEN", no=34, color="1;32")
    sink_id = local_logger.add(
        messages.append, level="TRACE", colorize=True, format="{level}:{message}"
    )
    local_logger.log("RAW_GREEN", "custom ansi")
    local_logger.remove(sink_id)

    assert messages
    assert "\x1b[1;32m" in messages[0]
