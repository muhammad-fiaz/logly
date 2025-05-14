use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple, PyString};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use std::fs::{self, File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;
use parking_lot::RwLock;
use chrono::Local;
use colored::{Colorize, ColoredString};
use serde::{Serialize, Deserialize};
use thiserror::Error;
use once_cell::sync::Lazy;
use std::collections::HashMap;
use regex::Regex;

// Error types
#[derive(Error, Debug)]
pub enum LoglyError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),
    #[error("Failed to initialize logger: {0}")]
    Initialization(String),
    #[error("Invalid log level: {0}")]
    InvalidLogLevel(String),
    #[error("JSON serialization error: {0}")]
    Json(#[from] serde_json::Error),
}

// Convert LoglyError to PyErr
impl From<LoglyError> for PyErr {
    fn from(err: LoglyError) -> PyErr {
        PyRuntimeError::new_err(err.to_string())
    }
}

// Log levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[pyclass]
pub enum LogLevel {
    DEBUG = 10,
    INFO = 20,
    WARNING = 30,
    ERROR = 40,
    CRITICAL = 50,
}

impl LogLevel {
    fn as_str(&self) -> &'static str {
        match self {
            LogLevel::DEBUG => "DEBUG",
            LogLevel::INFO => "INFO",
            LogLevel::WARNING => "WARNING",
            LogLevel::ERROR => "ERROR",
            LogLevel::CRITICAL => "CRITICAL",
        }
    }

    #[allow(dead_code)]
    fn color(&self) -> ColoredString {
        match self {
            LogLevel::DEBUG => self.as_str().bright_blue(),
            LogLevel::INFO => self.as_str().bright_green(),
            LogLevel::WARNING => self.as_str().bright_yellow(),
            LogLevel::ERROR => self.as_str().bright_red(),
            LogLevel::CRITICAL => self.as_str().on_red().white(),
        }
    }

    fn from_int(level: i32) -> Result<Self, LoglyError> {
        match level {
            10 => Ok(LogLevel::DEBUG),
            20 => Ok(LogLevel::INFO),
            30 => Ok(LogLevel::WARNING),
            40 => Ok(LogLevel::ERROR),
            50 => Ok(LogLevel::CRITICAL),
            _ => Err(LoglyError::InvalidLogLevel(format!("Invalid log level: {}", level))),
        }
    }
}

// Log record structure
#[derive(Debug, Clone, Serialize, Deserialize)]
struct LogRecord {
    timestamp: String,
    level: LogLevel,
    message: String,
    file: Option<String>,
    line: Option<u32>,
    function: Option<String>,
    // URLs found in the message
    urls: Option<Vec<String>>,
}

// Logger configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
struct LoggerConfig {
    enabled: bool,
    level: LogLevel,
    file_path: Option<PathBuf>,
    max_file_size: Option<u64>,  // in bytes
    max_backup_count: Option<usize>,
    colored_output: bool,
    format: String,
    debug_config: bool,  // Whether to print debug messages for configuration changes
    append_to_file: bool,  // Whether to append to existing log file or overwrite
    use_datetime_in_filename: bool,  // Whether to include date and time in rotated filenames
    use_date_in_filename: bool,  // Whether to include date in rotated filenames
    use_time_in_filename: bool,  // Whether to include time in rotated filenames
    show_timestamp: bool,  // Whether to show timestamp in log messages
    show_level: bool,  // Whether to show log level in log messages
    show_message: bool,  // Whether to show message in log messages
}

impl Default for LoggerConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            level: LogLevel::INFO,
            file_path: None,
            max_file_size: Some(10 * 1024 * 1024),  // 10MB
            max_backup_count: Some(5),
            colored_output: true,
            format: "{timestamp} [{level}] {message}".to_string(),
            debug_config: false,  // Don't print debug messages for configuration changes by default
            append_to_file: true,  // Append to existing log file by default
            use_datetime_in_filename: true,  // Include date and time in rotated filenames by default
            use_date_in_filename: true,  // Include date in rotated filenames by default
            use_time_in_filename: true,  // Include time in rotated filenames by default
            show_timestamp: true,  // Show timestamp in log messages by default
            show_level: true,  // Show log level in log messages by default
            show_message: true,  // Show message in log messages by default
        }
    }
}

// Logger implementation
struct LoggerImpl {
    config: RwLock<LoggerConfig>,
    file: RwLock<Option<File>>,
    current_file_size: RwLock<u64>,
}

impl LoggerImpl {
    fn new(config: LoggerConfig) -> Result<Self, LoglyError> {
        let file = if let Some(path) = &config.file_path {
            // Create directory if it doesn't exist
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent)?;
            }

            // Open or create log file based on append_to_file setting
            let mut options = OpenOptions::new();
            options.create(true);

            if config.append_to_file {
                options.append(true);
            } else {
                options.write(true).truncate(true);
            }

            let file = options.open(path)?;

            // Get current file size
            let metadata = file.metadata()?;
            let _file_size = metadata.len();

