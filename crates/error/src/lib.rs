//! Error types shared by all Logly crates.
//!
//! This crate defines the canonical error enum used across the entire Logly
//! workspace. Every crate returns `LoglyResult<T>` and the `PyO3` binding layer
//! maps each variant to the appropriate Python exception type.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use std::error::Error;
use std::fmt::{Display, Formatter};

/// Result alias used throughout the Rust workspace.
pub type LoglyResult<T> = Result<T, LoglyError>;

/// Canonical error type for the Logly engine.
///
/// Each variant maps to a specific Python exception at the `PyO3` boundary:
/// - `InvalidLevel` / `Config` → `ValueError`
/// - `Sink` / `Formatter` / `Filter` / `Rotation` / `Compression` → `RuntimeError`
/// - `Io` → `OSError`
#[derive(Debug)]
pub enum LoglyError {
    /// A level name or priority was invalid.
    InvalidLevel(String),
    /// A sink configuration or lifecycle operation failed.
    Sink(String),
    /// A formatter could not render a record.
    Formatter(String),
    /// A filter failed during evaluation.
    Filter(String),
    /// A user configuration value was invalid.
    Config(String),
    /// File rotation failed.
    Rotation(String),
    /// Compression failed.
    Compression(String),
    /// A standard I/O operation failed.
    Io(std::io::Error),
    /// A concurrency/queue operation failed.
    Concurrency(String),
    /// A context operation failed.
    Context(String),
    /// A scheduling operation failed.
    Schedule(String),
}

impl Display for LoglyError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidLevel(message)
            | Self::Sink(message)
            | Self::Formatter(message)
            | Self::Filter(message)
            | Self::Config(message)
            | Self::Rotation(message)
            | Self::Compression(message)
            | Self::Concurrency(message)
            | Self::Context(message)
            | Self::Schedule(message) => formatter.write_str(message),
            Self::Io(error) => Display::fmt(error, formatter),
        }
    }
}

impl Error for LoglyError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Io(error) => Some(error),
            Self::InvalidLevel(_)
            | Self::Sink(_)
            | Self::Formatter(_)
            | Self::Filter(_)
            | Self::Config(_)
            | Self::Rotation(_)
            | Self::Compression(_)
            | Self::Concurrency(_)
            | Self::Context(_)
            | Self::Schedule(_) => None,
        }
    }
}

impl From<std::io::Error> for LoglyError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn error_display_matches_message() {
        let err = LoglyError::InvalidLevel("bad level".to_owned());
        assert_eq!(err.to_string(), "bad level");
    }

    #[test]
    fn io_conversion_preserves_source() {
        let io_err = std::io::Error::new(std::io::ErrorKind::NotFound, "missing");
        let err: LoglyError = io_err.into();
        assert!(err.source().is_some());
    }

    #[test]
    fn all_variants_are_display() {
        let errors: Vec<LoglyError> = vec![
            LoglyError::InvalidLevel("x".into()),
            LoglyError::Sink("x".into()),
            LoglyError::Formatter("x".into()),
            LoglyError::Filter("x".into()),
            LoglyError::Config("x".into()),
            LoglyError::Rotation("x".into()),
            LoglyError::Compression("x".into()),
            LoglyError::Concurrency("x".into()),
            LoglyError::Context("x".into()),
            LoglyError::Schedule("x".into()),
        ];
        for e in &errors {
            let _ = e.to_string();
        }
    }
}
