---
title: Configure
description: Bulk configuration with logger.configure()
---

# Configure

The `logger.configure()` method provides a declarative way to replace the entire logging configuration at once.

## Basic Usage

```python
from logly import logger

logger.configure(
    handlers=[
        {"sink": "stderr", "level": "INFO"},
        {"sink": "app.log", "level": "DEBUG", "rotation": "daily"},
    ],
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `handlers` | `list[dict] \| None` | List of handler dicts. Each dict is passed to `logger.add()`. |
| `levels` | `list[dict] \| None` | Custom levels to register. Each dict has `name`, `no`, `color`. |
| `extra` | `dict \| None` | Default extra context fields added to all records. |
| `patcher` | `Callable \| None` | Function applied to every log record before dispatch. |
| `activation` | `list[tuple[str, bool]] \| None` | Enable/disable logger names by pattern. |

## Handlers

Each handler dict maps directly to `logger.add()` parameters:

```python
logger.configure(
    handlers=[
        {
            "sink": "stderr",
            "level": "INFO",
            "format": "{time:HH:mm:ss} | {level:<8} | {message}",
            "colorize": True,
        },
        {
            "sink": "logs/app.log",
            "level": "DEBUG",
            "rotation": "daily",
            "retention": "30 days",
            "compression": "gzip",
            "serialize": True,
        },
        {
            "sink": "logs/errors.log",
            "level": "ERROR",
            "rotation": "daily",
            "retention": "90 days",
        },
    ],
)
```

::: warning
Calling `logger.configure(handlers=[...])` **removes all existing handlers** before adding the new ones.
:::

## Levels

Register custom levels during configuration:

```python
logger.configure(
    levels=[
        {"name": "SECURITY", "no": 45, "color": "<red><bold>"},
        {"name": "METRIC", "no": 28, "color": "<blue>"},
        {"name": "AUDIT", "no": 35, "color": "<magenta>"},
    ],
    handlers=[
        {"sink": "stderr", "level": "INFO"},
    ],
)
```

## Extra Context

Bind default extra fields to all log records:

```python
logger.configure(
    extra={
        "service": "api",
        "version": "1.0.0",
        "environment": "production",
    },
)

logger.info("Server started")
# Output includes: service=api version=1.0.0 environment=production
```

## Patcher

Apply a mutation function to every log record:

```python
def enrich_records(record: dict) -> None:
    record.setdefault("extra", {})["hostname"] = socket.gethostname()
    record.setdefault("extra", {})["pid"] = os.getpid()

logger.configure(patcher=enrich_records)
logger.info("This has hostname and pid automatically")
```

## Activation

Enable or disable logger names by pattern:

```python
logger.configure(
    activation=[
        ("myapp.*", True),       # Enable myapp.*
        ("debug.*", False),       # Disable debug.*
        ("third_party.*", False), # Disable noisy third-party loggers
    ],
)
```

## Complete Example

```python
from logly import logger

logger.configure(
    handlers=[
        {"sink": "stderr", "level": "INFO", "colorize": True},
        {"sink": "logs/app.log", "level": "DEBUG", "rotation": "daily", "retention": "7 days"},
        {"sink": "logs/errors.log", "level": "ERROR", "serialize": True},
    ],
    levels=[
        {"name": "SECURITY", "no": 45, "color": "<red><bold>"},
    ],
    extra={"service": "api", "env": "prod"},
    patcher=lambda r: r.setdefault("extra", {}).setdefault("region", "us-east-1"),
    activation=[
        ("uvicorn.*", False),
        ("third_party.*", False),
    ],
)
```

## Programmatic vs Declarative

| Approach | Method | Use Case |
|----------|--------|----------|
| **Programmatic** | `logger.add()` | Add sinks one at a time, dynamic configuration |
| **Declarative** | `logger.configure()` | Replace entire config at once, startup configuration |
