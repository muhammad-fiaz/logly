//! # Backend Logging Module
//!
//! This module contains the core logging functionality for Logly, handling message
//! formatting, output dispatching, and async processing.
//!
//! ## Features
//!
//! - Message formatting for both text and JSON output
//! - Async callback execution in background threads
//! - File and console output with filtering
//! - Thread-safe state management integration

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::Bound;
use pyo3::exceptions::PyValueError;
use serde_json::json;
use tracing::{debug, error, info, trace, warn, Level};
use ahash::AHashMap;

use crate::config::state;
use crate::format::dict_to_pairs;
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
    }.to_string()
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
fn colorize_message(message: &str, level_str: &str, level_colors: &AHashMap<String, String>) -> String {
    if let Some(color_spec) = level_colors.get(level_str) {
        let color_code = color_name_to_code(color_spec);
        format!("\x1b[{}m{}\x1b[0m", color_code, message)
    } else {
        message.to_string()
    }
}/// Logs a message with the specified level and optional extra fields.
///
/// This is the main entry point for logging messages. It handles:
/// - Message formatting and field extraction
/// - Async callback execution
/// - Output dispatching to configured sinks
/// - JSON vs text output based on configuration
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

    // FAST PATH: Check if we can use optimized simple logging
    // This bypasses expensive features like JSON, colors, per-level controls, callbacks, and async writing
    let should_use_fast_path = state::with_state_read(|s| {
        // Check if fast path can be used: simple console-only logging without complex features
        let has_file_writer = s.file_writer.is_some();
        
        s.fast_path_enabled &&
           !s.format_json &&
           !s.color &&
           !s.show_time &&
           !s.show_module &&
           !s.show_function &&
           s.console_levels.is_empty() &&
           s.time_levels.is_empty() &&
           s.color_levels.is_empty() &&
           s.storage_levels.is_empty() &&
           s.callbacks.is_empty() &&
           s.console_enabled &&
           !has_file_writer
    });
    
    if should_use_fast_path {
        // Fast path: simple level:message format like std logging
        let formatted_msg = format!("{}:{}", level_to_str(level).to_uppercase(), msg);
        println!("{}", formatted_msg);
        return;
    }

    // Create log record data for callbacks
    let timestamp = Utc::now().to_rfc3339();
    let level_str = level_to_str(level).to_string();
    let message = msg.to_string();
    let extra_fields = pairs.clone();

    // Call callbacks asynchronously in background thread
    let has_callbacks = state::with_state(|s| !s.callbacks.is_empty());

    if has_callbacks {
        let timestamp_bg = timestamp.clone();
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

    // Emit structured JSON when requested, otherwise keep legacy formatted suffix.
    state::with_state(|s| {
        // filter checks (file sink filters only apply to file writes; console honored by global level)
        let mut allow_file = true;
        if let Some(min) = s.filter_min_level {
            let current: tracing_subscriber::filter::LevelFilter = to_filter(level);
            if current < min {
                allow_file = false;
            }
        }
        if let Some(ref want_mod) = s.filter_module {
            let mut found = false;
            for (k, v) in &pairs {
                if k == "module" && v == want_mod {
                    found = true;
                    break;
                }
            }
            if !found {
                allow_file = false;
            }
        }
        if let Some(ref want_fn) = s.filter_function {
            let mut found = false;
            for (k, v) in &pairs {
                if k == "function" && v == want_fn {
                    found = true;
                    break;
                }
            }
            if !found {
                allow_file = false;
            }
        }
        let lvl_str = level_to_str(level);
        if s.format_json {
            // Build a JSON record
            let fields: serde_json::Value = if pairs.is_empty() {
                json!({})
            } else {
                let mut map = serde_json::Map::with_capacity(pairs.len());
                for (k, v) in &pairs {
                    map.insert(k.clone(), serde_json::Value::String(v.clone()));
                }
                serde_json::Value::Object(map)
            };
            let rec = crate::format::JsonRecord {
                timestamp: Utc::now(),
                level: lvl_str,
                message: msg,
                module: None,
                function: None,
                line: None,
                fields,
            };
            let level_key = lvl_str.to_string();
            let console_per_level = s.console_levels.get(&level_key).copied().unwrap_or(s.console_enabled);
            let storage_per_level = s.storage_levels.get(&level_key).copied().unwrap_or(true);
            
            if console_per_level {
                // print JSON to stderr for console layer compatibility
                if s.pretty_json {
                    eprintln!("{}", serde_json::to_string_pretty(&rec).unwrap_or_default());
                } else {
                    eprintln!("{}", serde_json::to_string(&rec).unwrap_or_default());
                }
            }
            if allow_file && storage_per_level {
                if s.async_write {
                    if let Some(tx) = s.async_sender.as_ref() {
                        let line = if s.pretty_json {
                            serde_json::to_string_pretty(&rec).unwrap_or_default()
                        } else {
                            serde_json::to_string(&rec).unwrap_or_default()
                        };
                        let _ = tx.send(line);
                    }
                } else if let Some(writer) = s.file_writer.as_ref() {
                    let mut w = writer.lock();
                    let _ = writeln!(
                        &mut **w,
                        "{}",
                        serde_json::to_string(&rec).unwrap_or_default()
                    );
                }
            }
        } else {
            let lvl_str = level_to_str(level);
            let level_key = lvl_str.to_string();
            
            // Check per-level settings, fallback to global
            let show_time_per_level = s.time_levels.get(&level_key).copied().unwrap_or(s.show_time);
            let show_module_per_level = s.show_module; // module/function are global for now
            let show_function_per_level = s.show_function;
            let color_per_level = s.color_levels.get(&level_key).copied().unwrap_or(s.color);
            let console_per_level = s.console_levels.get(&level_key).copied().unwrap_or(s.console_enabled);
            let storage_per_level = s.storage_levels.get(&level_key).copied().unwrap_or(true); // default to true for storage
            
            let filtered_pairs = filter_caller_info(&pairs, show_module_per_level, show_function_per_level);
            let suffix = if filtered_pairs.is_empty() {
                String::new()
            } else {
                fast_format_suffix(&filtered_pairs)
            };
            let timestamp_str = if show_time_per_level {
                format!("{} | ", Utc::now().format("%Y-%m-%d %H:%M:%S%.3f"))
            } else {
                String::new()
            };
            let formatted_msg = format!("{}{}[{}] {}{}", timestamp_str, if show_time_per_level { "" } else { "" }, level_to_str(level), msg, suffix);
            let console_msg = if color_per_level {
                colorize_message(&formatted_msg, level_to_str(level), &s.level_colors)
            } else {
                formatted_msg.clone()
            };
            match level {
                Level::TRACE => trace!(target: "logly", "{}", formatted_msg),
                Level::DEBUG => debug!(target: "logly", "{}", formatted_msg),
                Level::INFO => info!(target: "logly", "{}", formatted_msg),
                Level::WARN => warn!(target: "logly", "{}", formatted_msg),
                Level::ERROR => error!(target: "logly", "{}", formatted_msg),
            }
            if console_per_level {
                println!("{}", console_msg);
            }
            if allow_file && storage_per_level {
                if s.async_write {
                    if let Some(tx) = s.async_sender.as_ref() {
                        let _ = tx.send(formatted_msg);
                    }
                } else if let Some(writer) = s.file_writer.as_ref() {
                    let mut w = writer.lock();
                    let _ = writeln!(&mut **w, "{}", formatted_msg);
                }
            }
        }
    });
}

