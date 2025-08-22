use crate::backend;
use crate::levels::{to_level};
use crate::state::{with_state};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::Level;

#[pyclass]
pub struct PyLogger;

#[pymethods]
impl PyLogger {
    #[new]
    pub fn new() -> Self { PyLogger }

    /// Initialize the global console logger and set level/color/json/pretty_json.
    #[pyo3(signature = (level="INFO", color=true, json=false, pretty_json=false))]
    pub fn configure(&self, level: &str, color: bool, json: bool, pretty_json: bool) -> PyResult<()> {
        backend::configure(level, color, json, pretty_json)
    }

    /// Add a sink. "console" or a file path. Rotation supports daily/hourly/minutely/never.
    /// Optional filters: filter_min_level, filter_module, filter_function. async_write enables background file writes.
    #[pyo3(signature = (sink, *, rotation=None, filter_min_level=None, filter_module=None, filter_function=None, async_write=true))]
    pub fn add(&self, sink: &str, rotation: Option<&str>, filter_min_level: Option<&str>, filter_module: Option<&str>, filter_function: Option<&str>, async_write: bool) -> PyResult<usize> {
        if sink == "console" { return Ok(0); }
        with_state(|s| {
            s.file_path = Some(sink.to_string());
            s.file_rotation = rotation.map(|r| r.to_string());
            s.file_writer = Some(backend::make_file_appender(sink, rotation));
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

    pub fn remove(&self, _handler_id: usize) -> PyResult<bool> { Ok(true) }

    #[pyo3(signature = (msg, **kwargs))]
    pub fn trace(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::TRACE, msg, kwargs); }
    #[pyo3(signature = (msg, **kwargs))]
    pub fn debug(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::DEBUG, msg, kwargs); }
    #[pyo3(signature = (msg, **kwargs))]
    pub fn info(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::INFO, msg, kwargs); }
    #[pyo3(signature = (msg, **kwargs))]
    pub fn success(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::INFO, msg, kwargs); }
    #[pyo3(signature = (msg, **kwargs))]
    pub fn warning(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::WARN, msg, kwargs); }
    #[pyo3(signature = (msg, **kwargs))]
    pub fn error(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::ERROR, msg, kwargs); }
    #[pyo3(signature = (msg, **kwargs))]
    pub fn critical(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) { backend::log_message(Level::ERROR, msg, kwargs); }

    #[pyo3(signature = (level, msg, **kwargs))]
    pub fn log(&self, level: &str, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
        backend::log_message(lvl, msg, kwargs);
        Ok(())
    }

    pub fn complete(&self) { crate::backend::complete(); }

    // Extra conveniences for tests and control
    /// Reset internal state (not global subscriber). Intended for tests only.
    pub fn _reset_for_tests(&self) { crate::state::reset_state(); }
}
