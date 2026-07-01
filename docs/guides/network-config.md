---
title: Network Sink Configuration
description: Configure network-based log sinks for HTTP, TCP, UDP, and Syslog
---

# Network Sink Configuration

Logly supports sending logs over various network protocols. This guide covers HTTP, TCP, UDP, and Syslog sink configuration with complete examples.

## HTTP JSON Sink

POST log messages as JSON to an HTTP endpoint.

### Basic HTTP Sink

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

### HttpJsonSink (Built-in)

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

### Custom HTTP Configuration

```python
import json
import urllib.request
from logly import logger

def http_sink(message: str) -> None:
    payload = json.dumps({
        "log": message,
        "source": "myapp",
        "timestamp": "2026-07-01T14:30:00Z",
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://logs.example.com/ingest",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_TOKEN",
            "X-Source": "myapp",
            "X-Environment": "production",
        },
        method="POST",
    )
    urllib.request.urlopen(request, timeout=10)

logger.add(
    http_sink,
    level="WARNING",
    enqueue=True,
    backpressure="block",
)
```

### HTTP with Retry Logic

```python
import json
import urllib.request
import time
from logly import logger

def http_sink_with_retry(message: str, max_retries=3) -> None:
    payload = json.dumps({"log": message}).encode("utf-8")

    for attempt in range(max_retries):
        try:
            request = urllib.request.Request(
                "https://logs.example.com/ingest",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(request, timeout=5)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error("HTTP sink failed after {} retries: {}", max_retries, e)

logger.add(http_sink_with_retry, level="WARNING", enqueue=True)
```

### HTTP Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `endpoint` | `str` | URL to POST logs to |
| `headers` | `dict` | HTTP headers for the request |
| `method` | `str` | HTTP method (default: `POST`) |
| `timeout` | `int` | Request timeout in seconds |
| `batch_size` | `int` | Number of logs to batch before sending |
| `batch_interval` | `float` | Time between batch sends (seconds) |

## TCP Sink

Send logs over a TCP socket for reliable delivery.

### Basic TCP Sink

```python
import socket
from logly import logger

def tcp_sink(message: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("logserver.example.com", 9000))
        sock.sendall(message.encode("utf-8"))

logger.add(tcp_sink, level="INFO")
```

### TCP with Delimiter

```python
import socket
from logly import logger

def tcp_sink_with_delimiter(message: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("logserver.example.com", 9000))
        # Add newline delimiter for line-based protocols
        sock.sendall(message.encode("utf-8") + b"\n")

logger.add(tcp_sink_with_delimiter, level="INFO")
```

### Persistent TCP Connection

```python
import socket
from logly import logger

class PersistentTCPSink:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def __call__(self, message: str) -> None:
        try:
            if self.sock is None:
                self.connect()
            self.sock.sendall(message.encode("utf-8") + b"\n")
        except (ConnectionError, OSError):
            self.sock = None
            self.connect()
            self.sock.sendall(message.encode("utf-8") + b"\n")

logger.add(PersistentTCPSink("logserver.example.com", 9000), level="INFO")
```

### TCP Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `str` | Server hostname or IP |
| `port` | `int` | Server port |
| `delimiter` | `str` | Message delimiter (default: `\n`) |
| `timeout` | `int` | Connection timeout in seconds |

## UDP Sink

Send logs over a UDP socket (fire-and-forget, low latency).

### Basic UDP Sink

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

### UDP with Structured Data

```python
import socket
import json
from logly import logger

def udp_structured_sink(message: str) -> None:
    payload = json.dumps({
        "log": message,
        "source": "myapp",
    }).encode("utf-8")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(payload, ("logserver.example.com", 514))

logger.add(udp_structured_sink, level="WARNING")
```

### UDP Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `str` | Server hostname or IP |
| `port` | `int` | Server port |
| `max_size` | `int` | Maximum packet size (default: 65535) |

::: warning
UDP is unreliable by design. Messages may be lost during network congestion. Use UDP only for non-critical logs or metrics.
:::

## Syslog Sink

Send logs to a Syslog server using the standard `logging.handlers.SysLogHandler`.

### Local Syslog

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

logger.add(SysLogHandler(address="/dev/log"), level="INFO")
```

### Remote Syslog (UDP)

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

logger.add(
    SysLogHandler(address=("logserver.example.com", 514)),
    level="WARNING",
)
```

### Remote Syslog (TCP)

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

logger.add(
    SysLogHandler(address=("logserver.example.com", 514), socktype=socket.SOCK_STREAM),
    level="WARNING",
)
```

### Windows Syslog

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

# Requires syslog-ng or similar on Windows
logger.add(
    SysLogHandler(address=("localhost", 514)),
    level="INFO",
)
```

