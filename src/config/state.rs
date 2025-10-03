use ahash::AHashMap;
use crossbeam_channel::Sender;
use once_cell::sync::Lazy;
use parking_lot::{Mutex, RwLock};
use pyo3::Py;
use pyo3::types::PyAny;
use std::io::Write;
use std::sync::Arc;
use std::thread::JoinHandle;
use tracing_subscriber::filter::LevelFilter;

/// Handler ID for managing sinks.
///
/// Each sink gets a unique ID when added via `logger.add()`.
pub type HandlerId = usize;

/// Compression algorithm for log files.
///
/// Supports multiple compression formats for reducing log file size.
/// Compression is applied during file rotation or on-demand (future feature).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[allow(dead_code)]
pub enum Compression {
    /// No compression (default)
    None,
    /// GZIP compression (balanced speed and compression ratio)
    Gzip,
    /// Zstandard compression (high compression ratio, fast decompression)
    Zstd,
}

#[allow(dead_code)]
impl Compression {
    /// Parse compression format from string.
    ///
    /// # Arguments
    /// * `s` - String representation: "gzip"/"gz", "zstd"/"zst", or "none" (case-insensitive)
    ///
    /// # Returns
    /// Compression variant, defaulting to None if unrecognized
    ///
    /// # Examples
    /// ```rust
    /// use logly::Compression;
    /// assert_eq!(Compression::from_str("gzip"), Compression::Gzip);
    /// assert_eq!(Compression::from_str("ZSTD"), Compression::Zstd);
    /// assert_eq!(Compression::from_str("invalid"), Compression::None);
    /// ```
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "gzip" | "gz" => Compression::Gzip,
            "zstd" | "zst" => Compression::Zstd,
            _ => Compression::None,
        }
    }
}

/// Rotation policy for log files.
///
/// Defines when and how log files should be rotated to manage file size
/// and organize logs by time period.
#[derive(Debug, Clone, PartialEq)]
#[allow(dead_code)]
pub enum RotationPolicy {
    /// Never rotate (single continuous log file)
    Never,
    /// Rotate once per day at midnight
    Daily,
    /// Rotate once per hour
    Hourly,
    /// Rotate once per minute
    Minutely,
    /// Rotate when file reaches specified size in bytes
    ///
    /// # Examples
    /// ```rust
    /// use logly::RotationPolicy;
    /// let policy = RotationPolicy::Size(10 * 1024 * 1024); // 10 MB
    /// ```
    Size(u64),
}

/// Configuration for a single log sink.
///
/// A sink represents a single output destination (file or console) with
/// its own rotation policy, compression, filtering, and formatting options.
#[allow(dead_code)]
pub struct SinkConfig {
    /// Unique handler ID for this sink
    pub id: HandlerId,
    /// File path (None for console sink)
    pub path: Option<String>,
    /// When/how to rotate this log file
    pub rotation: RotationPolicy,
    /// Compression algorithm for rotated files
    pub compression: Compression,
    /// Minimum log level for this sink (filter by level)
    pub min_level: Option<LevelFilter>,
    /// Module name filter (only logs from this module)
    pub module_filter: Option<String>,
    /// Function name filter (only logs from this function)
    pub function_filter: Option<String>,
    /// Enable asynchronous writing for better performance
    pub async_write: bool,
    /// Buffer size in bytes for async writing (default: 8192)
    pub buffer_size: usize,
    /// Flush interval in milliseconds for async writing (default: 1000)
    pub flush_interval: u64,
    /// Maximum number of buffered lines before blocking (default: 1000)
    pub max_buffered_lines: usize,
    /// Date/time format style (e.g., "rfc3339", "local", "utc")
    pub date_style: String,
    /// Enable timestamp in log output
    pub date_enabled: bool,
    /// Number of rotated files to keep (older files deleted)
    pub retention: Option<usize>,
    /// Custom format string for this sink (e.g., "{time} | {level} | {message}")
    pub format: Option<String>,
    /// Format this sink's output as JSON
    pub json: bool,
}

