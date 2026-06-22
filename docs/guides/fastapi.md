---
title: FastAPI Integration
description: ASGI middleware for request-scoped logging in FastAPI
---

# FastAPI Integration

`LoglyMiddleware` adds request metadata to the logging context for each request.

## Basic Setup

```python
from fastapi import FastAPI
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}
```

## What It Captures

The middleware automatically contextualizes these fields:

| Field | Description | Example |
|-------|-------------|---------|
| `request_id` | Unique request identifier | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| `method` | HTTP method | `GET` |
| `path` | Request path | `/api/users` |
| `client` | Client IP:port | `192.168.1.1:54321` |
| `user_agent` | User-Agent header | `Mozilla/5.0...` |

## Request Logging

```python
from fastapi import FastAPI
from logly import logger
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info("Fetching user {}", user_id)
    # Output: INFO | Fetching user 123 | request_id=... method=GET path=/users/123
    return {"user_id": user_id}

@app.post("/users")
async def create_user():
    logger.info("Creating user")
    # Output includes request context
    return {"created": True}
```

## With Custom Format

```python
from fastapi import FastAPI
from logly import logger
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)

# Add console sink with request context in format
logger.add(
    "stderr",
    level="INFO",
    format="{time:HH:mm:ss} | {level:<8} | {extra[request_id]} | {extra[method]} {extra[path]} | {message}",
    colorize=True,
)

@app.get("/")
async def root():
    logger.info("Request received")
    return {"message": "Hello"}
```

## Error Handling

```python
from fastapi import FastAPI, HTTPException
from logly import logger
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id == 0:
        logger.error("Invalid item ID: {}", item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("Item {} fetched", item_id)
    return {"item_id": item_id}
```

## With Stdlib Integration

```python
import logging
from fastapi import FastAPI
from logly import logger
from logly.integrations.fastapi import LoglyMiddleware
from logly.integrations.stdlib import InterceptHandler

app = FastAPI()
app.add_middleware(LoglyMiddleware)

# Route uvicorn logging through Logly
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
```
