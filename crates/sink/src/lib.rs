//! Sink trait and built-in sink implementations.
//!
//! Provides the core [`Sink`] trait, console sinks (stdout/stderr), file sinks,
//! background-worker sinks, callback sinks, and custom writer sinks.
//!
//! # Sink Types
//!
//! - [`ConsoleSink`]: Writes to stdout or stderr
//! - [`FileSink`]: Appends to a file with rotation and retention support
//! - [`EnqueueSink`]: Wraps any sink with a background worker thread
//! - [`CallbackSink`]: Invokes a closure for each record
//! - [`CustomSink`]: Delegates to a [`CustomWriter`] trait object
//!
//! # Lifecycle
//!
//! 1. Records arrive via [`Sink::handle`]
//! 2. The sink applies its filter; rejected records are silently dropped
//! 3. The sink formats the record using its formatter
//! 4. The formatted line is written to the destination
//! 5. Buffers are flushed via [`Sink::flush`]
//! 6. Resources are released via [`Sink::close`]

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use error::{LoglyError, LoglyResult};
use filter::Filter;
use format::Formatter;
use record::LogRecord;
use std::fs::{File, OpenOptions};
use std::io::{Write, stderr, stdout};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

/// Lifecycle and record handling contract for all sinks.
///
/// Every sink must implement at least [`handle`](Sink::handle). The default
/// implementations of [`flush`](Sink::flush) and [`close`](Sink::close) are
/// no-ops; override them if the sink buffers data or holds resources.
///
/// # Implementors
///
/// - [`ConsoleSink`]
/// - [`FileSink`]
/// - [`EnqueueSink`]
/// - [`CallbackSink`]
/// - [`CustomSink`]
pub trait Sink: Send + Sync {
    /// Handles one accepted log record.
    ///
    /// The sink should apply its filter, format the record, and write the
    /// output to its destination.
    ///
    /// # Errors
    ///
    /// Returns an error when writing or formatting fails.
    fn handle(&self, record: &LogRecord) -> LoglyResult<()>;

    /// Flushes buffered data.
    ///
    /// Override this if the sink buffers writes (e.g., file or network sinks).
    ///
    /// # Errors
    ///
    /// Returns an error when flushing fails.
    fn flush(&self) -> LoglyResult<()> {
        Ok(())
    }

    /// Closes the sink and releases resources.
    ///
    /// The default implementation calls [`flush`](Sink::flush). Override
    /// this to perform additional cleanup (e.g., closing file handles).
    ///
    /// # Errors
    ///
    /// Returns an error when closing fails.
    fn close(&self) -> LoglyResult<()> {
        self.flush()
    }
}

/// Standard stream selection for console output.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Stream {
    /// Write records to standard output.
    Stdout,
    /// Write records to standard error.
    Stderr,
}

/// Console sink for standard output or error.
///
/// Renders records using the configured formatter and optionally applies
/// ANSI colorization via [`color::paint`].
///
/// # Examples
///
/// ```rust,no_run
/// use sink::{ConsoleSink, Stream};
/// use format::TemplateFormatter;
/// use filter::LevelFilter;
/// use levels::LogLevel;
///
/// let sink = ConsoleSink::new(
///     Stream::Stdout,
///     Box::new(TemplateFormatter::new("{level} | {message}")),
///     Box::new(LevelFilter::new(LogLevel::new("INFO", 20, None))),
///     true,
/// );
/// ```
pub struct ConsoleSink {
    stream: Stream,
    formatter: Box<dyn Formatter>,
    filter: Box<dyn Filter>,
    colorize: bool,
}

impl ConsoleSink {
    /// Creates a console sink.
    ///
    /// # Arguments
    ///
    /// * `stream` - Target stream (stdout or stderr)
    /// * `formatter` - Formatter for rendering records
    /// * `filter` - Filter for accepting/rejecting records
    /// * `colorize` - Whether to apply ANSI color codes
    #[must_use]
    pub fn new(
        stream: Stream,
        formatter: Box<dyn Formatter>,
        filter: Box<dyn Filter>,
        colorize: bool,
    ) -> Self {
        Self {
            stream,
            formatter,
            filter,
            colorize,
        }
    }
}

impl Sink for ConsoleSink {
    fn handle(&self, record: &LogRecord) -> LoglyResult<()> {
        if !self.filter.accept(record) {
            return Ok(());
        }
        let line = self.formatter.format(record)?;
        let line = color::paint(&record.level, &line, self.colorize);
        match self.stream {
            Stream::Stdout => writeln!(stdout(), "{line}")?,
            Stream::Stderr => writeln!(stderr(), "{line}")?,
        }
        Ok(())
    }
}

