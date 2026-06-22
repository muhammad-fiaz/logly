//! Python bindings for the Logly Rust engine.
//!
//! This is the **only** crate allowed to depend on `pyo3`. It composes the
//! workspace crates, registers Python-facing classes/functions, converts
//! between Python types and the crates' native types, releases the GIL
//! around blocking operations, and maps `LoglyError` variants to Python
//! exception types. Contains no logging business logic.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use engine::LoggerEngine;
use error::LoglyError;
use filter::LevelFilter;
use format::{JsonFormatter, TemplateFormatter};
use levels::{level, levels, register_level};
use pyo3::IntoPyObject;
use pyo3::exceptions::{PyKeyError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use sink::{ConsoleSink, EnqueueSink, FileSink, Stream};
use std::sync::{Arc, Mutex};

// Network sink imports
use network::{
    HttpJsonConfig, HttpMethod, SyslogConfig, SyslogFacility, SyslogFormat, SyslogTransport,
    TcpConfig, UdpConfig,
};

fn to_py_error(error: LoglyError) -> PyErr {
    match error {
        LoglyError::InvalidLevel(message) | LoglyError::Config(message) => {
            PyValueError::new_err(message)
        }
        LoglyError::Sink(message)
        | LoglyError::Formatter(message)
        | LoglyError::Filter(message)
        | LoglyError::Rotation(message)
        | LoglyError::Compression(message)
        | LoglyError::Concurrency(message)
        | LoglyError::Context(message)
        | LoglyError::Schedule(message) => PyRuntimeError::new_err(message),
        LoglyError::Io(error) => PyRuntimeError::new_err(error.to_string()),
    }
}

fn record_to_py_dict<'py>(
    py: Python<'py>,
    record: &record::LogRecord,
    start_time: Option<f64>,
) -> Bound<'py, pyo3::types::PyDict> {
    use pyo3::types::PyDateTime;
    use pyo3::types::PyDelta;

    let record_dict = pyo3::types::PyDict::new(py);

    let duration = record
        .timestamp
        .duration_since(std::time::SystemTime::UNIX_EPOCH)
        .unwrap_or_default();
    #[expect(clippy::cast_precision_loss)]
    let secs = duration.as_secs() as f64 + f64::from(duration.subsec_nanos()) / 1e9;

    // Build datetime object from timestamp
    let datetime = if let Ok(dt) = PyDateTime::from_timestamp(py, secs, None) {
        dt
    } else {
        // Fallback: use utcfromtimestamp if timezone-aware fails
        let datetime_mod = py.import("datetime").unwrap();
        let utcfromtimestamp = datetime_mod
            .getattr("datetime")
            .unwrap()
            .getattr("utcfromtimestamp")
            .unwrap();
        utcfromtimestamp
            .call1((secs,))
            .unwrap()
            .cast_into::<pyo3::types::PyDateTime>()
            .unwrap()
    };

    let _ = record_dict.set_item("time", datetime);

    // Build timedelta for elapsed time
    #[allow(clippy::cast_possible_truncation)]
    if let Some(start) = start_time {
        let elapsed_secs = secs - start;
        let days = (elapsed_secs / 86400.0) as i32;
        let remaining = elapsed_secs - (f64::from(days) * 86400.0);
        let hours = (remaining / 3600.0) as i32;
        let remaining = remaining - (f64::from(hours) * 3600.0);
        let minutes = (remaining / 60.0) as i32;
        let remaining = remaining - (f64::from(minutes) * 60.0);
        let seconds = remaining as i32;
        let microseconds = ((remaining - f64::from(seconds)) * 1_000_000.0) as i32;
        match PyDelta::new(
            py,
            days,
            hours * 3600 + minutes * 60 + seconds,
            microseconds,
            true,
        ) {
            Ok(td) => {
                let _ = record_dict.set_item("elapsed", td);
            }
            Err(_) => {
                let _ = record_dict.set_item("elapsed", py.None());
            }
        }
    } else {
        let _ = record_dict.set_item("elapsed", py.None());
    }

    let extra = pyo3::types::PyDict::new(py);
    for (k, v) in &record.extra {
        let _ = extra.set_item(k, v);
    }

    let _ = record_dict.set_item("message", &record.message);
    let _ = record_dict.set_item("level", record.level.name());
    let _ = record_dict.set_item("priority", record.level.priority());
    let _ = record_dict.set_item("name", &record.name);

    // record["file"] as pathlib.PurePosixPath
    let file_str = record.file.as_deref().unwrap_or("");
    let pathlib_mod = py.import("pathlib");
    if let Ok(mod_obj) = pathlib_mod {
        if let Ok(pure_posix) = mod_obj.getattr("PurePosixPath") {
            if let Ok(path_obj) = pure_posix.call1((file_str,)) {
                let _ = record_dict.set_item("file", path_obj);
            } else {
                let _ = record_dict.set_item("file", file_str);
            }
        } else {
            let _ = record_dict.set_item("file", file_str);
        }
    } else {
        let _ = record_dict.set_item("file", file_str);
    }

    let _ = record_dict.set_item("line", record.line.unwrap_or(0));
    let _ = record_dict.set_item("function", record.function.as_deref().unwrap_or(""));
    let _ = record_dict.set_item("module", record.module.as_deref().unwrap_or(""));
    let _ = record_dict.set_item("thread", record.thread_name.as_deref().unwrap_or(""));
    let _ = record_dict.set_item("process", record.process_id);
    let _ = record_dict.set_item("extra", extra);

    // Exception is kept as formatted string from Rust side.
    // Python-side code reconstructs the full exception tuple when needed.
    if let Some(ref exc_str) = record.exception {
        let _ = record_dict.set_item("exception", exc_str);
    } else {
        let _ = record_dict.set_item("exception", py.None());
    }

    record_dict
}

