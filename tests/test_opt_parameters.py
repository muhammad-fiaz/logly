"""Tests for logger.opt() parameters: record, colors, depth, raw, lazy."""

from __future__ import annotations

from logly import logger


class TestOptRecord:
    def test_opt_record_parameter_accepted(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
        logger.opt(record=True).info("test")
        logger.remove(sink_id)
        assert len(messages) == 1


class TestOptDepth:
    def test_depth_skips_frames(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message} | {module}",
        )
        logger.opt(depth=1).info("depth test")
        logger.remove(sink_id)
        assert len(messages) == 1


class TestOptColors:
    def test_colors_markup(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message}",
        )
        logger.opt(colors=True).info("<red>colored</red>")
        logger.remove(sink_id)
        assert len(messages) == 1
        assert "colored" in messages[0]

    def test_italic_markup(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message}",
        )
        logger.opt(colors=True).info("<italic>italic text</italic>")
        logger.remove(sink_id)
        assert len(messages) == 1

    def test_strike_markup(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message}",
        )
        logger.opt(colors=True).info("<strike>struck text</strike>")
        logger.remove(sink_id)
        assert len(messages) == 1

    def test_reverse_markup(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message}",
        )
        logger.opt(colors=True).info("<reverse>reversed</reverse>")
        logger.remove(sink_id)
        assert len(messages) == 1

    def test_combined_markup(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message}",
        )
        logger.opt(colors=True).info("<bold><red>bold red</red></bold>")
        logger.remove(sink_id)
        assert len(messages) == 1