            Some(file)
        } else {
            None
        };

        Ok(Self {
            config: RwLock::new(config),
            file: RwLock::new(file),
            current_file_size: RwLock::new(0),
        })
    }

    fn is_enabled(&self) -> bool {
        self.config.read().enabled
    }

    fn set_enabled(&self, enabled: bool) {
        self.config.write().enabled = enabled;
    }

    fn get_level(&self) -> LogLevel {
        self.config.read().level
    }

    fn set_level(&self, level: LogLevel) {
        self.config.write().level = level;
    }

    fn should_log(&self, level: LogLevel) -> bool {
        let config = self.config.read();
        config.enabled && level >= config.level
    }

    fn format_record(&self, record: &LogRecord, custom_format: Option<&str>) -> String {
        // Use custom format if provided, otherwise use the global format
        let format_str = if let Some(fmt) = custom_format {
            fmt.to_string()
        } else {
            self.config.read().format.clone()
        };

        let mut result = format_str;
        let config = self.config.read();

        // Replace placeholders with actual values based on display options
        if config.show_timestamp {
            result = result.replace("{timestamp}", &record.timestamp);
        } else {
            result = result.replace("{timestamp}", "");
        }

        if config.show_level {
            result = result.replace("{level}", record.level.as_str());
        } else {
            result = result.replace("{level}", "");
        }

        // Process message for URLs
        let message = if config.show_message {
            // Simple URL detection and formatting for clickable links
            let url_regex = regex::Regex::new(r"(https?://[^\s]+)").unwrap();
            let message_with_clickable_urls = url_regex.replace_all(&record.message, |caps: &regex::Captures| {
                let url = &caps[1];
                // Format URL to be clickable in console/IDE
                format!("\x1B]8;;{}\x1B\\{}\x1B]8;;\x1B\\", url, url)
            });
            message_with_clickable_urls.to_string()
        } else {
            "".to_string()
        };

        result = result.replace("{message}", &message);

        // Check if we have any context information
        let has_file = record.file.is_some();
        let has_line = record.line.is_some();
        let has_function = record.function.is_some();

        // If we have any context information, replace the placeholders with actual values
        if has_file || has_line || has_function {
            if let Some(file) = &record.file {
                // Format file path to be clickable in IDE
                // Format: file://path/to/file:line
                let clickable_file = if let Some(line) = record.line {
                    // Make the file path clickable with line number
                    format!("\x1B]8;;file://{file}:{line}\x1B\\{file}:{line}\x1B]8;;\x1B\\")
                } else {
                    // Make just the file path clickable
                    format!("\x1B]8;;file://{file}\x1B\\{file}\x1B]8;;\x1B\\")
                };
                result = result.replace("{file}", &clickable_file);
            } else {
                result = result.replace("{file}", "");
            }

            if let Some(line) = record.line {
                result = result.replace("{line}", &line.to_string());
            } else {
                result = result.replace("{line}", "");
            }

            if let Some(function) = &record.function {
                result = result.replace("{function}", function);
            } else {
                result = result.replace("{function}", "");
            }
        } else {
            // If we don't have any context information, remove the entire parenthetical expression
            // This assumes the format is something like "... ({file}:{line} - {function})"
            if result.contains("({file}:{line} - {function})") {
                result = result.replace(" ({file}:{line} - {function})", "");
            } else {
                // Otherwise, just replace the placeholders with empty strings
                result = result.replace("{file}", "");
                result = result.replace("{line}", "");
                result = result.replace("{function}", "");
            }
        }

        // Clean up any empty brackets that might be left
        result = result.replace("[]", "");

        // Clean up multiple spaces
        while result.contains("  ") {
            result = result.replace("  ", " ");
        }

        // Clean up leading/trailing spaces
        result = result.trim().to_string();

        result
    }

    fn log(&self, level: LogLevel, message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> Result<(), LoglyError> {
        if self.config.read().debug_config {
            println!("Log: level={:?}, message={}, should_log={}", level, message, self.should_log(level));
        }
        if !self.should_log(level) {
            if self.config.read().debug_config {
                println!("Log: skipping message due to log level");
            }
            return Ok(());
        }

        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f").to_string();

        let record = LogRecord {
            timestamp,
            level,
            message: message.to_string(),
            file: file.map(String::from),
            line,
            function: function.map(String::from),
        };

        let formatted = self.format_record(&record, format);
        if self.config.read().debug_config {
            println!("Log: formatted message: {}", formatted);
        }

        // Log to console
        if self.config.read().colored_output {
            // Apply custom color if provided, otherwise use default color for the level
            if let Some(custom_color) = color {
                match custom_color.to_lowercase().as_str() {
                    "red" => println!("{}", formatted.bright_red()),
                    "green" => println!("{}", formatted.bright_green()),
                    "blue" => println!("{}", formatted.bright_blue()),
                    "yellow" => println!("{}", formatted.bright_yellow()),
                    "magenta" => println!("{}", formatted.bright_magenta()),
                    "cyan" => println!("{}", formatted.bright_cyan()),
                    "white" => println!("{}", formatted.bright_white()),
                    "black" => println!("{}", formatted.black()),
                    _ => {
                        // If color is not recognized, use default color for the level
                        match level {
                            LogLevel::DEBUG => println!("{}", formatted.bright_blue()),
                            LogLevel::INFO => println!("{}", formatted.bright_green()),
                            LogLevel::WARNING => println!("{}", formatted.bright_yellow()),
                            LogLevel::ERROR => println!("{}", formatted.bright_red()),
                            LogLevel::CRITICAL => println!("{}", formatted.on_red().white()),
                        }
                    }
                }
            } else {
                // Use default color for the level
                match level {
                    LogLevel::DEBUG => println!("{}", formatted.bright_blue()),
                    LogLevel::INFO => println!("{}", formatted.bright_green()),
                    LogLevel::WARNING => println!("{}", formatted.bright_yellow()),
                    LogLevel::ERROR => println!("{}", formatted.bright_red()),
                    LogLevel::CRITICAL => println!("{}", formatted.on_red().white()),
                }
            }
        } else {
            println!("{}", formatted);
        }

        // Log to file if configured
        if let Some(file_path) = &self.config.read().file_path {
            if self.config.read().debug_config {
                println!("Log: writing to file: {}", file_path.display());
            }
            let mut file_guard = self.file.write();

            // Check if we need to rotate the log file
            if let (Some(max_size), Some(_file)) = (self.config.read().max_file_size, file_guard.as_ref()) {
                let mut current_size = self.current_file_size.write();
                *current_size += formatted.len() as u64 + 1; // +1 for newline
                if self.config.read().debug_config {
                    println!("Log: current file size: {}, max size: {}", *current_size, max_size);
                }

                if *current_size >= max_size {
                    if self.config.read().debug_config {
                        println!("Log: rotating log files");
                    }
                    // Rotate log files
                    self.rotate_logs(file_path)?;

                    // Reset file and size
                    *file_guard = Some(OpenOptions::new()
                        .create(true)
                        .append(true)
                        .open(file_path)?);
                    *current_size = 0;
                }
            }

            // Write to file
            if let Some(file) = file_guard.as_mut() {
                if self.config.read().debug_config {
                    println!("Log: writing to file");
                }
                writeln!(file, "{}", formatted)?;
                file.flush()?;
                if self.config.read().debug_config {
                    println!("Log: successfully wrote to file");
                }
            } else {
                if self.config.read().debug_config {
                    println!("Log: file is None, cannot write");
                }
            }
        } else {
            if self.config.read().debug_config {
                println!("Log: no file_path configured");
            }
        }

        Ok(())
    }

    fn rotate_logs(&self, log_path: &Path) -> Result<(), LoglyError> {
        let config = self.config.read();
        let max_backups = config.max_backup_count.unwrap_or(5);

        // Generate timestamp for filename if needed
        let now = Local::now();
        let date_str = now.format("%Y-%m-%d").to_string();
        let time_str = now.format("%H%M%S").to_string();

        // Get the base name and extension of the log file
        let file_stem = log_path.file_stem()
            .and_then(|s| s.to_str())
            .unwrap_or("log");
        let extension = log_path.extension()
            .and_then(|s| s.to_str())
            .unwrap_or("log");

        // Function to generate backup filename based on config
        let generate_backup_name = |index: Option<usize>| -> String {
            let mut parts = Vec::new();
            parts.push(file_stem.to_string());

            // Add date if configured
            if config.use_date_in_filename && config.use_datetime_in_filename {
                parts.push(date_str.clone());
            }

            // Add time if configured
            if config.use_time_in_filename && config.use_datetime_in_filename {
                parts.push(time_str.clone());
            }

            // Add index if provided
            if let Some(idx) = index {
                parts.push(idx.to_string());
            }

            // Join parts with hyphens and add extension
            format!("{}.{}", parts.join("-"), extension)
        };

        // Remove oldest backup if we've reached the limit
        if max_backups > 0 {
            // Check if we're using datetime in filenames
            if config.use_datetime_in_filename {
                // With datetime, we don't need to shift files, just remove old ones
                // This would require listing directory and sorting by date, which is complex
                // For simplicity, we'll just keep adding new datetime-based files
                // and implement a cleanup mechanism to remove files exceeding max_backups
                let parent_dir = log_path.parent().unwrap_or(Path::new("."));

                // List all log files in the directory
                if let Ok(entries) = fs::read_dir(parent_dir) {
                    let mut log_files = Vec::new();

                    for entry in entries.filter_map(Result::ok) {
                        let path = entry.path();
                        if path.is_file() && 
                           path.extension().and_then(|s| s.to_str()) == Some(extension) &&
                           path.file_stem().and_then(|s| s.to_str()).map_or(false, |s| s.starts_with(file_stem)) {
                            log_files.push(path);
                        }
                    }

                    // Sort by modification time (oldest first)
                    log_files.sort_by(|a, b| {
                        let a_time = fs::metadata(a).and_then(|m| m.modified()).unwrap_or_else(|_| std::time::SystemTime::now());
                        let b_time = fs::metadata(b).and_then(|m| m.modified()).unwrap_or_else(|_| std::time::SystemTime::now());
                        a_time.cmp(&b_time)
                    });

                    // Remove oldest files if we have more than max_backups
                    while log_files.len() >= max_backups {
                        if let Some(oldest) = log_files.first() {
                            let _ = fs::remove_file(oldest); // Ignore errors
                            log_files.remove(0);
                        } else {
                            break;
                        }
                    }
                }
            } else {
                // Traditional numbered backup approach
                let backup_path = format!("{}.{}", log_path.display(), max_backups);
                let _ = fs::remove_file(backup_path); // Ignore errors if file doesn't exist

                // Shift existing backups
                for i in (1..max_backups).rev() {
                    let src = format!("{}.{}", log_path.display(), i);
                    let dst = format!("{}.{}", log_path.display(), i + 1);
                    if Path::new(&src).exists() {
                        fs::rename(src, dst)?;
                    }
                }
            }
        }

        // Create new backup filename
        let backup_path = if config.use_datetime_in_filename {
            // Use date/time in filename
            let parent_dir = log_path.parent().unwrap_or(Path::new("."));
            let backup_name = generate_backup_name(None);
            parent_dir.join(backup_name)
        } else {
            // Use traditional numbered backup
            let backup = format!("{}.1", log_path.display());
            PathBuf::from(backup)
        };

        // Rename current log file to backup
        if max_backups > 0 {
            fs::rename(log_path, backup_path)?;
        } else {
            // If no backups are kept, just remove the file
            fs::remove_file(log_path)?;
        }

        Ok(())
    }

    fn update_config(&self, config: LoggerConfig) -> Result<(), LoglyError> {
        if config.debug_config {
            println!("UpdateConfig: received config with level={:?}, file_path={:?}", config.level, config.file_path);
            println!("UpdateConfig: current config has level={:?}, file_path={:?}", self.config.read().level, self.config.read().file_path);
        }

        // Update file if path changed
        if self.config.read().file_path != config.file_path {
            if config.debug_config {
                println!("UpdateConfig: file path changed, updating file");
            }
            let mut file_guard = self.file.write();
            *file_guard = if let Some(path) = &config.file_path {
                if config.debug_config {
                    println!("UpdateConfig: opening file at path: {:?}", path);
                }
                // Create directory if it doesn't exist
                if let Some(parent) = path.parent() {
                    if config.debug_config {
                        println!("UpdateConfig: creating parent directory: {:?}", parent);
                    }
                    fs::create_dir_all(parent)?;
                }

                // Open or create log file based on append_to_file setting
                let mut options = OpenOptions::new();
                options.create(true);

                if config.append_to_file {
                    options.append(true);
                } else {
                    options.write(true).truncate(true);
                }

                let file = options.open(path)?;

                if config.debug_config {
                    println!("UpdateConfig: file opened successfully");
                }
                Some(file)
            } else {
                if config.debug_config {
                    println!("UpdateConfig: no file path provided, setting file to None");
                }
                None
            };

            // Reset file size counter
            *self.current_file_size.write() = 0;
            if config.debug_config {
                println!("UpdateConfig: reset file size counter");
            }
        } else if config.debug_config {
            println!("UpdateConfig: file path unchanged");
        }

        // Update config
        *self.config.write() = config;
        if self.config.read().debug_config {
            println!("UpdateConfig: config updated, new level={:?}, file_path={:?}", self.config.read().level, self.config.read().file_path);
        }

        Ok(())
    }
}