### Syslog Facilities

Syslog facilities categorize the source of log messages:

| Facility | Description | Typical Use |
|----------|-------------|-------------|
| `LOG_USER` | Generic user-level messages | General application logs |
| `LOG_LOCAL0` | Local use 0 | Application-specific |
| `LOG_LOCAL1` | Local use 1 | Application-specific |
| `LOG_LOCAL2` | Local use 2 | Application-specific |
| `LOG_LOCAL3` | Local use 3 | Application-specific |
| `LOG_LOCAL4` | Local use 4 | Application-specific |
| `LOG_LOCAL5` | Local use 5 | Application-specific |
| `LOG_LOCAL6` | Local use 6 | Application-specific |
| `LOG_LOCAL7` | Local use 7 | Application-specific |
| `LOG_DAEMON` | System daemons | Daemon processes |
| `LOG_AUTH` | Authentication/security | Login attempts |
| `LOG_CRON` | Cron/scheduled tasks | Job scheduler |
| `LOG_KERN` | Kernel messages | System-level |
| `LOG_MAIL` | Mail system | Email server |
| `LOG_NEWS` | Network news | Usenet |
| `LOG_SYSLOG` | Syslog internal | Internal messages |

### Syslog with Custom Facility

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

# Use LOG_LOCAL0 for application logs
handler = SysLogHandler(
    address=("logserver.example.com", 514),
    facility=SysLogHandler.LOG_LOCAL0,
)

logger.add(handler, level="INFO")
```

### Syslog Severity Mapping

Logly maps its log levels to Syslog severities:

| Logly Level | Syslog Severity |
|-------------|-----------------|
| `TRACE` | `DEBUG` |
| `DEBUG` | `DEBUG` |
| `INFO` | `INFO` |
| `NOTICE` | `NOTICE` |
| `SUCCESS` | `INFO` |
| `WARNING` | `WARNING` |
| `ERROR` | `ERROR` |
| `FAIL` | `CRITICAL` |
| `CRITICAL` | `CRITICAL` |
| `FATAL` | `EMERGENCY` |

### Syslog Formats

#### RFC 3164 (BSD Syslog)

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

# RFC 3164 format (default)
logger.add(
    SysLogHandler(
        address=("logserver.example.com", 514),
        facility=SysLogHandler.LOG_LOCAL0,
    ),
    level="INFO",
)
```

Example output:
```
<14>Jul  1 14:30:45 myapp[12345]: INFO | Application started
```

#### RFC 5424 (Modern Syslog)

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

# For RFC 5424, use structured data
logger.add(
    SysLogHandler(
        address=("logserver.example.com", 514),
        facility=SysLogHandler.LOG_LOCAL0,
    ),
    serialize=True,
    level="INFO",
)
```

Example output:
```
<14>1 2026-07-01T14:30:45.123Z myapp 12345 - - [app@48148 service="myapp"] Application started
```

## Network Reliability Considerations

### Reliability by Protocol

| Protocol | Delivery | Ordering | Reliability | Use Case |
|----------|----------|----------|-------------|----------|
| HTTP | Guaranteed | Guaranteed | High | Cloud logging, structured data |
| TCP | Guaranteed | Guaranteed | High | Local network, reliable delivery |
| UDP | Best effort | May reorder | Low | Metrics, non-critical logs |
| Syslog | Depends on transport | Depends | Medium | System logs, centralized logging |

### Error Handling

```python
import json
import urllib.request
from logly import logger