/// File sink that appends formatted records to a path.
///
/// Supports file rotation (by size, time, or schedule), retention policies,
/// compression of rotated files, and lazy file opening (delay mode).
///
/// # Rotation
///
/// When rotation triggers, the current file is renamed and a new file is
/// opened. The rotated file may be compressed based on the configured codec.
///
/// # Watch Mode
///
/// When `watch` is `true`, the sink detects if the log file has been deleted
/// (e.g., by an external log rotation tool) and re-opens it automatically.
pub struct FileSink {
    path: PathBuf,
    file: Mutex<Option<File>>,
    formatter: Box<dyn Formatter>,
    filter: Box<dyn Filter>,
    append: bool,
    rotation: rotate::RotationPolicy,
    retention: config::RetentionPolicy,
    compression: compress::CompressionCodec,
    #[expect(
        dead_code,
        reason = "delay is a user-facing config option stored for future use"
    )]
    delay: bool,
    watch: bool,
}

impl FileSink {
    /// Opens a file sink.
    ///
    /// Creates the parent directory if it doesn't exist. When `delay` is `true`,
    /// the file is not opened until the first record is written.
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the log file
    /// * `formatter` - Formatter for rendering records
    /// * `filter` - Filter for accepting/rejecting records
    /// * `append` - Whether to append to existing files
    /// * `rotation` - Rotation policy
    /// * `retention` - Retention policy for rotated files
    /// * `compression` - Compression codec for rotated files
    /// * `delay` - Defer file opening until first write
    /// * `watch` - Re-open file if deleted externally
    ///
    /// # Errors
    ///
    /// Returns an error when the file cannot be opened or the directory
    /// cannot be created.
    #[allow(clippy::too_many_arguments)]
    pub fn open(
        path: impl AsRef<Path>,
        formatter: Box<dyn Formatter>,
        filter: Box<dyn Filter>,
        append: bool,
        rotation: rotate::RotationPolicy,
        retention: config::RetentionPolicy,
        compression: compress::CompressionCodec,
        delay: bool,
        watch: bool,
    ) -> LoglyResult<Self> {
        let path = path.as_ref().to_path_buf();
        let file = if delay {
            None
        } else {
            if let Some(parent) = path.parent() {
                std::fs::create_dir_all(parent)?;
            }
            let f = OpenOptions::new()
                .create(true)
                .write(true)
                .append(append)
                .truncate(!append)
                .open(&path)?;
            Some(f)
        };
        Ok(Self {
            path,
            file: Mutex::new(file),
            formatter,
            filter,
            append,
            rotation,
            retention,
            compression,
            delay,
            watch,
        })
    }
}

impl Sink for FileSink {
    fn handle(&self, record: &LogRecord) -> LoglyResult<()> {
        if !self.filter.accept(record) {
            return Ok(());
        }
        let line = self.formatter.format(record)?;
        let line_bytes = line.len() + 1; // plus newline

        let mut guard = self
            .file
            .lock()
            .map_err(|_| LoglyError::Sink("file sink lock is unavailable".to_owned()))?;

        if self.watch
            && !self.path.exists()
            && let Some(f) = guard.take()
        {
            drop(f);
        }

        if guard.is_none() {
            if let Some(parent) = self.path.parent() {
                std::fs::create_dir_all(parent)?;
            }
            let f = OpenOptions::new()
                .create(true)
                .write(true)
                .append(self.append)
                .truncate(!self.append)
                .open(&self.path)?;
            *guard = Some(f);
        }

        // Check rotation
        let action = rotate::check_rotation(&self.path, &self.rotation, line_bytes)?;
        if let rotate::RotationAction::RotateTo(rotated_path) = action {
            if let Some(f) = guard.take() {
                drop(f);
            }
            rotate::perform_rotation(&self.path, rotate::OverwriteMode::Append)?;
            let f = OpenOptions::new()
                .create(true)
                .write(true)
                .append(self.append)
                .truncate(!self.append)
                .open(&self.path)?;
            *guard = Some(f);

            if self.compression != compress::CompressionCodec::None
                && let Ok(compressed) = compress::compress_file(&rotated_path, &self.compression)
                && compressed != rotated_path
            {
                let _ = std::fs::remove_file(&rotated_path);
            }

            let dir = self.path.parent().unwrap_or_else(|| Path::new("."));
            let base_name = self.path.file_name().and_then(|n| n.to_str()).unwrap_or("");
            let keep_count = self.retention.count;
            let max_age_secs = self.retention.seconds;
            if keep_count.is_some() || max_age_secs.is_some() {
                let _ = compress::cleanup_old_archives(dir, base_name, keep_count, max_age_secs);
            }
        }

        if let Some(ref mut f) = *guard {
            writeln!(f, "{line}")?;
        }
        Ok(())
    }

