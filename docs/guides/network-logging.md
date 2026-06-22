---
title: Network Logging
description: Send logs over HTTP, TCP, UDP, and Syslog
---

# Network Logging

Logly can send log messages to remote destinations using various network protocols.

## HTTP Sink

POST log messages as JSON to an HTTP endpoint:

```python
import json
import urllib.request
from logly import logger

def http_sink(message: str) -> None:
    payload = json.dumps({"log": message}).encode("utf-8")
    request = urllib.request.Request(
        "https://logs.example.com/ingest",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(request, timeout=5)

logger.add(http_sink, level="INFO", enqueue=True)
```

### Using HttpJsonSink

```python
from logly import logger
from logly.integrations.telemetry import HttpJsonSink

logger.add(
    HttpJsonSink(
        endpoint="https://logs.example.com/ingest",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
    ),
    level="WARNING",
    serialize=True,
)
logger.warning("Error sent via HTTP")
```

## TCP Sink

Send logs over a TCP socket:

```python
import socket
from logly import logger

def tcp_sink(message: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("logserver.example.com", 9000))
        sock.sendall(message.encode("utf-8"))

logger.add(tcp_sink, level="INFO")
```

## UDP Sink

Send logs over a UDP socket (fire-and-forget):

```python
import socket
from logly import logger

def udp_sink(message: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(
            message.encode("utf-8"),
            ("logserver.example.com", 514),
        )

logger.add(udp_sink, level="WARNING")
```

## Syslog Sink

Send logs to the system syslog:

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

# Local syslog
logger.add(SysLogHandler(address="/dev/log"), level="INFO")

# Remote syslog
logger.add(SysLogHandler(address=("logserver.example.com", 514)), level="WARNING")

# Windows (requires syslog-ng or similar)
logger.add(SysLogHandler(address=("localhost", 514)), level="INFO")
```

## Telemetry Sink

Forward logs to a telemetry callback:

```python
from logly import logger
from logly.integrations.telemetry import TelemetrySink

def send_to_collector(event: dict) -> None:
    print(f"Telemetry: {event}")

logger.add(TelemetrySink(emit=send_to_collector, service_name="myapp"), level="INFO")
```

## Loki Sink

Push logs to Grafana Loki:

```python
from logly import logger
from logly.integrations.loki import LokiSink

logger.add(
    LokiSink(
        "http://localhost:3100/loki/api/v1/push",
        labels={"app": "myapp", "env": "production"},
        timeout=5.0,
    ),
    level="INFO",
)
```

## Elasticsearch Sink

Index logs into Elasticsearch:

```python
from logly import logger
from logly.integrations.elasticsearch import ElasticsearchSink

logger.add(
    ElasticsearchSink(
        "http://localhost:9200",
        index="logs-{time:YYYY.MM.DD}",
    ),
    level="WARNING",
)
```

## Best Practices

| Protocol | Reliability | Latency | Use Case |
|----------|-------------|---------|----------|
| HTTP | High | Medium | Cloud logging, structured data |
| TCP | High | Low | Local network, reliable delivery |
| UDP | Low | Very Low | Metrics, non-critical logs |
| Syslog | Medium | Low | System logs, centralized logging |
| Loki | High | Medium | Grafana ecosystem |
| Elasticsearch | High | Medium | Searchable log archives |

## Enqueue for Reliability

For network sinks, use `enqueue=True` to decouple logging from network I/O:

```python
logger.add(http_sink, level="INFO", enqueue=True)
logger.info("This does not block on network")
logger.complete()  # Ensures all messages are sent
```
