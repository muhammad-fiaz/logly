//! Pure Rust logger engine.
//!
//! The central dispatch engine that owns the sink registry, dispatches
//! `LogRecord` instances to every registered sink whose level/filter
//! accepts it, and manages enable/disable state per logger name.

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

/// Identifier returned when a sink is registered.
pub type SinkId = u64;

/// Dispatch engine that owns registered sinks.
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
    /// Creates an empty logger engine.
    #[must_use]
    pub fn new() -> Self {
        Self {
            sinks: HashMap::new(),
            next_sink_id: 1,
            disabled: BTreeSet::new(),
        }
    }

    /// Adds a sink and returns its identifier.
    pub fn add_sink(&mut self, sink: Arc<dyn Sink>) -> SinkId {
        let sink_id = self.next_sink_id;
        self.next_sink_id = self.next_sink_id.saturating_add(1);
        self.sinks.insert(sink_id, sink);
        sink_id
    }

    /// Removes one sink or all sinks when `sink_id` is `None`.
    ///
    /// # Errors
    ///
    /// Returns an error when a requested sink id does not exist.
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

    /// Enables emission for a logger name.
    pub fn enable(&mut self, name: &str) {
        self.disabled.remove(name);
    }

    /// Disables emission for a logger name.
    pub fn disable(&mut self, name: &str) {
        self.disabled.insert(name.to_owned());
    }

    /// Checks if a logger name is disabled.
    #[must_use]
    pub fn is_disabled(&self, name: &str) -> bool {
        self.disabled.contains(name)
    }

    /// Returns the number of registered sinks.
    #[must_use]
    pub fn sink_count(&self) -> usize {
        self.sinks.len()
    }

    /// Logs a message at a named level.
    ///
    /// # Errors
    ///
    /// Returns an error when the level is invalid or a sink fails.
    pub fn log(&self, name: &str, level_name: &str, message: &str) -> LoglyResult<()> {
        if self.disabled.contains(name) {
            return Ok(());
        }
        let record = LogRecord::builder(level(level_name)?, message)
            .name(name)
            .build();
        self.dispatch(&record)
    }

    /// Logs a pre-built record.
    ///
    /// # Errors
    ///
    /// Returns an error when a sink fails.
    pub fn dispatch(&self, record: &LogRecord) -> LoglyResult<()> {
        for sink in self.sinks.values() {
            sink.handle(record)?;
        }
        Ok(())
    }

    /// Flushes all sinks.
    ///
    /// # Errors
    ///
    /// Returns an error when a sink cannot flush.
    pub fn complete(&self) -> LoglyResult<()> {
        for sink in self.sinks.values() {
            sink.flush()?;
        }
        Ok(())
    }

    /// Returns the numeric threshold for a level.
    ///
    /// # Errors
    ///
    /// Returns an error when the level is unknown.
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