    fn flush(&self) -> LoglyResult<()> {
        let mut guard = self
            .file
            .lock()
            .map_err(|_| LoglyError::Sink("file sink lock is unavailable".to_owned()))?;
        if let Some(ref mut f) = *guard {
            f.flush()?;
        }
        Ok(())
    }
}

/// Sink wrapper that processes logs on a background worker thread.
///
/// Wraps any [`Sink`] and dispatches records via a bounded channel. The
/// worker thread processes records asynchronously, reducing latency for
/// the calling thread.
///
/// # Backpressure
///
/// Uses drop-newest backpressure: when the queue is full, new records
/// are dropped rather than blocking the caller.
pub struct EnqueueSink {
    inner: Arc<dyn Sink>,
    worker: concurrency::BackgroundWorker<LogRecord>,
}

impl EnqueueSink {
    /// Wraps a sink in an enqueue background worker.
    ///
    /// Creates a background thread with a queue capacity of 1000 records.
    /// Records that arrive when the queue is full are silently dropped.
    #[must_use]
    pub fn new(inner: Arc<dyn Sink>) -> Self {
        let inner_clone = Arc::clone(&inner);
        let worker = concurrency::BackgroundWorker::new(
            1000,
            concurrency::Backpressure::DropNewest,
            move |record: LogRecord| {
                let _ = inner_clone.handle(&record);
            },
        );
        Self { inner, worker }
    }
}

impl Sink for EnqueueSink {
    fn handle(&self, record: &LogRecord) -> LoglyResult<()> {
        self.worker.send(record.clone())
    }

    fn flush(&self) -> LoglyResult<()> {
        while self.worker.pending_count() > 0 {
            std::thread::yield_now();
        }
        self.inner.flush()
    }

    fn close(&self) -> LoglyResult<()> {
        self.flush()?;
        self.inner.close()
    }
}

/// A generic callback sink that invokes a function for each record.
///
/// The callback receives the formatted string (after filtering). This is
/// useful for integrating with external logging systems or custom output
/// destinations.
///
/// # Examples
///
/// ```rust
/// use sink::CallbackSink;
/// use format::TemplateFormatter;
/// use filter::LevelFilter;
/// use levels::LogLevel;
/// use std::sync::Arc;
/// use std::sync::atomic::{AtomicUsize, Ordering};
///
/// let counter = Arc::new(AtomicUsize::new(0));
/// let counter_clone = Arc::clone(&counter);
///
/// let sink = CallbackSink::new(
///     Box::new(move |_line: &str| {
///         counter_clone.fetch_add(1, Ordering::SeqCst);
///     }),
///     Box::new(TemplateFormatter::new("{level} | {message}")),
///     Box::new(LevelFilter::new(LogLevel::new("INFO", 20, None))),
/// );
/// ```
pub struct CallbackSink {
    callback: Box<dyn Fn(&str) + Send + Sync>,
    formatter: Box<dyn Formatter>,
    filter: Box<dyn Filter>,
}

impl CallbackSink {
    /// Creates a callback sink.
    ///
    /// # Arguments
    ///
    /// * `callback` - Function called with each formatted log line
    /// * `formatter` - Formatter for rendering records
    /// * `filter` - Filter for accepting/rejecting records
    #[must_use]
    pub fn new(
        callback: Box<dyn Fn(&str) + Send + Sync>,
        formatter: Box<dyn Formatter>,
        filter: Box<dyn Filter>,
    ) -> Self {
        Self {
            callback,
            formatter,
            filter,
        }
    }
}

impl Sink for CallbackSink {
    fn handle(&self, record: &LogRecord) -> LoglyResult<()> {
        if !self.filter.accept(record) {
            return Ok(());
        }
        let line = self.formatter.format(record)?;
        (self.callback)(&line);
        Ok(())
    }
}

/// A custom sink that wraps a Rust trait object implementing [`CustomWriter`].
///
/// Delegates formatting and filtering to the standard pipeline, then passes
/// the formatted line to the writer. This is the primary extension point
/// for adding new output destinations.
pub struct CustomSink {
    writer: Arc<dyn CustomWriter>,
    formatter: Box<dyn Formatter>,
    filter: Box<dyn Filter>,
}