// Python-facing Logger class
#[pyclass]
struct Logger {
    inner: Arc<LoggerImpl>,
}

#[pymethods]
impl Logger {
    #[new]
    fn new() -> PyResult<Self> {
        let inner = get_global_logger()?;
        Ok(Self { inner })
    }

    #[staticmethod]
    fn init(_py: Python<'_>, config: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let logger = get_global_logger()?;
        let mut logger_config = logger.config.read().clone();

        if let Some(config_dict) = config {
            // Parse configuration from Python dict
            if let Some(enabled) = config_dict.get_item("enabled")? {
                logger_config.enabled = enabled.extract()?;
            }

            if let Some(debug_config) = config_dict.get_item("debug_config")? {
                logger_config.debug_config = debug_config.extract()?;
            }

            if let Some(level) = config_dict.get_item("level")? {
                if let Ok(level_str) = level.extract::<String>() {
                    logger_config.level = match level_str.to_uppercase().as_str() {
                        "DEBUG" => LogLevel::DEBUG,
                        "INFO" => LogLevel::INFO,
                        "WARNING" => LogLevel::WARNING,
                        "ERROR" => LogLevel::ERROR,
                        "CRITICAL" => LogLevel::CRITICAL,
                        _ => return Err(PyRuntimeError::new_err(format!("Invalid log level: {}", level_str))),
                    };
                } else if let Ok(level_int) = level.extract::<i32>() {
                    logger_config.level = LogLevel::from_int(level_int)?;
                }
            }

            if let Some(file_path) = config_dict.get_item("file_path")? {
                logger_config.file_path = Some(PathBuf::from(file_path.extract::<String>()?));
            }

            if let Some(max_file_size) = config_dict.get_item("max_file_size")? {
                logger_config.max_file_size = Some(max_file_size.extract::<u64>()?);
            }

            if let Some(max_backup_count) = config_dict.get_item("max_backup_count")? {
                logger_config.max_backup_count = Some(max_backup_count.extract::<usize>()?);
            }

            if let Some(colored_output) = config_dict.get_item("colored_output")? {
                logger_config.colored_output = colored_output.extract()?;
            }

            if let Some(format) = config_dict.get_item("format")? {
                logger_config.format = format.extract::<String>()?;
            }

            // New configuration options
            if let Some(append_to_file) = config_dict.get_item("append_to_file")? {
                logger_config.append_to_file = append_to_file.extract()?;
            }

            if let Some(use_datetime_in_filename) = config_dict.get_item("use_datetime_in_filename")? {
                logger_config.use_datetime_in_filename = use_datetime_in_filename.extract()?;
            }

            if let Some(use_date_in_filename) = config_dict.get_item("use_date_in_filename")? {
                logger_config.use_date_in_filename = use_date_in_filename.extract()?;
            }

            if let Some(use_time_in_filename) = config_dict.get_item("use_time_in_filename")? {
                logger_config.use_time_in_filename = use_time_in_filename.extract()?;
            }

            if let Some(show_timestamp) = config_dict.get_item("show_timestamp")? {
                logger_config.show_timestamp = show_timestamp.extract()?;
            }

            if let Some(show_level) = config_dict.get_item("show_level")? {
                logger_config.show_level = show_level.extract()?;
            }

            if let Some(show_message) = config_dict.get_item("show_message")? {
                logger_config.show_message = show_message.extract()?;
            }
        }

        // Update the global logger's configuration
        logger.update_config(logger_config)?;

        // Return a new Logger instance that uses the global logger
        Ok(Self { inner: logger })
    }

    #[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
    fn debug(&self, message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
        self.inner.log(LogLevel::DEBUG, message, file, line, function, format, color)?;
        Ok(())
    }

    #[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
    fn info(&self, message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
        self.inner.log(LogLevel::INFO, message, file, line, function, format, color)?;
        Ok(())
    }

    #[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
    fn warning(&self, message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
        self.inner.log(LogLevel::WARNING, message, file, line, function, format, color)?;
        Ok(())
    }

    #[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
    fn error(&self, message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
        self.inner.log(LogLevel::ERROR, message, file, line, function, format, color)?;
        Ok(())
    }

    #[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
    fn critical(&self, message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
        self.inner.log(LogLevel::CRITICAL, message, file, line, function, format, color)?;
        Ok(())
    }

    #[pyo3(signature = (level, message, file=None, line=None, function=None, format=None, color=None))]
    fn log(&self, level: &Bound<'_, PyAny>, message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
        let level = if let Ok(level_int) = level.extract::<i32>() {
            LogLevel::from_int(level_int)?
        } else if let Ok(level_str) = level.extract::<String>() {
            match level_str.to_uppercase().as_str() {
                "DEBUG" => LogLevel::DEBUG,
                "INFO" => LogLevel::INFO,
                "WARNING" => LogLevel::WARNING,
                "ERROR" => LogLevel::ERROR,
                "CRITICAL" => LogLevel::CRITICAL,
                _ => return Err(PyRuntimeError::new_err(format!("Invalid log level: {}", level_str))),
            }
        } else {
            return Err(PyRuntimeError::new_err("Invalid log level type"));
        };

        self.inner.log(level, message, file, line, function, format, color)?;
        Ok(())
    }

