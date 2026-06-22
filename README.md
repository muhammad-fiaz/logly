<div align="center">
<img src="https://github.com/user-attachments/assets/565fc3dc-dd2c-47a6-bab6-2f545c551f26" alt="logly logo" width="400" />

<a href="https://muhammad-fiaz.github.io/logly/"><img src="https://img.shields.io/badge/docs-muhammad--fiaz.github.io-blue" alt="Documentation"></a>
<a href="https://pypi.org/project/logly/"><img src="https://img.shields.io/pypi/v/logly?label=PyPI&logo=pypi&logoColor=white" alt="PyPI"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/stars/muhammad-fiaz/logly" alt="GitHub stars"></a>
<a href="https://github.com/muhammad-fiaz/logly/issues"><img src="https://img.shields.io/github/issues/muhammad-fiaz/logly" alt="GitHub issues"></a>
<a href="https://github.com/muhammad-fiaz/logly/pulls"><img src="https://img.shields.io/github/issues-pr/muhammad-fiaz/logly" alt="GitHub pull requests"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/last-commit/muhammad-fiaz/logly" alt="GitHub last commit"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/license/muhammad-fiaz/logly" alt="License"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/ci.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
<img src="https://img.shields.io/badge/platforms-linux%20%7C%20windows%20%7C%20macos-blue" alt="Supported Platforms">
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/github-code-scanning/codeql"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/github-code-scanning/codeql/badge.svg" alt="CodeQL"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/release.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/release.yml/badge.svg" alt="Release"></a>
<a href="https://github.com/muhammad-fiaz/logly/releases/latest"><img src="https://img.shields.io/github/v/release/muhammad-fiaz/logly?label=Latest%20Release&style=flat-square" alt="Latest Release"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/badge/Rust-2024-orange?logo=rust&logoColor=white" alt="Rust"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/badge/PyO3-0.29-blue" alt="PyO3"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/badge/Maturin-1.x-brightgreen?logo=rust&logoColor=white" alt="Maturin"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/badge/Ruff-checked-blue?logo=astral&logoColor=white" alt="Ruff"></a>
<a href="https://github.com/sponsors/muhammad-fiaz"><img src="https://img.shields.io/badge/Sponsor-&#x1F496;-pink?style=social&logo=github" alt="GitHub Sponsors"></a>
<a href="https://hits.sh/muhammad-fiaz/logly/"><img src="https://hits.sh/muhammad-fiaz/logly.svg?label=Visitors&extraCount=0&color=green" alt="Repo Visitors"></a>

<p><em>A Rust-powered, high-performance logging library for Python with structured sinks, custom levels, rotation, compression, and telemetry integrations.</em></p>

<b><a href="https://muhammad-fiaz.github.io/logly/">Documentation</a> |
<a href="https://muhammad-fiaz.github.io/logly/api-reference/logger/">API Reference</a> |
<a href="https://muhammad-fiaz.github.io/logly/getting-started/">Quick Start</a> |
<a href="CONTRIBUTING.md">Contributing</a></b>

</div>

A production-grade, high-performance logging library for Python, powered by a Rust-native engine built with PyO3. Designed with a clean, intuitive, and developer-friendly API, featuring a completely independent, from-scratch Rust implementation.

