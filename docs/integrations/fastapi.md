---
title: FastAPI
description: ASGI middleware for FastAPI with automatic request context.
---

# FastAPI

`LoglyMiddleware` adds `request_id`, `method`, `path`, `client`, and `user_agent` to the Logly context for each request. It logs timing and exceptions automatically.

## Installation

This integration requires the `fastapi` and `starlette` packages.

::: code-group

```bash [uv]
uv add logly[fastapi]
```

```bash [pip]
pip install "logly[fastapi]"
```

```bash [uv (without extras)]
uv add fastapi starlette
```

```bash [pip (without extras)]
pip install fastapi starlette
```

:::

::: warning Missing Dependency
If `fastapi` or `starlette` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'fastapi'
```
:::

## Usage

```python
from fastapi import FastAPI
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)
```

## Captured Fields

| Field | Source |
|-------|--------|
| `request_id` | UUID generated per request |
| `method` | HTTP method (GET, POST, etc.) |
| `path` | Request path |
| `client` | Client IP address |
| `user_agent` | User-Agent header |

## Full Example

```python
from fastapi import FastAPI
from logly import logger
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)

@app.get("/")
async def root():
    logger.info("Handling request")
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    logger.debug("Fetching item {}", item_id)
    return {"item_id": item_id}
```
