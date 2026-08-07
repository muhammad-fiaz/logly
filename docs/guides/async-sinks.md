---
title: Async Sinks
description: Use async coroutine functions as Logly sinks
---

# Async Sinks

Logly supports async callable sinks, including regular `async def` functions, class instances with async `__call__` methods, and `functools.partial` wrapping async callables.

## Basic Usage

```python
import asyncio
from logly import logger


async def async_sink(message: str) -> None:
    await send_to_cloud(message)


logger.add(async_sink, level="INFO")
logger.info("Hello from async sink")
```

## Class-Based Async Sinks

Logly correctly detects class instances with async `__call__` methods as async sinks:

```python
import asyncio
from logly import logger


class AsyncCloudSink:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def __call__(self, message: str) -> None:
        await send_to_cloud(message, self.api_key)


sink = AsyncCloudSink(api_key="your-key")
logger.add(sink, level="INFO")
logger.info("Sent via async class sink")
logger.complete()  # Flush pending async tasks
```

This also works with stateful sinks that maintain context between log calls:

```python
from logly import logger


class BufferedAsyncSink:
    def __init__(self):
        self.buffer = []

    async def __call__(self, message: str) -> None:
        self.buffer.append(message)
        if len(self.buffer) >= 10:
            await self.flush()

    async def flush(self):
        await send_batch(self.buffer)
        self.buffer.clear()


logger.add(BufferedAsyncSink(), level="INFO")
```

## functools.partial Wrapping

```python
import asyncio
import functools
from logly import logger


async def cloud_sink(prefix: str, message: str) -> None:
    await send_to_cloud(f"[{prefix}] {message}")


sink = functools.partial(cloud_sink, "APP")
logger.add(sink, level="INFO")
logger.info("Wrapped async sink")
```

## Event Loop Detection

Logly automatically detects the event loop context when you add an async sink:

**If an event loop is running** (e.g., inside `async def main()`):

```python
import asyncio
from logly import logger


async def cloud_sink(message: str) -> None:
    await http_client.post("https://logs.example.com", content=message)


async def main():
    logger.add(cloud_sink, level="INFO")
    logger.info("Running inside event loop")
    logger.complete()  # Waits for async tasks


asyncio.run(main())
```

**If no event loop is running** (e.g., in a sync script):

```python
from logly import logger


async def cloud_sink(message: str) -> None:
    await send_to_cloud(message)


logger.add(cloud_sink, level="INFO")
logger.info("Running outside event loop")
logger.complete()  # Logly creates a background loop and flushes
```

When no loop is running, Logly creates a background thread with its own event loop to run the async sink.

## Explicit Loop Parameter

You can pass a specific event loop via the `loop` parameter:

```python
import asyncio
from logly import logger

loop = asyncio.new_event_loop()


async def async_sink(message: str) -> None:
    await process_log(message)


logger.add(async_sink, level="INFO", loop=loop)
logger.info("Sent to async sink on custom loop")
logger.complete()
```

## Flushing Async Sinks

Always call `logger.complete()` before your process exits. This:

1. Drains all enqueued synchronous messages
2. Awaits all pending async sink tasks

```python
from logly import logger


async def metrics_sink(message: str) -> None:
    await send_to_metrics(message)


async def main():
    logger.add(metrics_sink, level="INFO")
    logger.info("Processing...")
    logger.complete()  # Ensures all async messages are flushed


asyncio.run(main())
```

## Multiple Async Sinks

```python
import asyncio
from logly import logger


async def cloud_sink(message: str) -> None:
    await send_to_cloud(message)


async def db_sink(message: str) -> None:
    await insert_into_database(message)


async def main():
    logger.add(cloud_sink, level="INFO")
    logger.add(db_sink, level="ERROR")
    logger.info("This goes to cloud only")
    logger.error("This goes to both cloud and database")
    logger.complete()


asyncio.run(main())
```

## Mixing Sync and Async Sinks

```python
import asyncio
from logly import logger


def sync_sink(message: str) -> None:
    print(f"SYNC: {message}", end="")


async def async_sink(message: str) -> None:
    await send_to_cloud(message)


async def main():
    logger.add(sync_sink, level="INFO")
    logger.add(async_sink, level="INFO")
    logger.info("Goes to both sync and async sinks")
    logger.complete()


asyncio.run(main())
```