fn update_record_from_py_dict(
    record: &mut record::LogRecord,
    record_dict: &Bound<'_, pyo3::types::PyDict>,
) -> PyResult<()> {
    if let Some(msg_val) = record_dict.get_item("message")? {
        record.message = msg_val.extract::<String>()?;
    }
    if let Some(level_val) = record_dict.get_item("level")?
        && let Ok(level_str) = level_val.extract::<String>()
        && let Ok(lvl) = levels::level(&level_str)
    {
        record.level = lvl;
    }
    if let Some(name_val) = record_dict.get_item("name")? {
        record.name = name_val.extract::<String>()?;
    }
    if let Some(file_val) = record_dict.get_item("file")?
        && let Ok(s) = file_val.extract::<String>()
    {
        record.file = Some(s);
    }
    if let Some(line_val) = record_dict.get_item("line")? {
        record.line = Some(line_val.extract::<u32>()?);
    }
    if let Some(func_val) = record_dict.get_item("function")? {
        record.function = Some(func_val.extract::<String>()?);
    }
    if let Some(mod_val) = record_dict.get_item("module")? {
        record.module = Some(mod_val.extract::<String>()?);
    }
    if let Some(thread_val) = record_dict.get_item("thread")? {
        record.thread_name = Some(thread_val.extract::<String>()?);
    }
    if let Some(process_val) = record_dict.get_item("process")? {
        record.process_id = process_val.extract::<u32>()?;
    }
    if let Some(extra_val) = record_dict.get_item("extra")?
        && let Ok(extra_dict) = extra_val.cast::<pyo3::types::PyDict>()
    {
        let mut new_extra = std::collections::BTreeMap::new();
        for (k, v) in extra_dict.iter() {
            let k_str = k.extract::<String>()?;
            let v_str = v.extract::<String>()?;
            new_extra.insert(k_str, v_str);
        }
        record.extra = new_extra;
    }
    if let Some(exc_val) = record_dict.get_item("exception")? {
        if exc_val.is_none() {
            record.exception = None;
        } else if let Ok(s) = exc_val.extract::<String>() {
            record.exception = Some(s);
        }
    }
    Ok(())
}

struct PyObjectSink {
    sink: Py<PyAny>,
    formatter: Box<dyn format::Formatter>,
    filter: Box<dyn filter::Filter>,
}

impl sink::Sink for PyObjectSink {
    fn handle(&self, record: &record::LogRecord) -> Result<(), LoglyError> {
        if !self.filter.accept(record) {
            return Ok(());
        }
        let mut line = self.formatter.format(record)?;
        if !line.ends_with('\n') {
            line.push('\n');
        }
        Python::attach(|py| {
            let py_sink = self.sink.bind(py);
            if py_sink.is_callable() {
                let _ = py_sink.call1((line,));
            } else if let Ok(write_meth) = py_sink.getattr("write") {
                let _ = write_meth.call1((line,));
            }
            Ok(())
        })
    }

    fn flush(&self) -> Result<(), LoglyError> {
        Python::attach(|py| {
            let py_sink = self.sink.bind(py);
            if let Ok(flush_meth) = py_sink.getattr("flush") {
                let _ = flush_meth.call0();
            }
            Ok(())
        })
    }
}

struct PyObjectFormatter {
    callable: Py<PyAny>,
}

impl format::Formatter for PyObjectFormatter {
    fn format(&self, record: &record::LogRecord) -> Result<String, error::LoglyError> {
        Python::attach(|py| {
            let record_dict = record_to_py_dict(py, record, None);
            let res = self.callable.bind(py).call1((record_dict,)).map_err(|e| {
                error::LoglyError::Formatter(format!("python custom formatter error: {e}"))
            })?;
            let s: String = res.extract().map_err(|e| {
                error::LoglyError::Formatter(format!(
                    "python custom formatter return type error: {e}"
                ))
            })?;
            Ok(s)
        })
    }
}

struct PyObjectFilter {
    callable: Py<PyAny>,
}

impl filter::Filter for PyObjectFilter {
    fn accept(&self, record: &record::LogRecord) -> bool {
        Python::attach(|py| {
            let record_dict = record_to_py_dict(py, record, None);
            if let Ok(res) = self.callable.bind(py).call1((record_dict,))
                && let Ok(accept) = res.extract::<bool>()
            {
                return Ok::<bool, LoglyError>(accept);
            }
            Ok::<bool, LoglyError>(false)
        })
        .unwrap_or(false)
    }
}

struct PatchedSink {
    inner: Arc<dyn sink::Sink>,
    patch: Py<PyAny>,
}

impl sink::Sink for PatchedSink {
    fn handle(&self, record: &record::LogRecord) -> Result<(), LoglyError> {
        let mut patched_record = record.clone();
        Python::attach(|py| {
            let record_dict = record_to_py_dict(py, &patched_record, None);
            self.patch
                .bind(py)
                .call1((&record_dict,))
                .map_err(|e| LoglyError::Sink(format!("failed to call patch: {e}")))?;
            update_record_from_py_dict(&mut patched_record, &record_dict)
                .map_err(|e| LoglyError::Sink(format!("failed to update record from dict: {e}")))?;
            Ok::<(), LoglyError>(())
        })?;
        self.inner.handle(&patched_record)
    }

