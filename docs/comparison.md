---
title: Comparison
description: Feature comparison between Logly, Loguru, structlog, and stdlib logging
---

# Comparison

Logly is a high-performance logging library with a Rust-native engine. It
provides a clean Python API with built-in levels, flexible sinks, rotation,
compression, structured output, and framework integrations.

## Feature Matrix

| Capability | Logly | Loguru | structlog | stdlib logging |
|------------|-------|--------|-----------|----------------|
| **Engine** | Rust (PyO3) | Pure Python | Pure Python | Pure Python |
| **10 built-in levels** | Yes | Partial | No | No |
| **Custom levels** | Yes | Yes | No | Manual |
| **Multiple sinks** | Yes | Yes | No | Yes |
| **JSON serialization** | Yes | Yes | Yes | Formatter dependent |
| **Pretty JSON** | Yes | Custom formatter | Yes | Formatter dependent |
| **Custom format strings** | Yes | Yes | No | Formatter dependent |
| **Callable formatting** | Yes | Yes | Processor based | Formatter based |
| **Level filtering** | Yes | Yes | No | Yes |
| **Callable filtering** | Yes | Yes | Processor based | Filter based |
| **Context binding** | Yes | Yes | Yes | Adapter based |
| **Scoped context** | Yes | Yes | Contextvars processors | No |
| **Record patching** | Yes | Yes | Processor based | No |
| **Exception catching** | Yes | Yes | No | No |
| **File rotation** | Yes | Yes | No | Handler dependent |
| **Retention** | Yes | Yes | No | Handler dependent |
| **Compression** | Yes | Yes | No | Handler dependent |
| **Background workers** | Yes | Yes | No | QueueHandler |
| **HTTP logging** | Yes | Custom sink | No | No |
| **TCP/UDP logging** | Yes | Custom sink | No | SocketHandler |
| **Syslog** | Yes | Custom sink | No | SysLogHandler |
| **FastAPI integration** | Yes | Community/manual | No | No |
| **Django integration** | Yes | Community/manual | No | DictConfig |
| **Flask integration** | Yes | Community/manual | No | Manual |
| **Rich console** | Yes | Yes | No | Manual |
| **OpenTelemetry** | Yes | Custom sink | Processor based | Manual |
| **Prometheus** | Yes | Custom sink | No | Manual |
| **Pydantic config** | Yes | No | No | No |
| **Type stubs** | Yes | Partial | Yes | No |
| **Zero unsafe Rust** | Yes | N/A | N/A | N/A |

## Migration Pattern

Start by configuring sinks explicitly at startup, then pass `logger` or
independent `Logger()` instances into the components that need logging.

## Migrating From Loguru

Most day-to-day calls are intentionally familiar:

```python
from logly import logger

logger.add("app.log", rotation="10 MB", retention="7 days", compression="gzip")
logger.bind(request_id="req-123").info("request accepted")
```

Use `Logger()` for independent sink sets:

```python
from logly import Logger

api_logger = Logger()
worker_logger = Logger()

api_logger.add("api.log")
worker_logger.add("worker.log")
```
