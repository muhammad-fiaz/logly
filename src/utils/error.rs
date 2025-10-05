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
    /// Invalid size limit format (e.g., not matching '500B', '5KB', '10MB', '1GB' pattern).
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
                    "Invalid size limit: '{}'. Expected format: '500B', '5KB', '10MB', '1GB'",
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

/// Validates a log level string.
///
/// Checks if the provided level string matches one of the valid log levels.
/// The comparison is case-insensitive.
///
/// # Valid Levels
///
/// - TRACE
/// - DEBUG
/// - INFO
/// - SUCCESS
/// - WARNING (or WARN)
/// - ERROR
/// - CRITICAL
/// - FAIL
///
/// # Arguments
///
/// * `level` - The log level string to validate
///
/// # Returns
///
/// * `Ok(())` if the level is valid
/// * `Err(LoglyError::InvalidLevel)` if the level is invalid
///
/// # Examples
///
/// ```rust
/// use logly::utils::error::validate_level;
///
/// assert!(validate_level("INFO").is_ok());
/// assert!(validate_level("info").is_ok());  // case-insensitive
/// assert!(validate_level("FAIL").is_ok());  // NEW in v0.1.5
/// assert!(validate_level("INVALID").is_err());
/// ```
pub fn validate_level(level: &str) -> Result<()> {
    const VALID_LEVELS: &[&str] = &[
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "WARN", "ERROR", "CRITICAL", "FAIL",
    ];
    if VALID_LEVELS.contains(&level.to_uppercase().as_str()) {
        Ok(())
    } else {
        Err(LoglyError::InvalidLevel(level.to_string()))
    }
}

/// Validates a rotation policy string.
///
/// Checks if the provided rotation string is either a valid rotation policy name
/// or a valid size-based rotation string.
///
/// # Valid Rotation Policies
///
/// - `daily` - Rotate logs daily
/// - `hourly` - Rotate logs hourly  
/// - `minutely` - Rotate logs every minute
/// - Size-based - e.g., `"10MB"`, `"1GB"` (see `validate_size_limit`)
///
/// The comparison is case-insensitive.
///
/// # Arguments
///
/// * `rotation` - The rotation policy string to validate
///
/// # Returns
///
/// * `Ok(())` if the rotation policy is valid
/// * `Err(LoglyError::InvalidRotation)` if the rotation policy is invalid
///
/// # Examples
///
/// ```rust
/// use logly::utils::error::validate_rotation;
///
/// assert!(validate_rotation("daily").is_ok());
/// assert!(validate_rotation("HOURLY").is_ok());
/// assert!(validate_rotation("10MB").is_ok());
/// assert!(validate_rotation("invalid").is_err());
/// ```
pub fn validate_rotation(rotation: &str) -> Result<()> {
    match rotation.to_lowercase().as_str() {
        "daily" | "hourly" | "minutely" => Ok(()),
        _ => {
            if parse_size_str(rotation).is_some() {
                Ok(())
            } else {
                Err(LoglyError::InvalidRotation(rotation.to_string()))
            }
        }
    }
}

/// Parses a size string into bytes.
///
/// Converts human-readable size strings (e.g., "10MB", "1GB") into byte counts.
/// Supports B, KB, MB, and GB units.
///
/// # Arguments
///
/// * `s` - The size string to parse
///
/// # Returns
///
/// * `Some(u64)` - The size in bytes if parsing succeeds
/// * `None` - If the format is invalid or the number cannot be parsed
///
/// # Supported Units
///
/// - `B` - Bytes (1 byte)
/// - `KB` - Kilobytes (1024 bytes)
/// - `MB` - Megabytes (1024 * 1024 bytes)
/// - `GB` - Gigabytes (1024 * 1024 * 1024 bytes)
fn parse_size_str(s: &str) -> Option<u64> {
    let s = s.trim().to_uppercase();
    let (num_str, unit) = if s.ends_with("KB") {
        (s.trim_end_matches("KB").trim(), 1024u64)
    } else if s.ends_with("MB") {
        (s.trim_end_matches("MB").trim(), 1024u64 * 1024)
    } else if s.ends_with("GB") {
        (s.trim_end_matches("GB").trim(), 1024u64 * 1024 * 1024)
    } else if s.ends_with("B") {
        (s.trim_end_matches("B").trim(), 1u64)
    } else {
        return None;
    };

    num_str.parse::<u64>().ok().map(|n| n * unit)
}

/// Validates a size limit string and returns the size in bytes.
///
/// Parses and validates a size limit string, ensuring it follows the expected format.
/// The string should consist of a number followed by a unit (B, KB, MB, or GB).
///
/// # Arguments
///
/// * `size` - The size limit string to validate (e.g., "500B", "10MB")
///
/// # Returns
///
/// * `Ok(u64)` - The size in bytes if validation succeeds
/// * `Err(LoglyError::InvalidSizeLimit)` - If the format is invalid
///
/// # Examples
///
/// ```rust
/// use logly::utils::error::validate_size_limit;
///
/// assert_eq!(validate_size_limit("500B").unwrap(), 500);
/// assert_eq!(validate_size_limit("1KB").unwrap(), 1024);
/// assert_eq!(validate_size_limit("10MB").unwrap(), 10 * 1024 * 1024);
/// assert!(validate_size_limit("invalid").is_err());
/// ```
pub fn validate_size_limit(size: &str) -> Result<u64> {
    parse_size_str(size).ok_or_else(|| LoglyError::InvalidSizeLimit(size.to_string()))
}

