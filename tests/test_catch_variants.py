"""Tests for catch() message customization and async/generator support."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest

from logly import Logger


async def _failing_agen() -> AsyncGenerator[int, None]:
    yield 1
    raise ValueError("async interrupted")


def _capture() -> tuple[Logger, list[str], int]:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    return logger, messages, sink_id


class TestCustomMessage:
    def test_default_message_preserved(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            with logger.catch():
                raise ValueError("boom")
        finally:
            logger.remove(sink_id)
        assert len(messages) == 1
        assert "An error has been caught" in messages[0]
        assert "ValueError: boom" in messages[0]

    def test_custom_message(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            with logger.catch(message="payment failed"):
                raise ValueError("card declined")
        finally:
            logger.remove(sink_id)
        assert len(messages) == 1
        assert "payment failed" in messages[0]
        assert "ValueError: card declined" in messages[0]

    def test_custom_message_decorator(self) -> None:
        logger, messages, sink_id = _capture()

        @logger.catch(message="job failed")
        def run() -> None:
            raise RuntimeError("worker blew up")

        try:
            run()
        finally:
            logger.remove(sink_id)
        assert "job failed" in messages[0]
        assert "RuntimeError: worker blew up" in messages[0]


class TestAsyncContextManager:
    def test_async_with(self) -> None:
        async def scenario() -> None:
            logger, messages, sink_id = _capture()
            try:
                async with logger.catch():
                    raise ValueError("async boom")
            finally:
                logger.remove(sink_id)
            assert "ValueError: async boom" in messages[0]

        asyncio.run(scenario())

    def test_async_with_reraise(self) -> None:
        async def scenario() -> None:
            logger, messages, sink_id = _capture()
            try:
                with pytest.raises(KeyError):
                    async with logger.catch(reraise=True):
                        raise KeyError("missing")
            finally:
                logger.remove(sink_id)
            assert "KeyError: 'missing'" in messages[0]

        asyncio.run(scenario())


class TestAsyncDecorator:
    def test_async_function_caught(self) -> None:
        logger, messages, sink_id = _capture()

        @logger.catch()
        async def fetch() -> str:
            raise ValueError("network down")

        async def scenario() -> None:
            result = await fetch()
            assert result is None

        try:
            asyncio.run(scenario())
        finally:
            logger.remove(sink_id)
        assert "ValueError: network down" in messages[0]

    def test_async_function_reraise(self) -> None:
        logger, messages, sink_id = _capture()

        @logger.catch(reraise=True)
        async def fetch() -> str:
            raise ValueError("network down")

        async def scenario() -> None:
            with pytest.raises(ValueError):
                await fetch()

        try:
            asyncio.run(scenario())
        finally:
            logger.remove(sink_id)
        assert "ValueError: network down" in messages[0]

    def test_async_function_exclude(self) -> None:
        logger, messages, sink_id = _capture()

        @logger.catch(exclude=(ValueError,))
        async def fetch() -> str:
            raise ValueError("let through")

        async def scenario() -> None:
            with pytest.raises(ValueError, match="let through"):
                await fetch()

        try:
            asyncio.run(scenario())
        finally:
            logger.remove(sink_id)
        assert messages == []


class TestGeneratorDecorator:
    def test_generator_catches_during_iteration(self) -> None:
        logger, messages, sink_id = _capture()

        @logger.catch()
        def stream() -> Generator[int, None, None]:
            yield 1
            raise ValueError("interrupted")

        try:
            assert list(stream()) == [1]
        finally:
            logger.remove(sink_id)
        assert "ValueError: interrupted" in messages[0]

    def test_generator_reraise(self) -> None:
        logger, messages, sink_id = _capture()

        @logger.catch(reraise=True)
        def stream() -> Generator[int, None, None]:
            yield 1
            raise ValueError("interrupted")

        try:
            with pytest.raises(ValueError, match="interrupted"):
                list(stream())
        finally:
            logger.remove(sink_id)
        assert "ValueError: interrupted" in messages[0]

    def test_async_generator(self) -> None:
        logger, messages, sink_id = _capture()
        decorated = logger.catch()(_failing_agen)

        async def scenario() -> list[int]:
            return [item async for item in decorated()]

        try:
            assert asyncio.run(scenario()) == [1]
        finally:
            logger.remove(sink_id)
        assert "ValueError: async interrupted" in messages[0]

    def test_async_generator_reraise(self) -> None:
        logger, messages, sink_id = _capture()
        decorated = logger.catch(reraise=True)(_failing_agen)

        async def scenario() -> list[int]:
            return [item async for item in decorated()]

        try:
            with pytest.raises(ValueError, match="async interrupted"):
                asyncio.run(scenario())
        finally:
            logger.remove(sink_id)
        assert "ValueError: async interrupted" in messages[0]
