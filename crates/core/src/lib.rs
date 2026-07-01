//! Pure Rust logger engine.
//!
//! The central dispatch engine that owns the sink registry, dispatches
//! [`LogRecord`] instances to every registered sink, and manages
//! enable/disable state per logger name.
//!
//! # Architecture
//!
//! ```text
//!  User code → log() → LoggerEngine → [Sink₁, Sink₂, …]
//! ```
//!
//! - **Sink registration**: Sinks are added via [`LoggerEngine::add_sink`]
//!   and returned a unique [`SinkId`] for later removal.
//! - **Dispatch**: Each record is sent to *every* registered sink. Sinks
//!   are responsible for their own level filtering.
//! - **Enable/disable**: Logger names can be disabled to suppress all
//!   output without removing sinks.
//!
//! # Examples
//!
//! ```rust,no_run
//! use core::LoggerEngine;
//!
//! let mut engine = LoggerEngine::new();
//! // engine.add_sink(sink);
//! engine.log("myapp", "INFO", "application started").unwrap();
//! ```

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use error::{LoglyError, LoglyResult};
use levels::{LogLevel, level};
use record::LogRecord;
use sink::Sink;
use std::collections::{BTreeSet, HashMap};
use std::sync::Arc;

/// Unique identifier for a registered sink.
///
/// Returned by [`LoggerEngine::add_sink`] and used to remove sinks via
/// [`LoggerEngine::remove_sink`].
pub type SinkId = u64;

/// The central dispatch engine for the logging system.
///
/// `LoggerEngine` owns a registry of sinks and dispatches every log record
/// to all of them. It also tracks which logger names are disabled, allowing
/// fine-grained control over output.
///
/// # Thread Safety
///
/// `LoggerEngine` is not `Sync` — it is designed to be used from a single
/// thread or wrapped in a `Mutex` for multi-threaded access.
pub struct LoggerEngine {
    sinks: HashMap<SinkId, Arc<dyn Sink>>,
    next_sink_id: SinkId,
    disabled: BTreeSet<String>,
}

impl Default for LoggerEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl LoggerEngine {
    /// Creates a new, empty logger engine with no registered sinks.
    #[must_use]
    pub fn new() -> Self {
        Self {
            sinks: HashMap::new(),
            next_sink_id: 1,
            disabled: BTreeSet::new(),
        }
    }

    /// Registers a sink and returns its unique identifier.
    ///
    /// The sink receives every log record dispatched through this engine.
    ///
    /// # Arguments
    ///
    /// * `sink` — The sink to register, wrapped in an `Arc`.
    ///
    /// # Returns
    ///
    /// A [`SinkId`] that can be used to remove the sink later.
    pub fn add_sink(&mut self, sink: Arc<dyn Sink>) -> SinkId {
        let sink_id = self.next_sink_id;
        self.next_sink_id = self.next_sink_id.saturating_add(1);
        self.sinks.insert(sink_id, sink);
        sink_id
    }

    /// Removes a specific sink or all sinks.
    ///
    /// # Arguments
    ///
    /// * `sink_id` — The sink to remove, or `None` to remove all sinks.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError::Sink`] if `sink_id` does not match any
    /// registered sink.
    pub fn remove_sink(&mut self, sink_id: Option<SinkId>) -> LoglyResult<()> {
        if let Some(sink_id) = sink_id {
            self.sinks
                .remove(&sink_id)
                .ok_or_else(|| LoglyError::Sink(format!("unknown sink id: {sink_id}")))?;
        } else {
            self.sinks.clear();
        }
        Ok(())
    }

    /// Enables log emission for the given logger name.
    ///
    /// If the name was previously disabled via [`disable`](Self::disable),
    /// it is re-enabled.
    ///
    /// # Arguments
    ///
    /// * `name` — The logger name to enable.
    pub fn enable(&mut self, name: &str) {
        self.disabled.remove(name);
    }

    /// Disables log emission for the given logger name.
    ///
    /// When disabled, [`log`](Self::log) calls for this name are silently
    /// ignored (no sinks are invoked).
    ///
    /// # Arguments
    ///
    /// * `name` — The logger name to disable.
    pub fn disable(&mut self, name: &str) {
        self.disabled.insert(name.to_owned());
    }

    /// Returns `true` if the given logger name is disabled.
    #[must_use]
    pub fn is_disabled(&self, name: &str) -> bool {
        self.disabled.contains(name)
    }

    /// Returns the number of currently registered sinks.
    #[must_use]
    pub fn sink_count(&self) -> usize {
        self.sinks.len()
    }

