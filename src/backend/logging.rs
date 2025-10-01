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

use crate::config::state;
use crate::format::dict_to_pairs;
use crate::utils::levels::{level_to_str, to_filter, to_level};

/// Logs a message with the specified level and optional extra fields.
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
            if s.console_enabled {
                // print JSON to stderr for console layer compatibility
                if s.pretty_json {
                    eprintln!("{}", serde_json::to_string_pretty(&rec).unwrap_or_default());
                } else {
                    eprintln!("{}", serde_json::to_string(&rec).unwrap_or_default());
                }
            }
            if allow_file {
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
            let suffix = if pairs.is_empty() {
                String::new()
            } else {
                fast_format_suffix(&pairs)
            };
            match level {
                Level::TRACE => trace!(target: "logly", "{}{}", msg, suffix),
                Level::DEBUG => debug!(target: "logly", "{}{}", msg, suffix),
                Level::INFO => info!(target: "logly", "{}{}", msg, suffix),
                Level::WARN => warn!(target: "logly", "{}{}", msg, suffix),
                Level::ERROR => error!(target: "logly", "{}{}", msg, suffix),
            }
            if allow_file {
                if s.async_write {
                    if let Some(tx) = s.async_sender.as_ref() {
                        let line = format!("[{}] {}{}", level_to_str(level), msg, suffix);
                        let _ = tx.send(line);
                    }
                } else if let Some(writer) = s.file_writer.as_ref() {
                    let mut w = writer.lock();
                    let _ = writeln!(&mut **w, "[{}] {}{}", level_to_str(level), msg, suffix);
                }
            }
        }
    });
}

pub fn configure(level: &str, color: bool, json: bool, pretty_json: bool) -> PyResult<()> {
    let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
    state::with_state(|s| {
        s.level_filter = to_filter(lvl);
        s.color = color;
        s.format_json = json;
        s.pretty_json = pretty_json;
        s.console_enabled = true;
    });
    Ok(())
}

fn fast_format_suffix(pairs: &[(String, String)]) -> String {
    let mut out = String::new();
    for (k, v) in pairs {
        out.push_str(&format!(" | {}={}", k, v));
    }
    out
}