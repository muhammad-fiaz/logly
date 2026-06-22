"""Tests for console sinks (stdout/stderr)."""

from __future__ import annotations

from logly import logger


class TestConsoleSink:
    """Tests for console/stdout/stderr sinks."""

    def test_add_stderr_sink(self) -> None:
        """Should be able to add a stderr sink."""
        sink_id = logger.add("stderr")
        assert isinstance(sink_id, int)
        logger.remove(sink_id)

    def test_add_stdout_sink(self) -> None:
        """Should be able to add a stdout sink."""
        sink_id = logger.add("stdout")
        assert isinstance(sink_id, int)
        logger.remove(sink_id)

    def test_console_sink_with_level_filter(self) -> None:
        """Console sink should respect level filtering."""
        sink_id = logger.add("stderr", level="WARNING")
        logger.info("this should be filtered")
        logger.warning("this should appear")
        logger.remove(sink_id)

    def test_console_sink_with_format(self) -> None:
        """Console sink should accept custom format strings."""
        sink_id = logger.add("stderr", format="{level}: {message}")
        logger.info("formatted message")
        logger.remove(sink_id)

    def test_console_sink_with_colorize(self) -> None:
        """Console sink should support colorization."""
        sink_id = logger.add("stderr", colorize=True)
        logger.info("colored message")
        logger.remove(sink_id)

    def test_console_sink_json_serialize(self) -> None:
        """Console sink should support JSON serialization."""
        sink_id = logger.add("stderr", serialize=True)
        logger.info("json message")
        logger.remove(sink_id)

    def test_remove_sink(self) -> None:
        """Removing a sink should work."""
        sink_id = logger.add("stderr")
        logger.remove(sink_id)

    def test_remove_all_sinks(self) -> None:
        """Removing all sinks should work."""
        logger.add("stderr")
        logger.add("stderr")
        logger.remove()

    def test_multiple_console_sinks(self) -> None:
        """Multiple console sinks should coexist."""
        id1 = logger.add("stderr")
        id2 = logger.add("stdout")
        logger.info("multi-sink message")
        logger.remove(id1)
        logger.remove(id2)