/// Validates a color name or ANSI code.
///
/// Checks if the provided color string is a valid color name or ANSI code.
/// The comparison is case-insensitive for color names.
///
/// # Valid Color Names
///
/// - BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
/// - BRIGHT_BLACK (or GRAY), BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW
/// - BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
///
/// # Valid ANSI Codes
///
/// - 30-37 (standard colors)
/// - 90-97 (bright colors)
///
/// # Arguments
///
/// * `color` - The color name or ANSI code to validate
///
/// # Returns
///
/// * `Ok(())` if the color is valid
/// * `Err(LoglyError::Configuration)` if the color is invalid
///
/// # Examples
///
/// ```rust
/// use logly::utils::error::validate_color;
///
/// assert!(validate_color("RED").is_ok());
/// assert!(validate_color("BRIGHT_GREEN").is_ok());
/// assert!(validate_color("31").is_ok());  // Red ANSI code
/// assert!(validate_color("INVALID").is_err());
/// ```
pub fn validate_color(color: &str) -> Result<()> {
    const VALID_COLORS: &[&str] = &[
        "BLACK",
        "RED",
        "GREEN",
        "YELLOW",
        "BLUE",
        "MAGENTA",
        "CYAN",
        "WHITE",
        "BRIGHT_BLACK",
        "GRAY",
        "BRIGHT_RED",
        "BRIGHT_GREEN",
        "BRIGHT_YELLOW",
        "BRIGHT_BLUE",
        "BRIGHT_MAGENTA",
        "BRIGHT_CYAN",
        "BRIGHT_WHITE",
    ];

    let upper_color = color.to_uppercase();

    // Check if it's a valid color name
    if VALID_COLORS.contains(&upper_color.as_str()) {
        return Ok(());
    }

    // Check if it's a valid ANSI code (30-37 or 90-97)
    if let Ok(code) = color.parse::<u8>()
        && ((30..=37).contains(&code) || (90..=97).contains(&code))
    {
        return Ok(());
    }

    Err(LoglyError::Configuration(format!(
        "Invalid color: '{}'. Valid colors: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, \
        or their BRIGHT_ variants, or ANSI codes 30-37, 90-97",
        color
    )))
}

/// Validates an auto-sink level name
///
/// # Arguments
/// * `level` - The level name to validate (e.g., "DEBUG", "INFO", "ERROR")
///
/// # Returns
/// * `Ok(())` if the level is valid
/// * `Err(LoglyError)` if the level is invalid
#[allow(dead_code)]
pub fn validate_auto_sink_level(level: &str) -> std::result::Result<(), LoglyError> {
    validate_level(level)
}

/// Validates an auto-sink path configuration
///
/// # Arguments
/// * `path` - The file path to validate
///
/// # Returns
/// * `Ok(())` if the path is valid
/// * `Err(LoglyError)` if the path is empty or invalid
#[allow(dead_code)]
pub fn validate_auto_sink_path(path: &str) -> std::result::Result<(), LoglyError> {
    if path.trim().is_empty() {
        return Err(LoglyError::AutoSinkLevels(
            "Auto-sink path cannot be empty".to_string(),
        ));
    }

    // Check for invalid characters that might cause issues
    let invalid_chars = ['<', '>', '|', '\0'];
    if path.chars().any(|c| invalid_chars.contains(&c)) {
        return Err(LoglyError::AutoSinkLevels(format!(
            "Auto-sink path contains invalid characters: '{}'",
            path
        )));
    }

    Ok(())
}

/// Validates an auto-sink type (sink destination)
///
/// # Arguments
/// * `sink_type` - The sink type to validate (e.g., "console", "file")
///
/// # Returns
/// * `Ok(())` if the sink type is valid
/// * `Err(LoglyError)` if the sink type is unsupported
#[allow(dead_code)]
pub fn validate_auto_sink_type(sink_type: &str) -> std::result::Result<(), LoglyError> {
    let valid_types = ["console", "file", "stdout", "stderr"];
    let sink_lower = sink_type.to_lowercase();

    if valid_types.contains(&sink_lower.as_str()) {
        Ok(())
    } else {
        Err(LoglyError::AutoSinkLevels(format!(
            "Invalid auto-sink type: '{}'. Valid types: console, file, stdout, stderr",
            sink_type
        )))
    }
}

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
        assert_eq!(validate_size_limit("5KB").unwrap(), 5 * 1024);
        assert_eq!(validate_size_limit("10 MB").unwrap(), 10 * 1024 * 1024);
        assert_eq!(validate_size_limit("1GB").unwrap(), 1024 * 1024 * 1024);
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
        if let Err(LoglyError::AutoSinkLevels(msg)) = result {
            assert!(msg.contains("cannot be empty"));
        }

        // Invalid: whitespace only
        let result = validate_auto_sink_path("   ");
        assert!(result.is_err());

        // Invalid: contains invalid characters
        let result = validate_auto_sink_path("logs/<invalid>.log");
        assert!(result.is_err());
        if let Err(LoglyError::AutoSinkLevels(msg)) = result {
            assert!(msg.contains("invalid characters"));
        }
    }

    #[test]
    fn test_validate_auto_sink_type() {
        // Valid types
        assert!(validate_auto_sink_type("console").is_ok());
        assert!(validate_auto_sink_type("file").is_ok());
        assert!(validate_auto_sink_type("stdout").is_ok());
        assert!(validate_auto_sink_type("stderr").is_ok());
        assert!(validate_auto_sink_type("CONSOLE").is_ok()); // case-insensitive

        // Invalid type
        let result = validate_auto_sink_type("invalid");
        assert!(result.is_err());
        if let Err(LoglyError::AutoSinkLevels(msg)) = result {
            assert!(msg.contains("Invalid auto-sink type"));
            assert!(msg.contains("invalid"));
        }
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
