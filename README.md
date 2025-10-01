<div align="center">
<img src="https://github.com/user-attachments/assets/565fc3dc-dd2c-47a6-bab6-2f545c551f26" alt="logly logo"  />

<a href="https://pypi.org/project/logly/"><img src="https://img.shields.io/pypi/v/logly" alt="PyPI"></a>
<a href="https://pypistats.org/packages/logly"><img src="https://img.shields.io/pypi/dm/logly" alt="PyPI - Downloads"></a>
<a href="https://muhammad-fiaz.github.io/logly/"><img src="https://img.shields.io/badge/docs-muhammad--fiaz.github.io-blue" alt="Documentation"></a>
<a href="https://pay.muhammadfiaz.com"><img src="https://img.shields.io/badge/Donate-%20-orange" alt="Donate"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%3E%3D3.9-brightgreen.svg" alt="Supported Python"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/stars/muhammad-fiaz/logly" alt="GitHub stars"></a>
<a href="https://github.com/muhammad-fiaz/logly/network"><img src="https://img.shields.io/github/forks/muhammad-fiaz/logly" alt="GitHub forks"></a>
<a href="https://github.com/muhammad-fiaz/logly/releases"><img src="https://img.shields.io/github/v/release/muhammad-fiaz/logly" alt="GitHub release"></a>
<a href="https://github.com/muhammad-fiaz/logly/issues"><img src="https://img.shields.io/github/issues/muhammad-fiaz/logly" alt="GitHub issues"></a>
<a href="https://github.com/muhammad-fiaz/logly/pulls"><img src="https://img.shields.io/github/issues-pr/muhammad-fiaz/logly" alt="GitHub pull requests"></a>
<a href="https://github.com/muhammad-fiaz/logly/commits"><img src="https://img.shields.io/github/last-commit/muhammad-fiaz/logly" alt="GitHub last commit"></a>
<a href="https://github.com/muhammad-fiaz/logly/graphs/contributors"><img src="https://img.shields.io/github/contributors/muhammad-fiaz/logly" alt="GitHub contributors"></a>
<a href="https://codecov.io/gh/muhammad-fiaz/logly"><img src="https://img.shields.io/codecov/c/gh/muhammad-fiaz/logly" alt="Codecov"></a>
<img src="https://img.shields.io/badge/pytest-%3E%3D7.0-blue.svg" alt="Pytest">
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/license/muhammad-fiaz/logly" alt="License"></a>


<p><em>Rust-powered, Loguru-like logging for Python.</em></p>

