"""Tests for async sink via logger.add(async_func)."""

from __future__ import annotations

import asyncio

from logly import Logger


def test_async_sink_is_detected() -> None:
    logger = Logger()
    messages: list[str] = []

    async def async_sink(msg: str) -> None:
        messages.append(msg)

    sink_id = logger.add(async_sink, level="DEBUG", format="{message}")
    logger.info("async hello")
    logger.complete()
    logger.remove(sink_id)
    assert any("async hello" in m for m in messages)


def test_async_sink_receives_message() -> None:
    logger = Logger()
    results: list[str] = []

    async def capture(msg: str) -> None:
        results.append(msg)

    sink_id = logger.add(capture, level="DEBUG", format="{message}")
    logger.info("test message")
    logger.complete()
    logger.remove(sink_id)
    assert len(results) >= 1
    assert "test message" in results[0]


def test_async_sink_with_explicit_loop() -> None:
    logger = Logger()
    results: list[str] = []

    async def capture(msg: str) -> None:
        results.append(msg)

    loop = asyncio.new_event_loop()
    try:
        sink_id = logger.add(capture, level="DEBUG", format="{message}", loop=loop)
        logger.info("loop test")
        logger.complete()
        logger.remove(sink_id)
        assert any("loop test" in m for m in results)
    finally:
        loop.close()


def test_async_sink_multiple_messages() -> None:
    logger = Logger()
    results: list[str] = []

    async def capture(msg: str) -> None:
        results.append(msg)

    sink_id = logger.add(capture, level="DEBUG", format="{message}")
    logger.info("msg1")
    logger.info("msg2")
    logger.info("msg3")
    logger.complete()
    logger.remove(sink_id)
    assert len(results) >= 3


def test_async_sink_is_coroutine_function_detection() -> None:
    def not_async(msg: str) -> None:
        pass

    async def is_async(msg: str) -> None:
        pass

    assert asyncio.iscoroutinefunction(is_async)
    assert not asyncio.iscoroutinefunction(not_async)
