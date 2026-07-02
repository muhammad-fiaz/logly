//! Level definitions and the custom level registry.
//!
//! Provides the [`LogLevel`] type with built-in levels (TRACE through FATAL),
//! a thread-safe global registry, and functions for registering custom levels
//! and resolving levels from strings or numeric priorities.
//!
//! # Built-in Levels
//!
//! | Name | Priority | Default Color |
//! |---|---|---|
//! | `TRACE` | 5 | dim |
//! | `DEBUG` | 10 | blue |
//! | `INFO` | 20 | (none) |
//! | `NOTICE` | 25 | cyan |
//! | `SUCCESS` | 30 | green |
//! | `WARNING` | 40 | yellow |
//! | `ERROR` | 50 | red |
//! | `FAIL` | 55 | magenta |
//! | `CRITICAL` | 60 | bold_red |
//! | `FATAL` | 70 | bold_red |

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use error::{LoglyError, LoglyResult};
use std::collections::HashMap;
use std::fmt::{Display, Formatter};
use std::str::FromStr;
use std::sync::{OnceLock, RwLock};

/// A logging level with a stable name and numeric priority.
///
/// Levels are ordered by priority: lower values are less severe. The level
/// name is always stored in uppercase. Levels implement [`Ord`] by priority,
/// so `TRACE` (5) < `INFO` (20) < `ERROR` (50).
///
/// # Examples
///
/// ```rust
/// use levels::LogLevel;
///
/// let level = LogLevel::new("warning", 40, Some("yellow".to_owned()));
/// assert_eq!(level.name(), "WARNING");
/// assert_eq!(level.priority(), 40);
/// assert_eq!(level.color(), Some("yellow"));
/// ```
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LogLevel {
    name: String,
    priority: u16,
    color: Option<String>,
    icon: Option<String>,
}

impl LogLevel {
    /// Creates a level value.
    ///
    /// The name is normalized to uppercase. The `color` parameter specifies
    /// a default ANSI color name (e.g., `"red"`, `"bold_blue"`) or `None`
    /// for no default color.
    #[must_use]
    pub fn new(name: impl Into<String>, priority: u16, color: Option<String>) -> Self {
        Self {
            name: name.into().to_ascii_uppercase(),
            priority,
            color,
            icon: None,
        }
    }

    /// Creates a level value with an icon.
    ///
    /// The icon is an optional string (e.g., an emoji or glyph) that can be
    /// displayed alongside the level name in formatted output.
    #[must_use]
    pub fn with_icon(
        name: impl Into<String>,
        priority: u16,
        color: Option<String>,
        icon: Option<String>,
    ) -> Self {
        Self {
            name: name.into().to_ascii_uppercase(),
            priority,
            color,
            icon,
        }
    }

    /// Returns the level name.
    ///
    /// The name is always uppercase (e.g., `"INFO"`, `"ERROR"`).
    #[must_use]
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Returns the numeric severity priority.
    ///
    /// Lower values indicate less severe levels. Built-in levels range from
    /// 5 (TRACE) to 70 (FATAL).
    #[must_use]
    pub const fn priority(&self) -> u16 {
        self.priority
    }

    /// Returns the optional default ANSI color name.
    ///
    /// This is used by the color module to apply default coloring when no
    /// theme override is present.
    #[must_use]
    pub fn color(&self) -> Option<&str> {
        self.color.as_deref()
    }

    /// Returns the optional icon string.
    ///
    /// Icons are typically emoji or Unicode glyphs used for visual distinction
    /// in formatted output.
    #[must_use]
    pub fn icon(&self) -> Option<&str> {
        self.icon.as_deref()
    }
}

/// Displays the level name (e.g., `"INFO"`, `"ERROR"`).
impl Display for LogLevel {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        formatter.write_str(&self.name)
    }
}

/// Compares two levels by priority. Always returns `Some`.
impl PartialOrd for LogLevel {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

/// Orders two levels by priority (lower = less severe).
impl Ord for LogLevel {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.priority.cmp(&other.priority)
    }
}

/// Parses a level name or numeric priority string into a `LogLevel`.
///
/// Supports both named levels (e.g., `"INFO"`, `"error"`) and numeric
/// strings (e.g., `"20"`, `"50"`). Numeric strings that don't match an
/// existing level will register a new one.
impl FromStr for LogLevel {
    type Err = LoglyError;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        level(value)
    }
}

fn registry() -> &'static RwLock<HashMap<String, LogLevel>> {
    static REGISTRY: OnceLock<RwLock<HashMap<String, LogLevel>>> = OnceLock::new();
    REGISTRY.get_or_init(|| RwLock::new(default_levels()))
}