**📚 [Complete Documentation](https://muhammad-fiaz.github.io/logly/) | [API Reference](https://muhammad-fiaz.github.io/logly/api-reference/) | [Quick Start](https://muhammad-fiaz.github.io/logly/quickstart/)**

</div>



Logly is a Rust-powered, Loguru-like logging library for Python that combines the familiarity of Python’s standard logging API with high-performance logging capabilities. It is designed for developers who need efficient, reliable logging in applications that generate large volumes of log messages.

Logly's core is implemented in Rust using tracing and exposed to Python via PyO3/Maturin for safety and performance.

**⭐ Don't forget to star the repository if you find Logly useful!**

<details>
<summary><strong>Table of contents</strong></summary>

- [Install (PyPI)](#install-pypi)
- [Nightly installation](#nightly-installation)
	- [Build from source](#build-from-source)
		- [Prerequisites](#prerequisites)
		- [Build steps](#build-steps)
		- [Docker/Container Installation](#dockercontainer-installation)
- [Architecture Overview](#architecture-overview)
	- [🏗️ **Modular Rust Backend**](#️-modular-rust-backend)
	- [🔧 **Key Components**](#-key-components)
	- [🚀 **Performance Optimizations**](#-performance-optimizations)
- [Quickstart](#quickstart)
	- [Filename rotation and retention](#filename-rotation-and-retention)
- [What’s new (features)](#whats-new-features)
- [Performance \& Benchmarks](#performance--benchmarks)
	- [🚀 Performance Results](#-performance-results)
		- [File Logging (50,000 messages, 3 repeats)](#file-logging-50000-messages-3-repeats)
		- [Concurrent Logging (4 threads × 25,000 messages, 3 repeats)](#concurrent-logging-4-threads--25000-messages-3-repeats)
		- [Latency Microbenchmark (30,000 messages)](#latency-microbenchmark-30000-messages)
	- [What's New](#whats-new)
	- [Reproduce These Benchmarks](#reproduce-these-benchmarks)
	- [Additional Benchmark Options](#additional-benchmark-options)
- [Concurrency benchmark](#concurrency-benchmark)
	- [Latency microbenchmark (p50/p95/p99)](#latency-microbenchmark-p50p95p99)
- [API reference (current features)](#api-reference-current-features)
- [Advanced examples](#advanced-examples)
- [Testing](#testing)
- [Changelog](#changelog)
- [Contributing](#contributing)
	- [Want to contribute?](#want-to-contribute)
- [License](#license)

</details>

---

## Install (PyPI)

logly is available on PyPI and can be installed with:

```powershell
python -m pip install --upgrade pip
pip install logly
```

For testing pre-releases on TestPyPI:

```powershell
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple logly
```

If you are a package consumer, this is all you need; the rest of this README documents usage and developer instructions.

## Nightly installation

You can install the latest code from the GitHub repository (useful for nightly builds or unreleased fixes).

⚠️ **Requires Rust toolchain and maturin installed on your system**

### Build from source

For developers who want to build logly from source code.

#### Prerequisites

- Python 3.9+
- Rust 1.70+
- maturin (Python package for building Rust extensions)

#### Build steps

```powershell
# Clone the repository
git clone https://github.com/muhammad-fiaz/logly.git
cd logly

# Create and activate virtual environment
python -m venv .venv
. .\.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate      # Linux/macOS

# Install build dependencies
pip install maturin

# Build and install
maturin develop  # For development (editable install)
# or
maturin build --release  # For production build
pip install target/wheels/*.whl
```

#### Docker/Container Installation

If you're using containers, you can build the wheel in a multi-stage Docker build:

```dockerfile
# Build stage
FROM rust:1.80-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install maturin
COPY . .
RUN maturin build --release

# Runtime stage  
FROM python:3.12-slim
COPY --from=builder /app/target/wheels/*.whl /tmp/
RUN pip install /tmp/*.whl
```

**Note**: Most users should use PyPI releases instead of building from source.

## Architecture Overview

Logly's architecture is designed for high performance, maintainability, and extensibility:

### 🏗️ **Modular Rust Backend**
```
src/
├── backend/          # Core logging functionality
│   ├── logging.rs    # Main logging logic with JSON/text formatting
│   ├── async.rs      # Asynchronous buffered writing
│   └── file.rs       # File appenders with rotation
├── config/           # Configuration and state management
│   └── state.rs      # Global state with thread-safe structures
├── format/           # Output formatting utilities
│   └── json.rs       # JSON record serialization
└── utils/            # Shared utilities and types
    └── levels.rs     # Log levels and rotation policies
```

### 🔧 **Key Components**

- **Backend Module**: Handles core logging operations, message formatting, and output dispatching
- **Config Module**: Manages global logger state, sink configurations, and thread-safe data structures
- **Format Module**: Provides JSON serialization and record formatting utilities
- **Utils Module**: Contains shared types, log levels, and rotation policies

### 🚀 **Performance Optimizations**

- **Async Buffering**: Background thread writing with configurable flush intervals
- **Memory Safety**: Zero-cost abstractions with proper error handling
- **Thread Safety**: Lock-free operations where possible, parking_lot Mutex for performance
- **Fast Hashing**: ahash for high-performance hash operations
- **Efficient Data Structures**: Crossbeam channels, Arc pointers, and optimized collections

## Quickstart

```python
from logly import logger

# -----------------------------
# Add sinks (logger.add)
# -----------------------------
# sink: "console" or a file path. Returns a handler id (int).
# rotation: "daily" | "hourly" | "minutely" | "never" (time-based rotation)
# size_limit: "500B" | "5KB" | "10MB" | "1GB" (size-based rotation)
console_hid = logger.add("console")                  # writes human-readable text to stderr
daily_file_hid = logger.add(
	"logs/app.log",
	rotation="daily",
	# control how rotation incorporates the date into the filename
	# date_style: "before_ext" (default) will produce files like app.2025-08-22.log
	#             "prefix" will produce files like 2025-08-22.app.log
	# date_enabled: when False (default) the date will not be appended to filenames
	#               even if rotation is set; rotation still controls rollover timing
	# retention: keep at most N rotated files (count-based). Oldest are pruned on rollover.
	date_style="before_ext",
	date_enabled=False,  # default: False (no date appended to filename)
	retention=7,
	# optional per-file-sink filters and async write
	filter_min_level="INFO",           # only write INFO+ to this file
	filter_module="myapp.handlers",    # only if module matches
	filter_function=None,               # or match a specific function name
	async_write=True,                   # write via background thread
)

# Size-based rotation examples:
logger.add("logs/app.log", size_limit="10MB")        # rotate when file reaches 10MB
logger.add("logs/debug.log", size_limit="1GB", retention=5)  # rotate at 1GB, keep 5 files
logger.add("logs/small.log", size_limit="500KB", rotation="daily")  # combine time and size

# Advanced filtering examples:
logger.add("logs/errors.log", filter_min_level="ERROR")  # only ERROR and above
logger.add("logs/django.log", filter_module="django.db")  # only Django DB logs
logger.add("logs/auth.log", filter_function="authenticate")  # only auth function logs

# Date and naming examples:
logger.add("logs/app.log", rotation="daily", date_style="prefix", date_enabled=True)
# Creates: 2025-08-22.app.log, 2025-08-23.app.log, etc.

logger.add("logs/app.log", rotation="hourly", date_enabled=False)
# Creates: app.log (no date, but rotates hourly based on time)

# -----------------------------
# Advanced sink configuration examples
# -----------------------------

# File size limits with retention:
logger.add("logs/large.log", size_limit="500MB", retention=3)  # Keep last 3 files

# Combined time and size rotation:
logger.add("logs/complex.log", rotation="daily", size_limit="50MB", retention=10)

# Filtered sinks for different log levels:
error_sink = logger.add("logs/errors.log", filter_min_level="ERROR")
debug_sink = logger.add("logs/debug.log", filter_min_level="DEBUG", filter_max_level="INFO")

# Module-specific logging:
logger.add("logs/database.log", filter_module="myapp.database")
logger.add("logs/api.log", filter_module="myapp.api", filter_function="handle_request")

# Custom date formatting:
logger.add("logs/dated.log", rotation="daily", date_style="prefix", date_enabled=True)
# Result: 2025-08-22.dated.log, 2025-08-23.dated.log, etc.

# Performance optimization with async writing:
logger.add("logs/performance.log", async_write=True)   # Default: background thread
logger.add("logs/precise.log", async_write=False)      # Synchronous for exact timing

# Remove sinks when no longer needed:
logger.remove(error_sink)
logger.remove(debug_sink)

# Async writing (default for performance):
logger.add("logs/fast.log", async_write=True)   # background thread, lower latency
logger.add("logs/sync.log", async_write=False)  # synchronous writes

# -----------------------------
# Configure behavior (logger.configure)
# -----------------------------
# level: string name (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
# color: enable or disable ANSI colors for console output (True/False)
# json: when True, emit newline-delimited JSON records with `fields` (structured logging)
# pretty_json: pretty-print JSON (human-friendly; higher cost than compact JSON)

# Text mode, colored console output, DEBUG level
logger.configure(level="DEBUG", color=True, json=False)

# Switch to JSON structured mode (useful for ingestion into log pipelines)
logger.configure(level="INFO", color=False, json=True)

# Pretty JSON (human-friendly) for local development
logger.configure(level="INFO", color=False, json=True, pretty_json=True)

# Example explanation:
# - json=False => human-friendly text; kwargs appended as key=value suffix
# - json=True  => each line is a JSON object: {timestamp, level, message, fields: {...}}

# -----------------------------
# Basic logging calls
# -----------------------------
# All log functions accept a message and optional kwargs that become structured fields
logger.trace("trace message", trace_id=1)
logger.debug("debug message", step=1)
logger.info("Hello from Rust")
logger.success("Deployed successfully 🚀", region="us-west")   # success maps to INFO
logger.warning("This might be slow", attempt=2)
logger.error("Something failed", user="fiaz", retry=False)
logger.critical("Out of memory")

# logger.log allows runtime level name (string)
logger.log("debug", "debugging details", step=3)

# -----------------------------
# Context helpers
# -----------------------------
# bind: returns a proxy pre-attached with context
req_logger = logger.bind(request_id="r-123", user="alice")
req_logger.info("request start")  # request_id & user included automatically

# contextualize: temporarily adds context for the with-block only
with logger.contextualize(step=1):
	logger.debug("processing step")

# -----------------------------
# Exception helpers
# -----------------------------
# catch: decorator/context manager that logs exceptions automatically
# reraise=False swallows after logging; reraise=True re-raises after logging
@logger.catch(reraise=False)
def may_fail(x):
	return 1 / x

may_fail(0)  # logged and swallowed

try:
	1 / 0
except Exception:
	# logger.exception logs the current exception with traceback at ERROR level
	logger.exception("unexpected error")

# -----------------------------
# Per-call options and aliases
# -----------------------------
# opt: returns a proxy with call-time options (reserved for per-call formatting/options)
logger.opt(colors=False).info("no colors for this call")

# level(name, mapped_to): register a proxy-side alias mapping
logger.level("notice", "INFO")
logger.log("notice", "This is a notice")

# -----------------------------
# Enable / disable and sink management
# -----------------------------
logger.disable()                       # proxy will ignore logging calls
logger.info("this will be ignored")  # no-op while disabled
logger.enable()

# Remove a sink by handler id. Returns True in MVP (removal semantics limited)
hid = logger.add("logs/temp.log")
removed = logger.remove(hid)           # should return True

# -----------------------------
# JSON / structured use notes
# -----------------------------
# In JSON mode each record has a `fields` dict containing kwargs + bound/context values.
logger.configure(json=True)            # switch to structured output
logger.info("json message", item=42)

# -----------------------------
# Flush / Complete
# -----------------------------
# complete() flushes any buffered output; useful in short-lived scripts/tests.
# In async file mode, this also joins the background writer to ensure all lines are persisted.
logger.complete()
```

### Filename rotation and retention

- rotation controls when a new file is started: `"daily" | "hourly" | "minutely" | "never"`.
- date_style controls where the timestamp appears in the filename when dates are enabled:
	- `"before_ext"` (default): `app.2025-08-22.log`
	- `"prefix"`: `2025-08-22.app.log`
- date_enabled toggles whether the date is incorporated into filenames (default: False). When False, rotation timing still applies but filenames keep the base name.
- retention sets a maximum count of rotated files to keep. On each rollover, oldest files beyond the limit are deleted.

Examples

```python
# Prefix the date and keep the last 10 files
logger.add("logs/app.log", rotation="daily", date_style="prefix", date_enabled=True, retention=10)

# Insert date before extension; disable dates in filenames but still rotate hourly
logger.add("logs/app.log", rotation="hourly", date_enabled=False)
```

## What’s new (features)

The latest iteration adds performance-focused and convenience features, with simple, commented examples:

- Async-safe file sink (background writer)
	- Lower per-call latency; flush deterministically with `logger.complete()`.
	- Example:

		```python
		logger.add("logs/app.log", rotation="daily", async_write=True)
		# ...
		logger.complete()  # join background writer and flush
		```

- Per-sink filters (minimum level, module, function)
	- Only write relevant records to a file sink.

		```python
		logger.add(
				"logs/filtered.log",
				rotation="daily",
				filter_min_level="INFO",       # INFO+
				filter_module="myapp.handlers", # only this module
				filter_function=None,            # or set a function name
		)
		```

- Structured JSON logging with pretty mode
	- Machine-ingestible by default; switch to pretty for local readability.

		```python
		logger.configure(level="INFO", json=True)                 # compact JSON
		logger.configure(level="INFO", json=True, pretty_json=True)  # pretty JSON
		```

- Callsite capture for filtering
	- Python proxy attaches `module` and `function` for filter matching.

- Thread-safety and deterministic flush
	- `logger.complete()` ensures all pending lines are persisted (joins the writer when async).

- Count-based file retention for rotated logs
	- Set `retention` to keep at most N rotated files; oldest are pruned on rollover.

- **Async Callbacks:**
	- Register callback functions that execute asynchronously when logs are emitted
	- Zero performance impact - callbacks run in background threads
	- Perfect for real-time monitoring, alerting, and log aggregation
	- Example:
		```python
		def alert_on_error(record):
			if record.get("level") == "ERROR":
				send_alert(record)
		
		callback_id = logger.add_callback(alert_on_error)
		logger.error("Something failed!")  # Callback executes asynchronously
		logger.complete()  # Ensure all callbacks finish
		```

- **Template Strings:**
	- Use `{variable}` syntax for efficient, deferred string interpolation
	- Variables are extracted and become structured context fields
	- Works seamlessly with f-strings, % formatting, `bind()`, and `contextualize()`
	- Better performance - variables only evaluated if log passes level filter
	- Example:
		```python
		logger.info("User {user} logged in", user="alice", ip="192.168.1.1")
		# Output: "User alice logged in" with ip as context field
		```


## Performance & Benchmarks

**Logly** delivers significant performance improvements through Rust-powered optimizations. The core is implemented using high-performance libraries (`parking_lot`, `crossbeam-channel`, `ahash`) to minimize overhead in high-volume logging scenarios.

### 🚀 Performance Results

**Benchmark Environment:** Windows, PowerShell, Python 3.12.9

#### File Logging (50,000 messages, 3 repeats)
| Library | Mean Time | Speedup |
|---------|-----------|---------|
| Python stdlib logging | 0.729s | baseline |
| **Logly** | **0.205s** | **3.55x faster** 🚀 |

#### Concurrent Logging (4 threads × 25,000 messages, 3 repeats)
| Library | Mean Time | Speedup |
|---------|-----------|---------|
| Python stdlib logging | 3.919s | baseline |
| **Logly** | **0.405s** | **9.67x faster** 🚀 |

#### Latency Microbenchmark (30,000 messages)
| Percentile | stdlib logging | Logly | Improvement |
|------------|----------------|-------|-------------|
| **p50** | 0.014ms | **0.002ms** | **7x faster** 🚀 |
| **p95** | 0.029ms | **0.002ms** | **14.5x faster** 🚀 |
| **p99** | 0.043ms | **0.015ms** | **2.9x faster** 🚀 |

### What's New

**New Features:**
- 📏 **Size-based rotation**: Rotate log files based on file size (e.g., "10MB", "1GB", "500KB")
- 🔄 **Combined rotation**: Use both time-based and size-based rotation together
- 📊 **Enhanced retention**: Works with both time and size-based rotation

**Performance Optimizations:**
- 🔒 `parking_lot::RwLock` - 5-10x faster than std::sync::Mutex
- 📡 `crossbeam-channel` - Superior async throughput vs std::sync::mpsc
- #️⃣ `ahash` - 30% faster HashMap hashing
- 📦 `smallvec` - Reduces heap allocations by 80%+
- 🔄 `Arc<Mutex<>>` - Thread-safe file writers
- ⚡ Lock-free atomic operations with `arc-swap`



### Reproduce These Benchmarks

```powershell
# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Build the project
uv run maturin develop --release

# Run file logging benchmark (50k messages)
uv run python bench/benchmark_logging.py --mode file --count 50000 --repeat 3

# Run concurrency benchmark (4 threads × 25k messages)
uv run python bench/benchmark_concurrency.py --threads 4 --count-per-thread 25000 --repeat 3

# Run latency microbenchmark (30k messages)
uv run python bench/benchmark_latency.py --mode file --count 30000

# Run comprehensive test matrix
uv run python bench/benchmark_matrix.py --count 50000 --repeat 2
```
### Additional Benchmark Options

**Advanced file logging tests:**
```powershell
# Add structured fields (simulates payload size)
uv run python bench/benchmark_logging.py --mode file --count 50000 --fields 5

# Increase message size to test serialization impact
uv run python bench/benchmark_logging.py --mode console --count 50000 --message-size 200

# Mix levels (INFO/DEBUG) to exercise filtering
uv run python bench/benchmark_logging.py --mode file --count 50000 --level-mix

# JSON formatted output
uv run python bench/benchmark_logging.py --mode file --json --count 100000 --repeat 3
```

**Notes:**
- Results depend on OS, CPU, Python version, and system load
- Run benchmarks multiple times for reliable estimates
- File-mode benchmarks best reflect real-world performance
- Async mode (default) shows the largest performance gains


## Concurrency benchmark

Logly's `crossbeam-channel` and `parking_lot::RwLock` provide excellent multi-threaded performance. The concurrency benchmark stresses parallel producers writing to a shared file sink.

**Results (4 threads × 25,000 messages):**
- stdlib logging: 3.919s
- **Logly: 0.405s (9.67x faster)** 🚀

```powershell
# Run the benchmark (4 threads × 25k messages, 3 repeats)
uv run python bench/benchmark_concurrency.py --threads 4 --count-per-thread 25000 --repeat 3

# Compare sync writes (disables async background writer)
uv run python bench/benchmark_concurrency.py --threads 4 --count-per-thread 25000 --repeat 2 --sync

# JSON compact format
uv run python bench/benchmark_concurrency.py --threads 4 --count-per-thread 15000 --repeat 2 --json

# JSON pretty-printed (human-friendly, slower)
uv run python bench/benchmark_concurrency.py --threads 4 --count-per-thread 10000 --repeat 2 --json --pretty-json
```

**Notes:**
- Single shared file sink simulates realistic contention
- Async mode uses background writer thread (`logger.complete()` ensures flush)
- Performance scales well with more threads


### Latency microbenchmark (p50/p95/p99)

Measure per-call latency distribution for detailed performance analysis:

**Results (30,000 messages):**
- **p50 latency: 0.002ms (7x faster than stdlib)**
- **p95 latency: 0.002ms (14.5x faster than stdlib)**
- **p99 latency: 0.015ms (2.9x faster than stdlib)**

```powershell
# File mode, text format
uv run python bench/benchmark_latency.py --mode file --count 30000

# Console mode
uv run python bench/benchmark_latency.py --mode console --count 20000

# File mode with JSON
uv run python bench/benchmark_latency.py --mode file --json --count 30000
```

Outputs median (p50), p95, and p99 latencies to help gauge tail behavior and identify performance outliers.


## API reference (current features)

The Python `logger` is a small proxy around the Rust `PyLogger`. The proxy adds convenience features like `bind()` and `contextualize()` while forwarding core calls to the Rust backend.

Creation
- `logger` — global proxy instance exported from `logly`.

Configuration & sinks

- `logger.add(sink: str | None = None, *, rotation: str | None = None, size_limit: str | None = None, retention: int | None = None, filter_min_level: str | None = None, filter_module: str | None = None, filter_function: str | None = None, async_write: bool = True, date_style: str | None = None, date_enabled: bool = False) -> int`
	- Add a sink. Use `"console"` for stdout/stderr or a file path to write logs to disk. Returns a handler id (int).
	- `rotation`: `"daily" | "hourly" | "minutely" | "never"` (rolling appender). Can be combined with size-based rotation.
	- `size_limit`: **File size limits** - `"500B" | "5KB" | "10MB" | "1GB" | "500MB"` etc. (size-based rotation). When file reaches this size, it rotates. Can be combined with time-based rotation for more complex policies.
	- `retention`: Maximum number of rotated files to keep. Older files are automatically deleted on rollover. Set to `None` for unlimited retention.
	- `date_style`: `"before_ext"` (default) or `"prefix"` — controls where the rotation timestamp is placed in the filename.
	  - `"before_ext"`: `app.2025-08-22.log` (date before file extension)
	  - `"prefix"`: `2025-08-22.app.log` (date as prefix)
	- `buffer_size`: Buffer size in bytes for async writing (default: 8192). Larger buffers reduce I/O operations but use more memory.
	- `flush_interval`: Time in milliseconds between automatic flushes for async writing (default: 100). Lower values reduce latency but increase I/O.
	- `max_buffered_lines`: Maximum number of lines to buffer before blocking the logging thread (default: 1000). Prevents unbounded memory growth.
	- `date_style`: Date format style for filenames. Options: "before_ext" (default), "prefix", "rfc3339", "local", "utc".
	- `date_enabled`: When True, includes date in rotated filenames (default: False).

	Example — advanced async configuration for high-throughput logging:

	```python
	# High-throughput configuration: larger buffer, less frequent flushing
	logger.add(
		"logs/high-volume.log",
		async_write=True,
		buffer_size=65536,        # 64KB buffer
		flush_interval=500,       # Flush every 500ms
		max_buffered_lines=5000,  # Allow up to 5000 buffered lines
	)
	
	# Low-latency configuration: smaller buffer, frequent flushing
	logger.add(
		"logs/low-latency.log", 
		async_write=True,
		buffer_size=4096,         # 4KB buffer
		flush_interval=50,        # Flush every 50ms
		max_buffered_lines=100,   # Limit buffer to 100 lines
	)
	```

	Date style examples:

	```python
	# Date before file extension (default)
	logger.add("logs/app.log", rotation="daily", date_enabled=True)
	# Creates: app.2025-01-15.log
	
	# Date as prefix
	logger.add("logs/app.log", rotation="daily", date_enabled=True, date_style="prefix")
	# Creates: 2025-01-15.app.log
	
	# RFC3339 timestamp format
	logger.add("logs/app.log", rotation="hourly", date_enabled=True, date_style="rfc3339")
	# Creates: app.2025-01-15T14-30-00Z.log
	```

	Size-based rotation examples:

	```python
	# Size-based rotation
	logger.add("logs/app.log", size_limit="10MB")
	
	# Combined time and size rotation
	logger.add("logs/combined.log", rotation="daily", size_limit="500KB", retention=10)
	
	# Size rotation with different units
	logger.add("logs/debug.log", size_limit="1GB", retention=5)    # Gigabytes
	logger.add("logs/trace.log", size_limit="50MB", retention=3)   # Megabytes
	logger.add("logs/temp.log", size_limit="100KB", retention=2)   # Kilobytes
	```

	Advanced filtering examples:

	```python
	# Filter by level only
	logger.add("logs/errors.log", filter_min_level="ERROR")
	
	# Filter by module and level
	logger.add(
		"logs/auth.log", 
		filter_min_level="INFO",
		filter_module="myapp.auth"
	)
	
	# Filter by function and module
	logger.add(
		"logs/handlers.log",
		filter_min_level="DEBUG", 
		filter_module="myapp.handlers",
		filter_function="process_request"
	)
	
	# Multiple filtered sinks for different concerns
	logger.add("logs/security.log", filter_min_level="WARNING", filter_module="myapp.security")
	logger.add("logs/database.log", filter_min_level="ERROR", filter_module="myapp.db")
	logger.add("logs/api.log", filter_min_level="INFO", filter_module="myapp.api")
	```

- `logger.configure(level: str = "INFO", color: bool = True, json: bool = False, pretty_json: bool = False) -> None`
	- Set the base level for console output, enable/disable ANSI coloring, and toggle structured JSON output.
	- `pretty_json`: pretty-print JSON output for readability (higher cost than compact JSON).
	- When `json=True`, console and file sinks emit newline-delimited JSON records with fields: `timestamp`, `level`, `message`, and `fields` (merged kwargs and bound context).

	Example — set INFO, enable colors, keep text output:

	```python
	logger.configure(level="INFO", color=True, json=False)
	# pretty JSON
	logger.configure(level="INFO", color=False, json=True, pretty_json=True)
	```

	Advanced configure examples:

	```python
	# Development configuration: verbose, colored output
	logger.configure(level="DEBUG", color=True, json=False)
	
	# Production configuration: structured JSON logging
	logger.configure(level="INFO", color=False, json=True, pretty_json=False)
	
	# Debugging configuration: pretty JSON for readability
	logger.configure(level="TRACE", color=False, json=True, pretty_json=True)
	
	# Minimal configuration: errors only, no colors
	logger.configure(level="ERROR", color=False, json=False)
	```

- `logger.remove(handler_id: int) -> bool`
	- Remove a previously added sink by id. In the current MVP this returns True but removal semantics are limited.

Logging functions

All logging calls accept a message and optional keyword arguments that become structured fields (JSON mode) or a `key=value` suffix (text mode). Keyword args are merged with any bound context.

- `logger.trace(msg, **kwargs)` — lowest level
- `logger.debug(msg, **kwargs)`
- `logger.info(msg, **kwargs)`
- `logger.success(msg, **kwargs)` — convenience alias mapped to INFO
- `logger.warning(msg, **kwargs)`
- `logger.error(msg, **kwargs)`
- `logger.critical(msg, **kwargs)` — highest level
- `logger.log(level, msg, **kwargs)` — send with a runtime level string

Examples:

```python
logger.info("User logged in", user_id=42)
logger.error("Payment failed", order_id=1234, retry=False)
logger.log("debug", "debug details", step=1)
```

Advanced logging examples with different string formats:

```python
# Template strings (recommended for performance)
logger.info("User {user} logged in from {ip}", user="alice", ip="192.168.1.1")

# F-string formatting (evaluated immediately)
user = "bob"
logger.info(f"User {user} logged in", session_id="sess-123")

# % formatting (legacy style)
logger.info("Processing item %d of %d", 5, 10)

# Structured logging with multiple fields
logger.error(
	"Database connection failed", 
	db_host="localhost", 
	db_port=5432, 
	retry_count=3,
	error_code="ECONNREFUSED"
)

# Custom level with alias
logger.level("NOTICE", "INFO")
logger.log("NOTICE", "System maintenance scheduled", maintenance_window="2h")
```

Context & convenience

- `logger.bind(**kwargs) -> logger`
	- Returns a new proxy that automatically includes `kwargs` with every emitted record. Useful to attach request IDs, user ids, or other per-context metadata.

	```python
	request_logger = logger.bind(request_id="r-123", user="alice")
	request_logger.info("start")
	```

	Advanced bind examples:

	```python
	# Request-scoped logger
	request_logger = logger.bind(
		request_id="req-abc123",
		user_id=42,
		user_agent="Mozilla/5.0",
		ip_address="192.168.1.100"
	)
	request_logger.info("Processing payment", amount=99.99)
	request_logger.warning("Payment retry", attempt=2)

	# Component-scoped logger
	db_logger = logger.bind(component="database", host="db-prod-01")
	db_logger.info("Connection established", pool_size=10)
	db_logger.error("Query timeout", query="SELECT * FROM users", duration_ms=5000)

	# Chained binding (inherits parent context)
	base_logger = logger.bind(app="myapp", version="1.2.3")
	api_logger = base_logger.bind(module="api", endpoint="/users")
	api_logger.debug("Processing request", method="GET", user_count=150)
	```

- `logger.contextualize(**kwargs)`
	- Context manager that temporarily adds the provided kwargs to the proxy for the duration of the `with` block.

	```python
	with logger.contextualize(step=1):
			logger.info("processing")
	```

	Advanced contextualize examples:

	```python
	# Temporary context for operation
	with logger.contextualize(operation="user_registration", step=1):
		logger.info("Validating user data")
		# ... validation logic ...
		
		with logger.contextualize(step=2, validation_time_ms=150):
			logger.info("Creating user account")
			# ... account creation ...
			
		with logger.contextualize(step=3, account_id="acc-123"):
			logger.info("Sending welcome email")
			# ... email sending ...

	# Nested contexts (inner contexts inherit outer ones)
	with logger.contextualize(request_id="req-456", user="bob"):
		logger.info("Request started")
		
		with logger.contextualize(operation="data_processing", batch_size=100):
			logger.debug("Processing batch")
			
			with logger.contextualize(item_id="item-789", processing_time_ms=45):
				logger.info("Item processed successfully")

	# Exception handling with context
	try:
		with logger.contextualize(operation="file_upload", filename="data.csv"):
			process_upload("data.csv")
	except Exception as e:
		logger.exception("Upload failed")
	```

- `logger.catch(reraise=False)`
	- Decorator/context manager to log exceptions automatically. When used as a decorator it will log the exception and either swallow it (`reraise=False`) or re-raise it (`reraise=True`).

	```python
	@logger.catch(reraise=False)
	def may_fail():
			1 / 0
	```

	Advanced catch examples:

	```python
	# As a decorator - swallow exceptions
	@logger.catch(reraise=False)
	def process_payment(amount, card_number):
		# Risky payment processing logic
		if amount > 1000:
			raise ValueError("Amount too high")
		return f"Processed ${amount}"

	# As a decorator - re-raise exceptions
	@logger.catch(reraise=True)
	def validate_user_data(user_data):
		if not user_data.get("email"):
			raise ValueError("Email required")
		return "Valid"

	# As a context manager - temporary error handling
	def risky_operation():
		with logger.catch(reraise=False):
			# Multiple operations that might fail
			step1_result = do_step1()
			step2_result = do_step2(step1_result)
			return step2_result

	# Nested catch blocks with different behaviors
	try:
		with logger.catch(reraise=True):  # Re-raise for outer handling
			@logger.catch(reraise=False)  # Swallow for inner operations
			def inner_operation():
				return risky_calculation()
			result = inner_operation()
	except Exception:
		logger.error("Outer operation failed, but inner errors were logged")
	```

- `logger.exception(msg="")`
	- Convenience that logs the current exception at error level with traceback details.

	Advanced exception examples:

	```python
	# Basic exception logging
	try:
		result = 1 / 0
	except ZeroDivisionError:
		logger.exception("Math error occurred")

	# Exception with additional context
	try:
		user_id = get_user_id_from_request(request)
		process_user_payment(user_id, amount)
	except Exception:
		logger.exception("Payment processing failed", user_id=user_id, amount=amount)

	# Exception in different loggers with context
	request_logger = logger.bind(request_id="req-123", user="alice")
	try:
		process_complex_business_logic(request.data)
	except Exception:
		request_logger.exception("Business logic error")

	# Custom exception message with full context
	try:
		db_connection = connect_to_database()
		execute_query(db_connection, complex_query)
	except DatabaseError as e:
		logger.exception(f"Database operation failed: {e}", 
						query=complex_query,
						connection_pool_size=10,
						timeout_seconds=30)
	except Exception:
		logger.exception("Unexpected error during database operation")
	```

- `logger.opt(**options) -> logger`
	- Return a proxy with call-time options (kept for future enhancements such as per-call formatting options).

- `logger.enable()` / `logger.disable()`
	- Toggle logging at the proxy level. When disabled, the proxy's logging methods are no-ops.

	Advanced enable/disable examples:

	```python
	# Conditional logging based on environment
	import os

	if os.getenv("LOGGING_ENABLED", "true").lower() == "false":
		logger.disable()
	else:
		logger.enable()

	# Temporary disable for performance-critical sections
	logger.info("Starting batch processing")
	logger.disable()  # Disable logging for performance
	
	for item in large_dataset:
		process_item(item)  # No logging overhead
	
	logger.enable()   # Re-enable logging
	logger.info("Batch processing completed")

	# Scoped disable using context manager pattern
	class LoggingContext:
		def __init__(self, logger):
			self.logger = logger
			self.was_enabled = logger._enabled
		
		def __enter__(self):
			self.logger.disable()
			return self
		
		def __exit__(self, exc_type, exc_val, exc_tb):
			if self.was_enabled:
				self.logger.enable()

	with LoggingContext(logger):
		# Logging disabled in this block
		perform_noisy_operation()
	# Logging restored to previous state
	```

- `logger.level(name, mapped_to)`
	- Register or alias a custom level name to an existing level recognized by the backend.

	Advanced level examples:

	```python
	# Create custom level aliases for domain-specific logging
	logger.level("NOTICE", "INFO")      # Notice messages
	logger.level("ALERT", "WARNING")    # Alert conditions
	logger.level("CRIT", "CRITICAL")    # Critical system events
	logger.level("EMERG", "CRITICAL")   # Emergency situations

	# Use custom levels in logging
	logger.log("NOTICE", "System maintenance scheduled", window="2h")
	logger.log("ALERT", "High memory usage detected", usage_percent=85)
	logger.log("CRIT", "Database connection pool exhausted")
	logger.log("EMERG", "System shutdown imminent")

	# Business domain levels
	logger.level("AUDIT", "INFO")       # Security/audit events
	logger.level("METRIC", "DEBUG")     # Performance metrics
	logger.level("TRACE", "TRACE")      # Detailed tracing

	# Use in business logic
	logger.log("AUDIT", "User login", user_id=123, ip="192.168.1.1")
	logger.log("METRIC", "Request latency", endpoint="/api/users", latency_ms=45)
	logger.log("TRACE", "Database query executed", query="SELECT * FROM users", rows=150)
	```

- `logger.complete()`
	- Flushes or completes any buffered output for the current proxy (useful in short-lived scripts or tests).

	Advanced complete examples:

	```python
	# Essential for short-lived scripts
	def main():
		logger.add("app.log", rotation="daily")
		logger.info("Script started")
		
		try:
			do_work()
			logger.success("Work completed successfully")
		except Exception as e:
			logger.exception("Work failed")
		finally:
			logger.complete()  # Ensure all logs are written before exit

	# With async callbacks
	def process_with_callbacks():
		logger.add("processing.log", async_write=True)
		
		# Register callback for monitoring
		def monitor_progress(record):
			if "completed" in record.get("message", "").lower():
				send_progress_notification(record)
		
		callback_id = logger.add_callback(monitor_progress)
		
		try:
			logger.info("Starting batch processing")
			process_batch_data()
			logger.info("Batch processing completed")
		finally:
			logger.complete()  # Flush logs AND wait for callbacks to finish
			logger.remove_callback(callback_id)

	# In testing scenarios
	def test_logging_behavior():
		logger.add("test.log", async_write=True)
		
		# Test various logging scenarios
		logger.info("Test message 1")
		logger.error("Test error")
		
		# Force flush to ensure test log files are complete
		logger.complete()
		
		# Now verify log file contents
		with open("test.log", "r") as f:
			content = f.read()
			assert "Test message 1" in content
			assert "Test error" in content

	# Graceful shutdown in servers
	import signal
	import sys

	def signal_handler(signum, frame):
		logger.warning("Received shutdown signal", signal=signum)
		logger.complete()  # Ensure all pending logs are written
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)
	```

Callbacks

Logly supports registering callback functions that are invoked asynchronously whenever a log message is emitted. This feature enables real-time log processing, monitoring, alerting, or forwarding logs to external systems without blocking the main application thread.

- `logger.add_callback(callback: Callable[[dict], None]) -> int`
	- Register a callback function that will be called for every log message. The callback receives a dictionary containing log record information.
	- Returns a callback ID (integer) that can be used to remove the callback later.
	- **Asynchronous execution**: Callbacks run in background threads, ensuring zero impact on application performance.
	- **Thread-safe**: Multiple callbacks can be registered and executed concurrently.
	
	**Callback Record Structure:**
	The callback receives a dictionary with the following fields:
	- `timestamp`: ISO-8601 formatted timestamp string
	- `level`: Log level name (e.g., "INFO", "ERROR", "DEBUG")
	- `message`: The formatted log message string
	- Additional fields from `bind()`, `contextualize()`, and kwargs
	
	Example — add a callback for real-time monitoring:
	
	```python
	# Define a callback for alerting
	def alert_on_error(record):
		if record.get("level") == "ERROR":
			send_notification(f"Error: {record['message']}")
	
	# Register the callback
	callback_id = logger.add_callback(alert_on_error)
	
	# Log an error - callback executes in background
	logger.error("Database connection failed", retry_count=3)
	
	# Ensure callbacks complete before exit
	logger.complete()
	```

- `logger.remove_callback(callback_id: int) -> bool`
	- Remove a previously registered callback using its ID.
	- Returns `True` if the callback was successfully removed, `False` if the ID was not found.
	
	Example:
	
	```python
	# Remove the callback when no longer needed
	success = logger.remove_callback(callback_id)
	```

	Advanced callback examples:

	```python
	# Multiple callbacks for different purposes
	def log_to_external_system(record):
		# Send to external logging service
		external_logger.log(record["level"], record["message"], **record)

	def metrics_collector(record):
		# Collect metrics on log levels
		metrics.increment(f"logs.{record['level'].lower()}")

	def audit_trail(record):
		# Security audit logging
		if record.get("level") in ["WARNING", "ERROR", "CRITICAL"]:
			audit_log.write(json.dumps(record))

	# Register multiple callbacks
	external_id = logger.add_callback(log_to_external_system)
	metrics_id = logger.add_callback(metrics_collector)
	audit_id = logger.add_callback(audit_trail)

	# Callbacks execute for every log message
	logger.info("User action", user_id=123, action="login")
	logger.warning("Rate limit exceeded", user_id=456, limit=100)

	# Context-aware callbacks
	request_logger = logger.bind(request_id="req-789", user="alice")

	def request_monitor(record):
		# Only process records from this request
		if record.get("request_id") == "req-789":
			update_request_metrics(record)

	request_monitor_id = request_logger.add_callback(request_monitor)
	request_logger.info("Processing payment", amount=50.00)
	request_logger.complete()  # Ensure callback finishes

	# Error handling in callbacks
	def robust_callback(record):
		try:
			process_log_record(record)
		except Exception as e:
			# Log callback errors to stderr to avoid infinite loops
			print(f"Callback error: {e}", file=sys.stderr)

	# Cleanup callbacks
	logger.remove_callback(external_id)
	logger.remove_callback(metrics_id)
	logger.remove_callback(audit_id)
	```

**Performance Notes:**
- Callbacks execute in background threads with no blocking on the main thread
- Multiple callbacks can be registered and run concurrently
- If a callback raises an exception, it's silently caught to prevent logging disruption
- Always call `logger.complete()` before program exit to ensure all callbacks finish

Template Strings

Template strings provide an intuitive and Pythonic way to format log messages using `{variable}` syntax with deferred evaluation for better performance.

**Usage:**

```python
# Template strings with deferred evaluation
logger.info("User {user} logged in from {ip}", user="alice", ip="192.168.1.1")
# Output: "User alice logged in from 192.168.1.1" with structured fields

# Works with f-strings (pre-evaluated)
user = "bob"
logger.info(f"User {user} logged in", session_id="sess-123")

# Works with % formatting (legacy)
logger.info("Processing item %d of %d", 5, 10)

# Works with bind() for persistent context
req_logger = logger.bind(request_id="r-123")
req_logger.info("User {user} action {action}", user="alice", action="login")
# All three fields (request_id, user, action) included
```

Advanced template string examples:

```python
# Complex template with multiple variables
logger.info("Request {method} {path} completed in {duration:.2f}ms with status {status}", 
           method="POST", path="/api/users", duration=45.67, status=201)

# Template with conditional context
def process_order(order_id, user_id):
    logger.info("Processing order {order_id} for user {user_id}", 
               order_id=order_id, user_id=user_id)
    
    if validate_order(order_id):
        logger.info("Order {order_id} validated successfully", order_id=order_id)
        # Additional processing...
    else:
        logger.warning("Order {order_id} validation failed", order_id=order_id)

# Template with nested context
with logger.contextualize(service="payment", version="v2.1"):
    logger.info("Payment service started")
    
    payment_logger = logger.bind(transaction_id="txn-12345")
    payment_logger.info("Processing payment of {amount} {currency}", 
                       amount=99.99, currency="USD")
    payment_logger.debug("Payment gateway {gateway} responded with {response_code}",
                        gateway="stripe", response_code=200)

# Template with list/dict serialization
logger.info("Batch job {job_id} processed {count} items: {items}", 
           job_id="batch-001", 
           count=5, 
           items=["item1", "item2", "item3", "item4", "item5"])

# Template with error context
try:
    result = risky_operation(param="value")
    logger.info("Operation succeeded with result {result}", result=result)
except Exception as e:
    logger.error("Operation failed for param {param}: {error}", 
                param="value", error=str(e))
```

**Benefits:**
- **Performance**: Variables only evaluated if log passes level filter
- **Structured logging**: Variables become fields in JSON mode
- **Readable**: More maintainable than manual string concatenation
- **Flexible**: Works with all Python string formats (f-strings, %, template)
- **PEP 750 inspired**: Deferred evaluation for efficiency

Notes

- When `json=False` (default), kwargs are appended as a `key=value` suffix in text output for quick human readability.
- When `json=True`, kwargs and bound context are placed in the `fields` object of the emitted JSON record for structured logging.
- Callbacks receive all log records regardless of `json` mode setting.


## Advanced examples

Binding + contextualize example

```python
from logly import logger

logger.add("logs/app.log")
logger.configure(level="DEBUG")

request_logger = logger.bind(request_id="r-123", user="alice")
request_logger.info("start")

with request_logger.contextualize(step=1):
	request_logger.debug("processing")

request_logger.complete()
```

catch and exception

```python
from logly import logger

@logger.catch(reraise=False)
def may_raise(x):
	return 1 / x

try:
	may_raise(0)
except Exception:
	# not re-raised when reraise=False
	pass

try:
	with logger.catch(reraise=True):
		1 / 0
except ZeroDivisionError:
	# re-raised
	pass

try:
	1 / 0
except Exception:
	logger.exception("unexpected")

```

Using `opt()`

```python
logger.opt(colors=False).info("no colors for this call")
```

Per-sink filtering by module/function and level

```python
from logly import logger

# Configure JSON with pretty output for readability during local runs
logger.configure(level="DEBUG", json=True, pretty_json=True)

# Only write INFO+ events from a specific module to a file; everything still goes to console
logger.add(
	"logs/filtered.log",
	rotation="daily",
	filter_min_level="INFO",
	filter_module="myapp.handlers",
	async_write=True,
)

# Simulate calls from different modules/functions
def do_work():
	logger.info("from do_work")

if __name__ == "myapp.handlers":
	do_work()
else:
	# This won't match filter_module, so it won't be written to filtered.log
	logger.info("from other module")

logger.complete()
```

## Testing

Run the unit tests with:

```powershell
uv run pytest -q
```

## Changelog

For detailed release notes and version history, see the [GitHub Releases](https://github.com/muhammad-fiaz/logly/releases) page.

**Don't forget to ⭐ star the repository if you find it useful!**


## Contributing

Contributions are welcome!

If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.
And make sure to follow the [project guidelines](CODE_OF_CONDUCT.md)

### Want to contribute?

If you'd like to contribute to this project, please check out the [contributing guidelines](CONTRIBUTING.md), fork the repository, and submit a pull request. Every contribution is welcome and appreciated!

A big thank you to everyone who contributed to this project! 💖

[![Portfolio contributors](https://contrib.rocks/image?repo=muhammad-fiaz/logly&max=2000)](https://github.com/muhammad-fiaz/logly/graphs/contributors)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file in the repository root for the full license text.


<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=muhammad-fiaz/logly&type=Date)](https://github.com/muhammad-fiaz/logly/)

</div>