def reliable_http_sink(message: str) -> None:
    try:
        payload = json.dumps({"log": message}).encode("utf-8")
        request = urllib.request.Request(
            "https://logs.example.com/ingest",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(request, timeout=5)
    except Exception as e:
        # Log to stderr if network sink fails
        logger.opt(exception=True).error("HTTP sink failed")

logger.add(reliable_http_sink, level="INFO", enqueue=True)
```

### Fallback Sinks

```python
from logly import logger

def primary_sink(message: str) -> None:
    # Try primary destination
    import urllib.request
    urllib.request.urlopen("https://primary.example.com/logs", data=message.encode())

def fallback_sink(message: str) -> None:
    # Fallback to local file
    with open("fallback.log", "a") as f:
        f.write(message + "\n")

# Primary: network sink
logger.add(primary_sink, level="INFO", enqueue=True, catch=True)

# Fallback: file sink
logger.add("fallback.log", level="INFO", enqueue=True)
```

## Reconnection Behavior

### Automatic Reconnection

Network sinks should handle reconnection automatically:

```python
import socket
from logly import logger

class ReconnectingTCPSink:
    def __init__(self, host: str, port: int, max_retries=3):
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.sock = None

    def connect(self):
        for attempt in range(self.max_retries):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                return
            except (ConnectionError, OSError) as e:
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    raise

    def __call__(self, message: str) -> None:
        try:
            if self.sock is None:
                self.connect()
            self.sock.sendall(message.encode("utf-8") + b"\n")
        except (ConnectionError, OSError):
            self.sock = None
            self.connect()
            self.sock.sendall(message.encode("utf-8") + b"\n")

logger.add(
    ReconnectingTCPSink("logserver.example.com", 9000),
    level="INFO",
    enqueue=True,
)
```

### Queue with Retry

```python
import json
import urllib.request
import time
from logly import logger

def http_sink_with_retry(message: str, max_retries=3) -> None:
    payload = json.dumps({"log": message}).encode("utf-8")

    for attempt in range(max_retries):
        try:
            request = urllib.request.Request(
                "https://logs.example.com/ingest",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(request, timeout=5)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error("HTTP sink failed after {} retries", max_retries)

logger.add(http_sink_with_retry, level="WARNING", enqueue=True)
```

## Complete Examples

### Production HTTP Logging

```python
import json
import urllib.request
from logly import logger

logger.remove()

def http_json_sink(message: str) -> None:
    payload = json.dumps({
        "log": message,
        "source": "myapp",
        "environment": "production",
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://logs.example.com/ingest",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_TOKEN",
            "X-Source": "myapp",
        },
        method="POST",
    )
    urllib.request.urlopen(request, timeout=5)

# HTTP sink for warnings and above
logger.add(
    http_json_sink,
    level="WARNING",
    enqueue=True,
    backpressure="block",
)

# Local file for all logs
logger.add(
    "app.log",
    level="DEBUG",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    enqueue=True,
)

# Console for immediate feedback
logger.add(
    "stderr",
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
    colorize=True,
)

logger.info("Application started")
logger.warning("Disk usage high")
logger.error("Connection failed")
logger.complete()
```

### Multi-Protocol Logging

```python
import socket
import json
import urllib.request
from logly import logger

logger.remove()

# TCP for reliable local delivery
def tcp_sink(message: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("logserver.local", 9000))
        sock.sendall(message.encode("utf-8") + b"\n")

# UDP for metrics (fire-and-forget)
def udp_sink(message: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode("utf-8"), ("logserver.local", 514))

# HTTP for cloud logging
def http_sink(message: str) -> None:
    payload = json.dumps({"log": message}).encode("utf-8")
    request = urllib.request.Request(
        "https://logs.example.com/ingest",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(request, timeout=5)

# All logs to TCP
logger.add(tcp_sink, level="DEBUG", enqueue=True)

# Warnings to HTTP
logger.add(http_sink, level="WARNING", enqueue=True)

# Metrics to UDP
logger.add(udp_sink, level="SUCCESS", enqueue=True)

# Console
logger.add("stderr", level="INFO", colorize=True)

logger.info("Debug to TCP and console")
logger.warning("Warning to all destinations")
logger.error("Error to all destinations")
logger.complete()
```

### Syslog with Custom Facility

```python
import logging
from logging.handlers import SysLogHandler
from logly import logger

logger.remove()

# Application logs to LOG_LOCAL0
app_handler = SysLogHandler(
    address=("syslog.example.com", 514),
    facility=SysLogHandler.LOG_LOCAL0,
)

# Security logs to LOG_AUTH
security_handler = SysLogHandler(
    address=("syslog.example.com", 514),
    facility=SysLogHandler.LOG_AUTH,
)

logger.add(app_handler, level="INFO")
logger.add(security_handler, level="WARNING")

# Custom level for security events
logger.level("SECURITY", no=45, color="bold red")

logger.info("Application started")
logger.warning("Configuration issue")
logger.log("SECURITY", "Unauthorized access attempt")
logger.complete()
```

### High-Throughput Network Logging

```python
import json
import urllib.request
from logly import logger
import time

logger.remove()

def batch_http_sink(message: str) -> None:
    payload = json.dumps({"log": message, "ts": time.time()}).encode("utf-8")
    request = urllib.request.Request(
        "https://logs.example.com/batch",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(request, timeout=10)

# High-throughput with batch processing
logger.add(
    batch_http_sink,
    level="INFO",
    enqueue=True,
    backpressure="drop_newest",
)

# Process millions of events
for i in range(1000000):
    logger.info("Event {}", i)
    if i % 10000 == 0:
        time.sleep(0.01)  # Simulate processing time

logger.complete()
```
