---
title: Environment Variables
description: Control Logly behavior with environment variables
---

# Environment Variables

Logly supports environment variables to control initialization behavior.

## LOGLY_AUTOINIT

Controls whether Logly automatically adds a stderr sink on import.

### Default Behavior

By default, Logly adds a `stderr` sink with `level="DEBUG"` when the module is first imported. This ensures log messages are visible immediately without any configuration.

```python
from logly import logger
# stderr sink is already active at DEBUG level
logger.info("This prints to stderr immediately")
```

### Disabling Auto-Init

Set `LOGLY_AUTOINIT` to `false`, `0`, or `no` to prevent the automatic stderr sink:

```bash
# Linux/macOS
export LOGLY_AUTOINIT=false

# Windows
set LOGLY_AUTOINIT=false
```

```python
from logly import logger
# No sinks configured - you must add your own
logger.add("app.log", level="INFO")
logger.info("This only goes to app.log")
```

### Values

| Value | Behavior |
|-------|----------|
| `true` (default) | Auto-add stderr sink |
| `false` | No automatic sink |
| `0` | No automatic sink |
| `no` | No automatic sink |

### Common Patterns

**Development** (default):

```bash
# Sinks: stderr at DEBUG level (automatic)
export LOGLY_AUTOINIT=true
```

**Production** (explicit configuration):

```python
import os
os.environ["LOGLY_AUTOINIT"] = "false"

from logly import logger

logger.add("logs/app.log", level="INFO", rotation="daily", compression="gzip")
logger.add("logs/errors.log", level="ERROR")
```

**Testing** (disable for clean output):

```bash
LOGLY_AUTOINIT=false python -m pytest
```

**Docker**:

```dockerfile
ENV LOGLY_AUTOINIT=false
```
