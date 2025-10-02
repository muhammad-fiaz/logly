mod backend;
mod config;
mod format;
mod logger;
mod utils;

use pyo3::prelude::*;

/// Python module initialization for logly.
///
/// This function sets up the Python extension module, exposing the logger
/// instance and version information to Python code.
#[pymodule]
fn _logly(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<logger::PyLogger>()?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    let py_logger = Py::new(py, logger::PyLogger::new())?;
    m.add("logger", py_logger)?;
    Ok(())
}
