---
title: Logstash
description: Send log records to Logstash via TCP/UDP.
---

# Logstash

`LogstashSink` sends log records to a Logstash instance over TCP or UDP in JSON format. Supports field prefixes and tags for filtering.

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Usage

```python
import logging
from logly.integrations.logstash import LogstashSink

logger = logging.getLogger("myapp")
logger.addHandler(LogstashSink(host="localhost", port=5044))
logger.setLevel(logging.INFO)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `host` | `"localhost"` | Logstash host |
| `port` | `5044` | Logstash port |
| `protocol` | `"tcp"` | `"tcp"` or `"udp"` |
| `prefix` | `""` | Prefix for extra fields |
| `tags` | `[]` | List of tags to add to each record |
| `message_type` | `"logstash"` | Message type field |

## Full Example

```python
import logging
from logly.integrations.logstash import LogstashSink

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# TCP handler
tcp_handler = LogstashSink(
    host="logstash.example.com",
    port=5044,
    protocol="tcp",
    prefix="app",
    tags=["production", "web"],
)
logger.addHandler(tcp_handler)

# UDP handler
udp_handler = LogstashSink(
    host="logstash.example.com",
    port=5045,
    protocol="udp",
)
logger.addHandler(udp_handler)

logger.info("Application started")
logger.warning("High memory usage")
logger.error("Request failed")
```
