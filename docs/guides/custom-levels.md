---
title: Custom Levels
description: Register and use custom log levels with priorities and colors
---

# Custom Levels

Logly has 10 built-in levels, but you can register custom levels with your own priorities and colors.

## Registering Custom Levels

```python
from logly import logger

# Register with priority and color
logger.level("AUDIT", no=25, color="<magenta>")
logger.level("SECURITY", no=35, color="<red><bold>")
logger.level("METRIC", no=28, color="<blue>")

# Use them
logger.log("AUDIT", "User action recorded")
logger.log("SECURITY", "Unauthorized access attempt")
logger.log("METRIC", "Response time: 235ms")
```

## Priority Ordering

Custom levels are ordered by priority. Choose priorities that fit between built-in levels:

| Built-in | Priority | Custom levels fit at |
|----------|----------|---------------------|
| TRACE | 5 | |
| DEBUG | 10 | |
| INFO | 20 | |
| NOTICE | 25 | |
| SUCCESS | 30 | |
| | | AUDIT (25), METRIC (28) |
| WARNING | 40 | |
| | | SECURITY (35) |
| ERROR | 50 | |
| FAIL | 55 | |
| CRITICAL | 60 | |
| FATAL | 70 | |

## Inspecting Levels

```python
from logly import logger

# Inspect a level
name, priority, color = logger.level("AUDIT")
print(f"Name: {name}, Priority: {priority}, Color: {color}")

# List all registered levels
print("All levels:", logger.levels)
# ['TRACE', 'DEBUG', 'INFO', 'NOTICE', 'SUCCESS', 'AUDIT', 'WARNING', 'METRIC', ...]
```

## Using Custom Levels with Sinks

```python
from logly import logger

# Register custom level
logger.level("AUDIT", no=25, color="<magenta>")

# Add sink that only receives AUDIT and above
logger.add("audit.log", level="AUDIT")

# Add sink for SECURITY and above
logger.add("security.log", level="SECURITY")

# Usage
logger.log("AUDIT", "User login")
logger.log("SECURITY", "Password changed")
```

## Custom Level with Extra Data

```python
from logly import logger

logger.level("METRIC", no=28, color="<blue>")

# Bind extra fields with custom level
logger.bind(response_time=235).log("METRIC", "Request completed")
logger.bind(cpu_usage=85.2).log("METRIC", "CPU spike detected")
```

## Custom Level Examples

```python
from logly import logger

# Audit logging
logger.level("AUDIT", no=25, color="<magenta>")
logger.add("audit.log", level="AUDIT", format="{time} | {level} | {message}")

# Security events
logger.level("SECURITY", no=35, color="<red><bold>")
logger.add("security.log", level="SECURITY", serialize=True)

# Performance metrics
logger.level("METRIC", no=28, color="<blue>")
logger.add("metrics.log", level="METRIC", format="{time:HH:mm:ss} | {message}")

# Usage
logger.log("AUDIT", "User alice logged in from 10.0.0.1")
logger.log("SECURITY", "Failed login attempt for user bob")
logger.log("METRIC", "GET /api/users 200 235ms")
```

## Level Registration from Native API

```python
from logly._logly import register_custom_level, inspect_level, list_levels

# Register via native API
register_custom_level("CUSTOM", 30, None)

# Inspect
name, priority, color = inspect_level("CUSTOM")
print(f"{name}: priority={priority}, color={color}")

# List all
print(list_levels())
```
