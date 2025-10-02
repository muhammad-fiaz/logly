use ahash::AHashMap;
use chrono::{Local, Utc};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::Bound;
use tracing::Level;

use crate::config::state;
use crate::format::dict_to_pairs;
use crate::format::template::format_with_template;
use crate::utils::levels::{level_to_str, to_filter, to_level};

/// Convert color name to ANSI color code.
///
/// Supports both color names (e.g., "RED", "CYAN") and direct ANSI codes (e.g., "31", "36").
/// Case-insensitive color names are supported.
///
/// # Arguments
/// * `color` - Color name or ANSI code
///
/// # Returns
/// ANSI color code as string, or the original string if it's already an ANSI code
fn color_name_to_code(color: &str) -> String {
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

/// Apply ANSI color codes to a log message based on the log level.
///
/// # Arguments
///
/// * `message` - The log message to colorize
/// * `level_str` - The log level as a string
/// * `level_colors` - Map of level names to color names or ANSI codes
///
/// # Returns
///
/// The colorized message with ANSI escape codes
fn colorize_message(
    message: &str,
    level_str: &str,
    level_colors: &AHashMap<String, String>,
) -> String {
    if let Some(color_spec) = level_colors.get(level_str) {
        let color_code = color_name_to_code(color_spec);
        format!("\x1b[{}m{}\x1b[0m", color_code, message)
    } else {
        message.to_string()
    }
}
/// Logs a message with the specified level and optional extra fields.
///
/// This is the main entry point for logging messages. It handles:
/// - Message formatting and field extraction
/// - Async callback execution
/// - Output dispatching to configured sinks with per-sink formatting
/// - JSON vs text output based on per-sink configuration
///
/// # Arguments
///
/// * `level` - The log level (TRACE, DEBUG, INFO, WARN, ERROR)
/// * `msg` - The log message string
/// * `extra` - Optional dictionary of extra fields to include
///
/// # Thread Safety
///
/// This function is thread-safe and can be called concurrently from multiple threads.
pub fn log_message(level: Level, msg: &str, extra: Option<&Bound<'_, PyDict>>) {
    let pairs = extra.map(|d| dict_to_pairs(d)).unwrap_or_default();

    // Create log record data for callbacks
    let timestamp_rfc3339 = Utc::now().to_rfc3339();
    let timestamp_local = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    let level_str = level_to_str(level).to_string();
    let message = msg.to_string();
    let extra_fields = pairs.clone();

    // Call callbacks asynchronously in background thread
    let has_callbacks = state::with_state(|s| !s.callbacks.is_empty());

    if has_callbacks {
        let timestamp_bg = timestamp_rfc3339.clone();
        let level_str_bg = level_str.clone();
        let message_bg = message.clone();
        let extra_fields_bg = extra_fields.clone();

        std::thread::spawn(move || {
            Python::attach(|py| {
                let callbacks = state::with_state(|s| s.callbacks.clone());
                for callback in callbacks {
                    // Create the record dict in the background thread
                    let dict = pyo3::types::PyDict::new(py);
                    let _ = dict.set_item("timestamp", &timestamp_bg);
                    let _ = dict.set_item("level", &level_str_bg);
                    let _ = dict.set_item("message", &message_bg);

                    // Add extra fields
                    for (k, v) in &extra_fields_bg {
                        let _ = dict.set_item(k, v);
                    }

                    // Call the callback with the record
                    let _ = callback.call1(py, (&dict,));
                }
            });
        });
    }

    // Process each sink individually with its own configuration
    state::with_state(|s| {
        for (sink_id, sink_config) in &s.sinks {
            // Apply per-sink filtering
            let mut allow_sink = true;

            // Level filtering
            if let Some(min_level) = sink_config.min_level {
                let current: tracing_subscriber::filter::LevelFilter = to_filter(level);
                if current != min_level {
                    allow_sink = false;
                }
            }

            // Module filtering
            if let Some(ref want_mod) = sink_config.module_filter {
                let mut found = false;
                for (k, v) in &pairs {
                    if k == "module" && v == want_mod {
                        found = true;
                        break;
                    }
                }
                if !found {
                    allow_sink = false;
                }
            }

            // Function filtering
            if let Some(ref want_fn) = sink_config.function_filter {
                let mut found = false;
                for (k, v) in &pairs {
                    if k == "function" && v == want_fn {
                        found = true;
                        break;
                    }
                }
                if !found {
                    allow_sink = false;
                }
            }

            // Per-level output controls
            let is_console = sink_config.path.is_none();
            if is_console {
                // Check per-level console output control
                if let Some(&enabled) = s.console_levels.get(&level_str) {
                    if !enabled {
                        allow_sink = false;
                    }
                } else if !s.console_enabled {
                    allow_sink = false;
                }
            } else {
                // Check per-level storage control for file sinks
                if let Some(&enabled) = s.storage_levels.get(&level_str) {
                    if !enabled {
                        allow_sink = false;
                    }
                }
            }

            if !allow_sink {
                continue;
            }

            // Determine formatting options based on per-level controls
            let show_time_for_level = if let Some(&show) = s.time_levels.get(&level_str) {
                show
            } else {
                s.show_time
            };

            let show_color_for_level = if is_console {
                if let Some(&show) = s.color_levels.get(&level_str) {
                    show
                } else {
                    s.color
                }
            } else {
                false // Never color file output
            };

            // Format the message according to sink configuration
            let formatted_msg = if sink_config.json {
                // JSON formatting for this sink
                let filtered_pairs = filter_caller_info(&pairs, s.show_module, s.show_function);
                let mut json_obj = serde_json::Map::new();

                json_obj.insert(
                    "timestamp".to_string(),
                    serde_json::Value::String(timestamp_rfc3339.clone()),
                );
                json_obj.insert(
                    "level".to_string(),
                    serde_json::Value::String(level_str.clone()),
                );
                json_obj.insert(
                    "message".to_string(),
                    serde_json::Value::String(msg.to_string()),
                );

                // Add extra fields
                for (k, v) in filtered_pairs {
                    json_obj.insert(k.clone(), serde_json::Value::String(v.clone()));
                }

                serde_json::to_string(&json_obj)
                    .unwrap_or_else(|_| format!("JSON serialization error for message: {}", msg))
            } else if let Some(ref format_str) = sink_config.format {
                // Use custom format string
                format_with_template(format_str, &timestamp_rfc3339, &level_str, msg, &pairs)
            } else if is_console && (s.format_json || s.pretty_json) {
                // JSON formatting for console output
                let filtered_pairs = filter_caller_info(&pairs, s.show_module, s.show_function);
                let mut json_obj = serde_json::Map::new();

                json_obj.insert(
                    "timestamp".to_string(),
                    serde_json::Value::String(timestamp_rfc3339.clone()),
                );
                json_obj.insert(
                    "level".to_string(),
                    serde_json::Value::String(level_str.clone()),
                );
                json_obj.insert(
                    "message".to_string(),
                    serde_json::Value::String(msg.to_string()),
                );

                // Add extra fields
                for (k, v) in filtered_pairs {
                    json_obj.insert(k.clone(), serde_json::Value::String(v.clone()));
                }

                if s.pretty_json {
                    serde_json::to_string_pretty(&json_obj).unwrap_or_else(|_| {
                        format!("JSON serialization error for message: {}", msg)
                    })
                } else {
                    serde_json::to_string(&json_obj).unwrap_or_else(|_| {
                        format!("JSON serialization error for message: {}", msg)
                    })
                }
            } else {
                // Use default format with extra fields (backward compatibility)
                let filtered_pairs = filter_caller_info(&pairs, s.show_module, s.show_function);

                if show_time_for_level && !is_console {
                    // For file output with timestamp: "timestamp [LEVEL] message | extra"
                    let mut result =
                        format!("{} [{}] {}", timestamp_local, level_str.to_uppercase(), msg);
                    if !filtered_pairs.is_empty() {
                        let extra_str = filtered_pairs
                            .iter()
                            .map(|(k, v)| format!("{}={}", k, v))
                            .collect::<Vec<_>>()
                            .join(" | ");
                        result.push_str(" | ");
                        result.push_str(&extra_str);
                    }
                    result
                } else {
                    // For output without timestamp: "[LEVEL] message | extra"
                    let mut result = format!("[{}] {}", level_str.to_uppercase(), msg);
                    if !filtered_pairs.is_empty() {
                        let extra_str = filtered_pairs
                            .iter()
                            .map(|(k, v)| format!("{}={}", k, v))
                            .collect::<Vec<_>>()
                            .join(" | ");
                        result.push_str(" | ");
                        result.push_str(&extra_str);
                    }
                    result
                }
            };

            // Apply colorization for console output if enabled for this level
            let final_msg = if show_color_for_level && is_console {
                colorize_message(&formatted_msg, &level_str, &s.level_colors)
            } else {
                formatted_msg
            };

            // Output to the appropriate destination
            if is_console {
                // Console output
                println!("{}", final_msg);
            } else {
                // File output - use async writing if available, otherwise synchronous
                if let Some(async_sender) = s.async_senders.get(&sink_id) {
                    // Async writing
                    let _ = async_sender.send(final_msg);
                } else if let Some(writer) = s.file_writers.get(&sink_id) {
                    // Synchronous fallback
                    let mut w = writer.lock();
                    let _ = writeln!(&mut **w, "{}", final_msg);
                }
            }
        }
    });
}

pub fn configure_with_colors(
    level: &str,
    color: bool,
    json: bool,
    pretty_json: bool,
    console: bool,
    show_time: bool,
    show_module: bool,
    show_function: bool,
    console_levels: Option<AHashMap<String, bool>>,
    time_levels: Option<AHashMap<String, bool>>,
    color_levels: Option<AHashMap<String, bool>>,
    storage_levels: Option<AHashMap<String, bool>>,
    level_colors: Option<AHashMap<String, String>>,
) -> PyResult<()> {
    let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
    state::with_state(|s| {
        s.level_filter = to_filter(lvl);
        s.color = color;
        s.format_json = json;
        s.pretty_json = pretty_json;
        s.console_enabled = console;
        s.show_time = show_time;
        s.show_module = show_module;
        s.show_function = show_function;
        s.console_levels = console_levels.unwrap_or_default();
        s.time_levels = time_levels.unwrap_or_default();
        s.color_levels = color_levels.unwrap_or_default();
        s.storage_levels = storage_levels.unwrap_or_default();
        if let Some(colors) = level_colors {
            s.level_colors = colors;
        }

        // Update fast path enabled flag based on current configuration
        let has_file_writer = s.file_writer.is_some();
        s.fast_path_enabled = !s.format_json
            && !s.color
            && !s.show_time
            && !s.show_module
            && !s.show_function
            && s.console_levels.is_empty()
            && s.time_levels.is_empty()
            && s.color_levels.is_empty()
            && s.storage_levels.is_empty()
            && s.callbacks.is_empty()
            && s.console_enabled
            && !has_file_writer;
    });
    Ok(())
}

fn filter_caller_info(
    pairs: &[(String, String)],
    show_module: bool,
    show_function: bool,
) -> Vec<(String, String)> {
    pairs
        .iter()
        .filter(|(key, _)| {
            match key.as_str() {
                "module" => show_module,
                "function" => show_function,
                _ => true, // Include all other fields
            }
        })
        .cloned()
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::state::{reset_state, with_state};
    use ahash::AHashMap;
    use pyo3::{prelude::*, types::PyDictMethods};
    use tracing::Level;

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
    fn test_colorize_message() {
        let mut level_colors = AHashMap::new();
        level_colors.insert("INFO".to_string(), "RED".to_string());
        level_colors.insert("ERROR".to_string(), "31".to_string()); // direct ANSI code

        // Test with color mapping
        let result = colorize_message("test message", "INFO", &level_colors);
        assert_eq!(result, "\x1b[31mtest message\x1b[0m");

        // Test with direct ANSI code
        let result = colorize_message("error message", "ERROR", &level_colors);
        assert_eq!(result, "\x1b[31merror message\x1b[0m");

        // Test without color mapping
        let result = colorize_message("debug message", "DEBUG", &level_colors);
        assert_eq!(result, "debug message");
    }

    #[test]
    fn test_filter_caller_info() {
        let pairs = vec![
            ("module".to_string(), "test_module".to_string()),
            ("function".to_string(), "test_func".to_string()),
            ("custom".to_string(), "value".to_string()),
        ];

        // Test with both module and function enabled
        let result = filter_caller_info(&pairs, true, true);
        assert_eq!(result.len(), 3);
        assert!(result.contains(&("module".to_string(), "test_module".to_string())));
        assert!(result.contains(&("function".to_string(), "test_func".to_string())));
        assert!(result.contains(&("custom".to_string(), "value".to_string())));

        // Test with module disabled
        let result = filter_caller_info(&pairs, false, true);
        assert_eq!(result.len(), 2);
        assert!(!result.iter().any(|(k, _)| k == "module"));
        assert!(result.contains(&("function".to_string(), "test_func".to_string())));
        assert!(result.contains(&("custom".to_string(), "value".to_string())));

        // Test with function disabled
        let result = filter_caller_info(&pairs, true, false);
        assert_eq!(result.len(), 2);
        assert!(result.contains(&("module".to_string(), "test_module".to_string())));
        assert!(!result.iter().any(|(k, _)| k == "function"));
        assert!(result.contains(&("custom".to_string(), "value".to_string())));

        // Test with both disabled
        let result = filter_caller_info(&pairs, false, false);
        assert_eq!(result.len(), 1);
        assert!(result.contains(&("custom".to_string(), "value".to_string())));
    }

    #[test]
    fn test_configure_with_colors() {
        reset_state();

        let console_levels = {
            let mut m = AHashMap::new();
            m.insert("DEBUG".to_string(), false);
            m.insert("INFO".to_string(), true);
            Some(m)
        };

        let level_colors = {
            let mut m = AHashMap::new();
            m.insert("ERROR".to_string(), "RED".to_string());
            Some(m)
        };

        // Configure logging
        let result = configure_with_colors(
            "INFO",
            true,
            false,
            false,
            true,
            true,
            true,
            true,
            console_levels,
            None,
            None,
            None,
            level_colors,
        );

        assert!(result.is_ok());

        // Verify configuration
        with_state(|s| {
            assert_eq!(s.level_filter, to_filter(Level::INFO));
            assert!(s.color);
            assert!(!s.format_json);
            assert!(!s.pretty_json);
            assert!(s.console_enabled);
            assert!(s.show_time);
            assert!(s.show_module);
            assert!(s.show_function);
            assert_eq!(s.console_levels.get("DEBUG"), Some(&false));
            assert_eq!(s.console_levels.get("INFO"), Some(&true));
            assert_eq!(s.level_colors.get("ERROR"), Some(&"RED".to_string()));
        });
    }

    #[test]
    fn test_configure_with_colors_invalid_level() {
        let result = configure_with_colors(
            "INVALID_LEVEL",
            false,
            false,
            false,
            true,
            false,
            false,
            false,
            None,
            None,
            None,
            None,
            None,
        );

        assert!(result.is_err());
    }

    #[test]
    fn test_log_message_console_output() {
        reset_state();

        // Set up console-only configuration
        with_state(|s| {
            s.console_enabled = true;
            s.show_time = false;
            s.show_module = false;
            s.show_function = false;
            s.color = false;
            s.console_levels.clear();
            s.time_levels.clear();
            s.color_levels.clear();
            s.storage_levels.clear();
            s.callbacks.clear();
            s.sinks.clear();
        });

        // Initialize Python for PyO3 operations
        pyo3::prepare_freethreaded_python();
        Python::initialize();

        // This test would require capturing stdout, which is complex in Rust
        // For now, we'll just ensure the function doesn't panic
        Python::attach(|_py| {
            let extra = None;
            log_message(Level::INFO, "test message", extra);
        });
    }

    #[test]
    fn test_log_message_with_extra_fields() {
        reset_state();

        // Set up console-only configuration
        with_state(|s| {
            s.console_enabled = true;
            s.show_time = false;
            s.show_module = true;
            s.show_function = true;
            s.color = false;
            s.console_levels.clear();
            s.time_levels.clear();
            s.color_levels.clear();
            s.storage_levels.clear();
            s.callbacks.clear();
            s.sinks.clear();
        });

        // Initialize Python for PyO3 operations
        pyo3::prepare_freethreaded_python();
        Python::initialize();

        // Test with extra fields
        Python::attach(|py| {
            let extra = pyo3::types::PyDict::new(py);
            let _ = extra.set_item("module", "test_module");
            let _ = extra.set_item("function", "test_func");
            let _ = extra.set_item("custom", "value");

            log_message(Level::INFO, "test message", Some(&extra));
        });
    }
}