    fn flush(&self) -> Result<(), LoglyError> {
        self.inner.flush()
    }

    fn close(&self) -> Result<(), LoglyError> {
        self.inner.close()
    }
}

fn resolve_filter(
    py: Python<'_>,
    filter_obj: Option<Py<PyAny>>,
) -> PyResult<Arc<dyn filter::Filter>> {
    if let Some(f_obj) = filter_obj {
        let f_bound = f_obj.bind(py);
        if f_bound.is_none() {
            Ok(Arc::new(filter::ConstFilter::new(true)))
        } else if let Ok(s) = f_bound.extract::<String>() {
            Ok(Arc::new(filter::PrefixFilter::new(s)))
        } else if let Ok(dict) = f_bound.clone().cast::<pyo3::types::PyDict>() {
            let mut map = std::collections::BTreeMap::new();
            for (k, v) in dict.iter() {
                let k_str = k.extract::<String>()?;
                let v_str = if let Ok(b) = v.extract::<bool>() {
                    if b {
                        "True".to_owned()
                    } else {
                        "False".to_owned()
                    }
                } else {
                    v.extract::<String>()?
                };
                map.insert(k_str, v_str);
            }
            Ok(Arc::new(filter::ExtraFilter::new(map)))
        } else if f_bound.is_callable() {
            Ok(Arc::new(PyObjectFilter { callable: f_obj }))
        } else {
            Err(PyValueError::new_err(
                "filter must be a string, dict, or callable",
            ))
        }
    } else {
        Ok(Arc::new(filter::ConstFilter::new(true)))
    }
}

fn resolve_rotation_policy_py(rot_obj: &Bound<'_, PyAny>) -> PyResult<rotate::RotationPolicy> {
    if rot_obj.is_none() {
        return Ok(rotate::RotationPolicy::Never);
    }

    if let Ok(s) = rot_obj.extract::<String>() {
        let canonical = config::parse_rotation_to_str(&s).map_err(to_py_error)?;
        return parse_canonical_rotation(&canonical);
    }

    if let Ok(bytes) = rot_obj.extract::<u64>() {
        return Ok(rotate::RotationPolicy::SizeBytes(bytes));
    }

    if rot_obj.is_callable() {
        return Ok(rotate::RotationPolicy::Never);
    }

    if let (Ok(kind_obj), Ok(value_obj)) = (rot_obj.getattr("kind"), rot_obj.getattr("value")) {
        let kind = kind_obj.extract::<String>()?;
        return match kind.as_str() {
            "size" => {
                if let Ok(b) = value_obj.extract::<u64>() {
                    Ok(rotate::RotationPolicy::SizeBytes(b))
                } else if let Ok(s) = value_obj.extract::<String>() {
                    let bytes = config::parse_size(&s);
                    Ok(rotate::RotationPolicy::SizeBytes(bytes))
                } else {
                    Ok(rotate::RotationPolicy::Never)
                }
            }
            "interval" => {
                if let Ok(secs) = value_obj.extract::<u64>() {
                    Ok(rotate::RotationPolicy::IntervalSeconds(secs))
                } else if let Ok(s) = value_obj.extract::<String>() {
                    let cleaned = s.trim().to_lowercase();
                    let seconds = if cleaned.ends_with(" seconds") || cleaned.ends_with(" second") {
                        cleaned
                            .split_whitespace()
                            .next()
                            .unwrap_or("0")
                            .parse()
                            .unwrap_or(0)
                    } else if cleaned.ends_with(" minutes") || cleaned.ends_with(" minute") {
                        cleaned
                            .split_whitespace()
                            .next()
                            .unwrap_or("0")
                            .parse::<u64>()
                            .unwrap_or(0)
                            * 60
                    } else if cleaned.ends_with(" hours") || cleaned.ends_with(" hour") {
                        cleaned
                            .split_whitespace()
                            .next()
                            .unwrap_or("0")
                            .parse::<u64>()
                            .unwrap_or(0)
                            * 3600
                    } else if cleaned.ends_with(" days") || cleaned.ends_with(" day") {
                        cleaned
                            .split_whitespace()
                            .next()
                            .unwrap_or("0")
                            .parse::<u64>()
                            .unwrap_or(0)
                            * 86400
                    } else {
                        match config::resolve_rotation_policy(&s) {
                            Ok(config::RotationPolicy::IntervalSeconds(secs)) => secs,
                            _ => 0,
                        }
                    };
                    Ok(rotate::RotationPolicy::IntervalSeconds(seconds))
                } else {
                    Ok(rotate::RotationPolicy::Never)
                }
            }
            _ => Ok(rotate::RotationPolicy::Never),
        };
    }

    Ok(rotate::RotationPolicy::Never)
}

