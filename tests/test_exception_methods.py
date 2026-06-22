"""Tests for logger.exception(), logger.warn() alias, and catch(exclude=...)."""

from __future__ import annotations

import pytest

from logly import logger


class TestExceptionMethod:
    def test_exception_logs_at_error(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
        try:
            raise ValueError("test error")
        except ValueError:
            logger.exception("Something failed")
        logger.remove(sink_id)
        assert len(messages) == 1
        assert "Something failed" in messages[0]

    def test_exception_without_active_exception(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
        logger.exception("No active exception")
        logger.remove(sink_id)
        assert len(messages) == 1

    def test_exception_with_args(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            logger.exception("Error on {}", "item_42")
        logger.remove(sink_id)
        assert len(messages) == 1
        assert "item_42" in messages[0]


class TestWarnAlias:
    def test_warn_aliases_warning(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
        logger.warn("test warning")
        logger.remove(sink_id)
        assert len(messages) == 1

    def test_warn_with_args(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
        logger.warn("Value is {}", 42)
        logger.remove(sink_id)
        assert len(messages) == 1
        assert "42" in messages[0]


class TestCatchExclude:
    def test_exclude_specific_exception(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")

        try:
            with pytest.raises(ValueError):
                with logger.catch(exclude=ValueError):
                    raise ValueError("excluded")
        finally:
            logger.remove(sink_id)
        assert len(messages) == 0

    def test_exclude_tuple_of_exceptions(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")

        try:
            with pytest.raises(ValueError):
                with logger.catch(exclude=(ValueError, TypeError)):
                    raise ValueError("excluded")
        finally:
            logger.remove(sink_id)
        assert len(messages) == 0

    def test_catches_non_excluded(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")

        with logger.catch(exclude=ValueError):
            raise RuntimeError("caught")

        logger.remove(sink_id)
        assert len(messages) == 1

    def test_exclude_with_decorator(self) -> None:
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="TRACE")

        @logger.catch(exclude=ValueError)
        def my_func() -> None:
            raise ValueError("excluded")

        try:
            with pytest.raises(ValueError):
                my_func()
        finally:
            logger.remove(sink_id)
        assert len(messages) == 0
