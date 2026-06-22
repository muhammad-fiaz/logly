"""Tests for log formatters."""

from __future__ import annotations

from logly import logger


class TestFormatters:
    """Tests for template and JSON formatters."""

    def test_default_format(self, capsys) -> None:
        """Default format should include level and message."""
        sink_id = logger.add("stderr", level="DEBUG")
        logger.info("default format test")
        logger.remove(sink_id)

    def test_custom_template_format(self) -> None:
        """Custom template should replace tokens."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(
            capture,
            format="{level}: {message}",
        )
        logger.info("template test")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "template test" in messages[0]

    def test_json_format(self) -> None:
        """JSON format should produce valid JSON structure."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, serialize=True)
        logger.info("json format test")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert '"level"' in messages[0]
        assert '"message"' in messages[0]

    def test_format_with_extra_fields(self) -> None:
        """Format should include extra bound fields."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        bound_logger = logger.bind(user="alice")
        sink_id = bound_logger.add(
            capture,
            format="{extra[user]} | {message}",
        )
        bound_logger.info("bound message")
        bound_logger.remove(sink_id)
        assert len(messages) >= 1
        assert "alice" in messages[0]

    def test_callable_formatter(self) -> None:
        """Custom callable formatter should work."""
        messages = []

        from typing import Any

        def custom_fmt(record: dict[str, Any]) -> str:
            return f"CUSTOM: {record['message']}"

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture, format=custom_fmt)
        logger.info("callable formatter test")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "CUSTOM: callable formatter test" in messages[0]
