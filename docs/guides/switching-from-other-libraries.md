---
title: Switching From Other Libraries
description: How to migrate from common Python logging libraries to Logly.
---

# Switching From Other Libraries

Logly works best when sinks are configured explicitly at application startup.
After that, pass either the module-level `logger` or independent `Logger()`
instances to components that need logging.

## Common Migration Steps

1. Replace imports with `from logly import logger` or `from logly import Logger`.
2. Add sinks with `logger.add(...)`.
3. Use `logger.bind(...)` for persistent context.
4. Use `logger.contextualize(...)` for request-scoped fields.
5. Call `logger.complete()` before process shutdown when using queued sinks.

## From Loguru

Replace the import and keep the same application-level sink setup shape:

```python
from logly import logger

logger.add("app.log", rotation="10 MB", retention="7 days", compression="gzip")
logger.info("service started")
```

For contextual logging:

```python
request_logger = logger.bind(request_id="req-123")
request_logger.info("request accepted")
```

For isolated handlers, use independent `Logger()` instances instead of bound
views.

## From `logging`

Use the stdlib bridge when you cannot change all call sites at once:

```python
import logging
from logly.integrations.stdlib import InterceptHandler

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
```

## From Structlog

Start with `bind()` and `contextualize()` for structured context:

```python
from logly import logger

log = logger.bind(service="billing")
log.info("invoice created")
```

## Independent Loggers

Use independent `Logger()` instances when separate subsystems need completely
separate sink sets.

```python
from logly import Logger

api_logger = Logger()
worker_logger = Logger()

api_logger.add("api.log", level="INFO")
worker_logger.add("worker.log", level="DEBUG")

api_logger.info("request accepted")
worker_logger.debug("job claimed")
```
