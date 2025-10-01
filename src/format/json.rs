//! # JSON Formatting Module
//!
//! This module provides JSON serialization and formatting utilities for structured logging.
//! It handles conversion between Python dictionaries and JSON records.
//!
//! ## Features
//!
//! - JSON record serialization with serde
//! - Python dict to key-value pairs conversion
//! - Structured logging with timestamp, level, and custom fields

use chrono::{DateTime, Utc};
use pyo3::types::{PyAnyMethods, PyDict, PyDictMethods};
use pyo3::Bound;
use serde::Serialize;
use serde_json;

/// Structured JSON log record.
///
/// Represents a complete log entry in JSON format with all standard fields
/// plus optional custom fields.
#[derive(Serialize)]
pub struct JsonRecord<'a> {
    /// ISO 8601 timestamp when the log was created
    pub timestamp: DateTime<Utc>,
    /// Log level (TRACE, DEBUG, INFO, WARN, ERROR)
    pub level: &'a str,
    /// The log message
    pub message: &'a str,
    /// Optional module name where the log originated
    pub module: Option<&'a str>,
    /// Optional function name where the log originated
    pub function: Option<&'a str>,
    /// Optional line number where the log originated
    pub line: Option<u32>,
    /// Custom fields as JSON value
    pub fields: serde_json::Value,
}

/// Convert a Python dictionary to a vector of key-value string pairs.
///
/// This function extracts string representations of keys and values from a
/// Python dictionary, handling various Python types gracefully.
///
/// # Arguments
///
/// * `dict` - The Python dictionary to convert
///
/// # Returns
///
/// A vector of (key, value) string pairs
pub fn dict_to_pairs(dict: &Bound<'_, PyDict>) -> Vec<(String, String)> {
    let mut out = Vec::new();
    for (k, v) in dict.iter() {
        let k_str = k.extract::<String>().unwrap_or_else(|_| "".to_string());
        let v_str = match v.str() {
            Ok(s) => s.extract::<String>().unwrap_or_else(|_| "".to_string()),
            Err(_) => "".to_string(),
        };
        out.push((k_str, v_str));
    }
    out
}

