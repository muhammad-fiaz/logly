---
title: Environment Variables
description: Control Logly behavior with environment variables
---

# Environment Variables

Logly supports environment variables to control initialization and configuration.

## LOGLY_AUTOINIT

Controls whether Logly automatically adds a stderr sink on import.

### Default Behavior

By default, Logly adds a `stderr` sink with `level="DEBUG"` when the module is first imported:

```python
from logly import logger

# stderr sink is already active at DEBUG level
logger.info("This prints to stderr immediately")
```

### Disabling Auto-Init

Set `LOGLY_AUTOINIT` to `false`, `0`, or `no` to prevent the automatic stderr sink:

```bash
export LOGLY_AUTOINIT=false
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

## LOGLY_* Configuration Overrides

These environment variables configure the automatic stderr sink described
above. Unrecognized values fall back to the defaults.

| Variable | Purpose | Example |
|----------|---------|---------|
| `LOGLY_LEVEL` | Sink log level (default `"DEBUG"`) | `LOGLY_LEVEL=WARNING` |
| `LOGLY_FORMAT` | Sink format string | `LOGLY_FORMAT="{level} \| {message}"` |
| `LOGLY_COLORIZE` | Enable/disable colors (`YES`/`NO`) | `LOGLY_COLORIZE=NO` |
| `LOGLY_SERIALIZE` | Enable/disable JSON output (`YES`/`NO`) | `LOGLY_SERIALIZE=YES` |

### Usage

```bash
# Disable colors
export LOGLY_COLORIZE=NO

# Force JSON output
export LOGLY_SERIALIZE=YES

# Set minimum level
export LOGLY_LEVEL=WARNING
```

```python
from logly import logger

# Configuration applied from environment
logger.info("This respects env overrides")
```

## Common Patterns

**Development** (default):

```bash
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
