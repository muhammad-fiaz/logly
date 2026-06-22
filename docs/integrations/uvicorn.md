---
title: Uvicorn
description: Log configuration for Uvicorn servers.
---

# Uvicorn

Routes Uvicorn access and error logs through Logly. Use `setup_uvicorn_logging()` or pass `get_log_config()` to uvicorn.

## Installation

This integration requires the `uvicorn` package.

::: code-group

```bash [uv]
uv add logly[uvicorn]
```

```bash [pip]
pip install "logly[uvicorn]"
```

```bash [uv (without extras)]
uv add uvicorn
```

```bash [pip (without extras)]
pip install uvicorn
```

:::

::: warning Missing Dependency
If `uvicorn` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'uvicorn'
```
:::

## Usage

```python
import uvicorn
from logly.integrations.uvicorn import setup_uvicorn_logging

setup_uvicorn_logging()
uvicorn.run("app:app")
```

## Log Config

```python
import uvicorn
from logly.integrations.uvicorn import get_log_config

uvicorn.run("app:app", log_config=get_log_config())
```

## Full Example

```python
import uvicorn
from fastapi import FastAPI
from logly.integrations.uvicorn import setup_uvicorn_logging

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    setup_uvicorn_logging(level="INFO")
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
```
