"""Tests for async sink via logger.add(async_func)."""

from __future__ import annotations

import asyncio
import inspect

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

    assert inspect.iscoroutinefunction(is_async)
    assert not inspect.iscoroutinefunction(not_async)


def test_class_like_async_sink() -> None:
    """Test that class instances with async __call__ are detected as async sinks."""
    from logly.logger import _is_async_callable

    class AsyncSink:
        def __init__(self) -> None:
            self.messages: list[str] = []

        async def __call__(self, message: str) -> None:
            self.messages.append(message)

    async_sink = AsyncSink()

    # Test that the helper function detects it correctly
    assert _is_async_callable(async_sink)
    assert callable(async_sink)

    # Test that it works as a sink
    logger = Logger()
    sink_id = logger.add(async_sink, level="DEBUG", format="{message}")
    logger.info("class-like async sink test")
    logger.complete()
    logger.remove(sink_id)

    assert len(async_sink.messages) >= 1
    assert "class-like async sink test" in async_sink.messages[0]


def test_class_like_async_sink_multiple_messages() -> None:
    """Test class-like async sink with multiple messages."""
    from logly.logger import _is_async_callable

    class AsyncCollector:
        def __init__(self) -> None:
            self.messages: list[str] = []

        async def __call__(self, message: str) -> None:
            self.messages.append(message)

    collector = AsyncCollector()
    assert _is_async_callable(collector)

    logger = Logger()
    sink_id = logger.add(collector, level="DEBUG", format="{message}")
    logger.info("msg1")
    logger.info("msg2")
    logger.info("msg3")
    logger.complete()
    logger.remove(sink_id)

    assert len(collector.messages) >= 3


def test_is_async_callable_helper() -> None:
    """Test the _is_async_callable helper function with various callables."""
    from functools import partial

    from logly.logger import _is_async_callable

    async def async_func(msg: str) -> None:
        pass

    def sync_func(msg: str) -> None:
        pass

    class AsyncCallableClass:
        async def __call__(self, msg: str) -> None:
            pass

    class SyncCallableClass:
        def __call__(self, msg: str) -> None:
            pass

    class NotCallableClass:
        pass

    # Test async function
    assert _is_async_callable(async_func)

    # Test sync function
    assert not _is_async_callable(sync_func)

    # Test async callable class instance
    assert _is_async_callable(AsyncCallableClass())

    # Test sync callable class instance
    assert not _is_async_callable(SyncCallableClass())  # sync, not async

    # Test non-callable class instance
    assert not _is_async_callable(NotCallableClass())

    # Test functools.partial wrapping async function
    partial_async = partial(async_func, "test")
    assert _is_async_callable(partial_async)

    # Test functools.partial wrapping sync function
    partial_sync = partial(sync_func, "test")
    assert not _is_async_callable(partial_sync)

    # Test non-callable objects
    assert not _is_async_callable("string")
    assert not _is_async_callable(42)
    assert not _is_async_callable(None)


def test_class_like_async_sink_with_loop() -> None:
    """Test class-like async sink with explicit event loop."""
    from logly.logger import _is_async_callable

    class AsyncSink:
        def __init__(self) -> None:
            self.messages: list[str] = []

        async def __call__(self, message: str) -> None:
            self.messages.append(message)

    async_sink = AsyncSink()
    assert _is_async_callable(async_sink)

    logger = Logger()
    loop = asyncio.new_event_loop()
    try:
        sink_id = logger.add(async_sink, level="DEBUG", format="{message}", loop=loop)
        logger.info("explicit loop test")
        logger.complete()
        logger.remove(sink_id)
        assert any("explicit loop test" in m for m in async_sink.messages)
    finally:
        loop.close()