    fn set_level(&self, level: &Bound<'_, PyAny>) -> PyResult<()> {
        let level = if let Ok(level_int) = level.extract::<i32>() {
            LogLevel::from_int(level_int)?
        } else if let Ok(level_str) = level.extract::<String>() {
            match level_str.to_uppercase().as_str() {
                "DEBUG" => LogLevel::DEBUG,
                "INFO" => LogLevel::INFO,
                "WARNING" => LogLevel::WARNING,
                "ERROR" => LogLevel::ERROR,
                "CRITICAL" => LogLevel::CRITICAL,
                _ => return Err(PyRuntimeError::new_err(format!("Invalid log level: {}", level_str))),
            }
        } else {
            return Err(PyRuntimeError::new_err("Invalid log level type"));
        };

        self.inner.set_level(level);
        Ok(())
    }

    fn get_level(&self) -> i32 {
        self.inner.get_level() as i32
    }

    fn enable(&self) {
        self.inner.set_enabled(true);
    }

    fn disable(&self) {
        self.inner.set_enabled(false);
    }

    fn is_enabled(&self) -> bool {
        self.inner.is_enabled()
    }

    #[pyo3(signature = (*, level=None, file_path=None, max_file_size=None, max_backup_count=None, colored_output=None, format=None, enabled=None, debug_config=None, append_to_file=None, use_datetime_in_filename=None, use_date_in_filename=None, use_time_in_filename=None, show_timestamp=None, show_level=None, show_message=None))]
    fn configure(
        &self,
        _py: Python<'_>,
        level: Option<&Bound<'_, PyAny>>,
        file_path: Option<&str>,
        max_file_size: Option<u64>,
        max_backup_count: Option<usize>,
        colored_output: Option<bool>,
        format: Option<&str>,
        enabled: Option<bool>,
        debug_config: Option<bool>,
        append_to_file: Option<bool>,
        use_datetime_in_filename: Option<bool>,
        use_date_in_filename: Option<bool>,
        use_time_in_filename: Option<bool>,
        show_timestamp: Option<bool>,
        show_level: Option<bool>,
        show_message: Option<bool>,
    ) -> PyResult<()> {
        let mut logger_config = self.inner.config.read().clone();

        // Update configuration based on provided parameters
        if let Some(enabled_val) = enabled {
            logger_config.enabled = enabled_val;
        }

        if let Some(debug_val) = debug_config {
            logger_config.debug_config = debug_val;
        }

        if let Some(level_val) = level {
            if let Ok(level_int) = level_val.extract::<i32>() {
                logger_config.level = LogLevel::from_int(level_int)?;
            } else if let Ok(level_str) = level_val.extract::<String>() {
                logger_config.level = match level_str.to_uppercase().as_str() {
                    "DEBUG" => LogLevel::DEBUG,
                    "INFO" => LogLevel::INFO,
                    "WARNING" => LogLevel::WARNING,
                    "ERROR" => LogLevel::ERROR,
                    "CRITICAL" => LogLevel::CRITICAL,
                    _ => return Err(PyRuntimeError::new_err(format!("Invalid log level: {}", level_str))),
                };
            } else {
                return Err(PyRuntimeError::new_err("Invalid log level type"));
            }
        }

        if let Some(path) = file_path {
            logger_config.file_path = Some(PathBuf::from(path));
        }

        if let Some(size) = max_file_size {
            logger_config.max_file_size = Some(size);
        }

        if let Some(count) = max_backup_count {
            logger_config.max_backup_count = Some(count);
        }

        if let Some(colored) = colored_output {
            logger_config.colored_output = colored;
        }

        if let Some(fmt) = format {
            logger_config.format = fmt.to_string();
        }

        // New configuration options
        if let Some(append) = append_to_file {
            logger_config.append_to_file = append;
        }

        if let Some(use_datetime) = use_datetime_in_filename {
            logger_config.use_datetime_in_filename = use_datetime;
        }

        if let Some(use_date) = use_date_in_filename {
            logger_config.use_date_in_filename = use_date;
        }

        if let Some(use_time) = use_time_in_filename {
            logger_config.use_time_in_filename = use_time;
        }

        if let Some(show_ts) = show_timestamp {
            logger_config.show_timestamp = show_ts;
        }

        if let Some(show_lvl) = show_level {
            logger_config.show_level = show_lvl;
        }

        if let Some(show_msg) = show_message {
            logger_config.show_message = show_msg;
        }

        self.inner.update_config(logger_config)?;
        Ok(())
    }

    // Method to support structured logging (JSON)
    fn json(&self, py: Python<'_>, level: &Bound<'_, PyAny>, data: &Bound<'_, PyDict>) -> PyResult<()> {
        let level = if let Ok(level_int) = level.extract::<i32>() {
            LogLevel::from_int(level_int)?
        } else if let Ok(level_str) = level.extract::<String>() {
            match level_str.to_uppercase().as_str() {
                "DEBUG" => LogLevel::DEBUG,
                "INFO" => LogLevel::INFO,
                "WARNING" => LogLevel::WARNING,
                "ERROR" => LogLevel::ERROR,
                "CRITICAL" => LogLevel::CRITICAL,
                _ => return Err(PyRuntimeError::new_err(format!("Invalid log level: {}", level_str))),
            }
        } else {
            return Err(PyRuntimeError::new_err("Invalid log level type"));
        };

        // Convert PyDict to JSON string
        let py_json = py.import("json")?;
        let json_str = py_json.getattr("dumps")?.call1((data,))?.extract::<String>()?;

        self.inner.log(level, &json_str, None, None, None, None, None)?;
        Ok(())
    }
}

// Create a default global logger instance using thread-safe lazy initialization
static GLOBAL_LOGGER: Lazy<Result<Arc<LoggerImpl>, LoglyError>> = Lazy::new(|| {
    let config = LoggerConfig::default();
    Ok(Arc::new(LoggerImpl::new(config)?))
});

fn get_global_logger() -> Result<Arc<LoggerImpl>, LoglyError> {
    match &*GLOBAL_LOGGER {
        Ok(logger) => Ok(logger.clone()),
        Err(e) => Err(LoglyError::Initialization(e.to_string())),
    }
}

