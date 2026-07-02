---
title: Graylog
description: Send log records to Graylog in GELF format.
---

# Graylog

`GraylogSink` sends log records to a Graylog server in GELF (Graylog Extended Log Format). Supports GELF 1.0 and 1.1, TCP/UDP, UDP chunking, and zlib compression.

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Usage

```python
import logging
from logly.integrations.graylog import GraylogSink

logger = logging.getLogger("myapp")
logger.addHandler(GraylogSink(host="localhost", port=12201))
logger.setLevel(logging.INFO)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `host` | `"localhost"` | Graylog server host |
| `port` | `12201` | Graylog server port |
| `protocol` | `"udp"` | `"tcp"` or `"udp"` |
| `version` | `"1.1"` | GELF version (`"1.0"` or `"1.1"`) |
| `compress` | `True` | Enable zlib compression (UDP only) |
| `chunk_size` | `1420` | UDP chunk size in bytes |

## Full Example

```python
import logging
from logly.integrations.graylog import GraylogSink

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# UDP with compression
handler = GraylogSink(
    host="graylog.example.com",
    port=12201,
    protocol="udp",
    version="1.1",
    compress=True,
    chunk_size=1420,
)
logger.addHandler(handler)

logger.info("Application started")
logger.warning("Disk usage above 80%")
logger.error("Database connection failed")
```
