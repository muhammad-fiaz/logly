"""Tests for custom level registration and usage."""

from __future__ import annotations

from logly import logger
from logly._logly import inspect_level, register_custom_level


class TestCustomLevels:
    """Tests for custom level functionality."""

    def test_register_and_use_custom_level(self) -> None:
        """Should register a custom level and log at it."""
        register_custom_level("SECURITY", 65, "bold_red")
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, level="TRACE")
        logger.log("SECURITY", "security event")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "security event" in messages[0]

    def test_custom_level_priority_ordering(self) -> None:
        """Custom level priority should determine ordering."""
        name, pri, _ = inspect_level("WARNING")
        assert name == "WARNING"
        assert pri == 40

    def test_custom_level_with_color(self) -> None:
        """Custom level should accept a color."""
        register_custom_level("AUDIT_LEVEL", 36, "magenta")
        name, _, color = inspect_level("AUDIT_LEVEL")
        assert name == "AUDIT_LEVEL"
        assert color == "magenta"

    def test_log_at_numeric_priority(self) -> None:
        """Should be able to log using a numeric priority."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, level="TRACE")
        logger.log(25, "numeric level")
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_level_method_register_and_inspect(self) -> None:
        """logger.level() should register and inspect levels."""
        name, pri, color = logger.level("MY_CUSTOM", no=42, color="blue")
        assert name == "MY_CUSTOM"
        assert pri == 42
