<div align="center">
	<img src="assets/logly_logo.png" alt="logly" width="96" />

	<h1>logly</h1>

	<p><em>Rust-powered, Loguru-like logging for Python.</em></p>
</div>


Logly is a Rust-powered, Loguru-like logging library for Python that combines the familiarity of Python’s standard logging API with high-performance logging capabilities. It is designed for developers who need efficient, reliable logging in applications that generate large volumes of log messages.

Logly's core is implemented in Rust using tracing and exposed to Python via PyO3/Maturin for safety and performance.

This README documents how to build, use, and extend the current MVP and which features are planned.

<details>
<summary><strong>Table of contents</strong></summary>

- [Install (PyPI)](#install-pypi)
- [Nightly / install from GitHub](#nightly--install-from-github)
- [Quickstart](#quickstart)
- [Performance \& Benchmarks](#performance--benchmarks)
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

# Add sinks (console and file). For the current MVP: call file adds before configure().
logger.add("console")
logger.add("logs/app.log", rotation="daily")

# Configure console level and color, and optionally emit JSON instead of text
logger.configure(level="INFO", color=True, json=False)

logger.info("Hello from Rust")
logger.error("Something failed", user="fiaz")
logger.success("Deployed successfully 🚀")

# Generic level and flush
logger.log("debug", "Debugging details", step=3)
logger.complete()
```

## Performance & Benchmarks

Logly's core is implemented in Rust to reduce the per-message overhead of logging in high-volume Python applications. The numbers below are illustrative results from a local, synchronous console benchmark that emitted 100,000 messages.

Example result (100,000 messages, console):

- Python standard logging (mean): 10.8566 s
- Logly (mean): 8.9319 s

What this shows

- Throughput improvement: Logly completed the workload approximately 21% faster on average — it finished the test in about 79% of the time required by the standard library logger.
- Relative speedup: 10.8566 / 8.9319 ≈ 1.215 (≈1.22× faster).

Reproduce the benchmark locally (from the repository root):

Ensure you have an activated virtual environment (.venv) or equivalent active before running these commands.

```powershell
# build and install the editable extension (requires maturin + Rust toolchain)
maturin develop

# run the console benchmark: 100k messages, 3 repeats
python .\bench\benchmark_logging.py --mode console --count 100000 --repeat 3
```

Notes and caveats

- Results depend on OS, CPU, Python version, interpreter warm-up, and console buffering. Run the benchmark multiple times and on your target environment for reliable estimates.
- This example targets synchronous console output. File sinks, JSON serialization, buffering, or async sinks will have different performance characteristics.
- To compare file-based logging, use `--mode file` with the benchmark script.

If you want, I can add a small helper that aggregates multiple runs (mean/median/stddev) or create a lightweight CI benchmark job that runs on push.


## API reference (current features)

The Python `logger` is a small proxy around the Rust `PyLogger`. The proxy adds convenience features like `bind()` and `contextualize()` while forwarding core calls to the Rust backend.

Creation
- `logger` — global proxy instance exported from `logly`.

Configuration & sinks

- `logger.add(sink: str | None = None, *, rotation: str | None = None) -> int`
	- Add a sink. Use `"console"` for stdout/stderr or a file path to write logs to disk. Returns a handler id (int).
	- `rotation` accepts `"daily"`, `"hourly"`, `"minutely"`, or `"never"` (MVP: simple rotation via rolling appender).

	Example — add console and a rotating file sink:

	```python
	logger.add("console")
	logger.add("logs/app.log", rotation="daily")
	```

- `logger.configure(level: str = "INFO", color: bool = True, json: bool = False) -> None`
	- Set the base level for console output, enable/disable ANSI coloring on the console, and toggle structured JSON output.
	- When `json=True`, console and file sinks emit newline-delimited JSON records with fields: `timestamp`, `level`, `message`, and `fields` (merged kwargs and bound context).

	Example — set INFO, enable colors, keep text output:

	```python
	logger.configure(level="INFO", color=True, json=False)
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