> [!NOTE]
> **Logly v0.2.0** — A refactor of Logly from v0.1.6 with a rebuilt Rust-native engine, improved APIs, and new features. See the [documentation](https://muhammad-fiaz.github.io/logly/) for details. This project is under active development — contributions are welcome!

**If you love `logly`, make sure to give it a star!**

---

<details>
<summary><strong>Table of Contents</strong> (click to expand)</summary>

- [Prerequisites](#prerequisites)
- [Supported Platforms](#supported-platforms)
- [Installation](#installation)
- [Quick Start](#quick Start)
- [Usage Examples](#usage-examples)
  - [Console Logging](#console-logging)
  - [File Logging](#file-logging)
  - [File Rotation](#file-rotation)
  - [JSON Logging](#json-logging)
  - [Context Binding](#context-binding)
  - [Custom Log Levels](#custom-log-levels)
  - [Multiple Sinks](#multiple-sinks)
  - [Filtering](#filtering)
  - [Custom Formatters](#custom-formatters)
  - [Patching Records](#patching-records)
  - [Exception Catching](#exception-catching)
  - [Lazy Evaluation](#lazy-evaluation)
  - [Enable/Disable](#enabledisable)
  - [Stdlib Logging Integration](#stdlib-logging-integration)
  - [FastAPI Integration](#fastapi-integration)
  - [Django Integration](#django-integration)
  - [Rich Console Integration](#rich-console-integration)
  - [Production Configuration](#production-configuration)
- [Configuration](#configuration)
  - [Pydantic Configuration](#pydantic-configuration)
- [Log Levels](#log-levels)
- [Architecture](#architecture)
- [Performance](#performance)
- [Building](#building)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Links](#links)

</details>

----

<details>
<summary><strong>Features of Logly</strong> (click to expand)</summary>

| Feature | Description | Documentation |
|---------|-------------|---------------|
| **Simple & Clean API** | User-friendly logging interface (`logger.info()`, `logger.error()`, etc.) | [Docs](https://muhammad-fiaz.github.io/logly/getting-started/) |
| **10 Log Levels** | TRACE, DEBUG, INFO, NOTICE, SUCCESS, WARNING, ERROR, FAIL, CRITICAL, FATAL | [Docs](https://muhammad-fiaz.github.io/logly/guides/custom-levels/) |
| **Custom Levels** | Define your own log levels with custom priorities and colors | [Docs](https://muhammad-fiaz.github.io/logly/guides/custom-levels/) |
| **Multiple Sinks** | Console, file, and custom callable outputs simultaneously | [Docs](https://muhammad-fiaz.github.io/logly/guides/sinks/) |
| **File Rotation** | Time-based (daily, hourly) and size-based rotation | [Docs](https://muhammad-fiaz.github.io/logly/guides/rotation-retention-compression/) |
| **Retention Policies** | Count-based or age-based log file retention | [Docs](https://muhammad-fiaz.github.io/logly/guides/rotation-retention-compression/) |
| **Compression** | Built-in support for gzip, zip, bz2, xz compression | [Docs](https://muhammad-fiaz.github.io/logly/guides/rotation-retention-compression/) |
| **JSON Logging** | Structured JSON output for file storage and analysis | [Docs](https://muhammad-fiaz.github.io/logly/guides/formatting/) |
| **Custom Formats** | Customizable log message format templates | [Docs](https://muhammad-fiaz.github.io/logly/guides/formatting/) |
| **Context Binding** | Attach persistent key-value pairs to logs | [Docs](https://muhammad-fiaz.github.io/logly/guides/context-binding/) |
| **Scoped Contexts** | Create child loggers with bound context that persists across calls | [Docs](https://muhammad-fiaz.github.io/logly/guides/context-binding/) |
| **Record Patching** | Modify log records before they reach sinks | [Docs](https://muhammad-fiaz.github.io/logly/guides/context-binding/) |
| **Exception Catching** | `catch()` decorator and context manager for exception logging | [Docs](https://muhammad-fiaz.github.io/logly/guides/exception-handling/) |
| **Lazy Evaluation** | `opt()` for deferred exception capturing and lazy message evaluation | [Docs](https://muhammad-fiaz.github.io/logly/guides/exception-handling/) |
| **Per-Sink Filtering** | Configure filters on each sink independently | [Docs](https://muhammad-fiaz.github.io/logly/guides/filtering/) |
| **Thread-Safe** | Safe concurrent logging from multiple threads | [Docs](https://muhammad-fiaz.github.io/logly/guides/concurrency/) |
| **Background Workers** | Optional enqueue mode for non-blocking writes | [Docs](https://muhammad-fiaz.github.io/logly/guides/concurrency/) |
| **Stdlib Integration** | Seamless integration with Python's `logging` module | [Docs](https://muhammad-fiaz.github.io/logly/guides/stdlib-logging/) |
| **FastAPI Integration** | Request-scoped logging middleware for FastAPI | [Docs](https://muhammad-fiaz.github.io/logly/guides/fastapi/) |
| **Django Integration** | Custom logging handler and middleware for Django | [Docs](https://muhammad-fiaz.github.io/logly/guides/django/) |
| **Rich Console** | Rich-formatted console output integration | [Docs](https://muhammad-fiaz.github.io/logly/guides/rich-console/) |
| **Custom Colors** | ANSI-based custom colors for all levels (works without Rich) | [Docs](https://muhammad-fiaz.github.io/logly/guides/custom_colors/) |
| **ANSI Colors** | Whole-line colorized console output | [Docs](https://muhammad-fiaz.github.io/logly/guides/sinks/) |
| **Pydantic Config** | Type-safe configuration models with validation | [Docs](https://muhammad-fiaz.github.io/logly/api-reference/models/) |
| **Rust Engine** | High-performance native engine built with PyO3 | [Docs](https://muhammad-fiaz.github.io/logly/architecture/) |
| **Telemetry** | OpenTelemetry, StatsD, and Prometheus metrics integration | [Docs](https://muhammad-fiaz.github.io/logly/guides/telemetry/) |

</details>

----

<details>
<summary><strong>Prerequisites & Supported Platforms</strong> (click to expand)</summary>

<br>

## Prerequisites

Before installing Logly, ensure you have the following:

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.10+ | Download from [python.org](https://www.python.org/downloads/) |
| **Operating System** | Windows 10+, Linux, macOS | Cross-platform support |
| **Rust** | Latest stable | Required for building from source (not needed for pip install) |

> Verify your Python installation by running `python --version` in your terminal.

---

## Supported Platforms

Logly supports a wide range of platforms:

| Platform | Architectures | Status |
|----------|---------------|--------|
| **Windows** | x86_64 | Full support |
| **Linux** | x86_64, aarch64 | Full support |
| **macOS** | x86_64, aarch64 (Apple Silicon) | Full support |

Pre-built wheels are available on PyPI for all supported platforms.

</details>

---

## Installation

### Method 1: PyPI (Recommended)

The easiest way to install Logly:

```bash
pip install logly
```

Or with [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv add logly
```

### Method 2: Building from Source

Clone the repository and build:

```bash
git clone https://github.com/muhammad-fiaz/logly.git
cd logly
uv sync
uv run maturin develop
```

---

## Quick Start

```python
from logly import logger

# Log at different levels
logger.trace("Detailed trace information")
logger.debug("Debug information")
logger.info("Application started")
logger.notice("Notice message")
logger.success("Operation completed!")
logger.warning("Warning message")
logger.error("Error occurred")
logger.fail("Operation failed")
logger.critical("Critical system error!")
logger.fatal("Fatal system failure!")

# Flush to ensure output is written
logger.complete()
```

---

## Usage Examples

### Console Logging

```python
from logly import logger

# Default console sink (stderr)
logger.info("Hello from Logly!")

# Add stdout sink
sink_id = logger.add("stdout", level="DEBUG")
logger.debug("This goes to stdout")
logger.remove(sink_id)
```

### File Logging

```python
from logly import logger

# Add file sink
sink_id = logger.add("app.log", level="DEBUG", format="{time} | {level} | {message}")
logger.info("Logging to file!")
logger.complete()
logger.remove(sink_id)
```

### File Rotation

```python
from logly import logger

# Daily rotation with 7-day retention
sink_id = logger.add(
    "logs/daily.log",
    rotation="daily",
    retention=7,
    compression="gzip",
)

logger.info("This log will be rotated daily")
logger.complete()
logger.remove(sink_id)

# Size-based rotation (10MB limit)
sink_id = logger.add("logs/app.log", rotation="10 MB", retention=5)
logger.info("This log will be rotated when file reaches 10MB")
logger.complete()
logger.remove(sink_id)
```

### JSON Logging

```python
from logly import logger

sink_id = logger.add("app.json", serialize=True, rotation="daily")
logger.info("JSON formatted log")
logger.complete()
logger.remove(sink_id)
# Output: {"text": "2026-06-21T12:00:00 | INFO | JSON formatted log", "record": {...}}
```

### Context Binding

```python
from logly import logger

# Bind context fields
bound_logger = logger.bind(user_id="12345", request_id="abc-789")
bound_logger.info("User logged in")
# Output includes: user_id=12345 request_id=abc-789

# Contextualize with context manager
with logger.contextualize(session_id="xyz-000"):
    logger.info("Inside session context")
    logger.info("Still in context")
# Context restored after block
```

### Custom Log Levels

```python
from logly import logger

# Register a custom level
logger.level("AUDIT", no=25, color="<magenta>")

# Use custom level
logger.log("AUDIT", "User action recorded")
logger.opt(exception=True).audit("Auditing with exception info")
```

### Multiple Sinks

```python
from logly import logger

# Console output
logger.add("stderr", level="INFO")

# Application logs
logger.add("app.log", level="DEBUG", rotation="daily")

# Error-only file
logger.add("errors.log", level="ERROR")

# JSON output
logger.add("structured.json", serialize=True, level="WARNING")
```

### Filtering

```python
from logly import logger

# Level filter (minimum level)
sink_id = logger.add("filtered.log", level="WARNING")

# Callable filter
def my_filter(record):
    return "important" in record["message"]

sink_id = logger.add("filtered.log", filter=my_filter)

# Prefix filter
sink_id = logger.add("app.log", filter={"name": "myapp."})

# Mapping filter
sink_id = logger.add(
    "filtered.log",
    filter={"name": "myapp.", "extra.status": "active"},
)
```

### Custom Formatters

```python
from logly import logger

# Template format
sink_id = logger.add(
    "formatted.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
)

# Callable formatter
def my_formatter(record):
    return f"[{record['time'].timestamp()}] {record['level'].name}: {record['message']}"

sink_id = logger.add("custom.log", format=my_formatter)
```

### Patching Records

```python
from logly import logger

# Global patcher
def add_version(record):
    record["extra"]["version"] = "1.0.0"

logger.add("app.log", patch=add_version)
logger.info("With version")
# Output includes: version=1.0.0

# Scoped patcher
with logger.contextualize(service="api"):
    logger.info("Request processed")
    # Output includes: service=api
```

### Exception Catching

```python
from logly import logger

# Context manager
with logger.catch():
    risky_function()

# Decorator
@logger.catch()
def risky_function():
    raise ValueError("Something went wrong")

# With custom level and message
with logger.catch(level="CRITICAL", message="Database failure"):
    database.connect()

# Re-raise exception after logging
with logger.catch(reraise=True):
    risky_function()
```

### Lazy Evaluation

```python
from logly import logger

# Lazy message evaluation
logger.opt(lazy=True).debug("User {} logged in", lambda: get_username())

# Exception capture
logger.opt(exception=True).error("Something failed")
```

### Enable/Disable

```python
from logly import logger

# Disable logging for a specific name
logger.disable("myapp")
logger.info("This won't appear")

# Re-enable
logger.enable("myapp")
logger.info("This will appear")
```

### Stdlib Logging Integration

```python
import logging
from logly.integrations.stdlib import InterceptHandler

# Route stdlib logging through Logly
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
logging.getLogger("uvicorn").info("Routed through Logly!")
```

### FastAPI Integration

```python
from fastapi import FastAPI
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)
```

### Django Integration

```python
# settings.py
LOGGING = {
    "handlers": ["logly"],
    "logly": {
        "class": "logly.integrations.django.LoglyHandler",
        "level": "INFO",
    },
}

MIDDLEWARE = [
    "logly.integrations.django.LoglyMiddleware",
    # ... other middleware
]
```

### Rich Console Integration

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

# Method 1: Using the Rich sink class
sink_id = logger.add(LoglyRichSink(), colorize=True)
logger.info("Rich-formatted output!")
logger.complete()

# Method 2: Using Rich's Console.print directly
from rich.console import Console

console = Console()
logger.add(console.print, colorize=True, format="{message}")
logger.info("Hello World")
logger.success("Operation completed")
logger.warning("Disk almost full")
logger.error("Something failed")

# Method 3: Rich tracebacks
from rich.traceback import install

install(show_locals=True)
logger.exception("Unhandled exception")
```

### Custom Colors

```python
from logly import logger

# Override built-in level colors
logger.level("DEBUG", color="<blue><bold>")
logger.level("WARNING", color="<yellow><bold>")

# Register new levels with custom colors
logger.level("SECURITY", no=45, color="<red><bold>")
logger.level("PERF", no=10, color="<cyan><bold>")

logger.add("colored.log", level="TRACE", colorize=True)

logger.log("SECURITY", "Unauthorized access attempt")
logger.log("PERF", "Request took 200ms")
```

### Production Configuration

```python
from logly import logger

# Production-ready setup
logger.add(
    "logs/app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    serialize=True,
    enqueue=True,
)

# Error monitoring
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
)

logger.info("Application started")
logger.complete()
```

---

## Configuration

### Pydantic Configuration

```python
from logly import logger
from logly.models import SinkConfig, LoggerConfig, RotationPolicy, RetentionPolicy

# Configure via Pydantic models
config = LoggerConfig(
    sinks=[
        SinkConfig(
            level="INFO",
            format="{time} | {level} | {message}",
            rotation=RotationPolicy(kind="daily"),
            retention=RetentionPolicy(count=30),
            compression="gzip",
        )
    ]
)
```

---

## Log Levels

| Level    | Priority | Method              | Use Case                |
| -------- | -------- | ------------------- | ----------------------- |
| TRACE    | 5        | `logger.trace()`    | Very detailed debugging |
| DEBUG    | 10       | `logger.debug()`    | Debugging information   |
| INFO     | 20       | `logger.info()`     | General information     |
| NOTICE   | 25       | `logger.notice()`   | Notice messages         |
| SUCCESS  | 30       | `logger.success()`  | Successful operations   |
| WARNING  | 40       | `logger.warning()`  | Warning messages        |
| ERROR    | 50       | `logger.error()`    | Error conditions        |
| FAIL     | 55       | `logger.fail()`     | Operation failures      |
| CRITICAL | 60       | `logger.critical()` | Critical system errors  |
| FATAL    | 70       | `logger.fatal()`    | Fatal system errors     |

---

## Architecture

Logly is built as a modular Rust workspace with a thin PyO3 binding:

| Crate | Purpose |
|-------|---------|
| `error` | Error types and conversions |
| `config` | Configuration data structures |
| `levels` | Log level definitions and registry |
| `record` | Log record builder |
| `color` | ANSI color engine and themes |
| `format` | Template, JSON, and custom formatters |
| `filter` | Level, prefix, extra, and chain filters |
| `rotate` | File rotation policies and execution |
| `compress` | Compression codecs (gzip, zip, bz2, xz, zstd) |
| `concurrency` | Background workers and thread pool |
| `schedule` | Scheduled tasks and scheduler |
| `context` | Bound context, scoped context, patchers |
| `sink` | Sink trait and built-in implementations |
| `core` | Logger engine dispatch |

---

## Performance

Logly's Rust engine provides near-zero overhead logging:

- **Native dispatch**: Log calls route through PyO3 to a Rust `LoggerEngine`
- **Efficient filtering**: Level checks happen in Rust before any Python overhead
- **Background workers**: Optional `enqueue=True` for non-blocking writes
- **Thread-safe**: `Mutex`-protected engine with graceful shutdown

---

## Building from Source

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Rust** | Latest stable (1.75+) | Compile the native engine |
| **Python** | 3.10+ | Runtime and build scripts |
| **uv** | Latest | Package manager (recommended) |
| **Maturin** | 1.x | Build backend for PyO3 wheels |
| **MkDocs** | <2 | Documentation site (Material theme) |

Install Rust via [rustup](https://rustup.rs/), then:

```bash
# Install uv (if not already installed)
pip install uv

# Build the extension in development mode
uv run maturin develop

# Run Python tests
uv run pytest tests/ -v

# Run Rust tests
cargo test --workspace

# Lint
uv run ruff check .
uv run ruff format --check .
cargo clippy --workspace --all-targets -- -D warnings

# Build documentation
uv run mkdocs serve
```

---

## Documentation

### Online Documentation
Full documentation is available at: https://muhammad-fiaz.github.io/logly

### Generating Local Documentation
To generate documentation locally:

```bash
uv run mkdocs serve
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Acknowledgment

The API design of this project is inspired by [Loguru](https://github.com/Delgan/loguru) by Delgan. We are grateful for the design inspiration.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Links

- **Documentation**: https://muhammad-fiaz.github.io/logly
- **PyPI**: https://pypi.org/project/logly/
- **Repository**: https://github.com/muhammad-fiaz/logly
- **Issues**: https://github.com/muhammad-fiaz/logly/issues
- **Zig Version**: https://github.com/muhammad-fiaz/logly.zig
- **Rust Version**: https://github.com/muhammad-fiaz/logly-rs
