"""Tests for logger.exception() method."""

from __future__ import annotations

from logly import Logger


def test_exception_logs_error_level() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{level}:{message}")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("failed")
    logger.remove(sink_id)
    assert len(messages) == 1
    assert "ERROR" in messages[0]
    assert "failed" in messages[0]


def test_exception_includes_exception_text() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    try:
        raise TypeError("type error")
    except TypeError:
        logger.exception("type issue")
    logger.remove(sink_id)
    assert len(messages) == 1


def test_exception_without_active_exception() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.exception("no exception active")
    logger.remove(sink_id)
    assert len(messages) == 1
    assert "no exception active" in messages[0]


def test_exception_with_format_args() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    try:
        raise RuntimeError("runtime err")
    except RuntimeError:
        logger.exception("error on item {}", 42)
    logger.remove(sink_id)
    assert len(messages) == 1
    assert "42" in messages[0]


def test_exception_with_kwargs() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    try:
        raise OSError("io err")
    except OSError:
        logger.exception("error for {user}", user="alice")
    logger.remove(sink_id)
    assert "alice" in messages[0]


def test_exception_on_opt_directly() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    try:
        raise RuntimeError("opt exception")
    except RuntimeError as exc:
        logger.opt(exception=exc).error("opt error")
    logger.remove(sink_id)
    assert len(messages) == 1
    assert "opt error" in messages[0]
