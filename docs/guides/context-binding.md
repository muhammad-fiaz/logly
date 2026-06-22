---
title: Context Binding
description: Bind persistent fields, contextualize scopes, and patch records
---

# Context Binding

Context binding attaches persistent key-value pairs to log records, making it easy to track request IDs, user IDs, and other metadata.

## bind() - Persistent Fields

`bind()` returns a new logger view with persistent fields:

```python
from logly import logger

# Bind fields to a logger
app_logger = logger.bind(user_id="12345", request_id="abc-789")
app_logger.info("User logged in")
# Output includes: user_id=12345 request_id=abc-789

# All subsequent logs include bound fields
app_logger.info("Processing request")
app_logger.warning("Rate limit approaching")
```

### Nested Bind

```python
from logly import logger

# Bind accumulates
base = logger.bind(service="api")
with_request = base.bind(request_id="req-123")
with_user = with_request.bind(user_id="user-456")

with_user.info("Request processed")
# Includes: service, request_id, user_id
```

### Bind Does Not Mutate Parent

```python
from logly import logger

original = logger.bind(env="production")
child = original.bind(request_id="123")

original.info("Parent log")  # Only has env
child.info("Child log")      # Has both env and request_id
```

## contextualize() - Scoped Context

`contextualize()` temporarily binds values for the current scope (thread/async-safe):

```python
from logly import logger

# Context manager
with logger.contextualize(request_id="req-123"):
    logger.info("Processing request")
    logger.info("Still in context")
    # Both logs include request_id

# Context is restored after the block
logger.info("Outside context")  # No request_id
```

### Nested Contexts

```python
from logly import logger

with logger.contextualize(service="api"):
    with logger.contextualize(endpoint="/users"):
        with logger.contextualize(method="GET"):
            logger.info("Handling request")
            # Includes: service, endpoint, method
```

### Async Context

```python
import asyncio
from logly import logger

async def handle_request(request_id: str):
    with logger.contextualize(request_id=request_id):
        logger.info("Starting request")
        await process()
        logger.info("Request complete")

# Each concurrent request gets its own context
asyncio.gather(
    handle_request("req-1"),
    handle_request("req-2"),
)
```

## patch() - Record Mutation

`patch()` adds a function that mutates each log record before dispatch:

```python
from logly import logger

# Add a field to all records
def add_version(record: dict) -> None:
    record.setdefault("extra", {})["version"] = "1.0.0"

patched_logger = logger.patch(add_version)
patched_logger.info("With version")
# Output includes: version=1.0.0

# Multiple patchers
def add_env(record: dict) -> None:
    record.setdefault("extra", {})["env"] = "production"

def add_region(record: dict) -> None:
    record.setdefault("extra", {})["region"] = "us-east-1"

patched = logger.patch(add_env).patch(add_region)
patched.info("With env and region")
```

### Per-Sink Patch

```python
from logly import logger

def enrich_record(record: dict) -> None:
    extra = record.setdefault("extra", {})
    extra["env"] = "production"
    extra["region"] = "us-east-1"
    extra["version"] = "2.0"

logger.add("enriched.log", patch=enrich_record)
logger.info("Enriched log entry")
```

### Patch Does Not Mutate Parent

```python
from logly import logger

def add_field(record: dict) -> None:
    record.setdefault("extra", {})["patched"] = "yes"

original = logger.bind(env="prod")
patched = original.patch(add_field)

original.info("Original")  # No "patched" field
patched.info("Patched")    # Has "patched" field
```

## Combining Context Features

```python
from logly import logger

# Bind for persistent fields
base_logger = logger.bind(service="api", version="1.0")

# Patch for record enrichment
def add_timestamp(record: dict) -> None:
    record.setdefault("extra", {})["logged_at"] = "2026-06-21"

enriched = base_logger.patch(add_timestamp)

# Contextualize for request scope
with logger.contextualize(request_id="req-123"):
    enriched.info("Processing request")
    # Includes: service, version, logged_at, request_id
```