#[allow(clippy::unnecessary_wraps)]
fn parse_canonical_rotation(canonical: &str) -> PyResult<rotate::RotationPolicy> {
    if canonical == "never" {
        return Ok(rotate::RotationPolicy::Never);
    }
    if let Some(rest) = canonical.strip_prefix("size:")
        && let Ok(bytes) = rest.parse::<u64>()
    {
        return Ok(rotate::RotationPolicy::SizeBytes(bytes));
    }
    if let Some(rest) = canonical.strip_prefix("interval:")
        && let Ok(secs) = rest.parse::<u64>()
    {
        return Ok(rotate::RotationPolicy::IntervalSeconds(secs));
    }
    Ok(rotate::RotationPolicy::Never)
}

fn resolve_retention_policy_py(ret_obj: &Bound<'_, PyAny>) -> PyResult<config::RetentionPolicy> {
    if ret_obj.is_none() {
        return Ok(config::RetentionPolicy::default());
    }

    if let Ok(s) = ret_obj.extract::<String>() {
        return config::resolve_retention_policy(&s).map_err(to_py_error);
    }

    if let Ok(count) = ret_obj.extract::<u32>() {
        return Ok(config::RetentionPolicy {
            count: Some(count),
            seconds: None,
        });
    }

    let count = if let Ok(c_obj) = ret_obj.getattr("count") {
        if c_obj.is_none() {
            None
        } else {
            Some(c_obj.extract::<u32>()?)
        }
    } else {
        None
    };

    let seconds = if let Ok(s_obj) = ret_obj.getattr("seconds") {
        if s_obj.is_none() {
            None
        } else {
            Some(s_obj.extract::<u64>()?)
        }
    } else {
        None
    };

    Ok(config::RetentionPolicy { count, seconds })
}

fn resolve_compression_codec_py(
    comp_obj: &Bound<'_, PyAny>,
) -> PyResult<compress::CompressionCodec> {
    if comp_obj.is_none() {
        return Ok(compress::CompressionCodec::None);
    }

    let codec_str = if let Ok(s) = comp_obj.extract::<String>() {
        s
    } else if let Ok(codec_val) = comp_obj.getattr("codec") {
        codec_val.extract::<String>()?
    } else {
        return Ok(compress::CompressionCodec::None);
    };

    match config::resolve_compression_codec(&codec_str).map_err(to_py_error)? {
        config::CompressionCodec::None => Ok(compress::CompressionCodec::None),
        config::CompressionCodec::Gzip => Ok(compress::CompressionCodec::Gzip),
        config::CompressionCodec::Zip => Ok(compress::CompressionCodec::Zip),
        config::CompressionCodec::Bz2 => Ok(compress::CompressionCodec::Bz2),
        config::CompressionCodec::Xz => Ok(compress::CompressionCodec::Xz),
        config::CompressionCodec::Zstd => Ok(compress::CompressionCodec::Zstd),
    }
}

/// Strips all HTML-like `<tag>` and `</tag>` markup from a string without
/// converting to ANSI escape codes. Used when `colorize=False`.
fn strip_all_tags(text: &str) -> String {
    let mut result = text.to_owned();
    let mut offset = 0;
    while offset < result.len() {
        let bytes = result.as_bytes();
        let Some(start) = bytes[offset..].iter().position(|&b| b == b'<') else {
            break;
        };
        let abs = offset + start;
        let next = abs + 1;
        let is_tag = if next < result.len() {
            let ch = bytes[next];
            ch.is_ascii_alphabetic() || ch == b'/'
        } else {
            false
        };
        if is_tag {
            if let Some(end) = result[abs..].find('>') {
                result.replace_range(abs..=abs + end, "");
                offset = abs;
            } else {
                break;
            }
        } else {
            offset = next;
        }
    }
    result
}

/// Python-facing logger wrapper around the Rust engine.
#[pyclass(name = "_Logger")]
struct PyLogger {
    engine: Mutex<LoggerEngine>,
    name: String,
}

#[pymethods]
impl PyLogger {
    #[new]
    fn new() -> Self {
        Self {
            engine: Mutex::new(LoggerEngine::new()),
            name: String::from("logly"),
        }
    }

