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
    async_write=True  # Enable async writing
)

def worker_thread(thread_id: int):
    """Simulate work that logs frequently"""
    for i in range(10):
        logger.info("Processing item", thread_id=thread_id, item=i)
        time.sleep(0.01)

    logger.info("Thread completed", thread_id=thread_id)

# Start multiple worker threads
threads = []
start_time = time.time()

for i in range(3):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

duration = time.time() - start_time
logger.info("All threads completed", duration_seconds=f"{duration:.2f}")

# Cleanup
logger.complete()
```

## Expected Output

**Console output:**
```
2025-01-15T10:30:45.123456+00:00 [INFO] Processing item | thread_id=0 | item=0
2025-01-15T10:30:45.124567+00:00 [INFO] Processing item | thread_id=1 | item=0
2025-01-15T10:30:45.125678+00:00 [INFO] Processing item | thread_id=2 | item=0
...
2025-01-15T10:30:45.523456+00:00 [INFO] Thread completed | thread_id=0
2025-01-15T10:30:45.524567+00:00 [INFO] Thread completed | thread_id=1
2025-01-15T10:30:45.525678+00:00 [INFO] Thread completed | thread_id=2
2025-01-15T10:30:45.526789+00:00 [INFO] All threads completed | duration_seconds=0.42
```

**File `async_app.log` contains:**
```
2025-01-15T10:30:45.123456+00:00 [INFO] Processing item | thread_id=0 | item=0
2025-01-15T10:30:45.124567+00:00 [INFO] Processing item | thread_id=1 | item=0
2025-01-15T10:30:45.125678+00:00 [INFO] Processing item | thread_id=2 | item=0
...
(33 total log entries from 3 threads)
```

### What Happens

1. **`async_write=True` enables async I/O**:
   - Log messages are written to a buffer immediately
   - Background thread flushes buffer to disk asynchronously
   - Main application threads don't wait for disk I/O

2. **Multiple threads log simultaneously**:
   - Logly is thread-safe, so logs from all threads are interleaved correctly
   - No locks block your worker threads
   - Messages maintain correct chronological order

3. **Performance benefit**:
   - Without async: Each log call waits ~5-10ms for disk write
   - With async: Log calls return in <1ms, writes happen in background
   - Result: 5-10x faster for high-volume logging

4. **`logger.complete()` ensures cleanup**:
   - Flushes any remaining buffered messages
   - Closes file handles gracefully
   - Waits for background writer thread to finish

## Performance Comparison

### Sync vs Async Logging

```python
# Synchronous logging (default)
logger.configure()
logger.add("sync.log")

# Asynchronous logging
logger.configure()
logger.add("async.log", async_write=True)
```

**Performance Results (1000 logs/second):**
- **Sync**: ~50ms average latency per log
- **Async**: ~1ms average latency per log (50x faster)

## Configuration Options

### Async Sink Options

```python
logger.configure(level="INFO")
logger.add("app.log", async_write=True)
```

### Multiple Async Sinks

```python
logger.configure(level="INFO")
logger.add("app.log", async_write=True)
logger.add("errors.log", async_write=True, filter_min_level="ERROR")  # Only errors to this file
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