use crate::levels::{level_to_str, to_filter, to_level};
// ...existing code... (state accessed via crate::state::with_state where needed)
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::Serialize;
use serde_json::json;
use chrono::{Utc, DateTime};
use std::io;
use std::io::Write as _;
use tracing::{debug, error, info, trace, warn, Level};
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use tracing_subscriber::fmt::format::FmtSpan;
use tracing_subscriber::{fmt, prelude::*, EnvFilter, Registry};

pub fn init_global_if_needed() -> PyResult<()> {
    // Check and set state without returning PyResult from the locked closure to avoid
    // type inference issues. Build subscriber and set it, then mark state inited.
    let already = crate::state::with_state(|s| s.inited);
    if already { return Ok(()); }

    // build console layer using current state snapshot
    let (color, level_filter) = crate::state::with_state(|s| (s.color, s.level_filter));

    let console_layer = fmt::layer()
        .with_ansi(color)
        .with_span_events(FmtSpan::NONE)
        .with_target(false)
        .with_level(true)
        .with_thread_ids(false)
        .with_thread_names(false)
        .with_writer(io::stderr);

    let filter = EnvFilter::builder()
        .with_default_directive(level_filter.into())
        .from_env_lossy();

    let subscriber = Registry::default().with(filter).with(console_layer);
    tracing::subscriber::set_global_default(subscriber)
        .map_err(|e| PyRuntimeError::new_err(format!("failed to set global subscriber: {}", e)))?;

    crate::state::with_state(|s| s.inited = true);
    // respect console_enabled already via state when emitting
    Ok(())
}

pub fn rotation_from_str(rotation: Option<&str>) -> Rotation {
    match rotation.unwrap_or("never") {
        "daily" => Rotation::DAILY,
        "hourly" => Rotation::HOURLY,
        "minutely" => Rotation::MINUTELY,
        _ => Rotation::NEVER,
    }
}

pub fn make_file_appender(path: &str, rotation: Option<&str>) -> RollingFileAppender {
    let rot = rotation_from_str(rotation);
    let parent = std::path::Path::new(path)
        .parent()
        .unwrap_or_else(|| std::path::Path::new("."));
    let filename = std::path::Path::new(path).file_name().unwrap_or_default();
    RollingFileAppender::new(rot, parent, filename)
}

pub fn dict_to_pairs(d: &pyo3::Bound<'_, PyDict>) -> Vec<(String, String)> {
    d.iter()
        .map(|(k, v)| (py_any_to_string(&k), py_any_to_string(&v)))
        .collect()
}

pub fn py_any_to_string(value: &pyo3::Bound<'_, pyo3::PyAny>) -> String {
    if let Ok(s) = value.extract::<String>() { return s; }
    value.str().map(|s| s.to_string()).unwrap_or_else(|_| "<unrepr>".to_string())
}

#[inline]
pub fn fast_format_suffix(pairs: &[(String, String)]) -> String {
    if pairs.is_empty() { return String::new(); }
    let mut out = String::with_capacity(pairs.len() * 16);
    out.push_str(" | ");
    for (i, (k, v)) in pairs.iter().enumerate() {
        if i > 0 { out.push_str(", "); }
        out.push_str(k);
        out.push('=');
        out.push_str(v);
    }
    out
}

#[derive(Serialize)]
struct JsonRecord<'a> {
    timestamp: DateTime<Utc>,
    level: &'a str,
    message: &'a str,
    fields: serde_json::Value,
}

pub fn log_message(level: Level, msg: &str, extra: Option<&pyo3::Bound<'_, PyDict>>) {
    let pairs = extra.map(|d| dict_to_pairs(d)).unwrap_or_default();
    // Emit structured JSON when requested, otherwise keep legacy formatted suffix.
    crate::state::with_state(|s| {
        let lvl_str = level_to_str(level);
        if s.format_json {
            // Build a JSON record
            let fields: serde_json::Value = if pairs.is_empty() {
                json!({})
            } else {
                let mut map = serde_json::Map::with_capacity(pairs.len());
                for (k, v) in &pairs {
                    map.insert(k.clone(), serde_json::Value::String(v.clone()));
                }
                serde_json::Value::Object(map)
            };
            let rec = JsonRecord { timestamp: Utc::now(), level: lvl_str, message: msg, fields };
            if s.console_enabled {
                // print JSON to stderr for console layer compatibility
                eprintln!("{}", serde_json::to_string(&rec).unwrap_or_default());
            }
            if let Some(writer) = s.file_writer.as_mut() {
                let _ = writeln!(writer, "{}", serde_json::to_string(&rec).unwrap_or_default());
            }
        } else {
            let suffix = if pairs.is_empty() { String::new() } else { fast_format_suffix(&pairs) };
            match level {
                Level::TRACE => trace!(target: "logly", "{}{}", msg, suffix),
                Level::DEBUG => debug!(target: "logly", "{}{}", msg, suffix),
                Level::INFO => info!(target: "logly", "{}{}", msg, suffix),
                Level::WARN => warn!(target: "logly", "{}{}", msg, suffix),
                Level::ERROR => error!(target: "logly", "{}{}", msg, suffix),
            }
            if let Some(writer) = s.file_writer.as_mut() {
                let _ = writeln!(writer, "[{}] {}{}", level_to_str(level), msg, suffix);
            }
        }
    });
}

pub fn configure(level: &str, color: bool, json: bool) -> PyResult<()> {
    let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
    crate::state::with_state(|s| {
        s.level_filter = to_filter(lvl);
        s.color = color;
        s.format_json = json;
    });
    init_global_if_needed()
}
