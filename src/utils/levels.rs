//! # Logging Utilities Module
//!
//! This module provides utility functions and types for log level handling,
//! rotation policies, and level conversions.
//!
//! ## Features
//!
//! - Log level parsing and conversion
//! - Rotation policy definitions
//! - Level filtering utilities

use tracing::Level;
use tracing_subscriber::filter::LevelFilter;

/// Log file rotation policies.
///
/// Defines when log files should be rotated based on time intervals.
/// Used by the file backend for automatic log rotation.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
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