// Global logger functions exposed to Python
#[pyfunction]
#[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
fn debug(message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
    let logger = get_global_logger()?;
    logger.log(LogLevel::DEBUG, message, file, line, function, format, color)?;
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
fn info(message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
    let logger = get_global_logger()?;
    logger.log(LogLevel::INFO, message, file, line, function, format, color)?;
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
fn warning(message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
    let logger = get_global_logger()?;
    logger.log(LogLevel::WARNING, message, file, line, function, format, color)?;
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
fn error(message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
    let logger = get_global_logger()?;
    logger.log(LogLevel::ERROR, message, file, line, function, format, color)?;
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (message, file=None, line=None, function=None, format=None, color=None))]
fn critical(message: &str, file: Option<&str>, line: Option<u32>, function: Option<&str>, format: Option<&str>, color: Option<&str>) -> PyResult<()> {
    let logger = get_global_logger()?;
    logger.log(LogLevel::CRITICAL, message, file, line, function, format, color)?;
    Ok(())
}

#[pyfunction]
fn set_level(level: &Bound<'_, PyAny>) -> PyResult<()> {
    let logger = get_global_logger()?;

    let level = if let Ok(level_int) = level.extract::<i32>() {
        LogLevel::from_int(level_int)?
    } else if let Ok(level_str) = level.extract::<String>() {
        match level_str.to_uppercase().as_str() {
            "DEBUG" => LogLevel::DEBUG,
            "INFO" => LogLevel::INFO,
            "WARNING" => LogLevel::WARNING,
            "ERROR" => LogLevel::ERROR,
            "CRITICAL" => LogLevel::CRITICAL,
            _ => return Err(PyRuntimeError::new_err(format!("Invalid log level: {}", level_str))),
        }
    } else {
        return Err(PyRuntimeError::new_err("Invalid log level type"));
    };

    logger.set_level(level);
    Ok(())
}

#[pyfunction]
fn enable() -> PyResult<()> {
    let logger = get_global_logger()?;
    logger.set_enabled(true);
    Ok(())
}

#[pyfunction]
fn disable() -> PyResult<()> {
    let logger = get_global_logger()?;
    logger.set_enabled(false);
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (*, level=None, file_path=None, max_file_size=None, max_backup_count=None, colored_output=None, format=None, enabled=None, debug_config=None, append_to_file=None, use_datetime_in_filename=None, use_date_in_filename=None, use_time_in_filename=None, show_timestamp=None, show_level=None, show_message=None))]
fn configure(
    _py: Python<'_>,
    level: Option<&Bound<'_, PyAny>>,
    file_path: Option<&str>,
    max_file_size: Option<u64>,
    max_backup_count: Option<usize>,
    colored_output: Option<bool>,
    format: Option<&str>,
    enabled: Option<bool>,
    debug_config: Option<bool>,
    append_to_file: Option<bool>,
    use_datetime_in_filename: Option<bool>,
    use_date_in_filename: Option<bool>,
    use_time_in_filename: Option<bool>,
    show_timestamp: Option<bool>,
    show_level: Option<bool>,
    show_message: Option<bool>,
) -> PyResult<()> {
    let logger = get_global_logger()?;
    let mut logger_config = logger.config.read().clone();

    // Update configuration based on provided parameters
    if let Some(enabled_val) = enabled {
        logger_config.enabled = enabled_val;
    }

    if let Some(debug_val) = debug_config {
        logger_config.debug_config = debug_val;
    }

    if let Some(level_val) = level {
        if logger_config.debug_config {
            println!("Configure: received level value: {:?}", level_val);
        }
        if let Ok(level_int) = level_val.extract::<i32>() {
            if logger_config.debug_config {
                println!("Configure: extracted level as int: {}", level_int);
            }
            logger_config.level = LogLevel::from_int(level_int)?;
            if logger_config.debug_config {
                println!("Configure: set log level to: {:?}", logger_config.level);
            }
        } else if let Ok(level_str) = level_val.extract::<String>() {
            if logger_config.debug_config {
                println!("Configure: extracted level as string: {}", level_str);
            }
            logger_config.level = match level_str.to_uppercase().as_str() {
                "DEBUG" => LogLevel::DEBUG,
                "INFO" => LogLevel::INFO,
                "WARNING" => LogLevel::WARNING,
                "ERROR" => LogLevel::ERROR,
                "CRITICAL" => LogLevel::CRITICAL,
                _ => return Err(PyRuntimeError::new_err(format!("Invalid log level: {}", level_str))),
            };
            if logger_config.debug_config {
                println!("Configure: set log level to: {:?}", logger_config.level);
            }
        } else {
            if logger_config.debug_config {
                println!("Configure: could not extract level as int or string");
            }
            return Err(PyRuntimeError::new_err("Invalid log level type"));
        }
    } else if logger_config.debug_config {
        println!("Configure: no level provided, using default: {:?}", logger_config.level);
    }

    if let Some(path) = file_path {
        logger_config.file_path = Some(PathBuf::from(path));
    }

    if let Some(size) = max_file_size {
        logger_config.max_file_size = Some(size);
    }

    if let Some(count) = max_backup_count {
        logger_config.max_backup_count = Some(count);
    }

    if let Some(colored) = colored_output {
        logger_config.colored_output = colored;
    }

    if let Some(fmt) = format {
        logger_config.format = fmt.to_string();
    }

    // New configuration options
    if let Some(append) = append_to_file {
        logger_config.append_to_file = append;
    }

    if let Some(use_datetime) = use_datetime_in_filename {
        logger_config.use_datetime_in_filename = use_datetime;
    }

    if let Some(use_date) = use_date_in_filename {
        logger_config.use_date_in_filename = use_date;
    }

    if let Some(use_time) = use_time_in_filename {
        logger_config.use_time_in_filename = use_time;
    }

    if let Some(show_ts) = show_timestamp {
        logger_config.show_timestamp = show_ts;
    }

    if let Some(show_lvl) = show_level {
        logger_config.show_level = show_lvl;
    }

    if let Some(show_msg) = show_message {
        logger_config.show_message = show_msg;
    }

    logger.update_config(logger_config)?;
    Ok(())
}

// Compatibility layer with Python's standard logging module
// This provides a Rust implementation of the compatibility layer
// that was previously implemented in Python (compat.py)

// Formatter for log records
#[pyclass]
struct LoglyFormatter {
    fmt: String,
    datefmt: Option<String>,
    logly_fmt: String,
}

#[pymethods]
impl LoglyFormatter {
    #[new]
    fn new(fmt: Option<&str>, datefmt: Option<&str>, style: Option<&str>) -> PyResult<Self> {
        // Check style
        if let Some(s) = style {
            if s != "%" {
                return Err(PyValueError::new_err("Only '%' style is supported"));
            }
        }

        let fmt_str = fmt.unwrap_or("%(levelname)s:%(name)s:%(message)s").to_string();

        // Convert Python logging format to logly format
        let mut logly_fmt = fmt_str.clone();
        logly_fmt = logly_fmt.replace("%(asctime)s", "{timestamp}");
        logly_fmt = logly_fmt.replace("%(levelname)s", "{level}");
        logly_fmt = logly_fmt.replace("%(message)s", "{message}");
        logly_fmt = logly_fmt.replace("%(pathname)s", "{file}");
        logly_fmt = logly_fmt.replace("%(filename)s", "{file}");
        logly_fmt = logly_fmt.replace("%(lineno)d", "{line}");
        logly_fmt = logly_fmt.replace("%(funcName)s", "{function}");

        Ok(Self {
            fmt: fmt_str,
            datefmt: datefmt.map(String::from),
            logly_fmt,
        })
    }

    fn format(&self, record: &Bound<'_, PyAny>) -> PyResult<String> {
        // This is a simplified implementation that just returns the format string
        // In a real implementation, we would format the record using the format string
        Ok(self.fmt.clone())
    }

    fn get_logly_format(&self) -> String {
        self.logly_fmt.clone()
    }
}

// Filter for log records
#[pyclass]
struct LoglyFilter {
    name: String,
}

#[pymethods]
impl LoglyFilter {
    #[new]
    fn new(name: Option<&str>) -> Self {
        Self {
            name: name.unwrap_or("").to_string(),
        }
    }

    fn filter(&self, record: &Bound<'_, PyAny>) -> PyResult<bool> {
        if self.name.is_empty() {
            return Ok(true);
        }

        let record_name = record.getattr("name")?.extract::<String>()?;
        Ok(record_name.starts_with(&self.name))
    }
}

// Base handler class
#[pyclass]
struct LoglyHandler {
    level: i32,
    formatter: Option<Py<LoglyFormatter>>,
    filters: Vec<Py<LoglyFilter>>,
}

#[pymethods]
impl LoglyHandler {
    #[new]
    fn new(level: Option<&Bound<'_, PyAny>>) -> PyResult<Self> {
        let level_val = if let Some(l) = level {
            if let Ok(level_int) = l.extract::<i32>() {
                level_int
            } else if let Ok(level_str) = l.extract::<String>() {
                match level_str.to_uppercase().as_str() {
                    "DEBUG" => LogLevel::DEBUG as i32,
                    "INFO" => LogLevel::INFO as i32,
                    "WARNING" => LogLevel::WARNING as i32,
                    "ERROR" => LogLevel::ERROR as i32,
                    "CRITICAL" => LogLevel::CRITICAL as i32,
                    _ => return Err(PyValueError::new_err(format!("Invalid log level: {}", level_str))),
                }
            } else {
                LogLevel::INFO as i32
            }
        } else {
            LogLevel::INFO as i32
        };

        Ok(Self {
            level: level_val,
            formatter: None,
            filters: Vec::new(),
        })
    }

    fn set_level(&mut self, level: &Bound<'_, PyAny>) -> PyResult<()> {
        self.level = if let Ok(level_int) = level.extract::<i32>() {
            level_int
        } else if let Ok(level_str) = level.extract::<String>() {
            match level_str.to_uppercase().as_str() {
                "DEBUG" => LogLevel::DEBUG as i32,
                "INFO" => LogLevel::INFO as i32,
                "WARNING" => LogLevel::WARNING as i32,
                "ERROR" => LogLevel::ERROR as i32,
                "CRITICAL" => LogLevel::CRITICAL as i32,
                _ => return Err(PyValueError::new_err(format!("Invalid log level: {}", level_str))),
            }
        } else {
            return Err(PyValueError::new_err("Invalid log level type"));
        };

        Ok(())
    }

    fn set_formatter(&mut self, formatter: &Bound<'_, PyAny>) -> PyResult<()> {
        self.formatter = Some(formatter.into_py(formatter.py()));
        Ok(())
    }

    fn add_filter(&mut self, filter: &Bound<'_, PyAny>) -> PyResult<()> {
        self.filters.push(filter.into_py(filter.py()));
        Ok(())
    }

    fn remove_filter(&mut self, filter: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = filter.py();
        let filter_py = filter.into_py(py);
        self.filters.retain(|f| !f.is_eq(&filter_py).unwrap_or(false));
        Ok(())
    }

    fn handle(&self, py: Python<'_>, record: &Bound<'_, PyAny>) -> PyResult<bool> {
        let record_level = record.getattr("levelno")?.extract::<i32>()?;
        if record_level < self.level {
            return Ok(false);
        }

        for filter in &self.filters {
            let filter_obj = filter.as_ref(py);
            let result = filter_obj.call_method1("filter", (record,))?;
            if !result.extract::<bool>()? {
                return Ok(false);
            }
        }

        self.emit(py, record)?;
        Ok(true)
    }

    fn emit(&self, _py: Python<'_>, _record: &Bound<'_, PyAny>) -> PyResult<()> {
        Err(PyRuntimeError::new_err("emit must be implemented by subclasses"))
    }

    fn flush(&self) -> PyResult<()> {
        Ok(())
    }

    fn close(&self) -> PyResult<()> {
        self.flush()
    }
}

// Stream handler
#[pyclass(extends=LoglyHandler)]
struct StreamHandler {
    stream: Option<Py<PyAny>>,
}

#[pymethods]
impl StreamHandler {
    #[new]
    fn new(stream: Option<&Bound<'_, PyAny>>, level: Option<&Bound<'_, PyAny>>) -> PyResult<(Self, LoglyHandler)> {
        let handler = LoglyHandler::new(level)?;
        let stream_py = if let Some(s) = stream {
            Some(s.into_py(s.py()))
        } else {
            // Default to sys.stderr
            let py = s.py();
            let sys = py.import("sys")?;
            let stderr = sys.getattr("stderr")?;
            Some(stderr.into_py(py))
        };

        Ok((Self { stream }, handler))
    }

    fn emit(&self, py: Python<'_>, record: &Bound<'_, PyAny>) -> PyResult<()> {
        let msg = record.call_method0("getMessage")?.extract::<String>()?;
        let level = record.getattr("levelno")?.extract::<i32>()?;

        // Convert level to LogLevel
        let log_level = match level {
            10 => LogLevel::DEBUG,
            20 => LogLevel::INFO,
            30 => LogLevel::WARNING,
            40 => LogLevel::ERROR,
            50 => LogLevel::CRITICAL,
            _ => LogLevel::INFO,
        };

        // Get format from formatter if available
        let fmt = if let Some(formatter) = &self.as_ref(py).formatter {
            let formatter_obj = formatter.as_ref(py);
            Some(formatter_obj.call_method0("get_logly_format")?.extract::<String>()?)
        } else {
            None
        };

        // Extract file, line, function from record
        let file = if record.hasattr("pathname")? {
            Some(record.getattr("pathname")?.extract::<String>()?)
        } else {
            None
        };

        let line = if record.hasattr("lineno")? {
            Some(record.getattr("lineno")?.extract::<u32>()?)
        } else {
            None
        };

        let function = if record.hasattr("funcName")? {
            Some(record.getattr("funcName")?.extract::<String>()?)
        } else {
            None
        };

        // Use the global logger to log the message
        let logger = get_global_logger()?;
        logger.log(
            log_level,
            &msg,
            file.as_deref(),
            line,
            function.as_deref(),
            fmt.as_deref(),
            None,
        )?;

        Ok(())
    }
}

// File handler
#[pyclass(extends=LoglyHandler)]
struct FileHandler {
    filename: String,
    mode: String,
    encoding: Option<String>,
    delay: bool,
    file_opened: bool,
}

#[pymethods]
impl FileHandler {
    #[new]
    fn new(
        filename: &str,
        mode: Option<&str>,
        encoding: Option<&str>,
        delay: Option<bool>,
        level: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<(Self, LoglyHandler)> {
        let handler = LoglyHandler::new(level)?;
        let file_handler = Self {
            filename: filename.to_string(),
            mode: mode.unwrap_or("a").to_string(),
            encoding: encoding.map(String::from),
            delay: delay.unwrap_or(false),
            file_opened: false,
        };

        // Open the file if not delayed
        if !file_handler.delay {
            file_handler.open_file()?;
        }

        Ok((file_handler, handler))
    }

    fn open_file(&self) -> PyResult<()> {
        let append = self.mode == "a";
        _configure(
            Python::acquire_gil().python(),
            None,
            Some(&self.filename),
            None,
            None,
            None,
            None,
            None,
            None,
            Some(append),
            None,
            None,
            None,
            None,
            None,
            None,
        )?;
        Ok(())
    }

    fn emit(&self, py: Python<'_>, record: &Bound<'_, PyAny>) -> PyResult<()> {
        // Open the file if not already opened
        if !self.file_opened {
            self.open_file()?;
        }

        let msg = record.call_method0("getMessage")?.extract::<String>()?;
        let level = record.getattr("levelno")?.extract::<i32>()?;

        // Convert level to LogLevel
        let log_level = match level {
            10 => LogLevel::DEBUG,
            20 => LogLevel::INFO,
            30 => LogLevel::WARNING,
            40 => LogLevel::ERROR,
            50 => LogLevel::CRITICAL,
            _ => LogLevel::INFO,
        };

        // Get format from formatter if available
        let fmt = if let Some(formatter) = &self.as_ref(py).formatter {
            let formatter_obj = formatter.as_ref(py);
            Some(formatter_obj.call_method0("get_logly_format")?.extract::<String>()?)
        } else {
            None
        };

        // Extract file, line, function from record
        let file = if record.hasattr("pathname")? {
            Some(record.getattr("pathname")?.extract::<String>()?)
        } else {
            None
        };

        let line = if record.hasattr("lineno")? {
            Some(record.getattr("lineno")?.extract::<u32>()?)
        } else {
            None
        };

        let function = if record.hasattr("funcName")? {
            Some(record.getattr("funcName")?.extract::<String>()?)
        } else {
            None
        };

        // Use the global logger to log the message
        let logger = get_global_logger()?;
        logger.log(
            log_level,
            &msg,
            file.as_deref(),
            line,
            function.as_deref(),
            fmt.as_deref(),
            None,
        )?;

        Ok(())
    }

    fn close(&self) -> PyResult<()> {
        // No need to close the file as logly handles this
        Ok(())
    }
}

// Null handler
#[pyclass(extends=LoglyHandler)]
struct NullHandler {}

#[pymethods]
impl NullHandler {
    #[new]
    fn new(level: Option<&Bound<'_, PyAny>>) -> PyResult<(Self, LoglyHandler)> {
        let handler = LoglyHandler::new(level)?;
        Ok((Self {}, handler))
    }

    fn emit(&self, _py: Python<'_>, _record: &Bound<'_, PyAny>) -> PyResult<()> {
        // Do nothing
        Ok(())
    }
}

// Logger registry
static LOGGER_REGISTRY: Lazy<RwLock<HashMap<String, Py<CompatLogger>>>> = Lazy::new(|| {
    RwLock::new(HashMap::new())
});

// Root logger
static ROOT_LOGGER: Lazy<RwLock<Option<Py<CompatLogger>>>> = Lazy::new(|| {
    RwLock::new(None)
});

// Logger class
#[pyclass]
struct CompatLogger {
    name: String,
    level: i32,
    parent: Option<Py<CompatLogger>>,
    propagate: bool,
    handlers: Vec<Py<PyAny>>,
    disabled: bool,
    logger: Py<Logger>,
}

#[pymethods]
impl CompatLogger {
    #[new]
    fn new(py: Python<'_>, name: &str, level: Option<&Bound<'_, PyAny>>) -> PyResult<Self> {
        let level_val = if let Some(l) = level {
            if let Ok(level_int) = l.extract::<i32>() {
                level_int
            } else if let Ok(level_str) = l.extract::<String>() {
                match level_str.to_uppercase().as_str() {
                    "DEBUG" => LogLevel::DEBUG as i32,
                    "INFO" => LogLevel::INFO as i32,
                    "WARNING" => LogLevel::WARNING as i32,
                    "ERROR" => LogLevel::ERROR as i32,
                    "CRITICAL" => LogLevel::CRITICAL as i32,
                    _ => return Err(PyValueError::new_err(format!("Invalid log level: {}", level_str))),
                }
            } else {
                LogLevel::INFO as i32
            }
        } else {
            LogLevel::INFO as i32
        };

        // Create a logly logger instance
        let logger = Logger::new()?;

        Ok(Self {
            name: name.to_string(),
            level: level_val,
            parent: None,
            propagate: true,
            handlers: Vec::new(),
            disabled: false,
            logger: logger.into_py(py),
        })
    }

    fn set_level(&mut self, level: &Bound<'_, PyAny>) -> PyResult<()> {
        self.level = if let Ok(level_int) = level.extract::<i32>() {
            level_int
        } else if let Ok(level_str) = level.extract::<String>() {
            match level_str.to_uppercase().as_str() {
                "DEBUG" => LogLevel::DEBUG as i32,
                "INFO" => LogLevel::INFO as i32,
                "WARNING" => LogLevel::WARNING as i32,
                "ERROR" => LogLevel::ERROR as i32,
                "CRITICAL" => LogLevel::CRITICAL as i32,
                _ => return Err(PyValueError::new_err(format!("Invalid log level: {}", level_str))),
            }
        } else {
            return Err(PyValueError::new_err("Invalid log level type"));
        };

        Ok(())
    }

    fn is_enabled_for(&self, level: i32) -> bool {
        if self.disabled {
            return false;
        }

        level >= self.level
    }

    fn get_effective_level(&self, py: Python<'_>) -> PyResult<i32> {
        let mut logger = self;
        while logger.level == 0 {
            if let Some(parent) = &logger.parent {
                let parent_obj = parent.as_ref(py);
                logger = parent_obj.extract::<&CompatLogger>()?;
            } else {
                return Ok(LogLevel::INFO as i32);
            }
        }

        Ok(logger.level)
    }

    fn add_handler(&mut self, handler: &Bound<'_, PyAny>) -> PyResult<()> {
        self.handlers.push(handler.into_py(handler.py()));
        Ok(())
    }

    fn remove_handler(&mut self, handler: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = handler.py();
        let handler_py = handler.into_py(py);
        self.handlers.retain(|h| !h.is_eq(&handler_py).unwrap_or(false));
        Ok(())
    }

    fn _log(&self, py: Python<'_>, level: i32, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        if !self.is_enabled_for(level) {
            return Ok(());
        }

        // Format message with args if provided
        let formatted_msg = if args.len() > 0 {
            let format_args = PyTuple::new(py, &[msg.into_py(py)]);
            format_args.call_method1("__mod__", args)?.extract::<String>()?
        } else {
            msg.to_string()
        };

        // Extract extra kwargs
        let exc_info = if let Some(kw) = kwargs {
            kw.get_item("exc_info")?.map(|v| v.extract::<bool>()).transpose()?
        } else {
            None
        };

        let extra = if let Some(kw) = kwargs {
            kw.get_item("extra")?.map(|v| v.extract::<&Bound<'_, PyDict>>()).transpose()?
        } else {
            None
        };

        let stack_info = if let Some(kw) = kwargs {
            kw.get_item("stack_info")?.map(|v| v.extract::<bool>()).transpose()?
        } else {
            None
        };

        // Create a record
        let logging = py.import("logging")?;
        let record = logging.call_method1(
            "LogRecord",
            (
                &self.name,
                level,
                kwargs.and_then(|kw| kw.get_item("file").ok().flatten()).map(|v| v.extract::<String>()).transpose()?.unwrap_or_default(),
                kwargs.and_then(|kw| kw.get_item("line").ok().flatten()).map(|v| v.extract::<i32>()).transpose()?.unwrap_or(0),
                formatted_msg,
                PyTuple::empty(py),
                exc_info.unwrap_or(false),
                kwargs.and_then(|kw| kw.get_item("function").ok().flatten()).map(|v| v.extract::<String>()).transpose()?.unwrap_or_default(),
                stack_info.unwrap_or(false),
            ),
        )?;

        // Add extra attributes to record
        if let Some(extra_dict) = extra {
            for (key, value) in extra_dict.iter() {
                record.setattr(key, value)?;
            }
        }

        // Handle the record
        self.handle(py, record)?;

        Ok(())
    }

    fn handle(&self, py: Python<'_>, record: &Bound<'_, PyAny>) -> PyResult<()> {
        if !self.disabled && self.filter(record)? {
            self.call_handlers(py, record)?;
        }
        Ok(())
    }

    fn filter(&self, record: &Bound<'_, PyAny>) -> PyResult<bool> {
        if self.disabled {
            return Ok(false);
        }

        let record_level = record.getattr("levelno")?.extract::<i32>()?;
        Ok(record_level >= self.level)
    }

    fn call_handlers(&self, py: Python<'_>, record: &Bound<'_, PyAny>) -> PyResult<()> {
        let mut c = Some(self);
        let mut found = 0;

        while let Some(current) = c {
            for handler in &current.handlers {
                found += 1;
                let handler_obj = handler.as_ref(py);
                let record_level = record.getattr("levelno")?.extract::<i32>()?;
                let handler_level = handler_obj.getattr("level")?.extract::<i32>()?;
                if record_level >= handler_level {
                    handler_obj.call_method1("handle", (record,))?;
                }
            }

            if !current.propagate {
                c = None;
            } else if let Some(parent) = &current.parent {
                let parent_obj = parent.as_ref(py);
                c = Some(parent_obj.extract::<&CompatLogger>()?);
            } else {
                c = None;
            }
        }

        // If no handlers were found, use the default logly logger
        if found == 0 {
            let record_level = record.getattr("levelno")?.extract::<i32>()?;
            let msg = record.call_method0("getMessage")?.extract::<String>()?;

            // Convert level to LogLevel
            let log_level = match record_level {
                10 => LogLevel::DEBUG,
                20 => LogLevel::INFO,
                30 => LogLevel::WARNING,
                40 => LogLevel::ERROR,
                50 => LogLevel::CRITICAL,
                _ => LogLevel::INFO,
            };

            // Extract file, line, function from record
            let file = if record.hasattr("pathname")? {
                Some(record.getattr("pathname")?.extract::<String>()?)
            } else {
                None
            };

            let line = if record.hasattr("lineno")? {
                Some(record.getattr("lineno")?.extract::<u32>()?)
            } else {
                None
            };

            let function = if record.hasattr("funcName")? {
                Some(record.getattr("funcName")?.extract::<String>()?)
            } else {
                None
            };

            // Use the global logger to log the message
            let logger = get_global_logger()?;
            logger.log(
                log_level,
                &msg,
                file.as_deref(),
                line,
                function.as_deref(),
                None,
                None,
            )?;
        }

        Ok(())
    }

    fn debug(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self._log(py, LogLevel::DEBUG as i32, msg, args, kwargs)
    }

    fn info(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self._log(py, LogLevel::INFO as i32, msg, args, kwargs)
    }

    fn warning(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self._log(py, LogLevel::WARNING as i32, msg, args, kwargs)
    }

    fn warn(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self.warning(py, msg, args, kwargs)
    }

    fn error(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self._log(py, LogLevel::ERROR as i32, msg, args, kwargs)
    }

    fn exception(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        let mut kwargs_dict = if let Some(kw) = kwargs {
            kw.copy()?
        } else {
            PyDict::new(py)
        };

        kwargs_dict.set_item("exc_info", true)?;
        self.error(py, msg, args, Some(&kwargs_dict))
    }

    fn critical(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self._log(py, LogLevel::CRITICAL as i32, msg, args, kwargs)
    }

    fn fatal(&self, py: Python<'_>, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self.critical(py, msg, args, kwargs)
    }

    fn log(&self, py: Python<'_>, level: i32, msg: &str, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        self._log(py, level, msg, args, kwargs)
    }
}

// Get logger function
#[pyfunction]
fn get_logger(py: Python<'_>, name: Option<&str>) -> PyResult<Py<CompatLogger>> {
    let name_str = name.unwrap_or("root").to_string();

    // Check if logger already exists in registry
    {
        let registry = LOGGER_REGISTRY.read();
        if let Some(logger) = registry.get(&name_str) {
            return Ok(logger.clone());
        }
    }

    // Create a new logger
    let logger = Py::new(py, CompatLogger::new(py, &name_str, None)?)?;

    // Set up parent logger
    if name_str != "root" {
        let mut logger_obj = logger.as_ref(py).borrow_mut();
        let i = name_str.rfind('.');
        if let Some(idx) = i {
            let parent_name = &name_str[..idx];
            let parent = get_logger(py, Some(parent_name))?;
            logger_obj.parent = Some(parent);
        } else {
            // Parent is the root logger
            let root_logger = {
                let mut root = ROOT_LOGGER.write();
                if root.is_none() {
                    *root = Some(Py::new(py, CompatLogger::new(py, "root", None)?)?);
                }
                root.clone().unwrap()
            };
            logger_obj.parent = Some(root_logger);
        }
    }

    // Add logger to registry
    {
        let mut registry = LOGGER_REGISTRY.write();
        registry.insert(name_str, logger.clone());
    }

    Ok(logger)
}

// Basic config function
#[pyfunction]
fn basic_config(
    py: Python<'_>,
    level: Option<&Bound<'_, PyAny>>,
    format: Option<&str>,
    datefmt: Option<&str>,
    style: Option<&str>,
    filename: Option<&str>,
    filemode: Option<&str>,
    stream: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    // Get or create root logger
    let root_logger = {
        let mut root = ROOT_LOGGER.write();
        if root.is_none() {
            *root = Some(Py::new(py, CompatLogger::new(py, "root", None)?)?);
        }
        root.clone().unwrap()
    };

    let root_logger_obj = root_logger.as_ref(py);

    // If handlers already exist, do nothing
    if !root_logger_obj.borrow().handlers.is_empty() {
        return Ok(());
    }

    // Get configuration options
    let level_val = if let Some(l) = level {
        if let Ok(level_int) = l.extract::<i32>() {
            level_int
        } else if let Ok(level_str) = l.extract::<String>() {
            match level_str.to_uppercase().as_str() {
                "DEBUG" => LogLevel::DEBUG as i32,
                "INFO" => LogLevel::INFO as i32,
                "WARNING" => LogLevel::WARNING as i32,
                "ERROR" => LogLevel::ERROR as i32,
                "CRITICAL" => LogLevel::CRITICAL as i32,
                _ => return Err(PyValueError::new_err(format!("Invalid log level: {}", level_str))),
            }
        } else {
            LogLevel::INFO as i32
        }
    } else {
        LogLevel::INFO as i32
    };

    let format_str = format.unwrap_or("%(levelname)s:%(name)s:%(message)s");
    let filemode_str = filemode.unwrap_or("a");

    // Create formatter
    let formatter = Py::new(py, LoglyFormatter::new(Some(format_str), datefmt, style)?)?;

    // Create handler
    let handler: Py<PyAny> = if let Some(path) = filename {
        Py::new(py, FileHandler::new(path, Some(filemode_str), None, Some(false), Some(level))?)?.into_py(py)
    } else {
        Py::new(py, StreamHandler::new(stream, Some(level))?)?.into_py(py)
    };

    // Configure handler
    let handler_obj = handler.as_ref(py);
    handler_obj.call_method1("set_formatter", (formatter.as_ref(py),))?;

    // Add handler to root logger
    root_logger_obj.borrow_mut().add_handler(handler_obj)?;
    root_logger_obj.borrow_mut().set_level(level.unwrap_or(level_val.into_py(py).as_ref(py)))?;

    // Configure logly
    let log_level = match level_val {
        10 => LogLevel::DEBUG,
        20 => LogLevel::INFO,
        30 => LogLevel::WARNING,
        40 => LogLevel::ERROR,
        50 => LogLevel::CRITICAL,
        _ => LogLevel::INFO,
    };

    _configure(
        py,
        Some(&log_level.into_py(py)),
        filename,
        None,
        None,
        None,
        Some(formatter.as_ref(py).call_method0("get_logly_format")?.extract::<String>()?),
        None,
        None,
        Some(filemode_str == "a"),
        None,
        None,
        None,
        None,
        None,
        None,
    )?;

    Ok(())
}

// Module initialization
#[pymodule]
fn _logly(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Initialize the global logger
    let _ = get_global_logger()?;

    // Add LogLevel enum
    m.add_class::<LogLevel>()?;

    // Add Logger class
    m.add_class::<Logger>()?;

    // Add global functions
    m.add_function(wrap_pyfunction!(debug, m)?)?;
    m.add_function(wrap_pyfunction!(info, m)?)?;
    m.add_function(wrap_pyfunction!(warning, m)?)?;
    m.add_function(wrap_pyfunction!(error, m)?)?;
    m.add_function(wrap_pyfunction!(critical, m)?)?;
    m.add_function(wrap_pyfunction!(set_level, m)?)?;
    m.add_function(wrap_pyfunction!(enable, m)?)?;
    m.add_function(wrap_pyfunction!(disable, m)?)?;
    m.add_function(wrap_pyfunction!(configure, m)?)?;

    // Add compatibility layer classes
    m.add_class::<LoglyFormatter>()?;
    m.add_class::<LoglyFilter>()?;
    m.add_class::<LoglyHandler>()?;
    m.add_class::<StreamHandler>()?;
    m.add_class::<FileHandler>()?;
    m.add_class::<NullHandler>()?;
    m.add_class::<CompatLogger>()?;

    // Add compatibility layer functions
    m.add_function(wrap_pyfunction!(get_logger, m)?)?;
    m.add_function(wrap_pyfunction!(basic_config, m)?)?;

    // Add constants
    m.add("DEBUG", LogLevel::DEBUG as i32)?;
    m.add("INFO", LogLevel::INFO as i32)?;
    m.add("WARNING", LogLevel::WARNING as i32)?;
    m.add("ERROR", LogLevel::ERROR as i32)?;
    m.add("CRITICAL", LogLevel::CRITICAL as i32)?;

    Ok(())
}
