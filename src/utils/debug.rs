/// Internal debug logging utilities for logly troubleshooting.
///
/// This module provides functions to log internal operations, warnings,
/// and errors when debug mode is enabled. Debug logs are written to a
/// separate file to avoid interfering with user logs.
use crate::config::state::with_state;
use chrono::Local;
use parking_lot::Mutex;
use std::fs::OpenOptions;
use std::io::Write;
use std::sync::Arc;

/// Write a debug log message if internal debug mode is enabled.
///
/// # Arguments
/// * `level` - Debug level (DEBUG, INFO, WARN, ERROR)
/// * `operation` - The operation being performed
/// * `message` - The debug message
///
/// # Example
/// ```rust
/// debug_log("INFO", "configure", "Setting log level to INFO");
/// debug_log("WARN", "add_sink", "Sink already exists, skipping");
/// ```
pub fn debug_log(level: &str, operation: &str, message: &str) {
    with_state(|state| {
        if !state.internal_debug {
            return;
        }

        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f");
        let debug_msg = format!(
            "[{}] [LOGLY-{}] [{}] {}\n",
            timestamp, level, operation, message
        );

        // Initialize debug writer if not already done
        if state.debug_writer.is_none() {
            if let Some(path) = &state.debug_log_path {
                match OpenOptions::new().create(true).append(true).open(path) {
                    Ok(file) => {
                        state.debug_writer = Some(Arc::new(Mutex::new(Box::new(file))));
                        // Log initialization message
                        let init_msg = format!(
                            "[{}] [LOGLY-INFO] [debug_init] Internal debug logging started\n",
                            timestamp
                        );
                        if let Some(writer) = &state.debug_writer {
                            let _ = writer.lock().write_all(init_msg.as_bytes());
                            let _ = writer.lock().flush();
                        }
                    }
                    Err(e) => {
                        eprintln!("[LOGLY] Failed to create debug log file: {}", e);
                        return;
                    }
                }
            } else {
                // No debug path specified, write to stderr
                eprint!("{}", debug_msg);
                return;
            }
        }

        // Write to debug log file
        if let Some(writer) = &state.debug_writer {
            let _ = writer.lock().write_all(debug_msg.as_bytes());
            let _ = writer.lock().flush();
        }
    });
}

/// Log configuration changes
pub fn debug_config(key: &str, value: &str) {
    debug_log("CONFIG", "configure", &format!("{} = {}", key, value));
}

/// Log sink operations
pub fn debug_sink(action: &str, sink_id: Option<usize>, details: &str) {
    let sink_info = sink_id
        .map(|id| format!("sink_id={}", id))
        .unwrap_or_else(|| "console".to_string());
    debug_log("SINK", action, &format!("{}: {}", sink_info, details));
}

/// Log file operations
#[allow(dead_code)]
pub fn debug_file(action: &str, path: &str, details: &str) {
    debug_log("FILE", action, &format!("path={}: {}", path, details));
}

/// Log errors
#[allow(dead_code)]
pub fn debug_error(operation: &str, error: &str) {
    debug_log("ERROR", operation, error);
}

/// Log warnings
#[allow(dead_code)]
pub fn debug_warn(operation: &str, warning: &str) {
    debug_log("WARN", operation, warning);
}

/// Log general info
pub fn debug_info(operation: &str, info: &str) {
    debug_log("INFO", operation, info);
}