/// Statistics for monitoring logger performance.
///
/// Tracks key metrics to help identify performance issues and monitor
/// log volume. All metrics use atomic operations for thread-safe updates.
#[derive(Debug, Clone, Default)]
#[allow(dead_code)]
pub struct LoggerMetrics {
    /// Total number of log messages processed
    pub total_logs: u64,
    /// Total bytes written across all sinks
    pub bytes_written: u64,
    /// Number of errors encountered during logging
    pub errors_count: u64,
    /// Number of log messages dropped (e.g., due to sampling or full buffers)
    pub dropped_logs: u64,
}

/// Global logger state with high-performance data structures.
///
/// Uses parking_lot::RwLock for 5-10x faster lock performance,
/// ahash::AHashMap for 30% faster hashing, and crossbeam channels
/// for lock-free async communication.
#[allow(dead_code)]
pub struct LoggerState {
    /// Whether logger has been initialized
    pub inited: bool,
    /// Whether console output is enabled
    pub console_enabled: bool,
    /// Global minimum log level filter
    pub level_filter: LevelFilter,
    /// Enable colored output
    pub color: bool,
    /// Custom color callback function (level, text) -> colored_text
    pub color_callback: Option<Py<PyAny>>,
    /// Custom color mapping for log levels (ANSI color codes or color names)
    pub level_colors: AHashMap<String, String>,
    /// Show timestamps in console output
    pub show_time: bool,
    /// Show module information in console output
    pub show_module: bool,
    /// Show function information in console output
    pub show_function: bool,
    /// Show filename information in console output
    pub show_filename: bool,
    /// Show line number information in console output
    pub show_lineno: bool,
    /// Per-level console output control (None = use global console_enabled)
    pub console_levels: AHashMap<String, bool>,
    /// Per-level time display control (None = use global show_time)
    pub time_levels: AHashMap<String, bool>,
    /// Per-level color control (None = use global color)
    pub color_levels: AHashMap<String, bool>,
    /// Per-level storage control (None = use global level_filter)
    pub storage_levels: AHashMap<String, bool>,
    /// Format logs as JSON
    pub format_json: bool,
    /// Format logs as pretty-printed JSON
    pub pretty_json: bool,
    /// Enable fast path optimization for simple console-only logging
    pub fast_path_enabled: bool,
    /// Map of handler IDs to sink configurations
    pub sinks: AHashMap<HandlerId, SinkConfig>,
    /// Next available handler ID (auto-incremented)
    pub next_handler_id: HandlerId,
    /// Thread-safe file writers wrapped in Arc<Mutex<>> for concurrent access
    pub file_writers: AHashMap<HandlerId, Arc<Mutex<Box<dyn Write + Send>>>>,

    // Async writing infrastructure using crossbeam (lock-free channels)
    /// Crossbeam channel senders for async log writing
    pub async_senders: AHashMap<HandlerId, Sender<String>>,
    /// Background thread handles for async writers
    pub async_handles: Vec<JoinHandle<()>>,

    // Global context for all log records
    /// Key-value context automatically attached to all logs
    pub global_context: AHashMap<String, String>,

    // Performance metrics
    /// Real-time logger performance statistics
    pub metrics: LoggerMetrics,

    // Sampling/throttling for high-volume scenarios (future feature)
    /// Sample rate for probabilistic logging (0.0-1.0, None = no sampling)
    pub sample_rate: Option<f64>,

    // Caller information capture (file:line:function like loguru, future feature)
    /// Capture source location information (file, line, function)
    pub capture_caller: bool,

    // Callback functions for custom processing
    /// Registered callback functions that run asynchronously on each log
    pub callbacks: Vec<std::sync::Arc<Py<PyAny>>>,

    // Backward compatibility fields (deprecated, will be removed in 1.0)
    /// Legacy file path (use sinks instead)
    pub file_path: Option<String>,
    pub file_rotation: Option<String>,
    pub file_writer: Option<Arc<Mutex<Box<dyn Write + Send>>>>,
    pub file_date_style: Option<String>,
    pub file_date_enabled: bool,
    pub retention_count: Option<usize>,
    pub async_sender: Option<Sender<String>>,
    pub async_write: bool,
    pub async_handle: Option<JoinHandle<()>>,
    pub buffer_size: usize,
    pub flush_interval: u64,
    pub max_buffered_lines: usize,
    pub filter_min_level: Option<LevelFilter>,
    pub filter_module: Option<String>,
    pub filter_function: Option<String>,
}