    #[pyo3(signature = (
        sink,
        *,
        level = "INFO",
        format = None,
        colorize = None,
        serialize = false,
        pretty_json = None,
        enqueue = false,
        rotation = None,
        retention = None,
        compression = None,
        delay = false,
        watch = false,
        mode = "a",
        encoding = "utf-8",
        filter = None,
        patch = None
    ))]
    #[allow(clippy::too_many_arguments)]
    #[allow(clippy::fn_params_excessive_bools)]
    #[allow(clippy::needless_pass_by_value)]
    #[allow(clippy::too_many_lines)]
    #[expect(unused_variables)]
    fn add(
        &self,
        py: Python<'_>,
        sink: Py<PyAny>,
        level: &str,
        format: Option<Py<PyAny>>,
        colorize: Option<bool>,
        serialize: bool,
        pretty_json: Option<Py<PyAny>>,
        enqueue: bool,
        rotation: Option<Py<PyAny>>,
        retention: Option<Py<PyAny>>,
        compression: Option<Py<PyAny>>,
        delay: bool,
        watch: bool,
        mode: &str,
        encoding: &str,
        filter: Option<Py<PyAny>>,
        patch: Option<Py<PyAny>>,
    ) -> PyResult<u64> {
        let level_filter: Arc<dyn filter::Filter> =
            Arc::new(LevelFilter::new(levels::level(level).map_err(to_py_error)?));
        let custom_filter = resolve_filter(py, filter)?;
        let filter_chain: Box<dyn filter::Filter> =
            Box::new(filter::FilterChain::all(vec![level_filter, custom_filter]));

        let formatter: Box<dyn format::Formatter> = if serialize {
            let pj_obj = pretty_json.as_ref().map(|p| p.bind(py));
            let (use_pretty, indent, sort_keys, ensure_ascii, separators) = match pj_obj {
                Some(obj) => {
                    if obj.is_none() {
                        (false, 4, false, false, None)
                    } else if let Ok(b) = obj.extract::<bool>() {
                        (b, 4, false, false, None)
                    } else if let Ok(indent_val) = obj.getattr("indent") {
                        let indent = indent_val.extract::<usize>().unwrap_or(4);
                        let sort_keys = obj
                            .getattr("sort_keys")
                            .and_then(|v| v.extract::<bool>())
                            .unwrap_or(false);
                        let ensure_ascii = obj
                            .getattr("ensure_ascii")
                            .and_then(|v| v.extract::<bool>())
                            .unwrap_or(false);
                        let separators = obj.getattr("separators").ok().and_then(|v| {
                            if v.is_none() {
                                None
                            } else if let Ok((a, b)) = v.extract::<(String, String)>() {
                                Some((a, b))
                            } else {
                                None
                            }
                        });
                        (true, indent, sort_keys, ensure_ascii, separators)
                    } else {
                        (false, 4, false, false, None)
                    }
                }
                None => (false, 4, false, false, None),
            };
            if use_pretty {
                let mut fmt = JsonFormatter::pretty();
                fmt = fmt
                    .with_indent(indent)
                    .with_sort_keys(sort_keys)
                    .with_ensure_ascii(ensure_ascii);
                if let Some((item_sep, key_sep)) = separators {
                    fmt = fmt.with_separators(item_sep, key_sep);
                }
                Box::new(fmt)
            } else {
                Box::new(JsonFormatter::new())
            }
        } else {
            let fmt_obj = format.unwrap_or_else(|| {
                let default_fmt = "{level} | {message}";
                default_fmt.into_pyobject(py).unwrap().unbind().into()
            });
            let fmt_bound = fmt_obj.bind(py);
            if let Ok(fmt_str) = fmt_bound.extract::<String>() {
                let use_color = colorize.unwrap_or(false);
                let processed = if use_color {
                    config::strip_ansi_markup(&fmt_str)
                } else {
                    strip_all_tags(&fmt_str)
                };
                Box::new(TemplateFormatter::new(processed))
            } else if fmt_bound.is_callable() {
                Box::new(PyObjectFormatter { callable: fmt_obj })
            } else {
                return Err(PyValueError::new_err("format must be a string or callable"));
            }
        };

        let py_sink = sink.bind(py);
        let sink_obj: Arc<dyn sink::Sink> = if let Ok(sink_str) = py_sink.extract::<String>() {
            match sink_str.as_str() {
                "stdout" => Arc::new(ConsoleSink::new(
                    Stream::Stdout,
                    formatter,
                    filter_chain,
                    colorize.unwrap_or(false),
                )),
                "stderr" => Arc::new(ConsoleSink::new(
                    Stream::Stderr,
                    formatter,
                    filter_chain,
                    colorize.unwrap_or(false),
                )),
                sink_path => {
                    let rotation_policy = if let Some(ref r) = rotation {
                        resolve_rotation_policy_py(r.bind(py))?
                    } else {
                        rotate::RotationPolicy::Never
                    };
                    let retention_policy = if let Some(ref r) = retention {
                        resolve_retention_policy_py(r.bind(py))?
                    } else {
                        config::RetentionPolicy::default()
                    };
                    let compression_codec = if let Some(ref c) = compression {
                        resolve_compression_codec_py(c.bind(py))?
                    } else {
                        compress::CompressionCodec::None
                    };
                    let append = mode == "a";
                    Arc::new(
                        FileSink::open(
                            sink_path,
                            formatter,
                            filter_chain,
                            append,
                            rotation_policy,
                            retention_policy,
                            compression_codec,
                            delay,
                            watch,
                        )
                        .map_err(to_py_error)?,
                    )
                }
            }
        } else {
            Arc::new(PyObjectSink {
                sink,
                formatter,
                filter: filter_chain,
            })
        };

        let mut final_sink: Arc<dyn sink::Sink> = if enqueue {
            Arc::new(EnqueueSink::new(sink_obj))
        } else {
            sink_obj
        };

        if let Some(p) = patch {
            final_sink = Arc::new(PatchedSink {
                inner: final_sink,
                patch: p,
            });
        }

        let mut engine = self
            .engine
            .lock()
            .map_err(|_| PyRuntimeError::new_err("logger lock is unavailable"))?;
        Ok(engine.add_sink(final_sink))
    }

    #[pyo3(signature = (sink_id = None))]
    fn remove(&self, py: Python<'_>, sink_id: Option<u64>) -> PyResult<()> {
        py.detach(|| {
            self.engine
                .lock()
                .map_err(|_| PyRuntimeError::new_err("logger lock is unavailable"))?
                .remove_sink(sink_id)
                .map_err(to_py_error)
        })
    }

    fn complete(&self, py: Python<'_>) -> PyResult<()> {
        py.detach(|| {
            self.engine
                .lock()
                .map_err(|_| PyRuntimeError::new_err("logger lock is unavailable"))?
                .complete()
                .map_err(to_py_error)
        })
    }

    fn enable(&self, name: &str) -> PyResult<()> {
        self.engine
            .lock()
            .map_err(|_| PyRuntimeError::new_err("logger lock is unavailable"))?
            .enable(name);
        Ok(())
    }

    fn disable(&self, name: &str) -> PyResult<()> {
        self.engine
            .lock()
            .map_err(|_| PyRuntimeError::new_err("logger lock is unavailable"))?
            .disable(name);
        Ok(())
    }

    fn log(&self, level: &str, message: &str) -> PyResult<()> {
        self.engine
            .lock()
            .map_err(|_| PyRuntimeError::new_err("logger lock is unavailable"))?
            .log(&self.name, level, message)
            .map_err(to_py_error)
    }

    #[pyo3(signature = (
        level,
        message,
        *,
        name = None,
        file = None,
        line = None,
        function = None,
        module = None,
        thread_name = None,
        process_id = None,
        extra = None,
        exception = None,
        colors = false
    ))]
    #[allow(clippy::too_many_arguments)]
    fn log_structured(
        &self,
        level: &str,
        message: &str,
        name: Option<String>,
        file: Option<String>,
        line: Option<u32>,
        function: Option<String>,
        module: Option<String>,
        thread_name: Option<String>,
        process_id: Option<u32>,
        extra: Option<std::collections::BTreeMap<String, String>>,
        exception: Option<String>,
        colors: bool,
    ) -> PyResult<()> {
        let lvl = levels::level(level).map_err(to_py_error)?;
        let msg = if colors {
            config::strip_ansi_markup(message)
        } else {
            message.to_owned()
        };
        let mut builder = record::LogRecord::builder(lvl, msg);
        if let Some(n) = name {
            builder = builder.name(n);
        }
        builder = builder.location(file, line);

        let mut record = builder.build();
        if let Some(f) = function {
            record.function = Some(f);
        }
        if let Some(m) = module {
            record.module = Some(m);
        }
        if let Some(t) = thread_name {
            record.thread_name = Some(t);
        }
        if let Some(p) = process_id {
            record.process_id = p;
        }
        if let Some(e) = extra {
            record.extra = e;
        }
        if let Some(exc) = exception {
            record.exception = Some(exc);
        }

        self.engine
            .lock()
            .map_err(|_| PyRuntimeError::new_err("logger lock is unavailable"))?
            .dispatch(&record)
            .map_err(to_py_error)
    }

    fn trace(&self, message: &str) -> PyResult<()> {
        self.log("TRACE", message)
    }

    fn debug(&self, message: &str) -> PyResult<()> {
        self.log("DEBUG", message)
    }

    fn info(&self, message: &str) -> PyResult<()> {
        self.log("INFO", message)
    }

    fn notice(&self, message: &str) -> PyResult<()> {
        self.log("NOTICE", message)
    }

    fn success(&self, message: &str) -> PyResult<()> {
        self.log("SUCCESS", message)
    }

    fn warning(&self, message: &str) -> PyResult<()> {
        self.log("WARNING", message)
    }

    fn error(&self, message: &str) -> PyResult<()> {
        self.log("ERROR", message)
    }

    fn fail(&self, message: &str) -> PyResult<()> {
        self.log("FAIL", message)
    }

    fn critical(&self, message: &str) -> PyResult<()> {
        self.log("CRITICAL", message)
    }

    fn fatal(&self, message: &str) -> PyResult<()> {
        self.log("FATAL", message)
    }
}

