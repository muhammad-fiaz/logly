# Crates

Logly's core is split into focused Rust crates, each handling a single concern. They are composed into the `logly` Python extension via [PyO3](https://pyo3.rs).

## Architecture

```
logly (Python extension)
├── core          Central dispatch engine
├── levels        Level definitions & registry
├── record        Immutable log record carrier
├── filter        Record filtering & level gates
├── format        Template & JSON formatters
├── sink          Console, file, callback sinks
├── source        Source location & editor links
├── color         ANSI rendering & markup parsing
├── config        Configuration types & policies
├── compress      Gzip, Zip, Bz2, Xz, Zstd codecs
├── concurrency   Worker pool & backpressure
├── rotate        Size, time, clock, weekday rotation
├── network       HTTP, TCP, UDP, Syslog sinks
└── error         Unified error types
```

## Crates

| Crate | Description |
|-------|-------------|
| **[core](core/)** | Central logger engine — owns the sink registry, dispatches log records, manages enable/disable state. |
| **[levels](levels/)** | Built-in level definitions (TRACE through FATAL) with a thread-safe global registry for custom levels. |
| **[record](record/)** | Immutable `LogRecord` carrier passed from engine to sinks, with builder pattern and structured extra fields. |
| **[filter](filter/)** | `Filter` trait with built-in level, prefix, and extra filters. Composable AND/OR chains for complex filtering. |
| **[format](format/)** | Template-based formatter with `{token}` placeholders, structured JSON output, and custom closure-based formatting. |
| **[sink](sink/)** | Core `Sink` trait and built-in implementations — Console, File, Enqueue (async worker), and Callback sinks. |
| **[source](source/)** | Source location capture, clickable editor links (VS Code, JetBrains, Vim, Emacs, Sublime), and surrounding context reading. |
| **[color](color/)** | ANSI color rendering — maps levels to styles, parses angle-bracket and Rich-style markup, supports themes. |
| **[config](config/)** | Serialization-friendly configuration types for sinks, rotation, retention, compression, and enqueue modes. |
| **[compress](compress/)** | Compression codecs (Gzip, Zip, Bz2, Xz, Zstd) for rotated log files with retention-based cleanup. |
| **[concurrency](concurrency/)** | Background worker thread pool with channel-based dispatch and configurable backpressure. |
| **[rotate](rotate/)** | File rotation policies — size, interval, clock, and weekday triggers with non-destructive file renaming. |
| **[network](network/)** | Network sinks — HTTP/JSON (with batching), TCP, UDP, and Syslog transports for remote log forwarding. |
| **[error](error/)** | Canonical `LoglyError` enum and `LoglyResult<T>` type alias shared across all crates. |

## Dependency Graph

```text
error
levels ← record ← core ← sink ← format
                  ↑       ↑       ↑
                filter  source  color
                        ↑
                      config
                                ↑
```

## Development

Each crate can be tested independently:

```bash
cargo test -p color
cargo test -p format
cargo test --workspace   # all crates
```

Lint across all crates:

```bash
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
```