/// Trait for custom sink writers.
///
/// Implement this trait to create a custom output destination. The
/// [`CustomSink`] handles filtering and formatting; the writer only
/// needs to handle the final output.
///
/// # Implementors
///
/// Any struct that implements `write_line` and optionally `flush`.
pub trait CustomWriter: Send + Sync {
    /// Writes a formatted log line.
    ///
    /// # Errors
    /// Returns an error if writing fails.
    fn write_line(&self, line: &str) -> LoglyResult<()>;

    /// Flushes the writer.
    ///
    /// # Errors
    /// Returns an error if flushing fails.
    fn flush(&self) -> LoglyResult<()> {
        Ok(())
    }
}

impl CustomSink {
    /// Creates a custom sink.
    ///
    /// # Arguments
    ///
    /// * `writer` - The custom writer implementation
    /// * `formatter` - Formatter for rendering records
    /// * `filter` - Filter for accepting/rejecting records
    #[must_use]
    pub fn new(
        writer: Arc<dyn CustomWriter>,
        formatter: Box<dyn Formatter>,
        filter: Box<dyn Filter>,
    ) -> Self {
        Self {
            writer,
            formatter,
            filter,
        }
    }
}

impl Sink for CustomSink {
    fn handle(&self, record: &LogRecord) -> LoglyResult<()> {
        if !self.filter.accept(record) {
            return Ok(());
        }
        let line = self.formatter.format(record)?;
        self.writer.write_line(&line)
    }

    fn flush(&self) -> LoglyResult<()> {
        self.writer.flush()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use format::TemplateFormatter;
    use levels::LogLevel;

    fn info_filter() -> Box<dyn Filter> {
        Box::new(filter::LevelFilter::new(LogLevel::new("INFO", 20, None)))
    }

    fn info_formatter() -> Box<dyn Formatter> {
        Box::new(TemplateFormatter::new("{level} | {message}"))
    }

    #[test]
    fn console_sink_writes_to_stderr() {
        let sink = ConsoleSink::new(Stream::Stderr, info_formatter(), info_filter(), false);
        let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "test msg").build();
        sink.handle(&record).unwrap();
    }

    #[test]
    fn console_sink_filters_below_level() {
        let sink = ConsoleSink::new(Stream::Stderr, info_formatter(), info_filter(), false);
        let record = LogRecord::builder(LogLevel::new("DEBUG", 10, None), "debug msg").build();
        // Should not error — just filtered out
        sink.handle(&record).unwrap();
    }

    #[test]
    fn callback_sink_invokes() {
        use std::sync::atomic::{AtomicUsize, Ordering};
        let counter = Arc::new(AtomicUsize::new(0));
        let counter_clone = Arc::clone(&counter);

        let sink = CallbackSink::new(
            Box::new(move |_line: &str| {
                counter_clone.fetch_add(1, Ordering::SeqCst);
            }),
            info_formatter(),
            info_filter(),
        );

        let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "test").build();
        sink.handle(&record).unwrap();
        assert_eq!(counter.load(Ordering::SeqCst), 1);
    }

    #[test]
    fn file_sink_writes() {
        let dir = std::env::temp_dir().join("logly_sink_test");
        let _ = std::fs::create_dir_all(&dir);
        let path = dir.join("test.log");

        let sink = FileSink::open(
            &path,
            info_formatter(),
            info_filter(),
            true,
            rotate::RotationPolicy::Never,
            config::RetentionPolicy::default(),
            compress::CompressionCodec::None,
            false,
            false,
        )
        .unwrap();
        let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "hello").build();
        sink.handle(&record).unwrap();
        sink.flush().unwrap();

        let content = std::fs::read_to_string(&path).unwrap();
        assert!(content.contains("hello"));

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn custom_writer_sink() {
        use std::sync::atomic::{AtomicUsize, Ordering};

        struct TestWriter(Arc<AtomicUsize>);
        impl CustomWriter for TestWriter {
            fn write_line(&self, _line: &str) -> LoglyResult<()> {
                self.0.fetch_add(1, Ordering::SeqCst);
                Ok(())
            }
        }

        let written = Arc::new(AtomicUsize::new(0));
        let written_clone = Arc::clone(&written);

        let sink = CustomSink::new(
            Arc::new(TestWriter(written_clone)),
            info_formatter(),
            info_filter(),
        );

        let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "test").build();
        sink.handle(&record).unwrap();
        assert_eq!(written.load(Ordering::SeqCst), 1);
    }
}
