---
title: PropagateHandler
description: Bridge Logly messages back to Python's standard logging module.
---

# PropagateHandler

The `PropagateHandler` bridges Logly messages back to Python's standard `logging` module.

## Usage

```python
from logly import logger
from logly.integrations.propagate import PropagateHandler

# Add PropagateHandler as a sink
logger.add(PropagateHandler(), format="{message}")
```

## Custom Logger Name

```python
logger.add(
    PropagateHandler(name="myapp"),
    format="{message}",
    level="INFO",
)
```

## How It Works

- Routes all Logly messages through Python's standard `logging` module
- Automatically maps Logly levels to stdlib levels
- Useful when you need to feed Logly output into existing monitoring tools that hook into stdlib logging

## Level Mapping

| Logly Level | stdlib Level |
|-------------|-------------|
| TRACE, DEBUG | DEBUG |
| INFO, NOTICE, SUCCESS | INFO |
| WARNING, WARN | WARNING |
| ERROR, FAIL | ERROR |
| CRITICAL, FATAL | CRITICAL |
