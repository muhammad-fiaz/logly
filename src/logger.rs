use crate::backend;
use crate::config::state::with_state;
use crate::utils::levels::to_level;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use tracing::Level;

/// Python logger class (main entry point from Python).
///
/// This struct is exposed to Python as the core logger interface.
/// All public methods are available via PyO3 bindings.
#[pyclass]
#[derive(Default)]
pub struct PyLogger;

#[pymethods]
impl PyLogger {
    /// Create a new PyLogger instance.
    ///
    /// # Returns
    /// A new PyLogger with default settings
    #[new]
    pub fn new() -> Self {
        PyLogger
    }

    /// Initialize and configure the global logger.
    ///
    /// Sets up the console output with the specified level, color, and format options.
    ///
    /// # Arguments
    /// * `level` - Minimum log level ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL")
    /// * `color` - Enable colored console output
    /// * `level_colors` - Optional dictionary mapping level names to ANSI color codes
    /// * `json` - Format logs as JSON
    /// * `pretty_json` - Format logs as pretty-printed JSON
    /// * `console` - Enable console output
    /// * `show_time` - Show timestamps in console output
    /// * `show_module` - Show module information in console output
    /// * `show_function` - Show function information in console output
    /// * `console_levels` - Optional dictionary mapping level names to console output enable/disable
    /// * `time_levels` - Optional dictionary mapping level names to time display enable/disable
    /// * `color_levels` - Optional dictionary mapping level names to color enable/disable
    /// * `storage_levels` - Optional dictionary mapping level names to file storage enable/disable
    /// * `color_callback` - Optional Python callable for custom color formatting with signature (level, text) -> colored_text
    ///
    /// # Returns
    /// PyResult indicating success or error
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (level="INFO", color=true, level_colors=None, json=false, pretty_json=false, console=true, show_time=true, show_module=true, show_function=true, show_filename=false, show_lineno=false, console_levels=None, time_levels=None, color_levels=None, storage_levels=None, color_callback=None))]
    pub fn configure(
        &self,
        level: &str,
        color: bool,
        level_colors: Option<HashMap<String, String>>,
        json: bool,
        pretty_json: bool,
        console: bool,
        show_time: bool,
        show_module: bool,
        show_function: bool,
        show_filename: bool,
        show_lineno: bool,
        console_levels: Option<HashMap<String, bool>>,
        time_levels: Option<HashMap<String, bool>>,
        color_levels: Option<HashMap<String, bool>>,
        storage_levels: Option<HashMap<String, bool>>,
        color_callback: Option<Py<PyAny>>,
    ) -> PyResult<()> {
        let colors = level_colors.map(|hm| hm.into_iter().collect());
        let console_lvls = console_levels.map(|hm| hm.into_iter().collect());
        let time_lvls = time_levels.map(|hm| hm.into_iter().collect());
        let color_lvls = color_levels.map(|hm| hm.into_iter().collect());
        let storage_lvls = storage_levels.map(|hm| hm.into_iter().collect());
        backend::configure_with_colors(
            level,
            color,
            json,
            pretty_json,
            console,
            show_time,
            show_module,
            show_function,
            show_filename,
            show_lineno,
            console_lvls,
            time_lvls,
            color_lvls,
            storage_lvls,
            colors,
            color_callback,
        )
    }

    /// Reset logger configuration to defaults.
    ///
    /// Resets all logger settings to their default values, clearing any per-level
    /// controls and custom configurations.
    ///
    /// # Returns
    /// PyResult indicating success or error
    pub fn reset(&self) -> PyResult<()> {
        // Clear all sinks and related state
        with_state(|s| {
            s.sinks.clear();
            s.file_writers.clear();
            s.async_senders.clear();
            s.callbacks.clear();
        });

        self.configure(
            "INFO", false, None, false, false, true, true, true, false, false, false, None, None,
            None, None, None,
        )
    }

    /// Add a logging sink (output destination).
    ///
    /// Creates a new sink with optional rotation, compression, filtering, and async writing.
    ///
    /// # Arguments
    /// * `sink` - "console" for stdout or file path for file output
    /// * `rotation` - Rotation policy: "daily", "hourly", "minutely", or None
    /// * `size_limit` - Maximum file size before rotation (e.g., "5KB", "10MB", "1GB")
    /// * `filter_min_level` - Minimum log level for this sink
    /// * `filter_module` - Only log messages from this module
    /// * `filter_function` - Only log messages from this function
    /// * `async_write` - Enable background async writing (better performance)
    /// * `buffer_size` - Buffer size in bytes for async writing (default: 8192)
    /// * `flush_interval` - Flush interval in milliseconds for async writing (default: 1000)
    /// * `max_buffered_lines` - Maximum number of buffered lines before blocking (default: 1000)
    /// * `date_style` - Date format: "rfc3339", "local", "utc"
    /// * `date_enabled` - Include timestamp in log output
    /// * `retention` - Number of rotated files to keep
    /// * `format` - Custom format string for this sink (e.g., "{time} | {level} | {message}")
    /// * `json` - Format logs as JSON for this sink
    ///
    /// # Returns
    /// Handler ID that can be used to remove the sink later
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (sink, *, rotation=None, size_limit=None, filter_min_level=None, filter_module=None, filter_function=None, async_write=true, buffer_size=8192, flush_interval=1000, max_buffered_lines=1000, date_style=None, date_enabled=false, retention=None, format=None, json=false))]
    pub fn add(
        &self,
        sink: &str,
        rotation: Option<&str>,
        size_limit: Option<&str>,
        filter_min_level: Option<String>,
        filter_module: Option<String>,
        filter_function: Option<String>,
        async_write: bool,
        buffer_size: usize,
        flush_interval: u64,
        max_buffered_lines: usize,
        date_style: Option<String>,
        date_enabled: bool,
        retention: Option<usize>,
        format: Option<String>,
        json: bool,
    ) -> PyResult<usize> {
        use crate::config::state::{RotationPolicy, SinkConfig};

        let handler_id = with_state(|s| {
            let id = s.next_handler_id;
            s.next_handler_id += 1;

            let rotation_policy = match rotation {
                Some("daily") => RotationPolicy::Daily,
                Some("hourly") => RotationPolicy::Hourly,
                Some("minutely") => RotationPolicy::Minutely,
                Some(size_str) => {
                    // Parse size string like "10 MB", "1 GB", etc.
                    if let Some(size_bytes) = backend::parse_size_limit(Some(size_str)) {
                        RotationPolicy::Size(size_bytes)
                    } else {
                        RotationPolicy::Never
                    }
                }
                None => RotationPolicy::Never,
            };

            let sink_config = SinkConfig {
                id,
                path: if sink == "console" {
                    None
                } else {
                    Some(sink.to_string())
                },
                rotation: rotation_policy,
                compression: crate::config::state::Compression::None, // Default for now
                min_level: filter_min_level
                    .as_ref()
                    .and_then(|l| crate::utils::levels::to_level(l))
                    .map(crate::utils::levels::to_filter),
                module_filter: filter_module.clone(),
                function_filter: filter_function.clone(),
                async_write,
                buffer_size,
                flush_interval,
                max_buffered_lines,
                date_style: date_style.as_deref().unwrap_or("rfc3339").to_string(),
                date_enabled,
                retention,
                format: if json && format.is_none() {
                    // Use default JSON format when json=True and no custom format provided
                    Some(r#"{"timestamp": "{time}", "level": "{level}", "message": "{message}", "extra": {extra}}"#.to_string())
                } else {
                    format
                },
                json,
            };

            s.sinks.insert(id, sink_config);
            id
        });

        // Create file writer for this sink if it's not console
        if sink != "console" {
            let file_writer = backend::make_file_appender(
                sink,
                rotation,
                date_style.as_deref(),
                date_enabled,
                retention,
                size_limit,
            );
            with_state(|s| {
                s.file_writers.insert(handler_id, file_writer.clone());
            });

            // Set up async writing if requested
            if async_write {
                backend::start_async_writer_for_sink(
                    handler_id,
                    file_writer,
                    buffer_size,
                    flush_interval,
                    max_buffered_lines,
                );
            }
        }

        // For backward compatibility, also set the old fields
        if sink != "console" {
            with_state(|s| {
                s.file_path = Some(sink.to_string());
                s.file_rotation = rotation.map(|r| r.to_string());
                s.file_date_style = date_style.clone().map(|d| d.to_string());
                s.file_date_enabled = date_enabled;
                s.retention_count = retention;
                s.file_writer = Some(backend::make_file_appender(
                    sink,
                    rotation,
                    date_style.as_deref(),
                    date_enabled,
                    retention,
                    size_limit,
                ));
                // filters
                if let Some(min) = filter_min_level.as_ref()
                    && let Some(level) = crate::utils::levels::to_level(min)
                {
                    s.filter_min_level = Some(crate::utils::levels::to_filter(level));
                }
                s.filter_module = filter_module;
                s.filter_function = filter_function;
                // async
                s.async_write = async_write;
                s.buffer_size = buffer_size;
                s.flush_interval = flush_interval;
                s.max_buffered_lines = max_buffered_lines;
            });
        }

        // start background writer if requested
        backend::start_async_writer_if_needed();
        Ok(handler_id)
    }

    /// Remove a logging sink by handler ID.
    ///
    /// # Arguments
    /// * `handler_id` - Handler ID returned by add()
    ///
    /// # Returns
    /// True if sink was removed or handler ID was not found (no-op)
    pub fn remove(&self, handler_id: usize) -> PyResult<bool> {
        let removed = crate::config::state::with_state(|s| {
            if s.sinks.contains_key(&handler_id) {
                s.sinks.remove(&handler_id);
                // Also remove associated file writer if it exists
                s.file_writers.remove(&handler_id);
                // Remove async sender if it exists (this will signal the thread to stop)
                s.async_senders.remove(&handler_id);
                true
            } else {
                // Return true for non-existent handlers (no-op)
                true
            }
        });
        Ok(removed)
    }

    /// Add a callback function that executes asynchronously on each log event.
    ///
    /// The callback function will be called in the background with a log record
    /// containing timestamp, level, message, and any additional fields.
    ///
    /// # Arguments
    /// * `callback` - Python callable that accepts a log record dict
    ///
    /// # Returns
    /// Callback ID that can be used to remove the callback later
    pub fn add_callback(&self, callback: Py<PyAny>) -> PyResult<usize> {
        let callback_arc = std::sync::Arc::new(callback);
        let id = crate::config::state::with_state(|s| {
            s.callbacks.push(callback_arc);
            s.callbacks.len() - 1
        });
        Ok(id)
    }

    /// Remove a callback function by its ID.
    ///
    /// # Arguments
    /// * `callback_id` - Callback ID returned by add_callback()
    ///
    /// # Returns
    /// True if callback was removed, false if ID was invalid
    pub fn remove_callback(&self, callback_id: usize) -> PyResult<bool> {
        let removed = crate::config::state::with_state(|s| {
            if callback_id < s.callbacks.len() {
                s.callbacks.remove(callback_id);
                true
            } else {
                false
            }
        });
        Ok(removed)
    }

    /// Log a message at TRACE level (most verbose).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn trace(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::TRACE, msg, kwargs, None);
    }

    /// Log a message at DEBUG level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn debug(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::DEBUG, msg, kwargs, None);
    }

    /// Log a message at INFO level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn info(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::INFO, msg, kwargs, None);
    }

    /// Log a message at SUCCESS level (mapped to INFO in tracing).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn success(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::INFO, msg, kwargs, None);
    }

    /// Log a message at WARNING level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn warning(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::WARN, msg, kwargs, None);
    }

    /// Log a message at ERROR level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn error(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::ERROR, msg, kwargs, None);
    }

    /// Log a message at CRITICAL level (mapped to ERROR in tracing).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn critical(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::ERROR, msg, kwargs, None);
    }

    /// Log a message at a custom or aliased level.
    ///
    /// # Arguments
    /// * `level` - Level name ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL")
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    ///
    /// # Returns
    /// PyResult indicating success or error (invalid level)
    #[pyo3(signature = (level, msg, **kwargs))]
    pub fn log(&self, level: &str, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
        backend::log_message(lvl, msg, kwargs, None);
        Ok(())
    }

    /// Flush all pending log messages and ensure they are written.
    ///
    /// Call this before application shutdown to ensure buffered logs
    /// (especially from async sinks) are persisted to disk.
    pub fn complete(&self) {
        crate::backend::complete();
    }

    /// Log a message with custom stdout for testing (internal use only).
    ///
    /// # Arguments
    /// * `level` - Level name
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    /// * `stdout` - Python stdout object for testing
    #[pyo3(signature = (level, msg, stdout, **kwargs))]
    pub fn _log_with_stdout(
        &self,
        level: &str,
        msg: &str,
        stdout: &Bound<'_, PyAny>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
        backend::log_message(lvl, msg, kwargs, Some(stdout));
        Ok(())
    }

    // Extra conveniences for tests and control
    /// Reset internal state for testing purposes.
    ///
    /// WARNING: This is for internal testing only and should not be used
    /// in production code. It does not reset the global tracing subscriber.
    pub fn _reset_for_tests(&self) {
        crate::config::state::reset_state();
    }
}
