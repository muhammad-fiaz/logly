mod levels;
mod state;
mod backend;
mod logger;

use pyo3::prelude::*;

#[pymodule]
fn _logly(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<logger::PyLogger>()?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    let py_logger = Py::new(py, logger::PyLogger::new())?;
    m.add("logger", py_logger)?;
    Ok(())
}
