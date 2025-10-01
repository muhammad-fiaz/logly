//! Python bindings for the logly logger.
//!
//! Provides the `PyLogger` class exposed to Python, with methods for
//! configuration, sink management, and logging at various levels.

use crate::backend;
use crate::levels::to_level;
use crate::state::with_state;
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
    pub fn configure(&self, level: &str, color: bool, json: bool, pretty_json: bool) -> PyResult<()> {
        backend::configure(level, color, json, pretty_json)
    }

    /// Add a logging sink (output destination).
    ///
    /// Creates a new sink with optional rotation, compression, filtering, and async writing.
    ///
    /// # Arguments
    /// * `sink` - "console" for stdout or file path for file output
    /// * `rotation` - Rotation policy: "daily", "hourly", "minutely", or None
    /// * `filter_min_level` - Minimum log level for this sink
    /// * `filter_module` - Only log messages from this module
    /// * `filter_function` - Only log messages from this function
    /// * `async_write` - Enable background async writing (better performance)
    /// * `date_style` - Date format: "rfc3339", "local", "utc"
    /// * `date_enabled` - Include timestamp in log output
    /// * `retention` - Number of rotated files to keep
    ///
    /// # Returns
    /// Handler ID that can be used to remove the sink later
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (sink, *, rotation=None, filter_min_level=None, filter_module=None, filter_function=None, async_write=true, date_style=None, date_enabled=false, retention=None))]
    pub fn add(&self, sink: &str, rotation: Option<&str>, filter_min_level: Option<&str>, filter_module: Option<&str>, filter_function: Option<&str>, async_write: bool, date_style: Option<&str>, date_enabled: bool, retention: Option<usize>) -> PyResult<usize> {
        if sink == "console" { return Ok(0); }
        with_state(|s| {
            s.file_path = Some(sink.to_string());
            s.file_rotation = rotation.map(|r| r.to_string());
            s.file_date_style = date_style.map(|d| d.to_string());
            s.file_date_enabled = date_enabled;
            s.retention_count = retention;
            s.file_writer = Some(backend::make_file_appender(sink, rotation, date_style, date_enabled, retention));
            // filters
            if let Some(min) = filter_min_level {
                if let Some(level) = crate::levels::to_level(min) {
                    s.filter_min_level = Some(crate::levels::to_filter(level));
                }
            }
            s.filter_module = filter_module.map(|m| m.to_string());
            s.filter_function = filter_function.map(|f| f.to_string());
            // async
            s.async_write = async_write;
        });
        // start background writer if requested
        backend::start_async_writer_if_needed();
        Ok(1)
    }

    /// Remove a logging sink by handler ID.
    ///
    /// # Arguments
    /// * `_handler_id` - Handler ID returned by add()
    ///
    /// # Returns
    /// True if sink was removed (currently always returns true)
    pub fn remove(&self, _handler_id: usize) -> PyResult<bool> { Ok(true) }

    /// Log a message at TRACE level (most verbose).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn trace(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::TRACE, msg, kwargs); }
    
    /// Log a message at DEBUG level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn debug(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::DEBUG, msg, kwargs); }
    
    /// Log a message at INFO level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn info(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::INFO, msg, kwargs); }
    
    /// Log a message at SUCCESS level (mapped to INFO in tracing).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn success(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::INFO, msg, kwargs); }
    
    /// Log a message at WARNING level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn warning(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::WARN, msg, kwargs); }
    
    /// Log a message at ERROR level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn error(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::ERROR, msg, kwargs); }
    
    /// Log a message at CRITICAL level (mapped to ERROR in tracing).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn critical(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::ERROR, msg, kwargs); }

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
    pub fn complete(&self) { crate::backend::complete(); }

    // Extra conveniences for tests and control
    /// Reset internal state for testing purposes.
    ///
    /// WARNING: This is for internal testing only and should not be used
    /// in production code. It does not reset the global tracing subscriber.
    pub fn _reset_for_tests(&self) { crate::state::reset_state(); }
}
