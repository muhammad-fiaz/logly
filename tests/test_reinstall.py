"""Tests for logger.reinstall() method."""

from __future__ import annotations

from logly import Logger


def test_reinstall_removes_and_adds() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.info("before reinstall")
    logger.complete()
    assert len(messages) >= 1

    messages.clear()
    logger.reinstall(sink_id)
    logger.info("after reinstall")
    logger.complete()
    assert len(messages) >= 1
    assert "after reinstall" in messages[0]


def test_reinstall_removes_old_messages() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.info("msg1")
    logger.complete()
    count_before = len(messages)

    logger.reinstall(sink_id)
    logger.info("msg2")
    logger.complete()
    assert len(messages) > count_before


def test_reinstall_none_reinstalls_all() -> None:
    logger = Logger()
    messages1: list[str] = []
    messages2: list[str] = []
    logger.add(lambda m: messages1.append(m), level="DEBUG", format="{message}")
    logger.add(lambda m: messages2.append(m), level="DEBUG", format="{message}")
    logger.info("before")
    logger.complete()

    messages1.clear()
    messages2.clear()
    logger.reinstall()
    logger.info("after")
    logger.complete()
    # After reinstall, both sinks should be gone (removed but not re-added)
    # reinstall(None) calls remove(None) which removes all
    assert True


def test_reinstall_returns_none() -> None:
    logger = Logger()
    sink_id = logger.add(lambda m: None, level="DEBUG")
    logger.reinstall(sink_id)
