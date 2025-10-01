//! Python bindings for the logly logger.
//!
//! Provides the `PyLogger` class exposed to Python, with methods for
//! configuration, sink management, and logging at various levels.

use crate::backend;
use crate::utils::levels::to_level;
use crate::config::state::with_state;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
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
    /// * `json` - Format logs as JSON
    /// * `pretty_json` - Format logs as pretty-printed JSON
    ///
    /// # Returns
    /// PyResult indicating success or error
    #[pyo3(signature = (level="INFO", color=true, json=false, pretty_json=false))]
    pub fn configure(
        &self,
        level: &str,
        color: bool,
        json: bool,
        pretty_json: bool,
    ) -> PyResult<()> {
        backend::configure(level, color, json, pretty_json)
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
    ///
    /// # Returns
    /// Handler ID that can be used to remove the sink later
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (sink, *, rotation=None, size_limit=None, filter_min_level=None, filter_module=None, filter_function=None, async_write=true, buffer_size=8192, flush_interval=1000, max_buffered_lines=1000, date_style=None, date_enabled=false, retention=None))]
    pub fn add(
        &self,
        sink: &str,
        rotation: Option<&str>,
        size_limit: Option<&str>,
        filter_min_level: Option<&str>,
        filter_module: Option<&str>,
        filter_function: Option<&str>,
        async_write: bool,
        buffer_size: usize,
        flush_interval: u64,
        max_buffered_lines: usize,
        date_style: Option<&str>,
        date_enabled: bool,
        retention: Option<usize>,
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
                path: if sink == "console" { None } else { Some(sink.to_string()) },
                rotation: rotation_policy,
                compression: crate::config::state::Compression::None, // Default for now
                min_level: filter_min_level.and_then(|l| crate::utils::levels::to_level(l)).map(crate::utils::levels::to_filter),
                module_filter: filter_module.map(|s| s.to_string()),
                function_filter: filter_function.map(|s| s.to_string()),
                async_write,
                buffer_size,
                flush_interval,
                max_buffered_lines,
                date_style: date_style.unwrap_or("rfc3339").to_string(),
                date_enabled,
                retention,
            };

            s.sinks.insert(id, sink_config);
            id
        });

        // For backward compatibility, also set the old fields
        if sink != "console" {
            with_state(|s| {
                s.file_path = Some(sink.to_string());
                s.file_rotation = rotation.map(|r| r.to_string());
                s.file_date_style = date_style.map(|d| d.to_string());
                s.file_date_enabled = date_enabled;
                s.retention_count = retention;
                s.file_writer = Some(backend::make_file_appender(
                    sink,
                    rotation,
                    date_style,
                    date_enabled,
                    retention,
                    size_limit,
                ));
                // filters
                if let Some(min) = filter_min_level
                    && let Some(level) = crate::utils::levels::to_level(min)
                {
                    s.filter_min_level = Some(crate::utils::levels::to_filter(level));
                }
                s.filter_module = filter_module.map(|m| m.to_string());
                s.filter_function = filter_function.map(|f| f.to_string());
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
    /// * `_handler_id` - Handler ID returned by add()
    ///
    /// # Returns
    /// True if sink was removed (currently always returns true)
    pub fn remove(&self, _handler_id: usize) -> PyResult<bool> {
        Ok(true)
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
        backend::log_message(Level::TRACE, msg, kwargs);
    }

    /// Log a message at DEBUG level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn debug(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::DEBUG, msg, kwargs);
    }

    /// Log a message at INFO level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn info(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::INFO, msg, kwargs);
    }

    /// Log a message at SUCCESS level (mapped to INFO in tracing).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn success(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::INFO, msg, kwargs);
    }

    /// Log a message at WARNING level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn warning(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::WARN, msg, kwargs);
    }

    /// Log a message at ERROR level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn error(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::ERROR, msg, kwargs);
    }

    /// Log a message at CRITICAL level (mapped to ERROR in tracing).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn critical(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::ERROR, msg, kwargs);
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
        backend::log_message(lvl, msg, kwargs);
        Ok(())
    }

    /// Flush all pending log messages and ensure they are written.
    ///
    /// Call this before application shutdown to ensure buffered logs
    /// (especially from async sinks) are persisted to disk.
    pub fn complete(&self) {
        crate::backend::complete();
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
