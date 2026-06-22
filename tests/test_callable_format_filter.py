"""Tests for callable format and filter on add()."""

from __future__ import annotations

from logly import Logger


def test_callable_format_receives_record() -> None:
    logger = Logger()
    messages: list[str] = []

    def my_format(record: dict) -> str:
        return f"{record['level']}:{record['message']}"

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format=my_format)
    logger.info("callable format")
    logger.remove(sink_id)
    assert "callable format" in messages[0]
    assert "INFO" in messages[0]


def test_callable_format_custom_output() -> None:
    logger = Logger()
    messages: list[str] = []

    def custom(record: dict) -> str:
        return f"CUSTOM|{record['message']}"

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format=custom)
    logger.info("custom output")
    logger.remove(sink_id)
    assert "CUSTOM|custom output" in messages[0]


def test_callable_filter_passes() -> None:
    logger = Logger()
    messages: list[str] = []

    def my_filter(record: dict) -> bool:
        return record["level"] == "INFO"

    sink_id = logger.add(
        lambda m: messages.append(m), level="DEBUG", format="{message}", filter=my_filter
    )
    logger.info("should pass")
    logger.error("should be filtered")
    logger.remove(sink_id)
    assert len(messages) == 1
    assert "should pass" in messages[0]


def test_callable_filter_blocks() -> None:
    logger = Logger()
    messages: list[str] = []

    def block_all(record: dict) -> bool:
        return False

    sink_id = logger.add(
        lambda m: messages.append(m), level="DEBUG", format="{message}", filter=block_all
    )
    logger.info("blocked")
    logger.remove(sink_id)
    assert len(messages) == 0


def test_callable_filter_blocks_all_levels() -> None:
    logger = Logger()
    messages: list[str] = []

    def only_warning(record: dict) -> bool:
        return record["level"] in ("WARNING", "ERROR")

    sink_id = logger.add(
        lambda m: messages.append(m), level="DEBUG", format="{message}", filter=only_warning
    )
    logger.info("info")
    logger.warning("warn")
    logger.error("err")
    logger.remove(sink_id)
    assert len(messages) == 2


def test_dict_filter_matches_extra() -> None:
    logger = Logger()
    messages: list[str] = []

    def patcher(record: dict) -> None:
        record.setdefault("extra", {})["service"] = "api"

    sink_id = logger.add(
        lambda m: messages.append(m),
        level="DEBUG",
        format="{message}",
        filter={"service": "api"},
        patch=patcher,
    )
    logger.info("api msg")
    logger.remove(sink_id)
    assert len(messages) == 1


def test_dict_filter_no_match() -> None:
    logger = Logger()
    messages: list[str] = []

    def patcher(record: dict) -> None:
        record.setdefault("extra", {})["service"] = "web"

    sink_id = logger.add(
        lambda m: messages.append(m),
        level="DEBUG",
        format="{message}",
        filter={"service": "api"},
        patch=patcher,
    )
    logger.info("web msg")
    logger.remove(sink_id)
    assert len(messages) == 0
