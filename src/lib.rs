//! # Logly - High-Performance Python Logging Library
//!
//! Logly is a Rust-powered logging library for Python that provides enterprise-grade
//! logging capabilities with exceptional performance and safety.
//!
//! ## Architecture
//!
//! The library is organized into focused modules:
//! - `backend`: Core logging functionality and output handling
//! - `config`: Configuration management and global state
//! - `format`: Output formatting utilities (JSON, text)
//! - `utils`: Shared utilities and type definitions
//!
//! ## Features
//!
//! - High-performance async logging with background buffering
//! - Structured JSON logging with custom fields
//! - File rotation with time and size-based policies
//! - Multi-sink architecture with per-sink filtering
//! - Thread-safe operations with lock-free optimizations
//! - Memory-safe with zero-cost abstractions
//! - Python bindings via PyO3/Maturin

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
