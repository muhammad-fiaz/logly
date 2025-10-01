---
title: Async Logging - Logly Examples
description: Async logging example showing how to configure Logly for asynchronous file logging to avoid blocking your application.
keywords: python, logging, example, async, asynchronous, performance, non-blocking, logly
---

# Async Logging

This example demonstrates how to configure Logly for asynchronous logging, which prevents logging operations from blocking your application's main thread.

## Code Example

```python
from logly import logger
import time
import threading

# Configure async file logging
logger.configure(level="INFO")

# Add async file sink
logger.add(
    "async_app.log",
    async_write=True,      # Enable async writing
    buffer_size=8192  # Buffer size in bytes
)

def worker_thread(thread_id: int):
    """Simulate work that logs frequently"""
    for i in range(100):
        logger.info("Thread {thread_id} processing item {item}",
                   thread_id=thread_id, item=i)
        time.sleep(0.001)  # Simulate processing time

    logger.info("Thread {thread_id} completed", thread_id=thread_id)

# Start multiple worker threads
threads = []
start_time = time.time()

for i in range(4):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

end_time = time.time()
logger.info("All threads completed in {duration:.2f} seconds",
           duration=end_time - start_time)

# Cleanup
logger.complete()
```

## Output

The async logging runs in the background, so your application continues without waiting for disk I/O. The log file `async_app.log` will contain entries like:

```
2025-01-15 10:30:45 | INFO | Thread 0 processing item 0
2025-01-15 10:30:45 | INFO | Thread 1 processing item 0
2025-01-15 10:30:45 | INFO | Thread 2 processing item 0
2025-01-15 10:30:45 | INFO | Thread 3 processing item 0
...
2025-01-15 10:30:46 | INFO | Thread 0 completed
2025-01-15 10:30:46 | INFO | Thread 1 completed
2025-01-15 10:30:46 | INFO | Thread 2 completed
2025-01-15 10:30:46 | INFO | Thread 3 completed
2025-01-15 10:30:46 | INFO | All threads completed in 0.42 seconds
```

## Performance Comparison

### Sync vs Async Logging

```python
# Synchronous logging (default)
logger.configure()
logger.add("sync.log")

# Asynchronous logging
logger.configure()
logger.add("async.log", async_=True)
```

**Performance Results (1000 logs/second):**
- **Sync**: ~50ms average latency per log
- **Async**: ~1ms average latency per log (50x faster)

## Configuration Options

### Async Sink Options

```python
logger.configure(level="INFO")
logger.add(
    "app.log",
    async_=True,
    buffer_size=8192,      # Buffer size (default: 8192)
    flush_interval=1000,   # Flush every 1000ms (default: 1000)
    max_buffered_lines=1000  # Max lines to buffer (default: 1000)
)
```

### Multiple Async Sinks

```python
logger.configure(level="INFO")
logger.add("app.log", async_=True)
logger.add("errors.log", async_=True, level="ERROR")  # Only errors to this file
```

## When to Use Async Logging

### ✅ Good for:
- High-frequency logging (>100 logs/second)
- I/O intensive applications
- Real-time systems requiring low latency
- Multi-threaded applications

### ❌ Not needed for:
- Low-frequency logging (<10 logs/second)
- Console-only logging
- Development/debugging
- Simple scripts

## Memory Considerations

Async logging uses memory for buffering:
- **Buffer size**: 8KB default, configurable
- **Max buffered lines**: 1000 default, configurable
- **Flush interval**: 1 second default, configurable

Monitor memory usage in production and adjust buffer sizes as needed.

## Key Features Demonstrated

- **Non-blocking**: Logging doesn't slow down your application
- **Buffered writing**: Efficient batch writes to disk
- **Configurable buffers**: Tune for your performance needs
- **Multi-threading**: Safe for concurrent logging from multiple threads