    /// Logs a message at the specified level for the given logger name.
    ///
    /// If the logger name is disabled, this is a no-op. Otherwise, a
    /// [`LogRecord`] is built and dispatched to all registered sinks.
    ///
    /// # Arguments
    ///
    /// * `name` — The logger name (e.g., `"myapp"`).
    /// * `level_name` — The level string (e.g., `"INFO"`, `"ERROR"`).
    /// * `message` — The log message.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError`] if the level name is unknown or a sink
    /// fails to handle the record.
    pub fn log(&self, name: &str, level_name: &str, message: &str) -> LoglyResult<()> {
        if self.disabled.contains(name) {
            return Ok(());
        }
        let record = LogRecord::builder(level(level_name)?, message)
            .name(name)
            .build();
        self.dispatch(&record)
    }

    /// Dispatches a pre-built [`LogRecord`] to all registered sinks.
    ///
    /// Each sink's [`Sink::handle`] method is called with the record.
    /// Sinks are responsible for their own level filtering.
    ///
    /// # Arguments
    ///
    /// * `record` — The log record to dispatch.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError`] if any sink fails to handle the record.
    pub fn dispatch(&self, record: &LogRecord) -> LoglyResult<()> {
        for sink in self.sinks.values() {
            sink.handle(record)?;
        }
        Ok(())
    }

    /// Flushes all registered sinks.
    ///
    /// Ensures any buffered data is written to the underlying destination.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError`] if any sink fails to flush.
    pub fn complete(&self) -> LoglyResult<()> {
        for sink in self.sinks.values() {
            sink.flush()?;
        }
        Ok(())
    }

    /// Resolves a level name to its numeric [`LogLevel`].
    ///
    /// # Arguments
    ///
    /// * `level_name` — The level string (e.g., `"INFO"`, `"DEBUG"`).
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError`] if the level name is not recognized.
    pub fn resolve_level(&self, level_name: &str) -> LoglyResult<LogLevel> {
        level(level_name)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use filter::LevelFilter;
    use format::TemplateFormatter;
    use sink::ConsoleSink;
    use sink::Stream;

    #[test]
    fn empty_logger_accepts_messages() {
        let logger = LoggerEngine::new();
        logger.log("tests", "INFO", "hello").unwrap();
    }

    #[test]
    fn add_and_remove_sink() {
        let mut logger = LoggerEngine::new();
        let sink = Arc::new(ConsoleSink::new(
            Stream::Stderr,
            Box::new(TemplateFormatter::default()),
            Box::new(LevelFilter::new(LogLevel::new("INFO", 20, None))),
            false,
        ));
        let id = logger.add_sink(sink);
        assert_eq!(logger.sink_count(), 1);
        logger.remove_sink(Some(id)).unwrap();
        assert_eq!(logger.sink_count(), 0);
    }

    #[test]
    fn remove_all_sinks() {
        let mut logger = LoggerEngine::new();
        let sink1 = Arc::new(ConsoleSink::new(
            Stream::Stderr,
            Box::new(TemplateFormatter::default()),
            Box::new(LevelFilter::new(LogLevel::new("INFO", 20, None))),
            false,
        ));
        let sink2 = Arc::new(ConsoleSink::new(
            Stream::Stdout,
            Box::new(TemplateFormatter::default()),
            Box::new(LevelFilter::new(LogLevel::new("INFO", 20, None))),
            false,
        ));
        logger.add_sink(sink1);
        logger.add_sink(sink2);
        assert_eq!(logger.sink_count(), 2);
        logger.remove_sink(None).unwrap();
        assert_eq!(logger.sink_count(), 0);
    }

    #[test]
    fn disable_and_enable() {
        let mut logger = LoggerEngine::new();
        logger.disable("myapp");
        assert!(logger.is_disabled("myapp"));
        logger.enable("myapp");
        assert!(!logger.is_disabled("myapp"));
    }

    #[test]
    fn disabled_logger_skips_dispatch() {
        let mut logger = LoggerEngine::new();
        logger.disable("myapp");
        // Should succeed without error, just skip
        logger.log("myapp", "INFO", "skipped").unwrap();
    }

    #[test]
    fn resolve_level_works() {
        let logger = LoggerEngine::new();
        let info = logger.resolve_level("INFO").unwrap();
        assert_eq!(info.priority(), 20);
    }

    #[test]
    fn remove_nonexistent_sink_errors() {
        let mut logger = LoggerEngine::new();
        assert!(logger.remove_sink(Some(999)).is_err());
    }

    #[test]
    fn complete_flushes_all() {
        let mut logger = LoggerEngine::new();
        let sink = Arc::new(ConsoleSink::new(
            Stream::Stderr,
            Box::new(TemplateFormatter::default()),
            Box::new(LevelFilter::new(LogLevel::new("INFO", 20, None))),
            false,
        ));
        logger.add_sink(sink);
        logger.complete().unwrap();
    }
}
