---
title: Comparison
description: Feature comparison between Logly, Loguru, structlog, and stdlib logging
---

# Comparison

Logly is a high-performance logging alternative with a Rust-native engine. It provides a clean, intuitive API with 10 built-in log levels, flexible sinks, file rotation, compression, and first-class framework integrations.

## Feature Matrix

| Capability | Logly | Loguru | structlog | stdlib logging |
|------------|-------|--------|-----------|----------------|
| **Engine** | Rust (PyO3) | Pure Python | Pure Python | Pure Python |
| **10 built-in levels** | ✅ | ✅ | ❌ | ❌ |
| **Custom levels** | ✅ | ✅ | ❌ | Manual |
| **Multiple sinks** | ✅ | ✅ | ❌ | ✅ |
| **JSON serialization** | ✅ | ✅ | ✅ | Formatter dependent |
| **Custom format strings** | ✅ | ✅ | ❌ | Formatter dependent |
| **Level filtering** | ✅ | ✅ | ❌ | ✅ |
| **Callable filtering** | ✅ | ✅ | ❌ | ❌ |
| **Context binding** | ✅ | ✅ | ✅ | Adapter based |
| **Scoped context** | ✅ | ✅ | ❌ | ❌ |
| **Record patching** | ✅ | ✅ | ❌ | ❌ |
| **Exception catching** | ✅ | ✅ | ❌ | ❌ |
| **File rotation** | ✅ | ✅ | ❌ | Handler dependent |
| **Compression** | ✅ | ✅ | ❌ | Handler dependent |
| **Background workers** | ✅ | ✅ | ❌ | QueueHandler |
| **HTTP logging** | ✅ | ✅ | ❌ | ❌ |
| **TCP/UDP logging** | ✅ | ✅ | ❌ | ❌ |
| **Syslog** | ✅ | ✅ | ❌ | ❌ |
| **FastAPI integration** | ✅ | ✅ | ❌ | ❌ |
| **Django integration** | ✅ | ✅ | ❌ | ❌ |
| **Flask integration** | ✅ | ✅ | ❌ | ❌ |
| **Rich console** | ✅ | ✅ | ❌ | ❌ |
| **OpenTelemetry** | ✅ | ✅ | ❌ | ❌ |
| **Prometheus** | ✅ | ✅ | ❌ | ❌ |
| **Elasticsearch** | ✅ | ✅ | ❌ | ❌ |
| **Sentry** | ✅ | ✅ | ❌ | ❌ |
| **Pydantic config** | ✅ | ❌ | ❌ | ❌ |
| **Type stubs** | ✅ | ❌ | ✅ | ❌ |
| **Zero unsafe Rust** | ✅ | N/A | N/A | N/A |

## Switching from Loguru

```python
# Before (Loguru)
from loguru import logger
logger.add("app.log", rotation="10 MB", retention="7 days")

# After (Logly)
from logly import logger
logger.add("app.log", rotation="10 MB", retention="7 days")
```

::: info Note
If you're currently using Loguru, switching to Logly is straightforward — just change your imports.
:::
