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

    /// Initialize the global console logger and set level/color/json.
    #[pyo3(signature = (level="INFO", color=true, json=false))]
    pub fn configure(&self, level: &str, color: bool, json: bool) -> PyResult<()> {
        backend::configure(level, color, json)
    }

    /// Add a sink. "console" or a file path. Rotation supports daily/hourly/minutely/never.
    #[pyo3(signature = (sink, *, rotation=None))]
    pub fn add(&self, sink: &str, rotation: Option<&str>) -> PyResult<usize> {
        if sink == "console" { return Ok(0); }
        with_state(|s| {
            s.file_path = Some(sink.to_string());
            s.file_rotation = rotation.map(|r| r.to_string());
            s.file_writer = Some(backend::make_file_appender(sink, rotation));
        });
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

    pub fn complete(&self) { tracing::dispatcher::get_default(|_| ()); }

    // Extra conveniences for tests and control
    /// Reset internal state (not global subscriber). Intended for tests only.
    pub fn _reset_for_tests(&self) { crate::state::reset_state(); }
}