/// Registers a custom logging level.
#[pyfunction]
#[pyo3(signature = (name, priority, color = None))]
fn register_custom_level(name: &str, priority: u16, color: Option<String>) -> PyResult<String> {
    register_level(name, priority, color)
        .map(|level| level.name().to_owned())
        .map_err(to_py_error)
}

/// Inspects a level and returns `(name, priority, color)`.
#[pyfunction]
fn inspect_level(name: &str) -> PyResult<(String, u16, Option<String>)> {
    let level = level(name).map_err(to_py_error)?;
    Ok((
        level.name().to_owned(),
        level.priority(),
        level.color().map(str::to_owned),
    ))
}

/// Returns all registered level names in severity order.
#[pyfunction]
fn list_levels() -> PyResult<Vec<String>> {
    levels()
        .map(|levels| {
            levels
                .into_iter()
                .map(|level| level.name().to_owned())
                .collect()
        })
        .map_err(to_py_error)
}

/// Raises a `KeyError` for unsupported native lookups.
#[pyfunction]
fn unsupported(name: &str) -> PyResult<()> {
    Err(PyKeyError::new_err(format!(
        "unsupported native item: {name}"
    )))
}

/// Parses a rotation string into its component type and value.
#[pyfunction]
fn parse_rotation_str(value: &str) -> PyResult<String> {
    config::parse_rotation_to_str(value).map_err(to_py_error)
}

/// Parses a retention string into counts and/or seconds.
#[pyfunction]
fn parse_retention_str(value: &str) -> PyResult<String> {
    config::parse_retention_to_str(value).map_err(to_py_error)
}

/// Parses a compression string to return the normalized codec name.
#[pyfunction]
fn parse_compression_str(value: &str) -> PyResult<String> {
    config::parse_compression_to_str(value).map_err(to_py_error)
}

