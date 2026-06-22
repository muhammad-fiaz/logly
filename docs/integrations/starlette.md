---
title: Starlette
description: ASGI middleware for Starlette applications.
---

# Starlette

`LoglyMiddleware` adds `request_id`, `method`, `path`, `client`, and `user_agent` to the Logly context for each request. Logs timing and exceptions automatically.

## Installation

This integration requires the `starlette` package.

::: code-group

```bash [uv]
uv add logly[starlette]
```

```bash [pip]
pip install "logly[starlette]"
```

```bash [uv (without extras)]
uv add starlette
```

```bash [pip (without extras)]
pip install starlette
```

:::

::: warning Missing Dependency
If `starlette` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'starlette'
```
:::

## Usage

```python
from starlette.applications import Starlette
from logly.integrations.starlette import LoglyMiddleware

app = Starlette()
app.add_middleware(LoglyMiddleware)
```

## Full Example

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from logly import logger
from logly.integrations.starlette import LoglyMiddleware

async def homepage(request):
    logger.info("Homepage accessed")
    return JSONResponse({"message": "Hello World"})

async def item(request):
    item_id = request.path_params["item_id"]
    logger.debug("Fetching item {}", item_id)
    return JSONResponse({"item_id": item_id})

app = Starlette(routes=[
    Route("/", homepage),
    Route("/items/{item_id}", item),
])
app.add_middleware(LoglyMiddleware)
```
