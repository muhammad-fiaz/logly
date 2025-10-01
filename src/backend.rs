use crate::levels::{level_to_str, to_filter, to_level};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::Serialize;
use serde_json::json;
use chrono::{Utc, DateTime};
use std::io;
use std::thread;
use std::sync::Arc;
use parking_lot::Mutex;
use tracing::{debug, error, info, trace, warn, Level};
use tracing_appender::rolling::Rotation;
use std::fs::{File, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use tracing_subscriber::fmt::format::FmtSpan;
use tracing_subscriber::{fmt, prelude::*, EnvFilter, Registry};
use crossbeam_channel::unbounded as channel;

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

// A simple rolling writer that places the rotation timestamp before the file extension,
// e.g. `app.log` -> `app.2025-08-22.log` for daily rotation. This avoids appending
// the date after the extension which some users find unexpected.
struct SimpleRollingWriter {
    base_path: PathBuf,
    rotation: Rotation,
    current_period: String,
    file: File,
    date_style: String, // "before_ext" or "prefix"
    retention_count: Option<usize>,
}

impl SimpleRollingWriter {
    fn new(path: &Path, rotation: Rotation, date_style: Option<&str>, retention: Option<usize>) -> io::Result<Self> {
        let style = date_style.unwrap_or("before_ext").to_string();
        let current_period = Self::period_string(&rotation);
        let file = Self::open_for_period(path, &current_period, &style)?;
        Ok(SimpleRollingWriter { base_path: path.to_path_buf(), rotation, current_period, file, date_style: style, retention_count: retention })
    }

    fn period_string(rotation: &Rotation) -> String {
        let now = chrono::Utc::now();
        match *rotation {
            Rotation::DAILY => now.format("%Y-%m-%d").to_string(),
            Rotation::HOURLY => now.format("%Y-%m-%d_%H").to_string(),
            Rotation::MINUTELY => now.format("%Y-%m-%d_%H-%M").to_string(),
            Rotation::NEVER => String::new(),
        }
    }

    fn path_for_period(base: &Path, period: &str, date_style: &str) -> PathBuf {
        if period.is_empty() { return base.to_path_buf(); }
        let file_name = base.file_name().and_then(|s| s.to_str()).unwrap_or_default();
        if date_style == "prefix" {
            // prefix style: place the date before the filename separated by a dot
            // e.g. `2025-08-22.app.log` (preferred) and handle dot-leading filenames
            let new_name = if file_name.starts_with('.') {
                // file_name like `.hidden` -> `2025-08-22.hidden`
                format!("{}{}", period, file_name)
            } else {
                format!("{}.{}", period, file_name)
            };
            base.with_file_name(new_name)
        } else {
            // default: insert before extension
            if let Some(pos) = file_name.rfind('.') {
                let (stem, ext) = file_name.split_at(pos);
                let new_name = format!("{}.{}{}", stem, period, ext);
                base.with_file_name(new_name)
            } else {
                // no extension
                let new_name = format!("{}.{}", file_name, period);
                base.with_file_name(new_name)
            }
        }
    }

    fn open_for_period(base: &Path, period: &str, date_style: &str) -> io::Result<File> {
        let p = Self::path_for_period(base, period, date_style);
        if let Some(parent) = p.parent() {
            std::fs::create_dir_all(parent)?;
        }
        OpenOptions::new().create(true).append(true).open(p)
    }

    fn rotate_if_needed(&mut self) -> io::Result<()> {
        let new_period = Self::period_string(&self.rotation);
        if new_period != self.current_period {
            self.current_period = new_period.clone();
            self.file = Self::open_for_period(&self.base_path, &new_period, &self.date_style)?;
            // prune old files if retention is configured
            if let Some(keep) = self.retention_count {
                let current_path = Self::path_for_period(&self.base_path, &self.current_period, &self.date_style);
                if let Some(dir) = current_path.parent() {
                    let _ = prune_old_files(dir, &self.base_path, &self.date_style, keep, &current_path);
                }
            }
        }
        Ok(())
    }
}

impl Write for SimpleRollingWriter {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        if self.rotation != Rotation::NEVER {
            let _ = self.rotate_if_needed();
        }
        self.file.write(buf)
    }

    fn flush(&mut self) -> io::Result<()> { self.file.flush() }
}

fn prune_old_files(dir: &Path, base: &Path, date_style: &str, keep: usize, current_path: &Path) -> io::Result<()> {
    use std::fs;
    let base_name = base.file_name().and_then(|s| s.to_str()).unwrap_or("");
    let (stem, ext_opt) = match base_name.rfind('.') {
        Some(pos) => (&base_name[..pos], Some(&base_name[pos+1..])),
        None => (base_name, None),
    };
    let mut candidates: Vec<(std::time::SystemTime, PathBuf)> = Vec::new();
    for entry in fs::read_dir(dir)? {
        let entry = match entry { Ok(e) => e, Err(_) => continue };
        let path = entry.path();
        if path == current_path { continue; }
        if !path.is_file() { continue; }
        let name = match path.file_name().and_then(|s| s.to_str()) { Some(n) => n, None => continue };
        let matches = if date_style == "prefix" {
            // rotated form ends with ".<base_name>"
            name.ends_with(&format!(".{}", base_name))
        } else {
            // before_ext: stem.period.ext or name starts with "stem." (no ext)
            match ext_opt {
                Some(ext) => name.starts_with(&format!("{}.", stem)) && name.ends_with(&format!(".{}", ext)),
                None => name.starts_with(&format!("{}.", stem)),
            }
        };
        if !matches { continue; }
        let modified = entry.metadata().and_then(|m| m.modified()).unwrap_or(std::time::SystemTime::UNIX_EPOCH);
        candidates.push((modified, path));
    }
    if candidates.len() > keep {
        candidates.sort_by_key(|(t, _)| *t);
        let to_delete = candidates.len().saturating_sub(keep);
        for (_, p) in candidates.into_iter().take(to_delete) {
            let _ = fs::remove_file(p);
        }
    }
    Ok(())
}

