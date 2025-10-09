use ahash::AHashMap;
use pyo3::prelude::*;

/// Converts a color name to its ANSI color code.
///
/// Supports both named colors and direct ANSI codes. Color names are
/// case-insensitive. If the input is already a numeric ANSI code or
/// an unknown color name, it is returned as-is.
///
/// # Supported Color Names
///
/// - Standard colors: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
/// - Bright colors: BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
/// - Aliases: GRAY (same as BRIGHT_BLACK)
///
/// # Arguments
///
/// * `color` - Color name or ANSI code
///
/// # Returns
///
/// ANSI color code as a string
///
/// # Examples
///
/// ```rust
/// use logly::backend::colorization::color_name_to_code;
///
/// assert_eq!(color_name_to_code("RED"), "31");
/// assert_eq!(color_name_to_code("red"), "31");  // case-insensitive
/// assert_eq!(color_name_to_code("BRIGHT_GREEN"), "92");
/// assert_eq!(color_name_to_code("31"), "31");  // numeric codes pass through
/// ```
#[allow(dead_code)]
pub fn color_name_to_code(color: &str) -> String {
    match color.to_uppercase().as_str() {
        "BLACK" => "30",
        "RED" => "31",
        "GREEN" => "32",
        "YELLOW" => "33",
        "BLUE" => "34",
        "MAGENTA" => "35",
        "CYAN" => "36",
        "WHITE" => "37",
        "BRIGHT_BLACK" | "GRAY" => "90",
        "BRIGHT_RED" => "91",
        "BRIGHT_GREEN" => "92",
        "BRIGHT_YELLOW" => "93",
        "BRIGHT_BLUE" => "94",
        "BRIGHT_MAGENTA" => "95",
        "BRIGHT_CYAN" => "96",
        "BRIGHT_WHITE" => "97",
        // If it's already a number (ANSI code), return as-is
        _ if color.chars().all(|c| c.is_ascii_digit()) => color,
        // Unknown color name, return as-is (might be a custom ANSI code)
        _ => color,
    }
    .to_string()
}

/// Applies color formatting to a log message.
///
/// Supports two colorization methods:
/// 1. **Built-in ANSI colors**: Uses predefined color mappings to apply ANSI escape codes
/// 2. **Custom callback**: Allows Python functions to provide custom colorization logic
///
/// When a color callback is provided, it takes precedence over the built-in coloring.
/// The callback receives the log level and message, and should return the colorized message.
///
/// # Arguments
///
/// * `message` - The log message to colorize
/// * `level_str` - The log level as a string (e.g., "INFO", "ERROR")
/// * `level_colors` - Map of level names to color names or ANSI codes
/// * `color_callback` - Optional Python callable for custom colorization
///
/// # Returns
///
/// * `Ok(String)` - The colorized message with ANSI codes or custom formatting
/// * `Err(PyErr)` - If the color callback raises a Python exception
///
/// # Examples
///
/// ```rust
/// use ahash::AHashMap;
/// use logly::backend::colorization::colorize_message;
///
/// let mut colors = AHashMap::new();
/// colors.insert("INFO".to_string(), "GREEN".to_string());
///
/// // Built-in coloring
/// let result = colorize_message("Hello", "INFO", &colors, None).unwrap();
/// assert!(result.contains("\x1b[32m"));  // ANSI green code
///
/// // With callback (requires Python runtime)
/// // let callback = ...; // Python callable
/// // let result = colorize_message("Hello", "INFO", &colors, Some(&callback));
/// ```
#[allow(dead_code)]
pub fn colorize_message(
    message: &str,
    level_str: &str,
    level_colors: &AHashMap<String, String>,
    color_callback: Option<&Py<PyAny>>,
) -> PyResult<String> {
    if let Some(callback) = color_callback {
        // Call the Python color callback
        Python::attach(|py| {
            let args = (level_str, message);
            let result = callback.call(py, args, None)?;
            result.extract::<String>(py)
        })
    } else {
        // Use built-in coloring
        if let Some(color_spec) = level_colors.get(level_str) {
            let color_code = color_name_to_code(color_spec);
            Ok(format!("\x1b[{}m{}\x1b[0m", color_code, message))
        } else {
            Ok(message.to_string())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_color_name_to_code() {
        assert_eq!(color_name_to_code("RED"), "31");
        assert_eq!(color_name_to_code("red"), "31"); // case insensitive
        assert_eq!(color_name_to_code("BLUE"), "34");
        assert_eq!(color_name_to_code("CYAN"), "36");
        assert_eq!(color_name_to_code("WHITE"), "37");
        assert_eq!(color_name_to_code("BRIGHT_RED"), "91");
        assert_eq!(color_name_to_code("GRAY"), "90");
        assert_eq!(color_name_to_code("42"), "42"); // numeric codes pass through
        assert_eq!(color_name_to_code("unknown"), "unknown"); // unknown names pass through
    }

    #[test]
    fn test_colorize_message_builtin() {
        let mut level_colors = AHashMap::new();
        level_colors.insert("INFO".to_string(), "RED".to_string());
        level_colors.insert("ERROR".to_string(), "31".to_string()); // direct ANSI code

        // Test with color mapping
        let result = colorize_message("test message", "INFO", &level_colors, None).unwrap();
        assert_eq!(result, "\x1b[31mtest message\x1b[0m");

        // Test with direct ANSI code
        let result = colorize_message("error message", "ERROR", &level_colors, None).unwrap();
        assert_eq!(result, "\x1b[31merror message\x1b[0m");

        // Test without color mapping
        let result = colorize_message("debug message", "DEBUG", &level_colors, None).unwrap();
        assert_eq!(result, "debug message");
    }

    #[test]
    fn test_colorize_message_with_callback() {
        // Initialize Python for callback testing
        Python::initialize();

        Python::attach(|py| {
            // Create a mock callback that adds brackets around the message
            let code = c"lambda level, text: f'[{level}] {text}'";
            let callback = py.eval(code, None, None).unwrap();
            let callback_py: Py<PyAny> = callback.into();

            let level_colors = AHashMap::new(); // Empty colors when using callback

            // Test callback takes precedence over level colors
            let result =
                colorize_message("test message", "INFO", &level_colors, Some(&callback_py))
                    .unwrap();
            assert_eq!(result, "[INFO] test message");

            // Test callback with different level
            let result =
                colorize_message("error message", "ERROR", &level_colors, Some(&callback_py))
                    .unwrap();
            assert_eq!(result, "[ERROR] error message");
        });
    }

    #[test]
    fn test_colorize_message_callback_error_handling() {
        Python::initialize();

        Python::attach(|py| {
            // Create a callback that raises an exception
            let code = c"lambda level, text: (_ for _ in ()).throw(ValueError('test error'))";
            let callback = py.eval(code, None, None).unwrap();
            let callback_py: Py<PyAny> = callback.into();

            let level_colors = AHashMap::new();

            // Test that callback errors are propagated
            let result =
                colorize_message("test message", "INFO", &level_colors, Some(&callback_py));
            assert!(result.is_err());
        });
    }
}