impl Default for LoggerState {
    fn default() -> Self {
        Self {
            inited: false,
            console_enabled: true,
            level_filter: LevelFilter::INFO,
            color: true,
            color_callback: None,
            level_colors: {
                let mut colors = AHashMap::new();
                colors.insert("TRACE".to_string(), "36".to_string()); // Cyan
                colors.insert("DEBUG".to_string(), "35".to_string()); // Magenta
                colors.insert("INFO".to_string(), "32".to_string()); // Green
                colors.insert("SUCCESS".to_string(), "92".to_string()); // Bright Green
                colors.insert("WARNING".to_string(), "33".to_string()); // Yellow
                colors.insert("ERROR".to_string(), "31".to_string()); // Red
                colors.insert("CRITICAL".to_string(), "91".to_string()); // Bright Red
                colors
            },
            show_time: true,
            show_module: true,
            show_function: true,
            show_filename: false,
            show_lineno: false,
            console_levels: AHashMap::new(),
            time_levels: AHashMap::new(),
            color_levels: AHashMap::new(),
            storage_levels: AHashMap::new(),
            format_json: false,
            pretty_json: false,
            fast_path_enabled: true,
            sinks: AHashMap::new(),
            next_handler_id: 1,
            file_writers: AHashMap::new(),
            async_senders: AHashMap::new(),
            async_handles: Vec::new(),
            global_context: AHashMap::new(),
            metrics: LoggerMetrics::default(),
            sample_rate: None,
            capture_caller: false,
            callbacks: Vec::new(),

            // Backward compatibility (deprecated)
            file_path: None,
            file_rotation: None,
            file_writer: None,
            file_date_style: None,
            file_date_enabled: false,
            retention_count: None,
            async_sender: None,
            async_write: true,
            async_handle: None,
            buffer_size: 8192,
            flush_interval: 1000,
            max_buffered_lines: 1000,
            filter_min_level: None,
            filter_module: None,
            filter_function: None,
        }
    }
}

static LOGGER: Lazy<RwLock<LoggerState>> = Lazy::new(|| RwLock::new(LoggerState::default()));

pub fn with_state<R>(f: impl FnOnce(&mut LoggerState) -> R) -> R {
    let mut guard = LOGGER.write();
    f(&mut guard)
}

#[allow(dead_code)]
pub fn with_state_read<R>(f: impl FnOnce(&LoggerState) -> R) -> R {
    let guard = LOGGER.read();
    f(&guard)
}

