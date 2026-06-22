"""Tests for opt(raw=True) raw mode."""

from __future__ import annotations

from logly import Logger


def test_raw_mode_bypasses_format() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{level}:{message}")
    logger.opt(raw=True).info("raw message")
    logger.remove(sink_id)
    assert len(messages) == 1
    # Raw mode should skip format template rendering
    assert "raw message" in messages[0]


def test_raw_mode_with_format_specifiers_ignored() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{level}:{message}")
    logger.opt(raw=True).info("user {} logged in {name}", "alice", name="bob")
    logger.remove(sink_id)
    assert len(messages) == 1
    # Raw mode should not substitute format specifiers
    assert "user {}" in messages[0]


def test_raw_mode_preserves_literal_text() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.opt(raw=True).info("{special} <tags> &amp;")
    logger.remove(sink_id)
    assert "{special}" in messages[0]
    assert "<tags>" in messages[0]


def test_raw_mode_with_empty_message() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.opt(raw=True).info("")
    logger.remove(sink_id)
    assert len(messages) == 1


def test_raw_mode_returns_logger_view() -> None:
    logger = Logger()
    raw_logger = logger.opt(raw=True)
    assert raw_logger is not logger
    assert raw_logger._options.raw is True
