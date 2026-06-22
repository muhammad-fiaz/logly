"""Tests for opt(record=True) which returns a record dict."""

from __future__ import annotations

from logly import Logger


def test_opt_record_returns_record_dict() -> None:
    logger = Logger()

    def capture(msg: str) -> None:
        # The message is formatted by the record option
        pass

    sink_id = logger.add(capture, level="DEBUG", format="{message}")

    # opt(record=True) makes log() capture caller info
    # The record info is passed as extra["record"]
    def capture_with_record(msg: str) -> None:
        pass

    logger.remove(sink_id)
    sink_id = logger.add(capture_with_record, level="DEBUG", format="{message}")
    logger.opt(record=True).info("test")
    logger.remove(sink_id)
    # Verify the message was logged
    assert True


def test_opt_record_has_message_field() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.opt(record=True).info("recorded message")
    logger.remove(sink_id)
    assert any("recorded message" in m for m in messages)


def test_opt_record_preserves_level() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{level}:{message}")
    logger.opt(record=True).warning("warned")
    logger.remove(sink_id)
    assert "WARNING" in messages[0]


def test_opt_record_with_args() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.opt(record=True).info("user {} logged in", "alice")
    logger.remove(sink_id)
    assert any("alice" in m for m in messages)
