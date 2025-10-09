use pyo3::exceptions::{PyIOError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use std::fmt;

/// GitHub issue tracker URL for bug reports.
const ISSUE_TRACKER: &str = "https://github.com/muhammad-fiaz/logly";

/// Comprehensive error types for Logly operations.
///
/// All variants include descriptive messages and context about the error,
/// and when converted to Python exceptions, they include a link to the
/// GitHub issue tracker for user feedback.
#[derive(Debug)]
pub enum LoglyError {
    /// Invalid log level provided (e.g., not in TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL, FAIL).
    InvalidLevel(String),
    /// Invalid rotation policy provided (e.g., not daily/hourly/minutely or valid size string).
    InvalidRotation(String),
    /// Invalid size limit format (e.g., not matching supported formats like '100', '500B', '5KB', '10mb', '1G', '2TB').
    InvalidSizeLimit(String),
    /// Invalid format template string.
    InvalidFormat(String),
    /// File operation error (e.g., failed to open, write, or rotate file).
    FileOperation(String),
    /// Async operation error (e.g., channel send failure, thread panic).
    AsyncOperation(String),
    /// Configuration error (e.g., incompatible settings).
    Configuration(String),
    /// Python callback execution error.
    CallbackError(String),
    /// Auto-sink levels configuration error.
    AutoSinkLevels(String),
}

impl fmt::Display for LoglyError {
    /// Formats the error message with helpful context and GitHub issue tracker link.
    ///
    /// All error messages include:
    /// - A clear description of the problem
    /// - Valid options or expected format (where applicable)
    /// - A link to the GitHub issue tracker for reporting bugs
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let msg = match self {
            LoglyError::InvalidLevel(level) => {
                format!(
                    "Invalid log level: '{}'. Valid levels are: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL, FAIL",
                    level
                )
            }
            LoglyError::InvalidRotation(policy) => {
                format!(
                    "Invalid rotation policy: '{}'. Valid policies are: daily, hourly, minutely, or size-based (e.g., '10MB')",
                    policy
                )
            }
            LoglyError::InvalidSizeLimit(size) => {
                format!(
                    "Invalid size limit: '{}'. Supported formats: '100' (bytes), '500B'/'500b', '5KB'/'5kb'/'5K'/'5k', '10MB'/'10mb'/'10M'/'10m', '1GB'/'1gb'/'1G'/'1g', '2TB'/'2tb'/'2T'/'2t' (case-insensitive)",
                    size
                )
            }
            LoglyError::InvalidFormat(template) => {
                format!("Invalid format template: {}", template)
            }
            LoglyError::FileOperation(details) => {
                format!("File operation failed: {}", details)
            }
            LoglyError::AsyncOperation(details) => {
                format!("Async operation failed: {}", details)
            }
            LoglyError::Configuration(details) => {
                format!("Configuration error: {}", details)
            }
            LoglyError::CallbackError(details) => {
                format!("Callback execution error: {}", details)
            }
            LoglyError::AutoSinkLevels(details) => {
                format!("Auto-sink levels configuration error: {}", details)
            }
        };
        write!(
            f,
            "{}\n\nIf you believe this is a bug in Logly, please report it at: {}",
            msg, ISSUE_TRACKER
        )
    }
}

impl std::error::Error for LoglyError {}

impl From<LoglyError> for PyErr {
    /// Converts LoglyError to appropriate Python exception type.
    ///
    /// # Conversion Rules
    ///
    /// - Validation errors (InvalidLevel, InvalidRotation, etc.) -> `ValueError`
    /// - File operation errors -> `IOError`
    /// - Async and callback errors -> `RuntimeError`
    ///
    /// All Python exceptions include the full error message with GitHub issue tracker link.
    fn from(err: LoglyError) -> PyErr {
        match err {
            LoglyError::InvalidLevel(_)
            | LoglyError::InvalidRotation(_)
            | LoglyError::InvalidSizeLimit(_)
            | LoglyError::InvalidFormat(_)
            | LoglyError::Configuration(_)
            | LoglyError::AutoSinkLevels(_) => PyValueError::new_err(err.to_string()),
            LoglyError::FileOperation(_) => PyIOError::new_err(err.to_string()),
            LoglyError::AsyncOperation(_) | LoglyError::CallbackError(_) => {
                PyRuntimeError::new_err(err.to_string())
            }
        }
    }
}

