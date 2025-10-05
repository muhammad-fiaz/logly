use crate::backend;
use crate::config::state::with_state;
use crate::utils::error::{LoglyError, validate_level, validate_rotation, validate_size_limit};
use crate::utils::levels::to_level;
use crate::utils::version_check;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;
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
    /// This creates a new PyLogger instance.
    ///
    /// # Arguments
    /// * `auto_update_check` - Enable automatic version checking on startup (default: true)
    ///
    /// # Returns
    /// A new PyLogger with default settings
    #[new]
    #[pyo3(signature = (auto_update_check = true))]
    pub fn new(auto_update_check: bool) -> Self {
        if auto_update_check {
            version_check::check_version_async();
        }
        PyLogger
    }

    /// Initialize and configure the global logger.
    ///
    /// Sets up the console output with the specified level, color, and format options.
    ///
    /// # Arguments
    /// * `level` - Minimum log level ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL")
    /// * `color` - Enable colored console output
    /// * `level_colors` - Optional dictionary mapping level names to ANSI color codes
    /// * `json` - Format logs as JSON
    /// * `pretty_json` - Format logs as pretty-printed JSON
    /// * `console` - Enable console output
    /// * `show_time` - Show timestamps in console output
    /// * `show_module` - Show module information in console output
    /// * `show_function` - Show function information in console output
    /// * `console_levels` - Optional dictionary mapping level names to console output enable/disable
    /// * `time_levels` - Optional dictionary mapping level names to time display enable/disable
    /// * `color_levels` - Optional dictionary mapping level names to color enable/disable
    /// * `storage_levels` - Optional dictionary mapping level names to file storage enable/disable
    /// * `color_callback` - Optional Python callable for custom color formatting with signature (level, text) -> colored_text
    /// * `auto_sink` - Automatically create a console sink if no sinks exist (default: true)
    /// * `auto_sink_levels` - Dictionary mapping log levels to file paths for automatic sink creation.
    ///                        Handled in Python layer, passed through for validation only.
    ///
    /// # Returns
    /// PyResult indicating success or error
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (level="INFO", color=true, level_colors=None, json=false, pretty_json=false, console=true, show_time=true, show_module=true, show_function=true, show_filename=false, show_lineno=false, console_levels=None, time_levels=None, color_levels=None, storage_levels=None, color_callback=None, auto_sink=true, auto_sink_levels=None))]
    pub fn configure(
        &self,
        py: Python<'_>,
        level: &str,
        color: bool,
        level_colors: Option<HashMap<String, String>>,
        json: bool,
        pretty_json: bool,
        console: bool,
        show_time: bool,
        show_module: bool,
        show_function: bool,
        show_filename: bool,
        show_lineno: bool,
        console_levels: Option<HashMap<String, bool>>,
        time_levels: Option<HashMap<String, bool>>,
        color_levels: Option<HashMap<String, bool>>,
        storage_levels: Option<HashMap<String, bool>>,
        color_callback: Option<Py<PyAny>>,
        auto_sink: bool,
        auto_sink_levels: Option<Py<PyAny>>,
    ) -> PyResult<()> {
        // Validate log level parameter
        validate_level(level)?;

        let colors = level_colors.map(|hm| hm.into_iter().collect());
        let console_lvls = console_levels.map(|hm| hm.into_iter().collect());
        let time_lvls = time_levels.map(|hm| hm.into_iter().collect());
        let color_lvls = color_levels.map(|hm| hm.into_iter().collect());
        let storage_lvls = storage_levels.map(|hm| hm.into_iter().collect());
        backend::configure_with_colors(
            level,
            color,
            json,
            pretty_json,
            console,
            show_time,
            show_module,
            show_function,
            show_filename,
            show_lineno,
            console_lvls,
            time_lvls,
            color_lvls,
            storage_lvls,
            colors,
            color_callback,
        )?;

        // Process auto_sink_levels if provided
        if let Some(auto_levels) = auto_sink_levels {
            let dict = auto_levels
                .downcast_bound::<pyo3::types::PyDict>(py)
                .map_err(|_| {
                    LoglyError::AutoSinkLevels("auto_sink_levels must be a dictionary".to_string())
                })?;

            for (key, value) in dict.iter() {
                let sink_level = key.extract::<String>().map_err(|_| {
                    LoglyError::AutoSinkLevels(
                        "auto_sink_levels keys must be strings (log level names)".to_string(),
                    )
                })?;

                // Validate the log level
                validate_level(&sink_level).map_err(|_| {
                    LoglyError::AutoSinkLevels(format!(
                        "Invalid log level '{}' in auto_sink_levels",
                        sink_level
                    ))
                })?;

                // Process value (either string path or dict config)
                if let Ok(path) = value.extract::<String>() {
                    // Simple string path: validate and create sink
                    if path.trim().is_empty() {
                        return Err(LoglyError::AutoSinkLevels(format!(
                            "Empty path for level '{}' in auto_sink_levels",
                            sink_level
                        ))
                        .into());
                    }

                    // Add sink with filter_min_level
                    self.add(
                        &path,
                        None,
                        None,
                        Some(sink_level.clone()),
                        None,
                        None,
                        true,
                        8192,
                        100,
                        1000,
                        None,
                        false,
                        None,
                        None,
                        false,
                    )?;
                } else if let Ok(config_dict) = value.downcast::<pyo3::types::PyDict>() {
                    // Advanced dict configuration
                    let path = config_dict.get_item("path")
                            .map_err(|_| LoglyError::AutoSinkLevels(
                                format!("Missing 'path' in auto_sink_levels configuration for level '{}'", sink_level)
                            ))?
                            .ok_or_else(|| LoglyError::AutoSinkLevels(
                                format!("Missing 'path' in auto_sink_levels configuration for level '{}'", sink_level)
                            ))?
                            .extract::<String>()
                            .map_err(|_| LoglyError::AutoSinkLevels(
                                format!("'path' must be a string in auto_sink_levels configuration for level '{}'", sink_level)
                            ))?;

                    if path.trim().is_empty() {
                        return Err(LoglyError::AutoSinkLevels(format!(
                            "Empty path for level '{}' in auto_sink_levels",
                            sink_level
                        ))
                        .into());
                    }

                    // Extract optional parameters with defaults
                    let rotation = config_dict
                        .get_item("rotation")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<String>().ok());
                    let size_limit = config_dict
                        .get_item("size_limit")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<String>().ok());
                    let filter_module = config_dict
                        .get_item("filter_module")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<String>().ok());
                    let filter_function = config_dict
                        .get_item("filter_function")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<String>().ok());
                    let async_write = config_dict
                        .get_item("async_write")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<bool>().ok())
                        .unwrap_or(true);
                    let buffer_size = config_dict
                        .get_item("buffer_size")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<usize>().ok())
                        .unwrap_or(8192);
                    let flush_interval = config_dict
                        .get_item("flush_interval")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<u64>().ok())
                        .unwrap_or(100);
                    let max_buffered_lines = config_dict
                        .get_item("max_buffered_lines")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<usize>().ok())
                        .unwrap_or(1000);
                    let date_style = config_dict
                        .get_item("date_style")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<String>().ok());
                    let date_enabled = config_dict
                        .get_item("date_enabled")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<bool>().ok())
                        .unwrap_or(false);
                    let retention = config_dict
                        .get_item("retention")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<usize>().ok());
                    let format = config_dict
                        .get_item("format")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<String>().ok());
                    let json_output = config_dict
                        .get_item("json")
                        .ok()
                        .flatten()
                        .and_then(|v| v.extract::<bool>().ok())
                        .unwrap_or(false);

                    // Add sink with all configuration
                    self.add(
                        &path,
                        rotation.as_deref(),
                        size_limit.as_deref(),
                        Some(sink_level.clone()),
                        filter_module,
                        filter_function,
                        async_write,
                        buffer_size,
                        flush_interval,
                        max_buffered_lines,
                        date_style,
                        date_enabled,
                        retention,
                        format,
                        json_output,
                    )?;
                } else {
                    return Err(LoglyError::AutoSinkLevels(format!(
                        "Invalid configuration type for level '{}' in auto_sink_levels. \
                                Expected str (file path) or dict (configuration)",
                        sink_level
                    ))
                    .into());
                }
            }
        }

        // Auto-create console sink if enabled and no sinks exist
        if auto_sink {
            let sink_count = with_state(|s| s.sinks.len());
            if sink_count == 0 {
                // Check if there's already a console sink to avoid duplicates
                let has_console = with_state(|s| s.sinks.values().any(|sink| sink.path.is_none()));

                if !has_console {
                    self.add(
                        "console", None, None, None, None, None, false, 8192, 1000, 1000, None,
                        false, None, None, false,
                    )?;
                }
            }
        }

        Ok(())
    }

    /// Reset logger configuration to defaults.
    ///
    /// Resets all logger settings to their default values, clearing any per-level
    /// controls and custom configurations.
    ///
    /// # Returns
    /// PyResult indicating success or error
    pub fn reset(&self, py: Python<'_>) -> PyResult<()> {
        // Clear all sinks and related state
        with_state(|s| {
            s.sinks.clear();
            s.file_writers.clear();
            s.async_senders.clear();
            s.callbacks.clear();
        });

        // Configure with defaults but don't auto-create console sink
        // This allows tests to start with a clean state
        self.configure(
            py, "INFO", false, None, false, false, true, true, true, false, false, false, None,
            None, None, None, None, false, None,
        )
    }

    /// Add a logging sink (output destination).
    ///
    /// Creates a new sink with optional rotation, compression, filtering, and async writing.
    ///
    /// # Arguments
    /// * `sink` - "console" for stdout or file path for file output
    /// * `rotation` - Rotation policy: "daily", "hourly", "minutely", or None
    /// * `size_limit` - Maximum file size before rotation (e.g., "5KB", "10MB", "1GB")
    /// * `filter_min_level` - Minimum log level for this sink
    /// * `filter_module` - Only log messages from this module
    /// * `filter_function` - Only log messages from this function
    /// * `async_write` - Enable background async writing (better performance)
    /// * `buffer_size` - Buffer size in bytes for async writing (default: 8192)
    /// * `flush_interval` - Flush interval in milliseconds for async writing (default: 1000)
    /// * `max_buffered_lines` - Maximum number of buffered lines before blocking (default: 1000)
    /// * `date_style` - Date format: "rfc3339", "local", "utc"
    /// * `date_enabled` - Include timestamp in log output
    /// * `retention` - Number of rotated files to keep
    /// * `format` - Custom format string for this sink (e.g., "{time} | {level} | {message}")
    /// * `json` - Format logs as JSON for this sink
    ///
    /// # Returns
    /// Handler ID that can be used to remove the sink later
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (sink, *, rotation=None, size_limit=None, filter_min_level=None, filter_module=None, filter_function=None, async_write=true, buffer_size=8192, flush_interval=1000, max_buffered_lines=1000, date_style=None, date_enabled=false, retention=None, format=None, json=false))]
    pub fn add(
        &self,
        sink: &str,
        rotation: Option<&str>,
        size_limit: Option<&str>,
        filter_min_level: Option<String>,
        filter_module: Option<String>,
        filter_function: Option<String>,
        async_write: bool,
        buffer_size: usize,
        flush_interval: u64,
        max_buffered_lines: usize,
        date_style: Option<String>,
        date_enabled: bool,
        retention: Option<usize>,
        format: Option<String>,
        json: bool,
    ) -> PyResult<usize> {
        use crate::config::state::{RotationPolicy, SinkConfig};

        // Validate filter_min_level if provided
        if let Some(ref level) = filter_min_level {
            validate_level(level)?;
        }

        // Validate rotation parameter
        if let Some(r) = rotation {
            validate_rotation(r)?;
        }

        // Validate size_limit parameter
        if let Some(sl) = size_limit {
            validate_size_limit(sl)?;
        }

        // Check for duplicate sinks and warn
        let is_console = sink == "console";
        let sink_path = if is_console {
            None
        } else {
            Some(sink.to_string())
        };

        let has_duplicate = with_state(|s| {
            s.sinks
                .values()
                .any(|existing_sink| existing_sink.path == sink_path)
        });

        if has_duplicate {
            Python::attach(|py| {
                let warnings = py.import("warnings")?;
                if is_console {
                    warnings.call_method1(
                        "warn",
                        (
                            "A console sink already exists. Adding another console sink may result in duplicate log output.",
                        ),
                    )?;
                } else {
                    warnings.call_method1(
                        "warn",
                        (
                            format!("A sink for path '{}' already exists. Adding another sink with the same path may cause conflicts.", sink),
                        ),
                    )?;
                }
                Ok::<_, PyErr>(())
            })?;
        }

        let handler_id = with_state(|s| {
            let id = s.next_handler_id;
            s.next_handler_id += 1;

            let rotation_policy = match rotation {
                Some("daily") => RotationPolicy::Daily,
                Some("hourly") => RotationPolicy::Hourly,
                Some("minutely") => RotationPolicy::Minutely,
                Some(size_str) => {
                    // Parse size string like "10 MB", "1 GB", etc.
                    if let Some(size_bytes) = backend::parse_size_limit(Some(size_str)) {
                        RotationPolicy::Size(size_bytes)
                    } else {
                        RotationPolicy::Never
                    }
                }
                None => RotationPolicy::Never,
            };

            let sink_config = SinkConfig {
                id,
                path: sink_path.clone(),
                rotation: rotation_policy,
                compression: crate::config::state::Compression::None, // Default for now
                min_level: filter_min_level
                    .as_ref()
                    .and_then(|l| crate::utils::levels::to_level(l))
                    .map(crate::utils::levels::to_filter),
                module_filter: filter_module.clone(),
                function_filter: filter_function.clone(),
                async_write,
                buffer_size,
                flush_interval,
                max_buffered_lines,
                date_style: date_style.as_deref().unwrap_or("rfc3339").to_string(),
                date_enabled,
                retention,
                format: if json && format.is_none() {
                    // Use default JSON format when json=True and no custom format provided
                    Some(r#"{"timestamp": "{time}", "level": "{level}", "message": "{message}", "extra": {extra}}"#.to_string())
                } else {
                    format
                },
                json,
                enabled: true, // Sinks are enabled by default
            };

            s.sinks.insert(id, sink_config);
            id
        });

        // Create file writer for this sink if it's not console
        if sink != "console" {
            let file_writer = backend::make_file_appender(
                sink,
                rotation,
                date_style.as_deref(),
                date_enabled,
                retention,
                size_limit,
            );
            with_state(|s| {
                s.file_writers.insert(handler_id, file_writer.clone());
            });

            // Set up async writing if requested
            if async_write {
                backend::start_async_writer_for_sink(
                    handler_id,
                    file_writer,
                    buffer_size,
                    flush_interval,
                    max_buffered_lines,
                );
            }
        }

        // For backward compatibility, also set the old fields
        if sink != "console" {
            with_state(|s| {
                s.file_path = Some(sink.to_string());
                s.file_rotation = rotation.map(|r| r.to_string());
                s.file_date_style = date_style.clone().map(|d| d.to_string());
                s.file_date_enabled = date_enabled;
                s.retention_count = retention;
                s.file_writer = Some(backend::make_file_appender(
                    sink,
                    rotation,
                    date_style.as_deref(),
                    date_enabled,
                    retention,
                    size_limit,
                ));
                // filters
                if let Some(min) = filter_min_level.as_ref()
                    && let Some(level) = crate::utils::levels::to_level(min)
                {
                    s.filter_min_level = Some(crate::utils::levels::to_filter(level));
                }
                s.filter_module = filter_module;
                s.filter_function = filter_function;
                // async
                s.async_write = async_write;
                s.buffer_size = buffer_size;
                s.flush_interval = flush_interval;
                s.max_buffered_lines = max_buffered_lines;
            });
        }

        // start background writer if requested
        backend::start_async_writer_if_needed();
        Ok(handler_id)
    }

    /// Remove a logging sink by handler ID.
    ///
    /// # Arguments
    /// * `handler_id` - Handler ID returned by add()
    ///
    /// # Returns
    /// True if sink was removed or handler ID was not found (no-op)
    pub fn remove(&self, handler_id: usize) -> PyResult<bool> {
        let removed = crate::config::state::with_state(|s| {
            if s.sinks.contains_key(&handler_id) {
                s.sinks.remove(&handler_id);
                // Also remove associated file writer if it exists
                s.file_writers.remove(&handler_id);
                // Remove async sender if it exists (this will signal the thread to stop)
                s.async_senders.remove(&handler_id);
                true
            } else {
                // Return true for non-existent handlers (no-op)
                true
            }
        });
        Ok(removed)
    }

    /// Remove all logging sinks.
    ///
    /// Clears all registered sinks (console and file outputs), their associated
    /// file writers, and async senders. This is useful for cleanup or reconfiguration.
    ///
    /// # Returns
    /// Number of sinks that were removed
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// logger.add("app.log")
    /// logger.add("error.log")
    /// count = logger.remove_all()  # Returns 2
    /// ```
    pub fn remove_all(&self) -> PyResult<usize> {
        let count = crate::config::state::with_state(|s| {
            let num_sinks = s.sinks.len();
            s.sinks.clear();
            s.file_writers.clear();
            s.async_senders.clear();
            num_sinks
        });
        Ok(count)
    }

    /// Get the number of active sinks.
    ///
    /// Returns the count of all registered sinks (file and console outputs).
    /// This is useful for monitoring and debugging logging configuration.
    ///
    /// # Returns
    /// Number of active sinks
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// logger.add("app.log")
    /// logger.add("error.log")
    /// count = logger.sink_count()  # Returns 2
    /// ```
    pub fn sink_count(&self) -> PyResult<usize> {
        let count = crate::config::state::with_state(|s| s.sinks.len());
        Ok(count)
    }

    /// List all active sink handler IDs.
    ///
    /// Returns a list of handler IDs for all registered sinks. These IDs can
    /// be used with remove() to selectively remove sinks.
    ///
    /// # Returns
    /// List of handler IDs (as integers)
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// id1 = logger.add("app.log")
    /// id2 = logger.add("error.log")
    /// ids = logger.list_sinks()  # Returns [id1, id2]
    /// logger.remove(ids[0])  # Remove first sink
    /// ```
    pub fn list_sinks(&self) -> PyResult<Vec<usize>> {
        let ids = crate::config::state::with_state(|s| s.sinks.keys().copied().collect::<Vec<_>>());
        Ok(ids)
    }

    /// Get detailed information about a specific sink.
    ///
    /// Returns a dictionary with sink configuration details including path,
    /// rotation policy, compression, async settings, and format options.
    ///
    /// # Arguments
    /// * `handler_id` - Handler ID returned by add()
    ///
    /// # Returns
    /// Dictionary with sink information, or None if handler ID not found
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// id = logger.add("app.log", rotation="daily", async_mode=True)
    /// info = logger.sink_info(id)
    /// print(info["path"])  # "app.log"
    /// print(info["rotation"])  # "daily"
    /// print(info["async_write"])  # True
    /// ```
    pub fn sink_info(&self, handler_id: usize) -> PyResult<Option<HashMap<String, String>>> {
        let info = crate::config::state::with_state(|s| {
            s.sinks.get(&handler_id).map(|sink| {
                let mut map = HashMap::new();
                map.insert("id".to_string(), handler_id.to_string());

                // Path information
                if let Some(ref path) = sink.path {
                    map.insert("path".to_string(), path.clone());
                    map.insert("type".to_string(), "file".to_string());
                } else {
                    map.insert("type".to_string(), "console".to_string());
                }

                // Rotation policy
                let rotation = match &sink.rotation {
                    crate::config::state::RotationPolicy::Never => "never".to_string(),
                    crate::config::state::RotationPolicy::Daily => "daily".to_string(),
                    crate::config::state::RotationPolicy::Hourly => "hourly".to_string(),
                    crate::config::state::RotationPolicy::Minutely => "minutely".to_string(),
                    crate::config::state::RotationPolicy::Size(bytes) => format!("{}B", bytes),
                };
                map.insert("rotation".to_string(), rotation);

                // Compression
                let compression = match sink.compression {
                    crate::config::state::Compression::None => "none".to_string(),
                    crate::config::state::Compression::Gzip => "gzip".to_string(),
                    crate::config::state::Compression::Zstd => "zstd".to_string(),
                };
                map.insert("compression".to_string(), compression);

                // Async settings
                map.insert("async_write".to_string(), sink.async_write.to_string());
                map.insert("buffer_size".to_string(), sink.buffer_size.to_string());
                map.insert(
                    "flush_interval".to_string(),
                    sink.flush_interval.to_string(),
                );

                // Format settings
                map.insert("json".to_string(), sink.json.to_string());
                map.insert("date_enabled".to_string(), sink.date_enabled.to_string());
                map.insert("date_style".to_string(), sink.date_style.clone());

                if let Some(ref format) = sink.format {
                    map.insert("format".to_string(), format.clone());
                }

                // Retention
                if let Some(retention) = sink.retention {
                    map.insert("retention".to_string(), retention.to_string());
                }

                // Enabled status
                map.insert("enabled".to_string(), sink.enabled.to_string());

                map
            })
        });
        Ok(info)
    }

    /// Get information about all active sinks.
    ///
    /// Returns a list of dictionaries containing configuration details for
    /// all registered sinks. This is useful for debugging and monitoring.
    ///
    /// # Returns
    /// List of sink information dictionaries
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// logger.add("app.log", rotation="daily")
    /// logger.add("error.log", rotation="1MB")
    /// sinks = logger.all_sinks_info()
    /// for sink in sinks:
    ///     print(f"{sink['path']}: {sink['rotation']}")
    /// ```
    pub fn all_sinks_info(&self) -> PyResult<Vec<HashMap<String, String>>> {
        let all_info = crate::config::state::with_state(|s| {
            s.sinks
                .iter()
                .map(|(id, sink)| {
                    let mut map = HashMap::new();
                    map.insert("id".to_string(), id.to_string());

                    // Path information
                    if let Some(ref path) = sink.path {
                        map.insert("path".to_string(), path.clone());
                        map.insert("type".to_string(), "file".to_string());
                    } else {
                        map.insert("type".to_string(), "console".to_string());
                    }

                    // Rotation policy
                    let rotation = match &sink.rotation {
                        crate::config::state::RotationPolicy::Never => "never".to_string(),
                        crate::config::state::RotationPolicy::Daily => "daily".to_string(),
                        crate::config::state::RotationPolicy::Hourly => "hourly".to_string(),
                        crate::config::state::RotationPolicy::Minutely => "minutely".to_string(),
                        crate::config::state::RotationPolicy::Size(bytes) => format!("{}B", bytes),
                    };
                    map.insert("rotation".to_string(), rotation);

                    // Compression
                    let compression = match sink.compression {
                        crate::config::state::Compression::None => "none".to_string(),
                        crate::config::state::Compression::Gzip => "gzip".to_string(),
                        crate::config::state::Compression::Zstd => "zstd".to_string(),
                    };
                    map.insert("compression".to_string(), compression);

                    // Async settings
                    map.insert("async_write".to_string(), sink.async_write.to_string());
                    map.insert("buffer_size".to_string(), sink.buffer_size.to_string());
                    map.insert(
                        "flush_interval".to_string(),
                        sink.flush_interval.to_string(),
                    );

                    // Format settings
                    map.insert("json".to_string(), sink.json.to_string());
                    map.insert("date_enabled".to_string(), sink.date_enabled.to_string());
                    map.insert("date_style".to_string(), sink.date_style.clone());

                    if let Some(ref format) = sink.format {
                        map.insert("format".to_string(), format.clone());
                    }

                    // Retention
                    if let Some(retention) = sink.retention {
                        map.insert("retention".to_string(), retention.to_string());
                    }

                    map
                })
                .collect()
        });
        Ok(all_info)
    }

    /// Add a callback function that executes asynchronously on each log event.
    ///
    /// The callback function will be called in the background with a log record
    /// containing timestamp, level, message, and any additional fields.
    ///
    /// # Arguments
    /// * `callback` - Python callable that accepts a log record dict
    ///
    /// # Returns
    /// Callback ID that can be used to remove the callback later
    pub fn add_callback(&self, callback: Py<PyAny>) -> PyResult<usize> {
        let callback_arc = std::sync::Arc::new(callback);
        let id = crate::config::state::with_state(|s| {
            s.callbacks.push(callback_arc);
            s.callbacks.len() - 1
        });
        Ok(id)
    }

    /// Remove a callback function by its ID.
    ///
    /// # Arguments
    /// * `callback_id` - Callback ID returned by add_callback()
    ///
    /// # Returns
    /// True if callback was removed, false if ID was invalid
    pub fn remove_callback(&self, callback_id: usize) -> PyResult<bool> {
        let removed = crate::config::state::with_state(|s| {
            if callback_id < s.callbacks.len() {
                s.callbacks.remove(callback_id);
                true
            } else {
                false
            }
        });
        Ok(removed)
    }

    /// Log a message at TRACE level (most verbose).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn trace(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::TRACE, msg, kwargs, None);
    }

    /// Log a message at DEBUG level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn debug(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::DEBUG, msg, kwargs, None);
    }

    /// Log a message at INFO level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn info(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::INFO, msg, kwargs, None);
    }

    /// Log a message at SUCCESS level (mapped to INFO in tracing).
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn success(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::INFO, msg, kwargs, None);
    }

    /// Log a message at WARNING level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn warning(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::WARN, msg, kwargs, None);
    }

    /// Log a message at ERROR level.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn error(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message(Level::ERROR, msg, kwargs, None);
    }

    /// Log a message at CRITICAL level (mapped to ERROR in tracing).
    ///
    /// Displays as [CRITICAL] while using ERROR level internally for filtering.
    /// Fixes: https://github.com/muhammad-fiaz/logly/issues/66
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn critical(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message_with_level_override(Level::ERROR, msg, kwargs, None, Some("CRITICAL"));
    }

    /// Log a message at FAIL level (mapped to ERROR in tracing).
    ///
    /// Displays as [FAIL] while using ERROR level internally for filtering.
    /// Use this for operation failures that are different from errors.
    ///
    /// # Arguments
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    #[pyo3(signature = (msg, **kwargs))]
    pub fn fail(&self, msg: &str, kwargs: Option<&Bound<'_, PyDict>>) {
        backend::log_message_with_level_override(Level::ERROR, msg, kwargs, None, Some("FAIL"));
    }

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
        backend::log_message(lvl, msg, kwargs, None);
        Ok(())
    }

    /// Flush all pending log messages and ensure they are written.
    ///
    /// Call this before application shutdown to ensure buffered logs
    /// (especially from async sinks) are persisted to disk.
    pub fn complete(&self) {
        crate::backend::complete();
    }

    /// Log a message with custom stdout for testing (internal use only).
    ///
    /// # Arguments
    /// * `level` - Level name
    /// * `msg` - Log message
    /// * `kwargs` - Optional key-value context fields
    /// * `stdout` - Python stdout object for testing
    #[pyo3(signature = (level, msg, stdout, **kwargs))]
    pub fn _log_with_stdout(
        &self,
        level: &str,
        msg: &str,
        stdout: &Bound<'_, PyAny>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let lvl = to_level(level).ok_or_else(|| PyValueError::new_err("invalid level"))?;
        backend::log_message(lvl, msg, kwargs, Some(stdout));
        Ok(())
    }

    /// Delete the log file associated with a specific sink.
    ///
    /// Removes the physical log file from disk for the given sink ID.
    /// The sink itself remains active and will create a new file on next write.
    ///
    /// # Arguments
    /// * `sink_id` - The handler ID of the sink whose log file should be deleted
    ///
    /// # Returns
    /// `true` if the file was deleted, `false` if sink not found or no file exists
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// sink_id = logger.add("app.log")
    /// logger.info("Some logs")
    /// logger.delete(sink_id)  # Deletes app.log
    /// ```
    pub fn delete(&self, sink_id: usize) -> PyResult<bool> {
        let deleted = with_state(|s| {
            if let Some(sink) = s.sinks.get(&sink_id) {
                if let Some(ref path) = sink.path {
                    std::fs::remove_file(path).is_ok()
                } else {
                    false
                }
            } else {
                false
            }
        });
        Ok(deleted)
    }

    /// Delete all log files associated with all sinks.
    ///
    /// Removes all physical log files from disk. Sinks remain active and will
    /// create new files on next write.
    ///
    /// # Returns
    /// Number of files successfully deleted
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// logger.add("app.log")
    /// logger.add("error.log")
    /// count = logger.delete_all()  # Deletes both files
    /// ```
    pub fn delete_all(&self) -> PyResult<usize> {
        let count = with_state(|s| {
            let mut deleted = 0;
            for sink in s.sinks.values() {
                if let Some(ref path) = sink.path
                    && std::fs::remove_file(path).is_ok()
                {
                    deleted += 1;
                }
            }
            deleted
        });
        Ok(count)
    }

    /// Clear the console display.
    ///
    /// Clears the terminal screen, useful for resetting the display.
    /// Uses ANSI escape sequences on Unix and CMD commands on Windows.
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// logger.info("Some logs")
    /// logger.clear()  # Clears the screen
    /// logger.info("Fresh start")
    /// ```
    pub fn clear(&self) -> PyResult<()> {
        #[cfg(target_os = "windows")]
        {
            std::process::Command::new("cmd")
                .args(["/C", "cls"])
                .status()
                .map_err(|e| PyValueError::new_err(format!("Failed to clear console: {}", e)))?;
        }
        #[cfg(not(target_os = "windows"))]
        {
            print!("\x1B[2J\x1B[1;1H");
            use std::io::Write;
            std::io::stdout()
                .flush()
                .map_err(|e| PyValueError::new_err(format!("Failed to clear console: {}", e)))?;
        }
        Ok(())
    }

    /// Read log contents from a specific sink.
    ///
    /// Returns the contents of the log file associated with the given sink ID.
    /// Only works for file sinks (not console).
    ///
    /// # Arguments
    /// * `sink_id` - The handler ID of the sink to read from
    ///
    /// # Returns
    /// String containing the log file contents, or None if sink not found or is console
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// sink_id = logger.add("app.log")
    /// logger.info("Test message")
    /// logs = logger.read(sink_id)
    /// print(logs)
    /// ```
    pub fn read(&self, sink_id: usize) -> PyResult<Option<String>> {
        let content = with_state(|s| {
            if let Some(sink) = s.sinks.get(&sink_id) {
                if let Some(ref path) = sink.path {
                    std::fs::read_to_string(path).ok()
                } else {
                    None
                }
            } else {
                None
            }
        });
        Ok(content)
    }

    /// Read log contents from all file sinks.
    ///
    /// Returns a dictionary mapping sink IDs to their log file contents.
    /// Only includes file sinks (console sinks are skipped).
    ///
    /// # Returns
    /// HashMap where keys are sink IDs and values are log file contents
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// logger.add("app.log")
    /// logger.add("error.log")
    /// all_logs = logger.read_all()
    /// for sink_id, content in all_logs.items():
    ///     print(f"Sink {sink_id}: {content}")
    /// ```
    pub fn read_all(&self) -> PyResult<HashMap<usize, String>> {
        let all_contents = with_state(|s| {
            let mut contents = HashMap::new();
            for (&id, sink) in s.sinks.iter() {
                if let Some(ref path) = sink.path
                    && let Ok(content) = std::fs::read_to_string(path)
                {
                    contents.insert(id, content);
                }
            }
            contents
        });
        Ok(all_contents)
    }

    /// Get the file size of a specific sink's log file in bytes.
    ///
    /// Returns `None` if:
    /// - The sink doesn't exist
    /// - The sink is not a file sink (e.g., console sink)
    /// - The file doesn't exist yet
    ///
    /// # Arguments
    ///
    /// * `sink_id` - The unique identifier of the sink
    ///
    /// # Returns
    ///
    /// * `PyResult<Option<u64>>` - File size in bytes, or None if not found
    ///
    /// # Example
    ///
    /// ```python
    /// from logly import logger
    ///
    /// sink_id = logger.add("app.log")
    /// logger.info("Hello")
    ///
    /// size = logger.file_size(sink_id)
    /// if size:
    ///     print(f"Log file is {size} bytes")
    /// ```
    #[pyo3(signature = (sink_id))]
    pub fn file_size(&self, sink_id: usize) -> PyResult<Option<u64>> {
        let result = with_state(|s| {
            if let Some(sink) = s.sinks.get(&sink_id) {
                if let Some(path) = &sink.path {
                    match std::fs::metadata(path) {
                        Ok(metadata) => Some(metadata.len()),
                        Err(_) => None, // File doesn't exist yet
                    }
                } else {
                    None // Not a file sink
                }
            } else {
                None // Sink doesn't exist
            }
        });
        Ok(result)
    }

    /// Get file metadata for a specific sink's log file.
    ///
    /// Returns a dictionary with:
    /// - `size`: File size in bytes
    /// - `created`: Creation timestamp (ISO 8601 format)
    /// - `modified`: Last modified timestamp (ISO 8601 format)
    /// - `path`: Full file path
    ///
    /// Returns `None` if:
    /// - The sink doesn't exist
    /// - The sink is not a file sink
    /// - The file doesn't exist yet
    ///
    /// # Arguments
    ///
    /// * `sink_id` - The unique identifier of the sink
    ///
    /// # Returns
    ///
    /// * `PyResult<Option<HashMap<String, String>>>` - Metadata dictionary or None
    ///
    /// # Example
    ///
    /// ```python
    /// from logly import logger
    ///
    /// sink_id = logger.add("app.log")
    /// metadata = logger.file_metadata(sink_id)
    /// if metadata:
    ///     print(f"Size: {metadata['size']} bytes")
    ///     print(f"Created: {metadata['created']}")
    ///     print(f"Modified: {metadata['modified']}")
    /// ```
    #[pyo3(signature = (sink_id))]
    pub fn file_metadata(&self, sink_id: usize) -> PyResult<Option<HashMap<String, String>>> {
        use std::time::UNIX_EPOCH;

        let result = with_state(|s| {
            if let Some(sink) = s.sinks.get(&sink_id) {
                if let Some(path) = &sink.path {
                    match std::fs::metadata(path) {
                        Ok(metadata) => {
                            let mut result = HashMap::new();

                            // File size
                            result.insert("size".to_string(), metadata.len().to_string());

                            // File path
                            result.insert("path".to_string(), path.clone()); // Created time
                            if let Ok(created) = metadata.created()
                                && let Ok(duration) = created.duration_since(UNIX_EPOCH)
                            {
                                let datetime =
                                    chrono::DateTime::from_timestamp(duration.as_secs() as i64, 0)
                                        .unwrap_or_default();
                                result.insert("created".to_string(), datetime.to_rfc3339());
                            }

                            // Modified time
                            if let Ok(modified) = metadata.modified()
                                && let Ok(duration) = modified.duration_since(UNIX_EPOCH)
                            {
                                let datetime =
                                    chrono::DateTime::from_timestamp(duration.as_secs() as i64, 0)
                                        .unwrap_or_default();
                                result.insert("modified".to_string(), datetime.to_rfc3339());
                            }

                            Some(result)
                        }
                        Err(_) => None, // File doesn't exist yet
                    }
                } else {
                    None // Not a file sink
                }
            } else {
                None // Sink doesn't exist
            }
        });
        Ok(result)
    }

    /// Read specific lines from a sink's log file.
    ///
    /// This allows you to read a specific range of lines rather than the entire file.
    /// Line numbers are 1-indexed. Use negative indices to count from the end:
    /// - `start=-10` means "start from 10th line from the end"
    /// - `end=-1` means "end at last line"
    ///
    /// # Arguments
    ///
    /// * `sink_id` - The unique identifier of the sink
    /// * `start` - Starting line number (1-indexed, negative for end-relative)
    /// * `end` - Ending line number (inclusive, negative for end-relative)
    ///
    /// # Returns
    ///
    /// * `PyResult<Option<String>>` - Selected lines joined with newlines, or None if sink/file doesn't exist
    ///
    /// # Example
    ///
    /// ```python
    /// from logly import logger
    ///
    /// sink_id = logger.add("app.log")
    ///
    /// # Read first 10 lines
    /// lines = logger.read_lines(sink_id, 1, 10)
    ///
    /// # Read last 5 lines
    /// lines = logger.read_lines(sink_id, -5, -1)
    ///
    /// # Read lines 100-200
    /// lines = logger.read_lines(sink_id, 100, 200)
    /// ```
    #[pyo3(signature = (sink_id, start, end))]
    pub fn read_lines(&self, sink_id: usize, start: i32, end: i32) -> PyResult<Option<String>> {
        use std::io::{BufRead, BufReader};

        let result = with_state(|s| {
            if let Some(sink) = s.sinks.get(&sink_id) {
                if let Some(path) = &sink.path {
                    match std::fs::File::open(path) {
                        Ok(file) => {
                            let reader = BufReader::new(file);
                            let all_lines: Vec<String> =
                                reader.lines().map_while(Result::ok).collect();

                            let total_lines = all_lines.len() as i32;

                            // Convert negative indices to positive
                            let start_idx = if start < 0 {
                                ((total_lines + start).max(0)) as usize
                            } else {
                                ((start - 1).max(0)) as usize
                            };

                            let end_idx = if end < 0 {
                                ((total_lines + end + 1).max(0)) as usize
                            } else {
                                (end.min(total_lines)) as usize
                            };

                            if start_idx < all_lines.len() && start_idx < end_idx {
                                let selected_lines: Vec<String> =
                                    all_lines[start_idx..end_idx.min(all_lines.len())].to_vec();
                                Some(selected_lines.join("\n"))
                            } else {
                                Some(String::new())
                            }
                        }
                        Err(_) => None,
                    }
                } else {
                    None // Not a file sink
                }
            } else {
                None // Sink doesn't exist
            }
        });
        Ok(result)
    }

    /// Count the number of lines in a sink's log file.
    ///
    /// # Arguments
    ///
    /// * `sink_id` - The unique identifier of the sink
    ///
    /// # Returns
    ///
    /// * `PyResult<Option<usize>>` - Number of lines, or None if sink/file doesn't exist
    ///
    /// # Example
    ///
    /// ```python
    /// from logly import logger
    ///
    /// sink_id = logger.add("app.log")
    /// logger.info("Line 1")
    /// logger.info("Line 2")
    ///
    /// count = logger.line_count(sink_id)
    /// print(f"Log has {count} lines")
    /// ```
    #[pyo3(signature = (sink_id))]
    pub fn line_count(&self, sink_id: usize) -> PyResult<Option<usize>> {
        use std::io::{BufRead, BufReader};

        let result = with_state(|s| {
            if let Some(sink) = s.sinks.get(&sink_id) {
                if let Some(path) = &sink.path {
                    match std::fs::File::open(path) {
                        Ok(file) => {
                            let reader = BufReader::new(file);
                            let count = reader.lines().count();
                            Some(count)
                        }
                        Err(_) => None,
                    }
                } else {
                    None // Not a file sink
                }
            } else {
                None // Sink doesn't exist
            }
        });
        Ok(result)
    }

    /// Read and parse JSON log file.
    ///
    /// This method reads a JSON-formatted log file and returns it as a parsed structure.
    /// Supports both JSON array format and newline-delimited JSON (NDJSON).
    ///
    /// # Arguments
    ///
    /// * `sink_id` - The unique identifier of the sink
    /// * `pretty` - If true, returns pretty-printed JSON string
    ///
    /// # Returns
    ///
    /// * `PyResult<Option<String>>` - JSON string (pretty or compact), or None if sink/file doesn't exist
    ///
    /// # Example
    ///
    /// ```python
    /// from logly import logger
    ///
    /// sink_id = logger.add("app.log", format="json")
    /// logger.info("Test message")
    ///
    /// # Get compact JSON
    /// json_logs = logger.read_json(sink_id)
    ///
    /// # Get pretty-printed JSON
    /// pretty_logs = logger.read_json(sink_id, pretty=True)
    /// ```
    #[pyo3(signature = (sink_id, pretty=false))]
    pub fn read_json(&self, sink_id: usize, pretty: bool) -> PyResult<Option<String>> {
        use std::io::{BufRead, BufReader};

        let result = with_state(|s| {
            if let Some(sink) = s.sinks.get(&sink_id) {
                if let Some(path) = &sink.path {
                    match std::fs::File::open(path) {
                        Ok(file) => {
                            let reader = BufReader::new(file);
                            let lines: Vec<String> = reader.lines().map_while(Result::ok).collect();

                            // Try to parse as JSON array first, then as NDJSON
                            let full_content = lines.join("\n");

                            // Try parsing the entire content as JSON array
                            if let Ok(parsed) =
                                serde_json::from_str::<serde_json::Value>(&full_content)
                            {
                                if pretty {
                                    Some(
                                        serde_json::to_string_pretty(&parsed)
                                            .unwrap_or(full_content),
                                    )
                                } else {
                                    Some(serde_json::to_string(&parsed).unwrap_or(full_content))
                                }
                            } else {
                                // Try NDJSON format (each line is a JSON object)
                                let mut json_objects = Vec::new();
                                for line in &lines {
                                    if let Ok(obj) = serde_json::from_str::<serde_json::Value>(line)
                                    {
                                        json_objects.push(obj);
                                    }
                                }

                                if !json_objects.is_empty() {
                                    let array = serde_json::Value::Array(json_objects);
                                    if pretty {
                                        Some(
                                            serde_json::to_string_pretty(&array)
                                                .unwrap_or(full_content),
                                        )
                                    } else {
                                        Some(serde_json::to_string(&array).unwrap_or(full_content))
                                    }
                                } else {
                                    // Not valid JSON, return as-is
                                    Some(full_content)
                                }
                            }
                        }
                        Err(_) => None,
                    }
                } else {
                    None // Not a file sink
                }
            } else {
                None // Sink doesn't exist
            }
        });
        Ok(result)
    }

    // Extra conveniences for tests and control
    /// Reset internal state for testing purposes.
    ///
    /// WARNING: This is for internal testing only and should not be used
    /// in production code. It does not reset the global tracing subscriber.
    pub fn _reset_for_tests(&self) {
        crate::config::state::reset_state();
    }

    /// Enable a specific sink by its handler ID.
    ///
    /// When a sink is enabled, log messages will be written to it.
    /// Sinks are enabled by default when created.
    ///
    /// # Arguments
    /// * `sink_id` - The handler ID of the sink to enable
    ///
    /// # Returns
    /// `true` if the sink was found and enabled, `false` if not found
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// sink_id = logger.add("app.log")
    /// logger.disable_sink(sink_id)
    /// logger.info("Not logged")  # Sink disabled
    /// logger.enable_sink(sink_id)
    /// logger.info("Logged")  # Sink re-enabled
    /// ```
    pub fn enable_sink(&self, sink_id: usize) -> PyResult<bool> {
        let enabled = with_state(|s| {
            if let Some(sink) = s.sinks.get_mut(&sink_id) {
                sink.enabled = true;
                true
            } else {
                false
            }
        });
        Ok(enabled)
    }

    /// Disable a specific sink by its handler ID.
    ///
    /// When a sink is disabled, log messages will not be written to it,
    /// but the sink remains registered and can be re-enabled later.
    ///
    /// # Arguments
    /// * `sink_id` - The handler ID of the sink to disable
    ///
    /// # Returns
    /// `true` if the sink was found and disabled, `false` if not found
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// sink_id = logger.add("app.log")
    /// logger.disable_sink(sink_id)
    /// logger.info("Not logged")  # Sink disabled
    /// ```
    pub fn disable_sink(&self, sink_id: usize) -> PyResult<bool> {
        let disabled = with_state(|s| {
            if let Some(sink) = s.sinks.get_mut(&sink_id) {
                sink.enabled = false;
                true
            } else {
                false
            }
        });
        Ok(disabled)
    }

    /// Check if a specific sink is enabled.
    ///
    /// # Arguments
    /// * `sink_id` - The handler ID of the sink to check
    ///
    /// # Returns
    /// `Some(true)` if enabled, `Some(false)` if disabled, `None` if not found
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    /// sink_id = logger.add("app.log")
    /// enabled = logger.is_sink_enabled(sink_id)  # Returns True
    /// logger.disable_sink(sink_id)
    /// enabled = logger.is_sink_enabled(sink_id)  # Returns False
    /// ```
    pub fn is_sink_enabled(&self, sink_id: usize) -> PyResult<Option<bool>> {
        let enabled = with_state(|s| s.sinks.get(&sink_id).map(|sink| sink.enabled));
        Ok(enabled)
    }

    /// Search a sink's log file for a pattern with advanced options.
    ///
    /// This is the Rust-powered search implementation providing high performance
    /// and advanced features like regex, filtering, and context lines.
    ///
    /// # Arguments
    /// * `sink_id` - The handler ID of the sink whose log file to search
    /// * `pattern` - The string or regex pattern to search for
    /// * `case_sensitive` - Perform case-sensitive matching (default: false)
    /// * `first_only` - Return only the first match (default: false)
    /// * `use_regex` - Treat pattern as regular expression (default: false)
    /// * `start_line` - Start searching from this line number (1-indexed)
    /// * `end_line` - Stop searching at this line number (inclusive)
    /// * `max_results` - Maximum number of results to return
    /// * `context_before` - Number of context lines before each match
    /// * `context_after` - Number of context lines after each match
    /// * `level_filter` - Only search lines containing this log level
    /// * `invert_match` - Return lines that DON'T match (like grep -v)
    ///
    /// # Returns
    /// List of dictionaries with:
    /// - `line`: Line number (1-indexed)
    /// - `content`: Full line content
    /// - `match`: The matched text
    /// - `context_before`: Lines before match (if requested)
    /// - `context_after`: Lines after match (if requested)
    ///
    /// Returns None if sink not found or file doesn't exist.
    ///
    /// # Example
    /// ```python
    /// from logly import logger
    ///
    /// sink_id = logger.add("app.log")
    /// logger.error("Connection failed")
    /// logger.info("Retrying...")
    /// logger.complete()
    ///
    /// # Basic search
    /// results = logger.search_log(sink_id, "error")
    ///
    /// # Case-sensitive search
    /// results = logger.search_log(sink_id, "ERROR", case_sensitive=True)
    ///
    /// # Regex search for error codes
    /// results = logger.search_log(sink_id, r"error:\s+\d+", use_regex=True)
    ///
    /// # Search with context lines
    /// results = logger.search_log(sink_id, "failed", context_before=2, context_after=2)
    ///
    /// # Filter by log level
    /// results = logger.search_log(sink_id, "timeout", level_filter="ERROR")
    ///
    /// # Find lines that don't contain pattern
    /// results = logger.search_log(sink_id, "success", invert_match=True)
    /// ```
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (
        sink_id,
        pattern,
        *,
        case_sensitive=false,
        first_only=false,
        use_regex=false,
        start_line=None,
        end_line=None,
        max_results=None,
        context_before=None,
        context_after=None,
        level_filter=None,
        invert_match=false
    ))]
    pub fn search_log<'py>(
        &self,
        py: Python<'py>,
        sink_id: usize,
        pattern: &str,
        case_sensitive: bool,
        first_only: bool,
        use_regex: bool,
        start_line: Option<usize>,
        end_line: Option<usize>,
        max_results: Option<usize>,
        context_before: Option<usize>,
        context_after: Option<usize>,
        level_filter: Option<String>,
        invert_match: bool,
    ) -> PyResult<Option<Bound<'py, PyList>>> {
        // Flush pending writes first
        self.complete();

        // Get file path from sink
        let file_path = with_state(|s| s.sinks.get(&sink_id).and_then(|sink| sink.path.clone()));

        let Some(path) = file_path else {
            return Ok(None); // Sink not found or no file path
        };

        // Build search options
        let options = backend::SearchOptions {
            case_sensitive,
            first_only,
            use_regex,
            start_line,
            end_line,
            max_results,
            context_before,
            context_after,
            level_filter,
            invert_match,
        };

        // Perform search in Rust
        match backend::search_file(&path, pattern, &options) {
            Ok(results) => {
                // Convert Rust results to Python list of dicts
                let py_list = PyList::empty(py);

                for result in results {
                    let dict = PyDict::new(py);
                    dict.set_item("line", result.line_number)?;
                    dict.set_item("content", result.content)?;
                    dict.set_item("match", result.matched_text)?;

                    if !result.context_before.is_empty() {
                        dict.set_item("context_before", result.context_before)?;
                    }

                    if !result.context_after.is_empty() {
                        dict.set_item("context_after", result.context_after)?;
                    }

                    py_list.append(dict)?;
                }

                Ok(Some(py_list))
            }
            Err(_) => Ok(None), // File read error
        }
    }
}
