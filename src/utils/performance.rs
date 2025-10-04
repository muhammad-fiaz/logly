use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

/// Global optimization toggle flag.
/// Controls whether optimization features are enabled at runtime.
#[allow(dead_code)]
static OPTIMIZATION_ENABLED: AtomicBool = AtomicBool::new(true);

/// Configuration for async writing performance parameters.
///
/// This struct provides a builder pattern for configuring async writing behavior,
/// including buffer sizes, flush intervals, and line buffering limits.
///
/// # Examples
///
/// ```rust
/// use logly::utils::performance::PerformanceConfig;
///
/// let config = PerformanceConfig::new()
///     .with_buffer_size(16384)
///     .with_flush_interval(200)
///     .with_max_buffered_lines(2000);
/// ```
#[allow(dead_code)]
pub struct PerformanceConfig {
    /// Buffer size in bytes for async writing.
    pub buffer_size: usize,
    /// Flush interval in milliseconds.
    pub flush_interval_ms: u64,
    /// Maximum number of lines to buffer before forcing a flush.
    pub max_buffered_lines: usize,
    /// Whether async writing is enabled.
    pub async_enabled: bool,
}

impl Default for PerformanceConfig {
    /// Creates a PerformanceConfig with sensible default values.
    ///
    /// # Defaults
    /// - buffer_size: 8192 bytes
    /// - flush_interval_ms: 100 milliseconds
    /// - max_buffered_lines: 1000 lines
    /// - async_enabled: true
    fn default() -> Self {
        Self {
            buffer_size: 8192,
            flush_interval_ms: 100,
            max_buffered_lines: 1000,
            async_enabled: true,
        }
    }
}

impl PerformanceConfig {
    /// Creates a new PerformanceConfig with default values.
    ///
    /// # Returns
    /// A new PerformanceConfig instance with default settings.
    #[allow(dead_code)]
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets the buffer size for async writing.
    ///
    /// The buffer size is clamped between 1KB and 1MB for safety.
    ///
    /// # Arguments
    /// * `size` - Desired buffer size in bytes
    ///
    /// # Returns
    /// Self for method chaining
    #[allow(dead_code)]
    pub fn with_buffer_size(mut self, size: usize) -> Self {
        self.buffer_size = size.clamp(1024, 1024 * 1024);
        self
    }

    /// Sets the flush interval for async writing.
    ///
    /// The interval is clamped between 10ms and 10 seconds for safety.
    ///
    /// # Arguments
    /// * `ms` - Flush interval in milliseconds
    ///
    /// # Returns
    /// Self for method chaining
    #[allow(dead_code)]
    pub fn with_flush_interval(mut self, ms: u64) -> Self {
        self.flush_interval_ms = ms.clamp(10, 10000);
        self
    }

    /// Sets the maximum number of buffered lines before forcing a flush.
    ///
    /// The line count is clamped between 100 and 100,000 for safety.
    ///
    /// # Arguments
    /// * `lines` - Maximum number of buffered lines
    ///
    /// # Returns
    /// Self for method chaining
    #[allow(dead_code)]
    pub fn with_max_buffered_lines(mut self, lines: usize) -> Self {
        self.max_buffered_lines = lines.clamp(100, 100000);
        self
    }

    /// Enables or disables async writing.
    ///
    /// # Arguments
    /// * `enabled` - Whether async writing should be enabled
    ///
    /// # Returns
    /// Self for method chaining
    #[allow(dead_code)]
    pub fn with_async(mut self, enabled: bool) -> Self {
        self.async_enabled = enabled;
        self
    }
}

/// Enables global optimization features.
///
/// When enabled, optimization features like pre-allocated strings and vectors
/// will be used to improve performance in high-throughput scenarios.
#[allow(dead_code)]
pub fn enable_optimization() {
    OPTIMIZATION_ENABLED.store(true, Ordering::Relaxed);
}

/// Disables global optimization features.
///
/// When disabled, standard allocation methods will be used.
/// This can be useful for debugging or reducing memory footprint.
#[allow(dead_code)]
pub fn disable_optimization() {
    OPTIMIZATION_ENABLED.store(false, Ordering::Relaxed);
}

/// Checks if global optimization is currently enabled.
///
/// # Returns
/// `true` if optimization is enabled, `false` otherwise
#[allow(dead_code)]
pub fn is_optimization_enabled() -> bool {
    OPTIMIZATION_ENABLED.load(Ordering::Relaxed)
}

