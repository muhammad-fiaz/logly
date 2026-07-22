"""Tests for format template tokens: {time:...}, {level}, {extra[...]}."""

from __future__ import annotations

from typing import Any

from logly import logger


class TestTimeFormatToken:
    def test_time_format(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{time:YYYY-MM-DD} | {message}",
        )
        logger.info("hello")
        logger.remove(sink_id)
        assert len(messages) == 1
        assert "YYYY" not in messages[0]


class TestLevelToken:
    def test_level_token(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{level} | {message}",
        )
        logger.warning("warn test")
        logger.remove(sink_id)
        assert "WARNING" in messages[0]


class TestExtraToken:
    def test_extra_token(self) -> None:
        messages: list[str] = []

        def patcher(record: dict[str, Any]) -> None:
            record.setdefault("extra", {})["env"] = "prod"

        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message} | {extra[env]}",
            patch=patcher,
        )
        logger.info("env test")
        logger.remove(sink_id)
        assert "prod" in messages[0]

    def test_extra_dot_notation(self) -> None:
        messages: list[str] = []

        def patcher(record: dict[str, Any]) -> None:
            record.setdefault("extra", {})["region"] = "us-east-1"

        sink_id = logger.add(
            lambda m: messages.append(m),
            level="TRACE",
            format="{message} | {extra.region}",
            patch=patcher,
        )
        logger.info("region test")
        logger.remove(sink_id)
        assert "us-east-1" in messages[0]


class TestSourceTokens:
    def test_source_link_is_terminal_hyperlink(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(
            messages.append,
            level="TRACE",
            format="{source_link} | {message}",
        )
        logger.info("linked")
        logger.remove(sink_id)
        assert "\x1b]8;;file:///" in messages[0]
        assert "linked" in messages[0]

    def test_direct_log_captures_calling_source(self) -> None:
        records: list[dict[str, object]] = []
        sink_id = logger.add(
            lambda message: records.append({"message": message}),
            level="TRACE",
            format="{file}:{line} | {message}",
        )
        logger.log("INFO", "direct")
        logger.remove(sink_id)
        assert records[0]["message"]
        assert "logger.py" not in str(records[0]["message"])