fn default_levels() -> HashMap<String, LogLevel> {
    [
        ("TRACE", 5, Some("dim")),
        ("DEBUG", 10, Some("blue")),
        ("INFO", 20, None),
        ("NOTICE", 25, Some("cyan")),
        ("SUCCESS", 30, Some("green")),
        ("WARNING", 40, Some("yellow")),
        ("ERROR", 50, Some("red")),
        ("FAIL", 55, Some("magenta")),
        ("CRITICAL", 60, Some("bold_red")),
        ("FATAL", 70, Some("bold_red")),
    ]
    .into_iter()
    .map(|(name, priority, color)| {
        let level = LogLevel::new(name, priority, color.map(str::to_owned));
        (level.name.clone(), level)
    })
    .collect()
}

/// Registers or replaces a custom level.
///
/// If a level with the same name already exists, it is replaced. The name
/// is normalized to uppercase.
///
/// # Errors
///
/// Returns [`LoglyError::InvalidLevel`] when the level name is empty
/// or the registry lock is poisoned.
///
/// # Examples
///
/// ```rust
/// use levels::register_level;
///
/// let level = register_level("AUDIT", 35, Some("cyan".to_owned())).unwrap();
/// assert_eq!(level.name(), "AUDIT");
/// assert_eq!(level.priority(), 35);
/// ```
pub fn register_level(name: &str, priority: u16, color: Option<String>) -> LoglyResult<LogLevel> {
    register_level_with_icon(name, priority, color, None)
}

/// Registers or replaces a custom level with an icon.
///
/// Like [`register_level`], but also sets an optional icon string for the level.
///
/// # Errors
///
/// Returns [`LoglyError::InvalidLevel`] when the level name is empty
/// or the registry lock is poisoned.
pub fn register_level_with_icon(
    name: &str,
    priority: u16,
    color: Option<String>,
    icon: Option<String>,
) -> LoglyResult<LogLevel> {
    if name.trim().is_empty() {
        return Err(LoglyError::InvalidLevel(
            "level name cannot be empty".to_owned(),
        ));
    }
    let upper = name.trim().to_ascii_uppercase();
    let builtins = [
        "TRACE", "DEBUG", "INFO", "NOTICE", "SUCCESS", "WARNING", "ERROR", "FAIL", "CRITICAL",
        "FATAL",
    ];
    if builtins.contains(&upper.as_str()) {
        // Allow updating properties of existing builtin levels (color, icon) but not the name
        let mut guard = registry()
            .write()
            .map_err(|_| LoglyError::InvalidLevel("level registry is unavailable".to_owned()))?;
        if let Some(existing) = guard.get(&upper) {
            let updated = LogLevel::with_icon(
                &existing.name,
                existing.priority,
                color.or(existing.color.clone()),
                icon.or(existing.icon.clone()),
            );
            guard.insert(upper, updated.clone());
            return Ok(updated);
        }
    }
    let level = LogLevel::with_icon(name.trim(), priority, color, icon);
    let mut guard = registry()
        .write()
        .map_err(|_| LoglyError::InvalidLevel("level registry is unavailable".to_owned()))?;
    guard.insert(level.name.clone(), level.clone());
    Ok(level)
}

/// Looks up a level by name.
///
/// The name lookup is case-insensitive. Returns the registered level or an error
/// if no level with that name exists.
///
/// # Errors
///
/// Returns [`LoglyError::InvalidLevel`] when the level is unknown.
///
/// # Examples
///
/// ```rust
/// use levels::level;
///
/// let info = level("INFO").unwrap();
/// assert_eq!(info.priority(), 20);
///
/// assert!(level("NONEXISTENT").is_err());
/// ```
pub fn level(name: &str) -> LoglyResult<LogLevel> {
    let guard = registry()
        .read()
        .map_err(|_| LoglyError::InvalidLevel("level registry is unavailable".to_owned()))?;
    guard
        .get(&name.to_ascii_uppercase())
        .cloned()
        .ok_or_else(|| LoglyError::InvalidLevel(format!("unknown level: {name}")))
}

/// Returns all currently registered levels sorted by priority.
///
/// Includes both built-in levels and any custom levels registered via
/// [`register_level`] or [`register_level_with_icon`].
///
/// # Errors
///
/// Returns [`LoglyError::InvalidLevel`] when the level registry lock is poisoned.
pub fn levels() -> LoglyResult<Vec<LogLevel>> {
    let mut values = registry()
        .read()
        .map_err(|_| LoglyError::InvalidLevel("level registry is unavailable".to_owned()))?
        .values()
        .cloned()
        .collect::<Vec<_>>();
    values.sort();
    Ok(values)
}