/// Creates a pre-allocated String with the specified capacity if optimization is enabled.
///
/// This function uses compile-time inlining for maximum performance.
///
/// # Arguments
/// * `capacity` - Desired string capacity in bytes
///
/// # Returns
/// A String with pre-allocated capacity if optimization is enabled,
/// or an empty String otherwise
#[inline(always)]
#[allow(dead_code)]
pub fn optimize_string_allocation(capacity: usize) -> String {
    if is_optimization_enabled() {
        String::with_capacity(capacity)
    } else {
        String::new()
    }
}

/// Creates a pre-allocated Vec with the specified capacity if optimization is enabled.
///
/// This function uses compile-time inlining for maximum performance.
///
/// # Arguments
/// * `capacity` - Desired vector capacity
///
/// # Returns
/// A Vec with pre-allocated capacity if optimization is enabled,
/// or an empty Vec otherwise
#[inline(always)]
#[allow(dead_code)]
pub fn optimize_vec_allocation<T>(capacity: usize) -> Vec<T> {
    if is_optimization_enabled() {
        Vec::with_capacity(capacity)
    } else {
        Vec::new()
    }
}

/// A thread-safe pool for reusing String allocations.
///
/// StringPool maintains a pool of pre-allocated strings to reduce
/// allocation overhead in high-frequency logging scenarios.
///
/// # Thread Safety
/// This struct is thread-safe and can be shared across threads using Arc.
///
/// # Examples
///
/// ```rust
/// use logly::utils::performance::StringPool;
///
/// let pool = StringPool::new(100);
/// let s = pool.acquire();
/// // Use the string...
/// pool.release(s);
/// ```
#[allow(dead_code)]
pub struct StringPool {
    pool: Arc<parking_lot::Mutex<Vec<String>>>,
    max_size: usize,
}

impl StringPool {
    /// Creates a new StringPool with the specified maximum size.
    ///
    /// # Arguments
    /// * `max_size` - Maximum number of strings to keep in the pool
    ///
    /// # Returns
    /// A new StringPool instance
    #[allow(dead_code)]
    pub fn new(max_size: usize) -> Self {
        Self {
            pool: Arc::new(parking_lot::Mutex::new(Vec::with_capacity(max_size))),
            max_size,
        }
    }

    /// Acquires a String from the pool.
    ///
    /// If the pool is empty, creates a new String with 256 bytes capacity.
    ///
    /// # Returns
    /// A String from the pool or a newly allocated String
    #[allow(dead_code)]
    pub fn acquire(&self) -> String {
        let mut pool = self.pool.lock();
        pool.pop().unwrap_or_else(|| String::with_capacity(256))
    }

    /// Returns a String to the pool for reuse.
    ///
    /// The string is cleared before being added back to the pool.
    /// If the pool is full, the string is dropped.
    ///
    /// # Arguments
    /// * `s` - The String to return to the pool
    #[allow(dead_code)]
    pub fn release(&self, mut s: String) {
        s.clear();
        let mut pool = self.pool.lock();
        if pool.len() < self.max_size {
            pool.push(s);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_performance_config_defaults() {
        let config = PerformanceConfig::default();
        assert_eq!(config.buffer_size, 8192);
        assert_eq!(config.flush_interval_ms, 100);
        assert_eq!(config.max_buffered_lines, 1000);
        assert!(config.async_enabled);
    }

    #[test]
    fn test_performance_config_builder() {
        let config = PerformanceConfig::new()
            .with_buffer_size(16384)
            .with_flush_interval(200)
            .with_max_buffered_lines(2000)
            .with_async(false);

        assert_eq!(config.buffer_size, 16384);
        assert_eq!(config.flush_interval_ms, 200);
        assert_eq!(config.max_buffered_lines, 2000);
        assert!(!config.async_enabled);
    }

    #[test]
    fn test_optimization_toggle() {
        enable_optimization();
        assert!(is_optimization_enabled());

        disable_optimization();
        assert!(!is_optimization_enabled());

        enable_optimization();
    }

    #[test]
    fn test_string_pool() {
        let pool = StringPool::new(10);
        let s1 = pool.acquire();
        assert!(s1.is_empty());

        pool.release(s1);

        let s2 = pool.acquire();
        assert!(s2.is_empty());
    }
}
