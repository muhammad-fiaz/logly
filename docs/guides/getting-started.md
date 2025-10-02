---
title: Getting Started Guide - Logly
description: Complete getting started guide for Logly Python logging library. Learn installation, basic setup, and core concepts.
keywords: python, logging, guide, getting started, tutorial, installation, setup, logly
---

# Getting Started Guide

Welcome to Logly! This guide will walk you through installing Logly and setting up your first logging configuration. By the end, you'll have a working logging setup that you can customize for your needs.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **pip** package manager
- Basic familiarity with Python

## Step 1: Installation

=== "pip (Recommended)"
    ```bash
    pip install logly
    ```

=== "uv"
    ```bash
    uv add logly
    ```

=== "poetry"
    ```bash
    poetry add logly
    ```

=== "From Source"
    ```bash
    git clone https://github.com/muhammad-fiaz/logly.git
    cd logly
    pip install -e .
    ```

## Step 2: Basic Setup

Create a new Python file and add this basic setup:

```python
# app.py
from logly import logger

# Configure logging
logger.configure(
    level="INFO",  # Minimum log level
    format="{time} | {level} | {message}"  # Log format
)

# Your application code
logger.info("Application started")
logger.warning("This is a warning")
logger.error("This is an error")

print("Check your console output above!")
```

Run it:
```bash
python app.py
```

You should see colored output like:
```
2025-01-15 10:30:45 | INFO  | Application started
2025-01-15 10:30:45 | WARN  | This is a warning
2025-01-15 10:30:45 | ERROR | This is an error
```

## Step 3: Understanding the Basics

### Log Levels

Logly supports standard logging levels:

```python
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical errors")
```

### Extra Data

Add extra fields to your logs:

```python
logger.info("Request processed",
           method="POST",
           url="/api/users",
           status_code=200,
           response_time=0.145)
```

## Step 4: File Logging

Let's add file logging to persist your logs:

```python
from logly import logger

logger.configure(
    level="INFO",
    format="{time} | {level} | {message}",
    sinks=[
        {
            "type": "console"  # Keep console logging
        },
        {
            "type": "file",
            "path": "app.log"  # Log to file
        }
    ]
)

logger.info("This goes to both console and file")
```

Now check `app.log` - it should contain your log messages.

## Step 5: Adding Context

Context helps track related operations:

```python
from logly import logger

# Set up logging
logger.configure(
    level="INFO",
    format="{time} | {level} | {context} | {message}"
)

# Add persistent context
logger.bind(user_id=12345, session_id="abc-123")

logger.info("User authentication started")
logger.info("Credentials validated")

# Temporary context for specific operations
with logger.contextualize(request_id="req-456"):
    logger.info("Processing request")
    logger.info("Request completed")

logger.info("Session ended")
```

## Step 6: Exception Handling

Logly makes exception handling easy:

```python
from logly import logger, catch

logger.configure(level="INFO")

@catch(level="ERROR", message="Function failed")
def risky_operation():
    raise ValueError("Something went wrong!")

# This will log the error automatically
result = risky_operation()
```

## Step 7: Production Configuration

For production, consider this setup:

```python
import os
from logly import logger

# Production configuration
logger.configure(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time} | {level} | {file}:{line} | {message}",
    sinks=[
        {
            "type": "console",
            "level": "INFO"
        },
        {
            "type": "file",
            "path": "/var/log/app.log",
            "level": "DEBUG",
            "rotation": "100 MB",
            "retention": "30 days"
        }
    ]
)
```

## Step 8: Next Steps

Now that you have the basics, explore:

- **[Configuration Guide](../guides/configuration.md)**: Advanced configuration options
- **[Examples](../examples/basic-console.md)**: Real-world usage examples
- **[API Reference](../api-reference/index.md)**: Complete API documentation

## Troubleshooting

### Common Issues

**No output?**
- Check your log level - messages below the configured level are filtered out
- Ensure you're calling `logger.configure()` before logging

**Import error?**
- Verify Logly is installed: `pip list | grep logly`
- Check Python version: `python --version` (needs 3.10+)

**Colors not showing?**
- Some terminals don't support colors - try setting `colorize: false` in console sink

### Getting Help

- Check the [API Reference](../api-reference/index.md) for detailed documentation
- Look at [Examples](../examples/basic-console.md) for common patterns
- File an issue on [GitHub](https://github.com/muhammad-fiaz/logly/issues)

## Summary

You've now learned:
- ✅ How to install Logly
- ✅ Basic console and file logging
- ✅ Log levels and formatting
- ✅ Context binding
- ✅ Exception handling
- ✅ Production configuration

Your logging setup is ready! Customize it further based on your application's needs.