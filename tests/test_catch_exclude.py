"""Tests for catch(exclude=...) behavior."""

from __future__ import annotations

import pytest

from logly import Logger


def test_exclude_specific_exception() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE", format="{message}")
    with pytest.raises(ValueError):
        with logger.catch(exclude=ValueError):
            raise ValueError("excluded")
    logger.remove(sink_id)
    assert len(messages) == 0


def test_exclude_tuple_of_exceptions() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE", format="{message}")
    with pytest.raises(TypeError):
        with logger.catch(exclude=(ValueError, TypeError)):
            raise TypeError("excluded")
    logger.remove(sink_id)
    assert len(messages) == 0


def test_catches_non_excluded() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE", format="{message}")
    with logger.catch(exclude=ValueError):
        raise RuntimeError("caught")
    logger.remove(sink_id)
    assert len(messages) == 1
    assert "caught" in messages[0]


def test_exclude_with_decorator() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE", format="{message}")

    @logger.catch(exclude=ValueError)
    def failing() -> None:
        raise ValueError("excluded")

    with pytest.raises(ValueError):
        failing()
    logger.remove(sink_id)
    assert len(messages) == 0


def test_exclude_none_catches_all() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE", format="{message}")
    with logger.catch(exclude=None):
        raise ValueError("caught all")
    logger.remove(sink_id)
    assert len(messages) == 1


def test_exclude_does_not_affect_other_exceptions() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE", format="{message}")
    with logger.catch(exclude=IOError):
        raise KeyError("caught")
    logger.remove(sink_id)
    assert len(messages) == 1