/// Resolves a level from a name string or numeric priority.
///
/// Resolution strategy:
/// 1. If `value` is a valid integer, look up the level with that priority.
/// 2. If no level matches that priority, register a new level named `LEVEL_{num}`.
/// 3. Otherwise, look up by name (case-insensitive).
///
/// # Errors
///
/// Returns [`LoglyError::InvalidLevel`] when the registry lock is poisoned
/// or the name is unknown.
///
/// # Examples
///
/// ```rust
/// use levels::resolve_level;
///
/// // Numeric priority matches existing level
/// let info = resolve_level("20").unwrap();
/// assert_eq!(info.name(), "INFO");
///
/// // Unknown numeric priority registers a new level
/// let custom = resolve_level("99").unwrap();
/// assert_eq!(custom.priority(), 99);
/// assert_eq!(custom.name(), "LEVEL_99");
/// ```
pub fn resolve_level(value: &str) -> LoglyResult<LogLevel> {
    if let Ok(num) = value.parse::<u16>() {
        let all = levels()?;
        if let Some(found) = all.into_iter().find(|l| l.priority() == num) {
            return Ok(found);
        }
        let name = format!("LEVEL_{num}");
        return register_level(&name, num, None);
    }
    level(value)
}

/// Formats exception text from an optional exception value.
///
/// Returns `None` if the exception is `None` or `false`.
/// Returns `"exception=True"` if the exception is `true`.
/// Otherwise returns `"TypeName: value"`.
///
/// # Examples
///
/// ```rust
/// use levels::format_exception_text;
///
/// assert_eq!(format_exception_text(None), None);
/// assert_eq!(format_exception_text(Some("ValueError: bad")), Some("ValueError: bad".to_owned()));
/// ```
#[must_use]
pub fn format_exception_text(exception: Option<&str>) -> Option<String> {
    exception.map(str::to_owned)
}

#[cfg(test)]
mod tests {
    use super::{LogLevel, level, levels, register_level, resolve_level};

    #[test]
    fn built_in_levels_are_ordered() {
        assert!(level("TRACE").unwrap() < level("INFO").unwrap());
        assert!(level("FATAL").unwrap() > level("ERROR").unwrap());
    }

    #[test]
    fn custom_level_can_be_registered() {
        let audit = register_level("AUDIT", 35, Some("cyan".to_owned())).unwrap();
        assert_eq!(audit, level("audit").unwrap());
    }

    #[test]
    fn level_trace_priority() {
        assert_eq!(level("TRACE").unwrap().priority(), 5);
    }

    #[test]
    fn level_debug_priority() {
        assert_eq!(level("DEBUG").unwrap().priority(), 10);
    }

    #[test]
    fn level_info_priority() {
        assert_eq!(level("INFO").unwrap().priority(), 20);
    }

    #[test]
    fn level_notice_priority() {
        assert_eq!(level("NOTICE").unwrap().priority(), 25);
    }

    #[test]
    fn level_success_priority() {
        assert_eq!(level("SUCCESS").unwrap().priority(), 30);
    }

    #[test]
    fn level_warning_priority() {
        assert_eq!(level("WARNING").unwrap().priority(), 40);
    }

    #[test]
    fn level_error_priority() {
        assert_eq!(level("ERROR").unwrap().priority(), 50);
    }

    #[test]
    fn level_fail_priority() {
        assert_eq!(level("FAIL").unwrap().priority(), 55);
    }

    #[test]
    fn level_critical_priority() {
        assert_eq!(level("CRITICAL").unwrap().priority(), 60);
    }

    #[test]
    fn level_fatal_priority() {
        assert_eq!(level("FATAL").unwrap().priority(), 70);
    }

    #[test]
    fn level_unknown_name_errors() {
        assert!(level("NONEXISTENT").is_err());
    }

    #[test]
    fn resolve_level_numeric_string() {
        let info = resolve_level("20").unwrap();
        assert_eq!(info, level("INFO").unwrap());
    }

    #[test]
    fn resolve_level_unknown_numeric_registers_new() {
        let l = resolve_level("99").unwrap();
        assert_eq!(l.priority(), 99);
        assert_eq!(l.name(), "LEVEL_99");
    }

    #[test]
    fn levels_returns_all_sorted() {
        let all = levels().unwrap();
        assert!(all.len() >= 10);
        for window in all.windows(2) {
            assert!(window[0].priority() <= window[1].priority());
        }
    }

    #[test]
    fn log_level_new_normalizes_to_uppercase() {
        let l = LogLevel::new("info", 20, None);
        assert_eq!(l.name(), "INFO");
    }

    #[test]
    fn log_level_display() {
        let l = LogLevel::new("WARNING", 40, None);
        assert_eq!(l.to_string(), "WARNING");
    }
}
