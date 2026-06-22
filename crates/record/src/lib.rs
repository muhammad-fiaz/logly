//! Immutable log record values.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use levels::LogLevel;
use std::collections::BTreeMap;
use std::time::SystemTime;

/// Immutable data passed from the engine to sinks.
#[derive(Clone, Debug)]
pub struct LogRecord {
    /// Record creation time.
    pub timestamp: SystemTime,
    /// Record severity level.
    pub level: LogLevel,
    /// Renderable message text.
    pub message: String,
    /// Module or logger name.
    pub name: String,
    /// Source file path, when known.
    pub file: Option<String>,
    /// Source line number, when known.
    pub line: Option<u32>,
    /// Function name, when known.
    pub function: Option<String>,
    /// Module name (filename without extension), when known.
    pub module: Option<String>,
    /// Current thread name.
    pub thread_name: Option<String>,
    /// Process identifier.
    pub process_id: u32,
    /// Bound structured fields.
    pub extra: BTreeMap<String, String>,
    /// Captured exception text, when attached.
    pub exception: Option<String>,
}

impl LogRecord {
    /// Starts building a log record.
    #[must_use]
    pub fn builder(level: LogLevel, message: impl Into<String>) -> LogRecordBuilder {
        LogRecordBuilder::new(level, message)
    }
}

/// Builder for [`LogRecord`].
#[derive(Debug)]
pub struct LogRecordBuilder {
    record: LogRecord,
}

impl LogRecordBuilder {
    /// Creates a builder with required values.
    #[must_use]
    pub fn new(level: LogLevel, message: impl Into<String>) -> Self {
        Self {
            record: LogRecord {
                timestamp: SystemTime::now(),
                level,
                message: message.into(),
                name: String::from("logly"),
                file: None,
                line: None,
                function: None,
                module: None,
                thread_name: std::thread::current().name().map(str::to_owned),
                process_id: std::process::id(),
                extra: BTreeMap::new(),
                exception: None,
            },
        }
    }

    /// Sets the logger name.
    #[must_use]
    pub fn name(mut self, name: impl Into<String>) -> Self {
        self.record.name = name.into();
        self
    }

    /// Sets the module name.
    #[must_use]
    pub fn module(mut self, module: impl Into<String>) -> Self {
        self.record.module = Some(module.into());
        self
    }

    /// Sets source file and line information.
    #[must_use]
    pub fn location(mut self, file: Option<String>, line: Option<u32>) -> Self {
        self.record.file = file;
        self.record.line = line;
        self
    }

    /// Adds one structured field.
    #[must_use]
    pub fn extra(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.record.extra.insert(key.into(), value.into());
        self
    }

    /// Finalizes the record.
    #[must_use]
    pub fn build(self) -> LogRecord {
        self.record
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use levels::level;

    #[test]
    fn builder_sets_timestamp() {
        let before = SystemTime::now();
        let record = LogRecord::builder(level("INFO").unwrap(), "hello").build();
        let after = SystemTime::now();
        assert!(record.timestamp >= before && record.timestamp <= after);
    }

    #[test]
    fn builder_default_name_is_logly() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m").build();
        assert_eq!(record.name, "logly");
    }

    #[test]
    fn builder_process_id_matches() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m").build();
        assert_eq!(record.process_id, std::process::id());
    }

    #[test]
    fn builder_thread_name_is_populated() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m").build();
        assert!(record.thread_name.is_some());
    }

    #[test]
    fn builder_name_override() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m")
            .name("mylogger")
            .build();
        assert_eq!(record.name, "mylogger");
    }

    #[test]
    fn builder_module_override() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m")
            .module("mymodule")
            .build();
        assert_eq!(record.module.as_deref(), Some("mymodule"));
    }

    #[test]
    fn builder_extra_insert() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m")
            .extra("key", "val")
            .build();
        assert_eq!(record.extra.get("key").unwrap(), "val");
    }

    #[test]
    fn builder_build_produces_correct_record() {
        let record = LogRecord::builder(level("ERROR").unwrap(), "oops")
            .name("test")
            .extra("k", "v")
            .build();
        assert_eq!(record.level, level("ERROR").unwrap());
        assert_eq!(record.message, "oops");
        assert_eq!(record.name, "test");
        assert_eq!(record.extra.get("k").unwrap(), "v");
    }

    #[test]
    fn clone_produces_independent_copy() {
        let original = LogRecord::builder(level("INFO").unwrap(), "msg")
            .name("orig")
            .extra("x", "1")
            .build();
        let mut cloned = original.clone();
        cloned.message = "changed".to_owned();
        cloned.extra.insert("y".to_owned(), "2".to_owned());
        assert_eq!(original.message, "msg");
        assert!(!original.extra.contains_key("y"));
    }

    #[test]
    fn empty_message_works() {
        let record = LogRecord::builder(level("INFO").unwrap(), "").build();
        assert_eq!(record.message, "");
    }

    #[test]
    fn builder_with_empty_name() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m")
            .name("")
            .build();
        assert_eq!(record.name, "");
    }

    #[test]
    fn default_optional_fields_are_none() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m").build();
        assert!(record.file.is_none());
        assert!(record.line.is_none());
        assert!(record.function.is_none());
        assert!(record.exception.is_none());
    }

    #[test]
    fn extra_accumulates() {
        let record = LogRecord::builder(level("INFO").unwrap(), "m")
            .extra("a", "1")
            .extra("b", "2")
            .extra("c", "3")
            .build();
        assert_eq!(record.extra.len(), 3);
        assert_eq!(record.extra.get("a").unwrap(), "1");
        assert_eq!(record.extra.get("b").unwrap(), "2");
        assert_eq!(record.extra.get("c").unwrap(), "3");
    }
}
