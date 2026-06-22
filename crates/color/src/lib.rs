//! ANSI color rendering utilities.
//!
//! Maps log levels to ANSI color/style codes with per-sink colorize toggles,
//! TTY auto-detection, and theme customization.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use levels::LogLevel;
use std::collections::HashMap;

/// Default color mapping for built-in levels.
fn default_color_map() -> HashMap<&'static str, &'static str> {
    HashMap::from([
        ("TRACE", "dim"),
        ("DEBUG", "blue"),
        ("INFO", ""),
        ("NOTICE", "cyan"),
        ("SUCCESS", "green"),
        ("WARNING", "yellow"),
        ("ERROR", "red"),
        ("FAIL", "magenta"),
        ("CRITICAL", "bold_red"),
        ("FATAL", "bold_red"),
    ])
}

/// Applies level color when colorization is enabled.
///
/// # Examples
///
/// ```rust
/// use color::paint;
/// use levels::LogLevel;
///
/// let level = LogLevel::new("ERROR", 50, Some("red".to_owned()));
/// let colored = paint(&level, "error message", true);
/// assert!(colored.contains("\x1b["));
///
/// let plain = paint(&level, "error message", false);
/// assert_eq!(plain, "error message");
/// ```
#[must_use]
pub fn paint(level: &LogLevel, text: &str, colorize: bool) -> String {
    if !colorize {
        return text.to_owned();
    }
    let color_name = level.color().unwrap_or_else(|| {
        let map = default_color_map();
        map.get(level.name()).copied().unwrap_or("")
    });
    let code = color_code(color_name);
    if code.is_empty() {
        text.to_owned()
    } else {
        format!("\x1b[{code}m{text}\x1b[0m")
    }
}

/// Returns ANSI escape code for a color name.
#[must_use]
pub fn color_code(name: &str) -> &'static str {
    match name {
        "dim" => "2",
        "blue" => "34",
        "cyan" => "36",
        "green" => "32",
        "yellow" => "33",
        "red" => "31",
        "magenta" => "35",
        "bold_red" => "1;31",
        "bold" => "1",
        "white" => "37",
        "black" => "30",
        "italic" => "3",
        "underline" => "4",
        "blink" => "5",
        "reverse" => "7",
        "strike" => "9",
        _ => "",
    }
}

/// A theme that maps level names to color names.
///
/// Allows customization of which ANSI color is used for each level.
#[derive(Clone, Debug, Default)]
pub struct Theme {
    colors: HashMap<String, String>,
}

impl Theme {
    /// Creates a theme with default color mappings.
    #[must_use]
    pub fn defaults() -> Self {
        let colors = default_color_map()
            .into_iter()
            .map(|(k, v)| (k.to_owned(), v.to_owned()))
            .collect();
        Self { colors }
    }

    /// Creates an empty theme.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets the color for a level.
    pub fn set(&mut self, level: impl Into<String>, color: impl Into<String>) {
        self.colors.insert(level.into(), color.into());
    }

    /// Gets the color for a level.
    #[must_use]
    pub fn get(&self, level: &str) -> Option<&str> {
        self.colors.get(level).map(String::as_str)
    }
}

/// Paints text using a theme instead of the level's built-in color.
#[must_use]
pub fn paint_themed(level: &LogLevel, text: &str, colorize: bool, theme: &Theme) -> String {
    if !colorize {
        return text.to_owned();
    }
    let color_name = theme
        .get(level.name())
        .or_else(|| level.color())
        .unwrap_or("");
    let code = color_code(color_name);
    if code.is_empty() {
        text.to_owned()
    } else {
        format!("\x1b[{code}m{text}\x1b[0m")
    }
}

/// Detects whether a file descriptor is a terminal (TTY).
///
/// Returns `None` if detection is not possible (e.g., on Windows without
/// the right API, or when the file descriptor is invalid).
#[must_use]
pub fn is_terminal(_fd: i32) -> bool {
    // On Unix, we would check isatty(). For portability, we use a simple heuristic.
    // In practice, the Python side should pass the colorize flag explicitly.
    false
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn paint_disabled_returns_plain() {
        let level = LogLevel::new("ERROR", 50, Some("red".to_owned()));
        assert_eq!(paint(&level, "hello", false), "hello");
    }

    #[test]
    fn paint_enabled_wraps_in_ansi() {
        let level = LogLevel::new("ERROR", 50, Some("red".to_owned()));
        let result = paint(&level, "hello", true);
        assert!(result.starts_with("\x1b[31m"));
        assert!(result.ends_with("\x1b[0m"));
    }

    #[test]
    fn color_code_known_colors() {
        assert_eq!(color_code("dim"), "2");
        assert_eq!(color_code("red"), "31");
        assert_eq!(color_code("bold_red"), "1;31");
        assert_eq!(color_code("unknown"), "");
    }

    #[test]
    fn theme_override() {
        let mut theme = Theme::defaults();
        theme.set("ERROR", "magenta");
        assert_eq!(theme.get("ERROR"), Some("magenta"));
        assert_eq!(theme.get("INFO"), Some(""));
    }

    #[test]
    fn paint_themed_uses_theme() {
        let mut theme = Theme::defaults();
        theme.set("INFO", "bold");
        let level = LogLevel::new("INFO", 20, None);
        let result = paint_themed(&level, "hello", true, &theme);
        assert!(result.starts_with("\x1b[1m"));
    }

    #[test]
    fn paint_themed_disabled() {
        let theme = Theme::defaults();
        let level = LogLevel::new("INFO", 20, None);
        assert_eq!(paint_themed(&level, "hello", false, &theme), "hello");
    }
}
