<div align="center">
<img src="https://github.com/user-attachments/assets/565fc3dc-dd2c-47a6-bab6-2f545c551f26" alt="logly logo" width="400" />

<a href="https://pypi.org/project/logly/"><img src="https://img.shields.io/pypi/v/logly" alt="PyPI"></a>
<a href="https://pypistats.org/packages/logly"><img src="https://img.shields.io/pypi/dm/logly" alt="PyPI - Downloads"></a>
<a href="https://muhammad-fiaz.github.io/logly/"><img src="https://img.shields.io/badge/docs-muhammad--fiaz.github.io-blue" alt="Documentation"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%3E%3D3.10-brightgreen.svg" alt="Supported Python"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/stars/muhammad-fiaz/logly" alt="GitHub stars"></a>
<a href="https://github.com/muhammad-fiaz/logly/issues"><img src="https://img.shields.io/github/issues/muhammad-fiaz/logly" alt="GitHub issues"></a>
<a href="https://github.com/muhammad-fiaz/logly/pulls"><img src="https://img.shields.io/github/issues-pr/muhammad-fiaz/logly" alt="GitHub pull requests"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/last-commit/muhammad-fiaz/logly" alt="GitHub last commit"></a>
<a href="https://github.com/muhammad-fiaz/logly/releases"><img src="https://img.shields.io/github/v/release/muhammad-fiaz/logly" alt="GitHub release"></a>
<a href="https://codecov.io/gh/muhammad-fiaz/logly"><img src="https://codecov.io/gh/muhammad-fiaz/logly/graph/badge.svg?token=1G3MU8SDX1" alt="codecov"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/license/muhammad-fiaz/logly" alt="License"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/testing.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/testing.yml/badge.svg" alt="Testing"></a>

<p><em>A Rust-powered, high-performance logging library for Python.</em></p>

<b><a href="https://muhammad-fiaz.github.io/logly/">Documentation</a> |
<a href="https://muhammad-fiaz.github.io/logly/api-reference/logger/">API Reference</a> |
<a href="https://muhammad-fiaz.github.io/logly/getting-started/">Quick Start</a> |
<a href="CONTRIBUTING.md">Contributing</a></b>

</div>


A Rust-powered, high-performance logging library for Python with structured sinks, custom levels, rotation, compression, and telemetry integrations.

> [!IMPORTANT]
> **Logly v0.2.0** is a major rewrite of v0.1.6, featuring a rebuilt Rust-powered core, improved APIs, and new features. See the [documentation](https://muhammad-fiaz.github.io/logly/) for details. This project is under active development. If you encounter any issues, bugs, or have feature requests, please open an issue on GitHub. Contributions are welcome!

**If you love `logly`, make sure to give it a star!**

---

## Features

| Feature | Description |
|---------|-------------|
| **Rust-native engine** | High-performance logging via PyO3 with zero unsafe Rust |
| **10 built-in levels** | TRACE, DEBUG, INFO, NOTICE, SUCCESS, WARNING, ERROR, FAIL, CRITICAL, FATAL |
| **Custom levels** | Define your own levels with custom priorities and colors |
| **Multiple sinks** | Console, file, callable, and network outputs simultaneously |
| **File rotation** | Time-based and size-based rotation with retention policies |
| **Compression** | gzip, zip, bz2, xz, zstd support out of the box |
| **JSON logging** | Structured JSON output for storage and analysis |
| **Context binding** | Attach persistent key-value pairs to logs |
| **Exception catching** | `catch()` decorator and context manager |
| **Background workers** | Non-blocking writes with `enqueue=True` |
| **40+ integrations** | FastAPI, Django, Flask, Rich, Redis, Kafka, and more |

For full details, see the [documentation](https://muhammad-fiaz.github.io/logly/).

---

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

---

## Quick Start

```python
from logly import logger

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

logger.complete()
```

> [!TIP]
> Logly is designed for production Python services that need structured records, multiple sinks, rotation, compression, background dispatch, color themes, source context display, and framework integrations without giving up native performance.

---

## Usage Examples

### File Logging

```python
from logly import logger

logger.add(
    "logs/app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

logger.info("Application started")
logger.complete()
```

### Context Binding

```python
from logly import logger

user_logger = logger.bind(user_id="12345", request_id="abc-789")
user_logger.info("User logged in")
# Output includes: user_id=12345 request_id=abc-789
```

### Exception Catching

```python
from logly import logger

with logger.catch():
    risky_operation()

# With options
with logger.catch(exclude=ValueError, onerror=lambda e: print(f"Failed: {e}")):
    dangerous_call()
```

### Multiple Sinks

```python
from logly import logger

logger.add("app.log", level="DEBUG", rotation="daily")
logger.add("errors.log", level="ERROR", retention="90 days")
logger.add("stdout", level="INFO", colorize=True)

logger.info("All three sinks receive this")
```

### Independent Loggers

Use `Logger()` when a subsystem needs a separate set of sinks that does not
write to the global logger.

```python
from logly import Logger

api_logger = Logger()
worker_logger = Logger()

api_logger.add("api.log", level="INFO")
worker_logger.add("worker.log", level="DEBUG")

api_logger.info("request accepted")
worker_logger.debug("job claimed")
```

### Lazy Evaluation

```python
from logly import logger

logger.opt(lazy=True).debug("Result: {}", lambda: expensive_computation())
```

### Custom Levels

```python
from logly import logger, register_custom_level

register_custom_level("AUDIT", 35, "magenta")
logger.audit("Security event detected")
```

For more examples, see the [documentation](https://muhammad-fiaz.github.io/logly/).

---

## Log Levels

| Level | Priority | Method | Use Case |
|-------|----------|--------|----------|
| TRACE | 5 | `logger.trace()` | Very detailed debugging |
| DEBUG | 10 | `logger.debug()` | Debugging information |
| INFO | 20 | `logger.info()` | General information |
| NOTICE | 25 | `logger.notice()` | Notice messages |
| SUCCESS | 30 | `logger.success()` | Successful operations |
| WARNING | 40 | `logger.warning()` | Warning messages |
| ERROR | 50 | `logger.error()` | Error conditions |
| FAIL | 55 | `logger.fail()` | Operation failures |
| CRITICAL | 60 | `logger.critical()` | Critical system errors |
| FATAL | 70 | `logger.fatal()` | Fatal system errors |

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
| `network` | HTTP, TCP, UDP, Syslog sinks |
| `source` | Caller frame inspection |

---

## Building from Source

| Tool | Version | Purpose |
|------|---------|---------|
| **Rust** | Latest stable | Compile the native engine |
| **Python** | 3.10+ | Runtime and build scripts |
| **uv** | Latest | Package manager (recommended) |
| **Maturin** | 1.x | Build backend for PyO3 wheels |

```bash
# Install uv (if not already installed)
pip install uv

# Build the extension in development mode
uv run maturin develop

# Run Python tests
uv run pytest

# Run Rust tests
cargo test --workspace

# Lint
uv run ruff check .
cargo clippy --workspace --all-targets -- -D warnings
```

---

## Documentation

Full documentation is available at: https://muhammad-fiaz.github.io/logly

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Acknowledgements

Logly's Python API syntax and ergonomics are inspired by [Loguru](https://github.com/Delgan/loguru). The underlying engine is an independent, from-scratch Rust implementation.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Links

- **Documentation**: https://muhammad-fiaz.github.io/logly
- **PyPI**: https://pypi.org/project/logly/
- **Repository**: https://github.com/muhammad-fiaz/logly
- **Issues**: https://github.com/muhammad-fiaz/logly/issues