## Error Handling

If an async sink raises an exception, the error is logged to stderr but does not crash the application. Use `catch=True` (default) to prevent sink errors from propagating:

```python
from logly import logger


async def risky_sink(message: str) -> None:
    # This might fail
    await unreliable_api_call(message)


logger.add(risky_sink, level="ERROR", catch=True)
```

## Common Patterns

### Cloud Logging

```python
import asyncio
from logly import logger


async def cloud_logger(message: str) -> None:
    async with aiohttp.ClientSession() as session:
        await session.post(
            "https://your-cloud-logging-endpoint.com/ingest",
            json={"log": message},
        )


async def main():
    logger.add(cloud_logger, level="WARNING")
    logger.complete()


asyncio.run(main())
```

### Database Logging

```python
import asyncio
from logly import logger


async def db_logger(message: str) -> None:
    async with aiosqlite.connect("logs.db") as db:
        await db.execute(
            "INSERT INTO logs (message, created_at) VALUES (?, datetime('now'))",
            (message,),
        )
        await db.commit()


async def main():
    logger.add(db_logger, level="INFO")
    logger.complete()


asyncio.run(main())
```

### Message Queue Logging

```python
import asyncio
from logly import logger


async def kafka_sink(message: str) -> None:
    producer = AIOKafkaProducer()
    await producer.start()
    await producer.send("log-topic", message.encode())
    await producer.stop()


async def main():
    logger.add(kafka_sink, level="INFO")
    logger.complete()


asyncio.run(main())
```

## API Reference

```python
logger.add(
    async_sink,  # async def callable, class with async __call__, or functools.partial
    level="INFO",  # Minimum log level
    format=None,  # Format string or callable
    loop=None,  # Explicit event loop (optional)
    catch=True,  # Catch sink errors
    enqueue=False,  # Use background worker
    **kwargs,  # Other add() parameters
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `loop` | `asyncio.AbstractEventLoop \| None` | Event loop for the async sink. If `None`, auto-detected. |
| `catch` | `bool` | Catch sink errors (default `True`). |
| `enqueue` | `bool` | Dispatch through background worker (default `False`). |

### Supported Async Callable Types

| Type | Detected as Async | Example |
|------|-------------------|---------|
| `async def` function | Yes | `async def sink(msg): ...` |
| Class with `async __call__` | Yes | `class Sink: async def __call__(self, msg): ...` |
| `functools.partial` wrapping async | Yes | `functools.partial(async_func, arg)` |
| Regular function | No (sync) | `def sink(msg): ...` |
| Lambda | No (sync) | `lambda msg: ...` |

## Batch HTTP Sink

For high-performance cloud logging, use `BatchHttpJsonSink` to batch multiple log records before sending:

```python
from logly import BatchHttpJsonSink, logger

# Create a batch HTTP sink
sink = BatchHttpJsonSink(
    url="https://logs.example.com/ingest",
    batch_size=100,  # Send after 100 records
    flush_interval=5.0,  # Or flush every 5 seconds
    headers={"Authorization": "Bearer token"},
)

logger.add(sink, level="INFO")
logger.info("This will be batched")
```

### Batch Sink Features

- **Automatic batching**: Groups log records into batches
- **Time-based flushing**: Flushes after a configurable interval
- **Size-based flushing**: Flushes when batch reaches max size
- **Thread-safe**: Safe to use from multiple threads
- **Rust-native**: Implemented in Rust for maximum performance

### Batch Sink API

```python
from logly import BatchHttpJsonSink

sink = BatchHttpJsonSink(
    url="https://logs.example.com/ingest",
    batch_size=100,  # Max records per batch
    flush_interval=5.0,  # Seconds between flushes
    timeout=10.0,  # HTTP timeout in seconds
    headers={},  # Custom HTTP headers
)

# Manual control
sink.write(record)  # Add record to buffer
sink.flush()  # Force flush all buffered records
sink.buffer_len()  # Get current buffer size
```
