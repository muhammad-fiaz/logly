use tracing::Level;
use tracing_subscriber::filter::LevelFilter;

/// Log file rotation policies.
///
/// Defines when log files should be rotated based on time intervals.
/// Used by the file backend for automatic log rotation.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[allow(clippy::upper_case_acronyms)]
pub enum Rotation {
    /// Rotate daily (at midnight)
    DAILY,
    /// Rotate hourly (at the top of each hour)
    HOURLY,
    /// Rotate minutely (at the top of each minute)
    MINUTELY,
    /// Never rotate (single file, may grow indefinitely)
    NEVER,
}

/// Convert a string log level name to a tracing Level.
///
/// Supports common log level names with aliases:
/// - "trace" → TRACE
/// - "debug" → DEBUG
/// - "info", "success" → INFO
/// - "warn", "warning" → WARN
/// - "error", "critical", "fatal" → ERROR
///
/// # Arguments
///
/// * `name` - The log level name as a string
///
/// # Returns
///
/// Some(Level) if the name is recognized, None otherwise
pub fn to_level(name: &str) -> Option<Level> {
    match name.to_ascii_lowercase().as_str() {
        "trace" => Some(Level::TRACE),
        "debug" => Some(Level::DEBUG),
        "info" | "success" => Some(Level::INFO),
        "warn" | "warning" => Some(Level::WARN),
        "error" | "critical" | "fatal" => Some(Level::ERROR),
        _ => None,
    }
}

/// Convert a tracing Level to a LevelFilter for filtering.
///
/// # Arguments
///
/// * `level` - The tracing Level to convert
///
/// # Returns
///
/// The corresponding LevelFilter
pub fn to_filter(level: Level) -> LevelFilter {
    level.into()
}

/// Convert a tracing Level to its string representation.
///
/// # Arguments
///
/// * `level` - The tracing Level to convert
///
/// # Returns
///
/// The uppercase string representation of the level
pub fn level_to_str(level: Level) -> &'static str {
    match level {
        Level::TRACE => "TRACE",
        Level::DEBUG => "DEBUG",
        Level::INFO => "INFO",
        Level::WARN => "WARN",
        Level::ERROR => "ERROR",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tracing::Level;

    #[test]
    fn test_to_level_valid_names() {
        assert_eq!(to_level("trace"), Some(Level::TRACE));
        assert_eq!(to_level("TRACE"), Some(Level::TRACE));
        assert_eq!(to_level("debug"), Some(Level::DEBUG));
        assert_eq!(to_level("DEBUG"), Some(Level::DEBUG));
        assert_eq!(to_level("info"), Some(Level::INFO));
        assert_eq!(to_level("INFO"), Some(Level::INFO));
        assert_eq!(to_level("success"), Some(Level::INFO));
        assert_eq!(to_level("SUCCESS"), Some(Level::INFO));
        assert_eq!(to_level("warn"), Some(Level::WARN));
        assert_eq!(to_level("warning"), Some(Level::WARN));
        assert_eq!(to_level("WARN"), Some(Level::WARN));
        assert_eq!(to_level("WARNING"), Some(Level::WARN));
        assert_eq!(to_level("error"), Some(Level::ERROR));
        assert_eq!(to_level("critical"), Some(Level::ERROR));
        assert_eq!(to_level("fatal"), Some(Level::ERROR));
        assert_eq!(to_level("ERROR"), Some(Level::ERROR));
        assert_eq!(to_level("CRITICAL"), Some(Level::ERROR));
        assert_eq!(to_level("FATAL"), Some(Level::ERROR));
    }

    #[test]
    fn test_to_level_invalid_names() {
        assert_eq!(to_level(""), None);
        assert_eq!(to_level("invalid"), None);
        assert_eq!(to_level("log"), None);
        assert_eq!(to_level("verbose"), None);
    }

    #[test]
    fn test_to_filter() {
        assert_eq!(to_filter(Level::TRACE), LevelFilter::TRACE);
        assert_eq!(to_filter(Level::DEBUG), LevelFilter::DEBUG);
        assert_eq!(to_filter(Level::INFO), LevelFilter::INFO);
        assert_eq!(to_filter(Level::WARN), LevelFilter::WARN);
        assert_eq!(to_filter(Level::ERROR), LevelFilter::ERROR);
    }

    #[test]
    fn test_level_to_str() {
        assert_eq!(level_to_str(Level::TRACE), "TRACE");
        assert_eq!(level_to_str(Level::DEBUG), "DEBUG");
        assert_eq!(level_to_str(Level::INFO), "INFO");
        assert_eq!(level_to_str(Level::WARN), "WARN");
        assert_eq!(level_to_str(Level::ERROR), "ERROR");
    }
}