/// Resolves a level name from a string that may be a name or numeric priority.
///
/// If the input is a number (e.g., `"20"`), returns the name of the level
/// with that priority (e.g., `"INFO"`). If the number doesn't match any
/// registered level, registers a new `LEVEL_N` and returns its name.
/// Otherwise looks up by name and returns the canonical uppercase name.
#[pyfunction]
fn resolve_level_name(value: &str) -> PyResult<String> {
    levels::resolve_level(value)
        .map(|lvl| lvl.name().to_owned())
        .map_err(to_py_error)
}

/// Formats exception text from a Python exception object.
///
/// Returns `None` if exc is `None` or `False`.
/// Returns `"exception=True"` if exc is `True`.
/// If `backtrace` is true, returns the full traceback string.
/// Otherwise returns `"TypeName: str(exc)"`.
#[pyfunction]
#[pyo3(signature = (exc, backtrace=false))]
fn format_exception_text(
    exc: Option<&Bound<'_, PyAny>>,
    backtrace: bool,
) -> PyResult<Option<String>> {
    match exc {
        None => Ok(None),
        Some(obj) => {
            if obj.is_none() {
                return Ok(None);
            }
            if let Ok(b) = obj.extract::<bool>() {
                if !b {
                    return Ok(None);
                }
                return Ok(Some("exception=True".to_owned()));
            }
            if backtrace {
                let tb_module = PyModule::import(obj.py(), "traceback")?;
                let formatted: Vec<String> = tb_module
                    .getattr("format_exception")?
                    .call1((obj,))?
                    .extract()?;
                return Ok(Some(formatted.join("")));
            }
            let type_name = obj.get_type().name()?.to_string();
            let value = obj.str()?.to_string();
            Ok(Some(format!("{type_name}: {value}")))
        }
    }
}

/// Python-facing HTTP JSON sink wrapper.
#[pyclass(name = "HttpJsonSink")]
struct PyHttpJsonSink {
    inner: network::HttpJsonSink,
}

#[pymethods]
impl PyHttpJsonSink {
    #[new]
    #[pyo3(signature = (url, *, method = "POST", headers = None, timeout = 30))]
    fn new(
        url: &str,
        method: &str,
        headers: Option<Vec<(String, String)>>,
        timeout: u64,
    ) -> PyResult<Self> {
        let http_method = match method.to_uppercase().as_str() {
            "POST" => HttpMethod::Post,
            "PUT" => HttpMethod::Put,
            _ => return Err(PyValueError::new_err("method must be POST or PUT")),
        };
        let config = HttpJsonConfig {
            url: url.to_owned(),
            method: http_method,
            headers: headers.unwrap_or_default(),
            timeout_secs: timeout,
        };
        Ok(Self {
            inner: network::HttpJsonSink::new(config),
        })
    }

    fn write(&self, line: &str) -> PyResult<()> {
        self.inner
            .write(line)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    fn flush(&self) {
        self.inner.flush();
    }
}

/// Python-facing TCP sink wrapper.
#[pyclass(name = "TcpSink")]
struct PyTcpSink {
    inner: network::TcpSink,
}

#[pymethods]
impl PyTcpSink {
    #[new]
    #[pyo3(signature = (host = "127.0.0.1", port = 514, delimiter = "\n"))]
    fn new(host: &str, port: u16, delimiter: &str) -> Self {
        let config = TcpConfig {
            host: host.to_owned(),
            port,
            delimiter: delimiter.to_owned(),
        };
        Self {
            inner: network::TcpSink::new(config),
        }
    }