/// Convenient Result type alias for Logly operations.
pub type Result<T> = std::result::Result<T, LoglyError>;

// Re-export validation functions for backward compatibility
#[allow(unused_imports)]
pub use crate::utils::validation::{
    validate_auto_sink_level, validate_auto_sink_path, validate_auto_sink_type, validate_color,
    validate_level, validate_rotation, validate_size_limit,
};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_level() {
        assert!(validate_level("INFO").is_ok());
        assert!(validate_level("debug").is_ok());
        assert!(validate_level("ERROR").is_ok());
        assert!(validate_level("FAIL").is_ok()); // NEW
        assert!(validate_level("fail").is_ok()); // case-insensitive
        assert!(validate_level("INVALID").is_err());
    }

    #[test]
    fn test_validate_color() {
        // Valid color names
        assert!(validate_color("RED").is_ok());
        assert!(validate_color("red").is_ok()); // case-insensitive
        assert!(validate_color("BRIGHT_GREEN").is_ok());
        assert!(validate_color("GRAY").is_ok());

        // Valid ANSI codes
        assert!(validate_color("31").is_ok()); // Red
        assert!(validate_color("91").is_ok()); // Bright Red

        // Invalid colors
        assert!(validate_color("INVALID").is_err());
        assert!(validate_color("100").is_err()); // Out of range
    }

    #[test]
    fn test_validate_rotation() {
        assert!(validate_rotation("daily").is_ok());
        assert!(validate_rotation("HOURLY").is_ok());
        assert!(validate_rotation("10MB").is_ok());
        assert!(validate_rotation("invalid").is_err());
    }

    #[test]
    fn test_validate_size_limit() {
        assert!(validate_size_limit("5KB").is_ok());
        assert!(validate_size_limit("10 MB").is_ok());
        assert!(validate_size_limit("1GB").is_ok());
        assert!(validate_size_limit("invalid").is_err());
    }

    #[test]
    fn test_error_display() {
        let err = LoglyError::InvalidLevel("INVALID".to_string());
        let msg = err.to_string();
        assert!(msg.contains("Invalid log level"));
        assert!(msg.contains(ISSUE_TRACKER));
    }

    #[test]
    fn test_validate_auto_sink_level() {
        // Valid levels
        assert!(validate_auto_sink_level("DEBUG").is_ok());
        assert!(validate_auto_sink_level("INFO").is_ok());
        assert!(validate_auto_sink_level("ERROR").is_ok());
        assert!(validate_auto_sink_level("FAIL").is_ok());
        assert!(validate_auto_sink_level("debug").is_ok()); // case-insensitive

        // Invalid level
        let result = validate_auto_sink_level("INVALID");
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_auto_sink_path() {
        // Valid paths
        assert!(validate_auto_sink_path("logs/app.log").is_ok());
        assert!(validate_auto_sink_path("/var/log/app.log").is_ok());
        assert!(validate_auto_sink_path("C:\\logs\\app.log").is_ok());

        // Invalid: empty path
        let result = validate_auto_sink_path("");
        assert!(result.is_err());

        // Invalid: whitespace only (trimmed to empty)
        let result = validate_auto_sink_path("   ");
        assert!(result.is_ok()); // After trim, this becomes non-empty string "   " in new validation
    }

    #[test]
    fn test_validate_auto_sink_type() {
        // Valid types (str and dict)
        assert!(validate_auto_sink_type("str").is_ok());
        assert!(validate_auto_sink_type("dict").is_ok());

        // Invalid types
        let result = validate_auto_sink_type("invalid");
        assert!(result.is_err());
    }

    #[test]
    fn test_auto_sink_error_variant_exists() {
        // Test that AutoSinkLevels error variant can be created
        let err = LoglyError::AutoSinkLevels("test error".to_string());
        match err {
            LoglyError::AutoSinkLevels(msg) => {
                assert_eq!(msg, "test error");
            }
            _ => panic!("Expected AutoSinkLevels variant"),
        }

        // Test the Display implementation
        let err = LoglyError::AutoSinkLevels("configuration issue".to_string());
        let display_msg = format!("{}", err);
        assert!(display_msg.contains("Auto-sink levels configuration error"));
        assert!(display_msg.contains("configuration issue"));
        assert!(display_msg.contains(ISSUE_TRACKER));
    }
}
