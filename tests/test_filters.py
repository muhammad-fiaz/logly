"""Tests for log filters."""

from __future__ import annotations

from logly import logger


class TestFilters:
    """Tests for level and custom filters."""

    def test_level_filter(self) -> None:
        """Filter should reject records below the threshold."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, level="WARNING")
        logger.info("should be filtered")
        logger.warning("should pass")
        logger.remove(sink_id)
        assert len(messages) == 1
        assert "should pass" in messages[0]

    def test_prefix_filter(self) -> None:
        """Prefix filter should match logger name prefix."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, filter="myapp")
        my_logger = logger.bind()
        my_logger._name = "myapp.core"
        my_logger.info("prefix match")
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_callable_filter(self) -> None:
        """Custom callable filter should work."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        from typing import Any

        def my_filter(record: dict[str, Any]) -> bool:
            return "important" in str(record.get("message", ""))

        sink_id = logger.add(capture, filter=my_filter, level="TRACE")
        logger.info("not important")
        logger.info("very important message")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert any("important" in m for m in messages)

    def test_mapping_filter(self) -> None:
        """Mapping filter should match extra fields."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, filter={"env": "prod"})
        bound = logger.bind(env="prod")
        bound.info("production message")
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_all_levels_pass_with_trace(self) -> None:
        """TRACE level should pass all messages."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, level="TRACE")
        logger.trace("trace msg")
        logger.debug("debug msg")
        logger.info("info msg")
        logger.remove(sink_id)
        assert len(messages) == 3