    fn connect(&self) -> PyResult<()> {
        self.inner
            .connect()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    fn write(&self, line: &str) -> PyResult<()> {
        self.inner
            .write(line)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    fn flush(&self) -> PyResult<()> {
        self.inner
            .flush()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }
}

/// Python-facing UDP sink wrapper.
#[pyclass(name = "UdpSink")]
struct PyUdpSink {
    inner: network::UdpSink,
}

#[pymethods]
impl PyUdpSink {
    #[new]
    #[pyo3(signature = (host = "127.0.0.1", port = 514))]
    fn new(host: &str, port: u16) -> Self {
        let config = UdpConfig {
            host: host.to_owned(),
            port,
        };
        Self {
            inner: network::UdpSink::new(config),
        }
    }

    fn write(&self, line: &str) -> PyResult<()> {
        self.inner
            .write(line)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }
}

/// Python-facing Syslog sink wrapper.
#[pyclass(name = "SyslogSink")]
struct PySyslogSink {
    inner: network::SyslogSink,
}

#[pymethods]
impl PySyslogSink {
    #[new]
    #[pyo3(signature = (host = "127.0.0.1", port = 514, facility = "USER", transport = "UDP", format = "RFC3164", process_name = "logly"))]
    fn new(
        host: &str,
        port: u16,
        facility: &str,
        transport: &str,
        format: &str,
        process_name: &str,
    ) -> PyResult<Self> {
        let syslog_facility = match facility.to_uppercase().as_str() {
            "KERN" => SyslogFacility::Kernel,
            "USER" => SyslogFacility::User,
            "MAIL" => SyslogFacility::Mail,
            "DAEMON" => SyslogFacility::Daemon,
            "AUTH" => SyslogFacility::Auth,
            "SYSLOG" => SyslogFacility::Syslog,
            "LPR" => SyslogFacility::Lpr,
            "NEWS" => SyslogFacility::News,
            "UUCP" => SyslogFacility::Uucp,
            "CRON" => SyslogFacility::Cron,
            "AUTHPRIV" => SyslogFacility::AuthPriv,
            "FTP" => SyslogFacility::Ftp,
            "LOCAL0" => SyslogFacility::Local0,
            "LOCAL1" => SyslogFacility::Local1,
            "LOCAL2" => SyslogFacility::Local2,
            "LOCAL3" => SyslogFacility::Local3,
            "LOCAL4" => SyslogFacility::Local4,
            "LOCAL5" => SyslogFacility::Local5,
            "LOCAL6" => SyslogFacility::Local6,
            "LOCAL7" => SyslogFacility::Local7,
            _ => return Err(PyValueError::new_err("invalid syslog facility")),
        };
        let syslog_transport = match transport.to_uppercase().as_str() {
            "UDP" => SyslogTransport::Udp,
            "TCP" => SyslogTransport::Tcp,
            _ => return Err(PyValueError::new_err("transport must be UDP or TCP")),
        };
        let syslog_format = match format.to_uppercase().as_str() {
            "RFC3164" => SyslogFormat::Rfc3164,
            "RFC5424" => SyslogFormat::Rfc5424,
            _ => return Err(PyValueError::new_err("format must be RFC3164 or RFC5424")),
        };
        let config = SyslogConfig {
            host: host.to_owned(),
            port,
            facility: syslog_facility,
            transport: syslog_transport,
            format: syslog_format,
            process_name: process_name.to_owned(),
        };
        Ok(Self {
            inner: network::SyslogSink::new(config),
        })
    }

    fn write(&self, line: &str) -> PyResult<()> {
        self.inner
            .write(line)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    fn flush(&self) -> PyResult<()> {
        self.inner
            .flush()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }
}

/// Renders a format string with positional and keyword arguments.
///
/// Supports `{0}`, `{1}`, `"{name}"` style placeholders and lazy callable evaluation.
/// If `lazy` is true, callable args are invoked before substitution.
#[pyfunction]
#[pyo3(signature = (message, args=None, kwargs=None, lazy=false))]
fn render_message(
    message: &str,
    args: Option<Vec<Py<PyAny>>>,
    kwargs: Option<Bound<'_, pyo3::types::PyDict>>,
    lazy: bool,
) -> PyResult<String> {
    Python::attach(|py| {
        let py_args = args.unwrap_or_default();
        let py_kwargs = kwargs;

        // Resolve lazy args
        let mut final_args: Vec<Py<PyAny>> = Vec::new();
        for arg in &py_args {
            if lazy {
                let bound = arg.bind(py);
                if bound.is_callable() {
                    let result = bound.call0()?;
                    final_args.push(result.unbind());
                } else {
                    final_args.push(arg.clone_ref(py));
                }
            } else {
                final_args.push(arg.clone_ref(py));
            }
        }

        // Resolve lazy kwargs
        let resolved_kw = if let Some(kw) = py_kwargs {
            let dict = pyo3::types::PyDict::new(py);
            for (k, v) in kw.iter() {
                let key: String = k.extract()?;
                if lazy && v.is_callable() {
                    let result = v.call0()?;
                    dict.set_item(&key, result)?;
                } else {
                    dict.set_item(&key, v)?;
                }
            }
            Some(dict)
        } else {
            None
        };

        // Call message.format(*args, **kwargs) by building the call properly
        let msg_py: Py<PyAny> = message.into_pyobject(py)?.unbind().into();
        let format_fn = msg_py.bind(py).getattr("format")?;

        let result = match (&final_args, &resolved_kw) {
            (args, Some(kw)) if !args.is_empty() => {
                let args_bound: Vec<Bound<'_, PyAny>> =
                    final_args.iter().map(|a| a.bind(py).clone()).collect();
                let args_tuple = pyo3::types::PyTuple::new(py, &args_bound)?;
                format_fn.call(args_tuple, Some(kw))?
            }
            (args, None) if !args.is_empty() => {
                let args_bound: Vec<Bound<'_, PyAny>> =
                    final_args.iter().map(|a| a.bind(py).clone()).collect();
                let args_tuple = pyo3::types::PyTuple::new(py, &args_bound)?;
                format_fn.call1(args_tuple)?
            }
            (_, Some(kw)) => format_fn.call((), Some(kw))?,
            _ => format_fn.call0()?,
        };

        result.extract::<String>()
    })
}

#[pymodule]
fn _logly(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyLogger>()?;
    module.add_class::<PyHttpJsonSink>()?;
    module.add_class::<PyTcpSink>()?;
    module.add_class::<PyUdpSink>()?;
    module.add_class::<PySyslogSink>()?;
    module.add_function(wrap_pyfunction!(register_custom_level, module)?)?;
    module.add_function(wrap_pyfunction!(inspect_level, module)?)?;
    module.add_function(wrap_pyfunction!(list_levels, module)?)?;
    module.add_function(wrap_pyfunction!(unsupported, module)?)?;
    module.add_function(wrap_pyfunction!(parse_rotation_str, module)?)?;
    module.add_function(wrap_pyfunction!(parse_retention_str, module)?)?;
    module.add_function(wrap_pyfunction!(parse_compression_str, module)?)?;
    module.add_function(wrap_pyfunction!(resolve_level_name, module)?)?;
    module.add_function(wrap_pyfunction!(format_exception_text, module)?)?;
    module.add_function(wrap_pyfunction!(render_message, module)?)?;
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