pub fn configure_with_colors(level: &str, color: bool, json: bool, pretty_json: bool, console: bool, show_time: bool, show_module: bool, show_function: bool, console_levels: Option<AHashMap<String, bool>>, time_levels: Option<AHashMap<String, bool>>, color_levels: Option<AHashMap<String, bool>>, storage_levels: Option<AHashMap<String, bool>>, level_colors: Option<AHashMap<String, String>>) -> PyResult<()> {
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
        s.fast_path_enabled = !s.format_json &&
                              !s.color &&
                              !s.show_time &&
                              !s.show_module &&
                              !s.show_function &&
                              s.console_levels.is_empty() &&
                              s.time_levels.is_empty() &&
                              s.color_levels.is_empty() &&
                              s.storage_levels.is_empty() &&
                              s.callbacks.is_empty() &&
                              s.console_enabled &&
                              !has_file_writer;
    });
    Ok(())
}

fn filter_caller_info(pairs: &[(String, String)], show_module: bool, show_function: bool) -> Vec<(String, String)> {
    pairs.iter().filter(|(key, _)| {
        match key.as_str() {
            "module" => show_module,
            "function" => show_function,
            _ => true, // Include all other fields
        }
    }).cloned().collect()
}

fn fast_format_suffix(pairs: &[(String, String)]) -> String {
    let mut out = String::new();
    for (k, v) in pairs {
        out.push_str(&format!(" | {}={}", k, v));
    }
    out
}