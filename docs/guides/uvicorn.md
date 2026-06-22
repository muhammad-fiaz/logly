# Uvicorn Integration

Logly integrates with Uvicorn to provide structured logging for ASGI applications.

## Quick Setup

```python
import uvicorn
from logly.integrations.uvicorn import setup_uvicorn_logging

setup_uvicorn_logging()
uvicorn.run("app:app")
```

## Using log_config

```python
import uvicorn
from logly.integrations.uvicorn import get_log_config

uvicorn.run("app:app", log_config=get_log_config())
```

## Configuration

```python
setup_uvicorn_logging(
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)
```

## With FastAPI

```python
from fastapi import FastAPI
from logly.integrations.uvicorn import setup_uvicorn_logging

app = FastAPI()

@app.on_event("startup")
async def startup():
    setup_uvicorn_logging()
```

## How It Works

- Replaces Uvicorn's logging handlers with Logly's `InterceptHandler`
- Routes `uvicorn`, `uvicorn.error`, and `uvicorn.access` loggers through Logly
- Supports all Logly features: custom levels, filtering, rotation, etc.
