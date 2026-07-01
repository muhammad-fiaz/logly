//! Error types shared by all Logly crates.
//!
//! This crate defines the canonical error enum used across the entire Logly
//! workspace. Every crate returns [`LoglyResult<T>`] and the `PyO3` binding layer
//! maps each variant to the appropriate Python exception type.
//!
//! # Error Mapping
//!
//! | Rust Variant | Python Exception |
//! |---|---|
//! | `InvalidLevel` / `Config` | `ValueError` |
//! | `Sink` / `Formatter` / `Filter` / `Rotation` / `Compression` | `RuntimeError` |
//! | `Io` | `OSError` |

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use std::error::Error;
use std::fmt::{Display, Formatter};

/// Result alias used throughout the Rust workspace.
///
/// All public APIs in the Logly workspace return this type, ensuring consistent
/// error handling across crate boundaries.
pub type LoglyResult<T> = Result<T, LoglyError>;

/// Canonical error type for the Logly engine.
///
/// Each variant maps to a specific Python exception at the `PyO3` boundary:
/// - `InvalidLevel` / `Config` → `ValueError`
/// - `Sink` / `Formatter` / `Filter` / `Rotation` / `Compression` → `RuntimeError`
/// - `Io` → `OSError`
///
/// # Examples
///
/// ```rust
/// use error::LoglyError;
///
/// let err = LoglyError::Config("bad value".to_owned());
/// assert_eq!(err.to_string(), "bad value");
/// ```
#[derive(Debug)]
pub enum LoglyError {
    /// A level name or priority was invalid.
    ///
    /// Returned when a log level name is not registered or a numeric priority
    /// is out of range. Maps to `ValueError` at the Python boundary.
    InvalidLevel(String),
    /// A sink configuration or lifecycle operation failed.
    ///
    /// Covers sink initialization, file opening, and write failures.
    /// Maps to `RuntimeError` at the Python boundary.
    Sink(String),
    /// A formatter could not render a record.
    ///
    /// Returned when template parsing fails or the formatter encounters
    /// an unrecoverable rendering error. Maps to `RuntimeError`.
    Formatter(String),
    /// A filter failed during evaluation.
    ///
    /// Returned when a custom filter callback panics or returns an error.
    /// Maps to `RuntimeError`.
    Filter(String),
    /// A user configuration value was invalid.
    ///
    /// Returned for malformed size strings, unknown compression codecs,
    /// or invalid rotation/retention specifications. Maps to `ValueError`.
    Config(String),
    /// File rotation failed.
    ///
    /// Returned when the rotation scheduler cannot create or rename log files.
    /// Maps to `RuntimeError`.
    Rotation(String),
    /// Compression failed.
    ///
    /// Returned when the compression backend (gzip, zstd, etc.) encounters an
    /// I/O or encoding error. Maps to `RuntimeError`.
    Compression(String),
    /// A standard I/O operation failed.
    ///
    /// Wraps `std::io::Error` and maps to `OSError` at the Python boundary.
    Io(std::io::Error),
    /// A concurrency/queue operation failed.
    ///
    /// Returned when the background worker queue is full or the channel is closed.
    /// Maps to `RuntimeError`.
    Concurrency(String),
    /// A context operation failed.
    ///
    /// Returned when binding or extracting context values fails.
    /// Maps to `RuntimeError`.
    Context(String),
    /// A scheduling operation failed.
    ///
    /// Returned when the rotation or retention scheduler encounters an error.
    /// Maps to `RuntimeError`.
    Schedule(String),
}

/// Displays the human-readable error message.
///
/// For string-based variants, returns the inner message directly.
/// For `Io`, delegates to the underlying `std::io::Error` display.
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

/// Implements the standard `Error` trait.
///
/// Returns the underlying `std::io::Error` as the source for the `Io` variant;
/// all other variants have no chained source error.
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

/// Converts a `std::io::Error` into a `LoglyError::Io`.
///
/// This enables the `?` operator to propagate I/O errors directly into
/// `LoglyResult` return types.
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
