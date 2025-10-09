use crate::backend::rotation::parse_size_limit;
use crate::utils::error::{LoglyError, Result};
use pyo3::PyResult;
use pyo3::exceptions::PyValueError;

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
/// use logly::utils::validation::validate_level;
///
/// assert!(validate_level("INFO").is_ok());
/// assert!(validate_level("info").is_ok());  // case-insensitive
/// assert!(validate_level("FAIL").is_ok());  // NEW in v0.1.5
/// assert!(validate_level("INVALID").is_err());
/// ```
pub fn validate_level(level: &str) -> Result<()> {
    let valid_levels = [
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "WARN", "ERROR", "CRITICAL", "FAIL",
    ];
    if valid_levels.iter().any(|&l| l.eq_ignore_ascii_case(level)) {
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
/// use logly::utils::validation::validate_rotation;
///
/// assert!(validate_rotation("daily").is_ok());
/// assert!(validate_rotation("HOURLY").is_ok());
/// assert!(validate_rotation("10MB").is_ok());
/// assert!(validate_rotation("invalid").is_err());
/// ```
pub fn validate_rotation(rotation: &str) -> Result<()> {
    let valid_rotations = ["daily", "hourly", "minutely"];
    if valid_rotations
        .iter()
        .any(|&r| r.eq_ignore_ascii_case(rotation))
        || parse_size_limit(Some(rotation)).is_some()
    {
        Ok(())
    } else {
        Err(LoglyError::InvalidRotation(rotation.to_string()))
    }
}

/// Validates a size limit string.
///
/// Checks if the provided size limit string can be parsed into a valid byte count.
/// Supports units: B, KB, MB, GB, TB (case-insensitive).
///
/// # Arguments
///
/// * `size_limit` - The size limit string to validate (e.g., "10MB", "1GB")
///
/// # Returns
///
/// * `Ok(())` if the size limit is valid
/// * `Err(LoglyError::InvalidSizeLimit)` if the size limit is invalid
///
/// # Examples
///
/// ```rust
/// use logly::utils::validation::validate_size_limit;
///
/// assert!(validate_size_limit("10MB").is_ok());
/// assert!(validate_size_limit("1GB").is_ok());
/// assert!(validate_size_limit("invalid").is_err());
/// ```
pub fn validate_size_limit(size_limit: &str) -> Result<()> {
    if parse_size_limit(Some(size_limit)).is_some() {
        Ok(())
    } else {
        Err(LoglyError::InvalidSizeLimit(size_limit.to_string()))
    }
}

/// Validates a color specification.
///
/// Checks if the provided color is either a valid color name or ANSI color code.
///
/// # Valid Color Names
///
/// - Standard: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
/// - Bright: BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
/// - Aliases: GRAY (for BRIGHT_BLACK)
/// - ANSI codes: Any numeric string (e.g., "31", "91")
///
/// The comparison is case-insensitive.
///
/// # Arguments
///
/// * `color` - The color name or ANSI code to validate
///
/// # Returns
///
/// * `Ok(())` if the color is valid
/// * `Err(LoglyError::InvalidColor)` if the color is invalid
///
/// # Examples
///
/// ```rust
/// use logly::utils::validation::validate_color;
///
/// assert!(validate_color("RED").is_ok());
/// assert!(validate_color("31").is_ok());  // ANSI code
/// assert!(validate_color("BRIGHT_CYAN").is_ok());
/// ```
pub fn validate_color(color: &str) -> Result<()> {
    let valid_colors = [
        "BLACK",
        "RED",
        "GREEN",
        "YELLOW",
        "BLUE",
        "MAGENTA",
        "CYAN",
        "WHITE",
        "BRIGHT_BLACK",
        "BRIGHT_RED",
        "BRIGHT_GREEN",
        "BRIGHT_YELLOW",
        "BRIGHT_BLUE",
        "BRIGHT_MAGENTA",
        "BRIGHT_CYAN",
        "BRIGHT_WHITE",
        "GRAY",
    ];

    // Check if it's a valid color name
    if valid_colors.iter().any(|&c| c.eq_ignore_ascii_case(color)) {
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

/// Validates auto_sink level in configuration.
///
/// Ensures the level is a valid log level string.
///
/// # Arguments
///
/// * `level` - The level string to validate
///
/// # Returns
///
/// * `Ok(())` if valid
/// * `Err(PyValueError)` if invalid
#[allow(dead_code)]
pub fn validate_auto_sink_level(level: &str) -> PyResult<()> {
    validate_level(level)
        .map_err(|e| PyValueError::new_err(format!("Invalid level in auto_sink_levels: {}", e)))
}

/// Validates auto_sink path.
///
/// Ensures the path is not empty.
///
/// # Arguments
///
/// * `path` - The file path to validate
///
/// # Returns
///
/// * `Ok(())` if valid
/// * `Err(PyValueError)` if invalid
#[allow(dead_code)]
pub fn validate_auto_sink_path(path: &str) -> PyResult<()> {
    if path.is_empty() {
        Err(PyValueError::new_err(
            "Path in auto_sink_levels cannot be empty",
        ))
    } else {
        Ok(())
    }
}

/// Validates auto_sink type.
///
/// Ensures the value is either a string or a dict.
///
/// # Arguments
///
/// * `type_name` - Type description for error messages
///
/// # Returns
///
/// * `Ok(())` if valid
/// * `Err(PyValueError)` if invalid
#[allow(dead_code)]
pub fn validate_auto_sink_type(type_name: &str) -> PyResult<()> {
    if type_name != "str" && type_name != "dict" {
        Err(PyValueError::new_err(format!(
            "auto_sink_levels values must be either str (file path) or dict (sink config), got {}",
            type_name
        )))
    } else {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_level() {
        assert!(validate_level("TRACE").is_ok());
        assert!(validate_level("DEBUG").is_ok());
        assert!(validate_level("INFO").is_ok());
        assert!(validate_level("SUCCESS").is_ok());
        assert!(validate_level("WARNING").is_ok());
        assert!(validate_level("WARN").is_ok());
        assert!(validate_level("ERROR").is_ok());
        assert!(validate_level("CRITICAL").is_ok());
        assert!(validate_level("FAIL").is_ok());

        // Case insensitive
        assert!(validate_level("info").is_ok());
        assert!(validate_level("InFo").is_ok());

        // Invalid
        assert!(validate_level("INVALID").is_err());
        assert!(validate_level("").is_err());
    }

    #[test]
    fn test_validate_rotation() {
        assert!(validate_rotation("daily").is_ok());
        assert!(validate_rotation("DAILY").is_ok());
        assert!(validate_rotation("hourly").is_ok());
        assert!(validate_rotation("minutely").is_ok());
        assert!(validate_rotation("10MB").is_ok());
        assert!(validate_rotation("1GB").is_ok());

        assert!(validate_rotation("invalid").is_err());
    }

    #[test]
    fn test_validate_size_limit() {
        assert!(validate_size_limit("100").is_ok());
        assert!(validate_size_limit("10MB").is_ok());
        assert!(validate_size_limit("1GB").is_ok());

        assert!(validate_size_limit("invalid").is_err());
        assert!(validate_size_limit("").is_err());
    }

    #[test]
    fn test_validate_color() {
        assert!(validate_color("RED").is_ok());
        assert!(validate_color("red").is_ok());
        assert!(validate_color("BRIGHT_CYAN").is_ok());
        assert!(validate_color("31").is_ok());
        assert!(validate_color("91").is_ok());

        assert!(validate_color("INVALID_COLOR").is_err());
    }
}
