---
title: Gunicorn
description: Worker hooks for Gunicorn logging.
---

# Gunicorn

`LoglyWorker` is a Gunicorn worker class that routes all worker logs through Logly. `setup_gunicorn_logging()` configures Gunicorn loggers manually.

## Installation

This integration requires the `gunicorn` package.

::: code-group

```bash [uv]
uv add logly[gunicorn]
```

```bash [pip]
pip install "logly[gunicorn]"
```

```bash [uv (without extras)]
uv add gunicorn
```

```bash [pip (without extras)]
pip install gunicorn
```

:::

::: warning Missing Dependency
If `gunicorn` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'gunicorn'
```
:::

## Usage

```python
# gunicorn.conf.py
worker_class = "logly.integrations.gunicorn.LoglyWorker"
```

## Manual Setup

```python
# gunicorn.conf.py
from logly.integrations.gunicorn import setup_gunicorn_logging
setup_gunicorn_logging(level="INFO")
```

## Full Example

```python
# gunicorn.conf.py
from logly.integrations.gunicorn import LoglyWorker, setup_gunicorn_logging

# Option 1: Use LoglyWorker
worker_class = "logly.integrations.gunicorn.LoglyWorker"
bind = "0.0.0.0:8000"
workers = 4

# Option 2: Manual setup (if using default worker)
# setup_gunicorn_logging(level="INFO")
# bind = "0.0.0.0:8000"
# workers = 4
```
