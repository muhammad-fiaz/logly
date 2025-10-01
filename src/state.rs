//! Logger state management with high-performance data structures.
//!
//! This module provides the core state management for the logly logger,
//! including compression, rotation policies, sink configuration, metrics,
//! and thread-safe state tracking using parking_lot and ahash for optimal performance.

use once_cell::sync::Lazy;
use parking_lot::{RwLock, Mutex};
use std::sync::Arc;
use std::thread::JoinHandle;
use tracing_subscriber::filter::LevelFilter;
use std::io::Write;
use crossbeam_channel::Sender;
use ahash::AHashMap;
use pyo3::Py;
use pyo3::types::PyAny;

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
    /// Date/time format style (e.g., "rfc3339", "local", "utc")
    pub date_style: String,
    /// Enable timestamp in log output
    pub date_enabled: bool,
    /// Number of rotated files to keep (older files deleted)
    pub retention: Option<usize>,
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
    /// Format logs as JSON
    pub format_json: bool,
    /// Format logs as pretty-printed JSON
    pub pretty_json: bool,
    
    // Sink management (support multiple sinks using fast AHashMap)
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
            format_json: false,
            pretty_json: false,
            
            // New fields
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
