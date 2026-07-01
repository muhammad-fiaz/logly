---
title: File Directories & Root Directory
description: Configure custom directories and root paths for log files in Logly
---

# File Directories & Root Directory

Logly's `root_dir()` method sets a default directory for all relative file paths passed to `add()`. This simplifies configuration by allowing you to specify a single base path instead of repeating it for every sink.

## `root_dir()` Method

### Basic Usage

```python
from logly import logger

# Set root directory
logger.root_dir("/var/log/myapp")

# These paths are relative to the root
logger.add("app.log")          # /var/log/myapp/app.log
logger.add("errors.log")       # /var/log/myapp/errors.log
logger.add("access.log")       # /var/log/myapp/access.log
```

::: info
`root_dir()` creates the directory if it doesn't exist, including all parent directories.
:::

### With Path Objects

```python
from pathlib import Path
from logly import logger

logger.root_dir(Path("/var/log/myapp"))
logger.add("app.log")  # /var/log/myapp/app.log
```

### Relative Paths

```python
from logly import logger

logger.root_dir("/var/log/myapp")

# All of these resolve relative to root_dir
logger.add("app.log")                          # /var/log/myapp/app.log
logger.add("errors/app.log")                   # /var/log/myapp/errors/app.log
logger.add("modules/auth/auth.log")            # /var/log/myapp/modules/auth/auth.log
```

## How `root_dir` Interacts with `add()`

### Relative Paths

When `root_dir` is set, relative paths are resolved against it:

```python
from logly import logger

logger.root_dir("/var/log/myapp")

logger.add("app.log")          # Resolves to /var/log/myapp/app.log
logger.add("subdir/app.log")   # Resolves to /var/log/myapp/subdir/app.log
```

### Absolute Paths

Absolute paths are unaffected by `root_dir`:

```python
from logly import logger

logger.root_dir("/var/log/myapp")

logger.add("/tmp/debug.log")              # /tmp/debug.log (not affected)
logger.add("/var/log/system.log")         # /var/log/system.log (not affected)
```

### stdout/stderr

Console outputs are not affected by `root_dir`:

```python
from logly import logger

logger.root_dir("/var/log/myapp")

logger.add("stderr")           # stderr (not affected)
logger.add("stdout")           # stdout (not affected)
logger.add(sys.stderr)         # stderr (not affected)
```

## Creating Directories Automatically

```python
from logly import logger

# root_dir creates the directory tree
logger.root_dir("/var/log/myapp/modules/auth")

# All parent directories are created
logger.add("auth.log")  # /var/log/myapp/modules/auth/auth.log
```

::: warning
Directory creation requires write permissions to the parent path. The method will raise an error if the directory cannot be created.
:::

## Production Directory Setup Patterns

### Standard Production Layout

```python
from logly import logger

# Production root
logger.root_dir("/var/log/myapp")

# Application logs
logger.add(
    "app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Error logs
logger.add(
    "errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    compression="gzip",
)

# Access logs
logger.add(
    "access.log",
    level="INFO",
    rotation="daily",
    retention="7 days",
)
```

### Multi-Service Layout

```python
from logly import logger

logger.root_dir("/var/log/services")

# API service logs
logger.add("api/app.log", level="INFO", rotation="daily")
logger.add("api/errors.log", level="ERROR", rotation="daily")

# Worker service logs
logger.add("worker/app.log", level="INFO", rotation="daily")
logger.add("worker/errors.log", level="ERROR", rotation="daily")

# Gateway logs
logger.add("gateway/access.log", level="INFO", rotation="hourly")
```

### Development Layout

```python
from logly import logger
from pathlib import Path

# Use current directory for development
logger.root_dir(Path.cwd() / "logs")

logger.add("dev.log", level="DEBUG")
logger.add("errors.log", level="ERROR")
```

## Environment Variable-Based Directory Configuration

```python
import os
from logly import logger

# Configure log directory from environment
log_dir = os.environ.get("LOGLY_LOG_DIR", "/var/log/myapp")
logger.root_dir(log_dir)

logger.add(
    "app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)
```

### Using Different Directories Per Environment

```python
import os
from logly import logger

env = os.environ.get("APP_ENV", "development")

if env == "production":
    logger.root_dir("/var/log/myapp")
elif env == "staging":
    logger.root_dir("/var/log/myapp-staging")
else:
    logger.root_dir("./logs")

logger.add("app.log", level="INFO", rotation="daily")
```

### Docker/Kubernetes Setup

```python
import os
from logly import logger

# In containers, use a mounted volume
log_dir = os.environ.get("LOGLY_LOG_DIR", "/var/log/app")
logger.root_dir(log_dir)

logger.add(
    "app.log",
    level="INFO",
    rotation="100 MB",
    retention="7 days",
    compression="gzip",
    enqueue=True,
)
```

## Subdirectories

### Automatic Subdirectory Creation

```python
from logly import logger

logger.root_dir("/var/log/myapp")

# Creates subdirectories as needed
logger.add("modules/auth/auth.log")     # Creates modules/auth/
logger.add("modules/db/db.log")         # Creates modules/db/
logger.add("http/requests.log")         # Creates http/
```

### Organized by Component

```python
from logly import logger

logger.root_dir("/var/log/myapp")

# Web server logs
logger.add("web/access.log", level="INFO", rotation="daily")
logger.add("web/error.log", level="ERROR", rotation="daily")

# Database logs
logger.add("db/slow-queries.log", level="WARNING", rotation="daily")
logger.add("db/errors.log", level="ERROR", rotation="daily")

# Background worker logs
logger.add("worker/tasks.log", level="INFO", rotation="daily")
logger.add("worker/errors.log", level="ERROR", rotation="daily")
```

## Complete Example

```python
import os
from logly import logger

# Configure root directory from environment
log_root = os.environ.get("LOGLY_LOG_DIR", "/var/log/myapp")
logger.root_dir(log_root)

# Application logs
logger.add(
    "app.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    enqueue=True,
)

# Error logs
logger.add(
    "errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    compression="gzip",
    enqueue=True,
)

# Debug logs (development only)
if os.environ.get("APP_ENV") != "production":
    logger.add(
        "debug.log",
        level="DEBUG",
        rotation="10 MB",
        retention=5,
    )

# Structured JSON logs
logger.add(
    "structured.json",
    level="WARNING",
    serialize=True,
    rotation="daily",
    retention="60 days",
    compression="gzip",
)

# Console output
logger.add("stderr", level="INFO", colorize=True)

# Log with context
logger.info("Application started in {}", os.environ.get("APP_ENV", "development"))
logger.complete()
```

## Troubleshooting

### Permission Denied

If `root_dir()` fails with a permission error, ensure the process has write access to the parent directory:

```python
from logly import logger

try:
    logger.root_dir("/var/log/myapp")
except PermissionError:
    # Fall back to user directory
    logger.root_dir(os.path.expanduser("~/logs"))
```

### Directory Already Exists

```python
from logly import logger

# This is safe - root_dir won't fail if directory exists
logger.root_dir("/var/log/myapp")  # Works even if directory already exists
```

### Path Does Not Exist Yet

```python
from logly import logger

# root_dir creates the full path including parent directories
logger.root_dir("/var/log/myapp/subdir/deep")
# All directories are created automatically
```
