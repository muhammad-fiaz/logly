<div align="center">
<img src="https://github.com/user-attachments/assets/565fc3dc-dd2c-47a6-bab6-2f545c551f26" alt="logly logo"  />

[![PyPI](https://img.shields.io/pypi/v/logly.svg)](https://pypi.org/project/logly/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/logly.svg)](https://pypistats.org/packages/logly)
[![Donate](https://img.shields.io/badge/Donate-%20-orange)](https://pay.muhammadfiaz.com)
[![Supported Python](https://img.shields.io/badge/python-%3E%3D3.9-brightgreen.svg)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly)
[![GitHub forks](https://img.shields.io/github/forks/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly/network)
[![GitHub release](https://img.shields.io/github/v/release/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly/releases)
[![GitHub issues](https://img.shields.io/github/issues/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly/pulls)
[![GitHub last commit](https://img.shields.io/github/last-commit/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly/commits)
[![GitHub contributors](https://img.shields.io/github/contributors/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly/graphs/contributors)
[![Codecov](https://img.shields.io/codecov/c/gh/muhammad-fiaz/logly.svg)](https://codecov.io/gh/muhammad-fiaz/logly)
[![Pytest](https://img.shields.io/badge/pytest-%3E%3D7.0-blue.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/github/license/muhammad-fiaz/logly.svg)](https://github.com/muhammad-fiaz/logly)


<p><em>Rust-powered, Loguru-like logging for Python.</em></p>

</div>



Logly is a Rust-powered, Loguru-like logging library for Python that combines the familiarity of Python’s standard logging API with high-performance logging capabilities. It is designed for developers who need efficient, reliable logging in applications that generate large volumes of log messages.

Logly's core is implemented in Rust using tracing and exposed to Python via PyO3/Maturin for safety and performance.

<details>
<summary><strong>Table of contents</strong></summary>

- [Install (PyPI)](#install-pypi)
- [Nightly / install from GitHub](#nightly--install-from-github)
- [Quickstart](#quickstart)
- [What’s new (features)](#whats-new-features)
- [Performance \& Benchmarks](#performance--benchmarks)
- [Concurrency benchmark](#concurrency-benchmark)
	- [Latency microbenchmark (p50/p95/p99)](#latency-microbenchmark-p50p95p99)
- [API reference (current features)](#api-reference-current-features)
- [Advanced examples](#advanced-examples)
- [Testing](#testing)
- [Roadmap (planned features)](#roadmap-planned-features)
- [Contributing](#contributing)
- [License](#license)
- [Development (build from source)](#development-build-from-source)

</details>

---

## Install (PyPI)

The recommended installation is from PyPI. Once published, users can install with:

```powershell
python -m pip install --upgrade pip
pip install logly
```

If you want to test a pre-release on TestPyPI (when releases are uploaded there):

```powershell
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple logly
```

If you are a package consumer, this is all you need; the rest of this README documents usage and developer instructions.

## Nightly / install from GitHub

You can install the latest code from the GitHub repository (useful for nightly builds or unreleased fixes). 

```powershell
pip install git+https://github.com/muhammad-fiaz/logly.git
```

## Quickstart

```python
from logly import logger

# -----------------------------
# Add sinks (logger.add)
# -----------------------------
# sink: "console" or a file path. Returns a handler id (int).
# rotation: "daily" | "hourly" | "minutely" | "never" (MVP supports simple rolling behavior).
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

# Examples of other rotation values:
logger.add("logs/hourly.log", rotation="hourly")
logger.add("logs/never.log", rotation="never")    # no rotation

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


## Performance & Benchmarks

Logly's core is implemented in Rust to reduce the per-message overhead of logging in high-volume Python applications. Below are two representative, reproducible runs performed locally on this machine (Windows, PowerShell). The first is a console run (noisy — terminal I/O can dominate timings). The second is a file-mode run which is a fairer test of serialization + IO performance and reflects the benefits of the async background writer.

Measured results (100,000 messages)

- Console run (single repeat, console-formatted output written to a temp file to exclude terminal I/O):

	- Python standard logging (mean): 1.5578 s
	- Logly (mean): 0.6603 s

	Note: previous console runs were noisy due to terminal I/O. The benchmark script now writes console-formatted output to a temp file when running `--mode console` so timing excludes terminal overhead. File-mode remains a fair test of serialization + IO, but this corrected console run also shows Logly is faster in this environment.

- File run (single repeat, async file sink):

	- Python standard logging (mean): 1.5439 s
	- Logly (mean): 0.6646 s

	What this shows

	- File-mode improvement: In this environment Logly completed the file-based workload roughly 57% faster than Python's standard logging and produced about a 2.32× speedup (1.5439 / 0.6646 ≈ 2.32). In other environments the improvement may be larger — up to 10× depending on the OS and CPU.
	- Why file-mode is a better comparison: console output adds variable terminal overhead; the async background writer plus compact serialization in Logly shows the most tangible gains when measuring disk-bound or structured-output scenarios.

Reproduce the exact runs I used (from the repository root)

Important: activate your virtual environment first (PowerShell):

```powershell
# if you used `uv` or `python -m venv` to create .venv
. .\.venv\Scripts\Activate.ps1
```

```powershell
# build and install the editable extension (requires maturin + Rust toolchain)
maturin develop

# run the console benchmark: 100k messages, 3 repeats
python .\bench\benchmark_logging.py --mode console --count 100000 --repeat 1

# additional scenarios
# JSON compact, console
python .\bench\benchmark_logging.py --mode console --json --count 100000 --repeat 3
# File sink, async (default)
python .\bench\benchmark_logging.py --mode file --count 100000 --repeat 1
# File sink, sync writes
python .\bench\benchmark_logging.py --mode file --sync --count 100000 --repeat 3
# JSON pretty (human-friendly; slower), console
python .\bench\benchmark_logging.py --mode console --json --pretty-json --count 50000 --repeat 3

# run a small matrix of scenarios
python .\bench\benchmark_matrix.py --count 50000 --repeat 2
```

Advanced options for benchmark_logging

- Add structured fields per log call (simulates payload size):

```powershell
python .\bench\benchmark_logging.py --mode file --count 50000 --fields 5
```

- Increase message size (bytes) to test serialization/IO impact:

```powershell
python .\bench\benchmark_logging.py --mode console --count 50000 --message-size 200
```

- Mix levels (INFO/DEBUG) to exercise level checks and filtering:

```powershell
python .\bench\benchmark_logging.py --mode file --count 50000 --level-mix
```

Notes and caveats

- Results depend on OS, CPU, Python version, interpreter warm-up, and console buffering. Run the benchmark multiple times and on your target environment for reliable estimates.
- This example targets synchronous console output. File sinks, JSON serialization, buffering, or async sinks will have different performance characteristics.
- To compare file-based logging, use `--mode file` with the benchmark script.

If you want, I can add a small helper that aggregates multiple runs (mean/median/stddev) or create a lightweight CI benchmark job that runs on push.


## Concurrency benchmark

To stress-test multi-threaded producers writing to a shared file sink, use the concurrency benchmark. This highlights the benefits of logly's async writer thread under parallel load.

```powershell
# 4 threads x 25k msgs each, JSON off, async on (default)
python .\bench\benchmark_concurrency.py --threads 4 --count-per-thread 25000 --repeat 2

# Compare sync file writes
python .\bench\benchmark_concurrency.py --threads 4 --count-per-thread 25000 --repeat 2 --sync

# JSON compact
python .\bench\benchmark_concurrency.py --threads 4 --count-per-thread 15000 --repeat 2 --json

# JSON pretty (human-friendly; slower)
python .\bench\benchmark_concurrency.py --threads 4 --count-per-thread 10000 --repeat 2 --json --pretty-json
```

Notes:
- The script uses a single shared file sink for each run to simulate realistic contention.
- In async mode, logly uses a background writer; `logger.complete()` ensures logs are flushed before timing stops.


### Latency microbenchmark (p50/p95/p99)

Measure per-call latency distribution for console or file sinks:

```powershell
# console, text
python .\bench\benchmark_latency.py --mode console --count 20000

# file, async, JSON compact
python .\bench\benchmark_latency.py --mode file --json --count 30000
```

Outputs median (p50), p95, and p99 latencies to help gauge tail behavior.


## API reference (current features)

The Python `logger` is a small proxy around the Rust `PyLogger`. The proxy adds convenience features like `bind()` and `contextualize()` while forwarding core calls to the Rust backend.

Creation
- `logger` — global proxy instance exported from `logly`.

Configuration & sinks

- `logger.add(sink: str | None = None, *, rotation: str | None = None, filter_min_level: str | None = None, filter_module: str | None = None, filter_function: str | None = None, async_write: bool = True) -> int`
-- `logger.add(sink: str | None = None, *, rotation: str | None = None, filter_min_level: str | None = None, filter_module: str | None = None, filter_function: str | None = None, async_write: bool = True, date_style: str | None = None, date_enabled: bool = True) -> int`
	- Add a sink. Use `"console"` for stdout/stderr or a file path to write logs to disk. Returns a handler id (int).
	- `rotation`: `"daily" | "hourly" | "minutely" | "never"` (rolling appender).
	- `date_style`: `"before_ext"` (default) or `"prefix"` — controls where the rotation timestamp is placed in the filename.
	- `date_enabled`: when False (default) no date is appended to filenames even if rotation is set; set to True to enable dated filenames.
	- `filter_min_level`: only write to this file if the record level is >= this level (e.g., `"INFO"`).
	- `filter_module`: only write if the callsite module matches this string.
	- `filter_function`: only write if the callsite function matches this string.
	- `async_write`: when True (default), file writes go through a background thread for lower latency.

	Example — add console and a rotating file sink:

	```python
	logger.add("console")
	logger.add(
		"logs/app.log",
		rotation="daily",
		filter_min_level="INFO",
		async_write=True,
	)
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

Context & convenience

- `logger.bind(**kwargs) -> logger`
	- Returns a new proxy that automatically includes `kwargs` with every emitted record. Useful to attach request IDs, user ids, or other per-context metadata.

	```python
	request_logger = logger.bind(request_id="r-123", user="alice")
	request_logger.info("start")
	```

- `logger.contextualize(**kwargs)`
	- Context manager that temporarily adds the provided kwargs to the proxy for the duration of the `with` block.

	```python
	with logger.contextualize(step=1):
			logger.info("processing")
	```

- `logger.catch(reraise=False)`
	- Decorator/context manager to log exceptions automatically. When used as a decorator it will log the exception and either swallow it (`reraise=False`) or re-raise it (`reraise=True`).

	```python
	@logger.catch(reraise=False)
	def may_fail():
			1 / 0
	```

- `logger.exception(msg="")`
	- Convenience that logs the current exception at error level with traceback details.

- `logger.opt(**options) -> logger`
	- Return a proxy with call-time options (kept for future enhancements such as per-call formatting options).

- `logger.enable()` / `logger.disable()`
	- Toggle logging at the proxy level. When disabled, the proxy's logging methods are no-ops.

- `logger.level(name, mapped_to)`
	- Register or alias a custom level name to an existing level recognized by the backend.

- `logger.complete()`
	- Flushes or completes any buffered output for the current proxy (useful in short-lived scripts or tests).

Notes

- When `json=False` (default), kwargs are appended as a `key=value` suffix in text output for quick human readability.
- When `json=True`, kwargs and bound context are placed in the `fields` object of the emitted JSON record for structured logging.


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

## Roadmap (planned features)

- Structured/JSON logging improvements (custom schemas, pretty mode, filtering nested types).
- Colorized console output with format options.
- Rotating policies and compression support for file sinks.
- Async-safe sinks that don't block Python threads and integrate with async runtimes.
- Fine-grained runtime configuration via `logger.configure()` accepting a full config dict.
- Full Loguru API parity (including sinks filters, exception formatting, record depth, contextual lazy formatting).

## Contributing

Problems, PRs and feature requests are welcome. For implementation tasks that touch Rust code, prefer small incremental PRs so the build and tests stay green.

## License

This project is licensed under the MIT License. See the `LICENSE` file in the repository root for the full license text.

---

If you'd like, I can now:
- Add unit tests for `bind()`, `contextualize()`, `catch()`, and `exception()`.
- Implement JSON structured output in the Rust core so bound context becomes structured logs rather than `key=value` suffixes.

Pick which to do next.

## Development (build from source)

If you plan to develop or build from source you will need the Rust toolchain and `maturin`.

From this repo (recommended, uses `uv` helper if present):

```powershell
# sync virtualenv and build in editable mode
uv sync
uv run maturin develop
```

Alternatively, run directly with:

```powershell
python -m pip install --upgrade maturin
maturin develop
```

To build distributable wheels for publishing:

```powershell
uv run maturin build --release
# packages will be placed in target/wheels
```


 logs rather than `key=value` suffixes.

Pick which to do next.

## Development (build from source)

If you plan to develop or build from source you will need the Rust toolchain and `maturin`.

From this repo (recommended, uses `uv` helper if present):

```powershell
# sync virtualenv and build in editable mode
uv sync
uv run maturin develop
```

Alternatively, run directly with:

```powershell
python -m pip install --upgrade maturin
maturin develop
```

To build distributable wheels for publishing:

```powershell
uv run maturin build --release
# packages will be placed in target/wheels
```
