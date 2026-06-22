---
layout: home
title: Logly - Rust-Powered Logging for Python
description: A high-performance, Rust-powered logging library for Python with structured logging, flexible sinks, and modern developer-friendly APIs.

hero:
  name: Logly
  text: Rust-Powered Logging for Python
  tagline: A high-performance logging library built with PyO3 for maximum speed and memory safety.
  image:
    src: /logo.png
    alt: Logly
  actions:
    - theme: brand
      text: Get Started
      link: /getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/muhammad-fiaz/logly

features:
  - icon: ⚡
    title: Rust-Native Engine
    details: Powered by a Rust engine built with PyO3 for maximum performance and memory safety.
  - icon: 📊
    title: 10 Built-in Levels
    details: From TRACE to FATAL, with custom level support for your specific needs.
  - icon: 🔌
    title: Flexible Sinks
    details: Console, file, callable, and network sinks with per-sink configuration.
  - icon: 📁
    title: File Rotation
    details: Size-based, time-based, and clock-based rotation with retention policies and compression.
  - icon: 🏷️
    title: Context Binding
    details: Persistent fields and scoped context for structured logging across requests.
  - icon: 🧩
    title: Framework Integrations
    details: First-class support for FastAPI, Django, Flask, Rich, and many more.
---

## Quick Example

```python
from logly import logger

# Add sinks with per-sink configuration
logger.add("app.log", level="DEBUG", rotation="daily", retention="30 days", compression="gzip")
logger.add("errors.log", level="ERROR", rotation="daily", retention="90 days")
logger.add("stdout", level="INFO", colorize=True)

# Log at all levels
logger.trace("Detailed trace")
logger.debug("Debug info")
logger.info("Application started")
logger.notice("Notice message")
logger.success("Operation completed!")
logger.warning("Warning message")
logger.error("Error occurred")
logger.fail("Operation failed")
logger.critical("Critical system error!")
logger.fatal("Fatal system failure!")

# Bind context
app_logger = logger.bind(user_id="12345", request_id="abc-789")
app_logger.info("User logged in")

# Exception handling
with logger.catch():
    risky_operation()

logger.complete()
```

## Installation

::: code-group

```bash [pip]
pip install logly
```

```bash [uv]
uv add logly
```

```bash [From Source]
git clone https://github.com/muhammad-fiaz/logly.git
cd logly
uv sync
uv run maturin develop
```

:::

## Why Logly?

| Feature | Logly | stdlib logging |
|---------|-------|----------------|
| **Rust-native engine** | ✅ | ❌ |
| **10 built-in log levels** | ✅ | ❌ |
| **Custom levels** | ✅ | Manual |
| **Multiple sinks** | ✅ | ✅ |
| **File rotation** | ✅ | Handler dependent |
| **Retention policies** | ✅ | Handler dependent |
| **Compression** | ✅ | Handler dependent |
| **JSON serialization** | ✅ | Formatter dependent |
| **Context binding** | ✅ | Adapter based |
| **Record patching** | ✅ | ❌ |
| **Exception catching** | ✅ | ❌ |
| **Background workers** | ✅ | QueueHandler |
| **FastAPI integration** | ✅ | ❌ |
| **Django integration** | ✅ | ❌ |
| **Rich console** | ✅ | ❌ |
| **Custom colors (ANSI)** | ✅ | Manual |
| **Type-safe config** | ✅ | ❌ |
| **Zero unsafe Rust** | ✅ | N/A |

::: info Acknowledgment
The API design of this project is inspired by [Loguru](https://github.com/Delgan/loguru) by Delgan. We are grateful for the design inspiration.
:::

::: warning Active Development
Logly is still evolving and improving. This project is under active development. If you encounter any issues, please feel free to [report them](https://github.com/muhammad-fiaz/logly/issues/new).
:::