pub fn reset_state() {
    with_state(|s| {
        // Clean up async handles
        let handles = std::mem::take(&mut s.async_handles);
        s.async_senders.clear();
        drop(handles);

        *s = LoggerState::default();
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compression_from_str() {
        assert_eq!(Compression::from_str("none"), Compression::None);
        assert_eq!(Compression::from_str("gzip"), Compression::Gzip);
        assert_eq!(Compression::from_str("gz"), Compression::Gzip);
        assert_eq!(Compression::from_str("zstd"), Compression::Zstd);
        assert_eq!(Compression::from_str("zst"), Compression::Zstd);
        assert_eq!(Compression::from_str("GZIP"), Compression::Gzip);
        assert_eq!(Compression::from_str("ZSTD"), Compression::Zstd);
        assert_eq!(Compression::from_str("invalid"), Compression::None);
        assert_eq!(Compression::from_str(""), Compression::None);
    }

    #[test]
    fn test_logger_metrics_default() {
        let metrics = LoggerMetrics::default();
        assert_eq!(metrics.total_logs, 0);
        assert_eq!(metrics.bytes_written, 0);
        assert_eq!(metrics.errors_count, 0);
        assert_eq!(metrics.dropped_logs, 0);
    }

    #[test]
    fn test_logger_state_default() {
        let state = LoggerState::default();

        assert!(!state.inited);
        assert!(state.console_enabled);
        assert_eq!(state.level_filter, LevelFilter::INFO);
        assert!(state.color);
        assert!(state.show_time);
        assert!(state.show_module);
        assert!(state.show_function);
        assert!(!state.format_json);
        assert!(!state.pretty_json);
        assert!(state.fast_path_enabled);
        assert_eq!(state.next_handler_id, 1);
        assert_eq!(state.sample_rate, None);
        assert!(!state.capture_caller);

        // Check level colors are set
        assert!(state.level_colors.contains_key("INFO"));
        assert!(state.level_colors.contains_key("ERROR"));
        assert!(state.level_colors.contains_key("DEBUG"));

        // Check collections are empty
        assert!(state.sinks.is_empty());
        assert!(state.file_writers.is_empty());
        assert!(state.async_senders.is_empty());
        assert!(state.async_handles.is_empty());
        assert!(state.global_context.is_empty());
        assert!(state.callbacks.is_empty());

        // Check backward compatibility fields
        assert_eq!(state.file_path, None);
        assert!(state.async_write);
        assert_eq!(state.buffer_size, 8192);
        assert_eq!(state.flush_interval, 1000);
        assert_eq!(state.max_buffered_lines, 1000);
    }

    #[test]
    fn test_with_state() {
        // Reset to clean state
        reset_state();

        // Test modifying state
        let result = with_state(|state| {
            state.inited = true;
            state.console_enabled = false;
            42
        });
        assert_eq!(result, 42);

        // Verify state was modified
        with_state_read(|state| {
            assert!(state.inited);
            assert!(!state.console_enabled);
        });
    }

    #[test]
    fn test_with_state_read() {
        // Reset to clean state
        reset_state();

        // Test reading state
        let result = with_state_read(|state| (state.inited, state.console_enabled));
        assert_eq!(result, (false, true));
    }

    #[test]
    fn test_reset_state() {
        // Modify state first
        with_state(|state| {
            state.inited = true;
            state.console_enabled = false;
            state.next_handler_id = 100;
            state
                .global_context
                .insert("test".to_string(), "value".to_string());
        });

        // Verify state was modified
        with_state_read(|state| {
            assert!(state.inited);
            assert!(!state.console_enabled);
            assert_eq!(state.next_handler_id, 100);
            assert!(state.global_context.contains_key("test"));
        });

        // Reset state
        reset_state();

        // Verify state was reset to defaults
        with_state_read(|state| {
            assert!(!state.inited);
            assert!(state.console_enabled);
            assert_eq!(state.next_handler_id, 1);
            assert!(state.global_context.is_empty());
        });
    }

    #[test]
    fn test_sink_config_creation() {
        let config = SinkConfig {
            id: 1,
            path: Some("test.log".to_string()),
            rotation: RotationPolicy::Daily,
            compression: Compression::Gzip,
            min_level: Some(LevelFilter::DEBUG),
            module_filter: Some("test_module".to_string()),
            function_filter: Some("test_function".to_string()),
            async_write: true,
            buffer_size: 4096,
            flush_interval: 500,
            max_buffered_lines: 500,
            date_style: "rfc3339".to_string(),
            date_enabled: true,
            retention: Some(10),
            format: Some("{time} | {level} | {message}".to_string()),
            json: false,
        };

        assert_eq!(config.id, 1);
        assert_eq!(config.path, Some("test.log".to_string()));
        assert_eq!(config.rotation, RotationPolicy::Daily);
        assert_eq!(config.compression, Compression::Gzip);
        assert_eq!(config.min_level, Some(LevelFilter::DEBUG));
        assert_eq!(config.module_filter, Some("test_module".to_string()));
        assert_eq!(config.function_filter, Some("test_function".to_string()));
        assert!(config.async_write);
        assert_eq!(config.buffer_size, 4096);
        assert_eq!(config.flush_interval, 500);
        assert_eq!(config.max_buffered_lines, 500);
        assert_eq!(config.date_style, "rfc3339");
        assert!(config.date_enabled);
        assert_eq!(config.retention, Some(10));
        assert_eq!(
            config.format,
            Some("{time} | {level} | {message}".to_string())
        );
    }
}