pub fn make_file_appender(path: &str, rotation: Option<&str>, date_style: Option<&str>, date_enabled: bool, retention: Option<usize>) -> Arc<Mutex<Box<dyn Write + Send>>> {
    let mut rot = rotation_from_str(rotation);
    if !date_enabled { rot = Rotation::NEVER; }
    let p = Path::new(path);
    // try to create a SimpleRollingWriter; on error, fallback to writing directly to the given path
    match SimpleRollingWriter::new(p, rot, date_style, retention) {
        Ok(w) => Arc::new(Mutex::new(Box::new(w))),
        Err(_) => {
            // fallback: open a simple append file
            let _ = std::fs::create_dir_all(p.parent().unwrap_or_else(|| Path::new(".")));
            let f = OpenOptions::new().create(true).append(true).open(p).unwrap_or_else(|_| {
                // If all else fails, create a no-op writer
                File::create("fallback.log").expect("Cannot create fallback log file")
            });
            Arc::new(Mutex::new(Box::new(f)))
        }
    }
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
        // filter checks (file sink filters only apply to file writes; console honored by global level)
        let mut allow_file = true;
        if let Some(min) = s.filter_min_level {
            let current: tracing_subscriber::filter::LevelFilter = to_filter(level);
            if current < min { allow_file = false; }
        }
        if let Some(ref want_mod) = s.filter_module {
            let mut found = false;
            for (k, v) in &pairs { if k == "module" && v == want_mod { found = true; break; } }
            if !found { allow_file = false; }
        }
        if let Some(ref want_fn) = s.filter_function {
            let mut found = false;
            for (k, v) in &pairs { if k == "function" && v == want_fn { found = true; break; } }
            if !found { allow_file = false; }
        }
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
                if s.pretty_json {
                    eprintln!("{}", serde_json::to_string_pretty(&rec).unwrap_or_default());
                } else {
                    eprintln!("{}", serde_json::to_string(&rec).unwrap_or_default());
                }
            }
            if allow_file {
                if s.async_write {
                    if let Some(tx) = s.async_sender.as_ref() {
                        let line = if s.pretty_json { serde_json::to_string_pretty(&rec).unwrap_or_default() } else { serde_json::to_string(&rec).unwrap_or_default() };
                        let _ = tx.send(line);
                    }
                } else if let Some(writer) = s.file_writer.as_ref() {
                    let mut w = writer.lock();
                    let _ = writeln!(&mut **w, "{}", serde_json::to_string(&rec).unwrap_or_default());
                }
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
            if allow_file {
                if s.async_write {
                    if let Some(tx) = s.async_sender.as_ref() {
                        let line = format!("[{}] {}{}", level_to_str(level), msg, suffix);
                        let _ = tx.send(line);
                    }
                } else if let Some(writer) = s.file_writer.as_ref() {
                    let mut w = writer.lock();
                    let _ = writeln!(&mut **w, "[{}] {}{}", level_to_str(level), msg, suffix);
                }
            }
        }
    });
}

pub fn configure(level: &str, color: bool, json: bool, pretty_json: bool) -> PyResult<()> {
    let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
    crate::state::with_state(|s| {
        s.level_filter = to_filter(lvl);
        s.color = color;
        s.format_json = json;
        s.pretty_json = pretty_json;
    });
    init_global_if_needed()
}

pub fn start_async_writer_if_needed() {
    // spawn background thread to drain channel and write to file
    crate::state::with_state(|s| {
        if s.async_write && s.async_sender.is_none() && s.file_writer.is_some() {
            let (tx, rx) = channel::<String>();
            // Clone the Arc to the file writer for the background thread
            let file_writer = s.file_writer.as_ref().unwrap().clone();
            let handle = thread::spawn(move || {
                while let Ok(line) = rx.recv() {
                    let mut w = file_writer.lock();
                    let _ = writeln!(&mut **w, "{}", line);
                }
            });
            s.async_sender = Some(tx);
            s.async_handle = Some(handle);
        }
    });
}

pub fn complete() {
    // drop sender to signal thread to stop, then join
    let handle_opt = crate::state::with_state(|s| {
        // take sender and handle out of state
        let _ = s.async_sender.take();
        s.async_handle.take()
    });
    if let Some(handle) = handle_opt {
        let _ = handle.join();
    }
}
