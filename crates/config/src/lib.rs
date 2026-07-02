//! Serialization-friendly configuration value types.
//!
//! These are the canonical Rust-side config shapes that the Python Pydantic
//! models mirror/validate before crossing the `PyO3` boundary. Every field is
//! explicit and documented so that defaults are never hidden.
//!
//! # Module Structure
//!
//! - **Enums**: [`RotationPolicy`], [`RetentionPolicy`], [`CompressionCodec`], [`EnqueueMode`]
//! - **Config structs**: [`SinkConfig`], [`LoggerConfig`]
//! - **Parser functions**: [`parse_size`], [`resolve_rotation_policy`], [`resolve_retention_policy`], [`resolve_compression_codec`]
//! - **Serialization helpers**: [`strip_ansi_markup`], [`env_config_overrides`]

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use error::{LoglyError, LoglyResult};

/// Sink enqueue behavior.
///
/// Controls whether log records are dispatched synchronously on the caller's
/// thread or asynchronously via a background worker.
///
/// # Examples
///
/// ```rust
/// use config::EnqueueMode;
///
/// assert_eq!(EnqueueMode::default(), EnqueueMode::Synchronous);
/// ```
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub enum EnqueueMode {
    /// Dispatch on the caller thread (blocking).
    ///
    /// The log call blocks until the record is written. This is the simplest
    /// and most predictable mode.
    #[default]
    Synchronous,
    /// Dispatch using a background worker thread.
    ///
    /// The log call returns immediately; records are queued and written
    /// asynchronously. Useful for high-throughput scenarios where blocking
    /// the caller is unacceptable.
    Background,
}

/// Rotation policy for file sinks.
///
/// Determines when log files should be rotated (closed and a new file opened).
/// Supports time-based, size-based, and calendar-based rotation strategies.
///
/// # Examples
///
/// ```rust
/// use config::{RotationPolicy, resolve_rotation_policy};
///
/// // Named intervals
/// assert_eq!(resolve_rotation_policy("daily").unwrap(), RotationPolicy::IntervalSeconds(86400));
/// assert_eq!(resolve_rotation_policy("hourly").unwrap(), RotationPolicy::IntervalSeconds(3600));
///
/// // Size-based
/// assert_eq!(resolve_rotation_policy("10 MB").unwrap(), RotationPolicy::SizeBytes(10_000_000));
///
/// // Clock rotation
/// assert_eq!(resolve_rotation_policy("00:00").unwrap(), RotationPolicy::ClockRotation("00:00".to_owned()));
///
/// // Weekday rotation
/// assert_eq!(resolve_rotation_policy("monday").unwrap(), RotationPolicy::WeekdayRotation(0));
/// ```
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub enum RotationPolicy {
    /// Rotation is disabled.
    #[default]
    Never,
    /// Rotate when the file reaches this many bytes.
    SizeBytes(u64),
    /// Rotate after this many seconds since the file was created/last rotated.
    IntervalSeconds(u64),
    /// Rotate at a specific time of day (HH:MM format, 24-hour).
    ClockRotation(String),
    /// Rotate on a specific day of the week (0=Monday through 6=Sunday).
    WeekdayRotation(u8),
    /// Rotate on a specific day of the week at a specific time.
    /// Tuple of `(weekday_index, time_string)`.
    WeekdayClockRotation(u8, String),
}

/// Retention policy for rotated files.
///
/// Controls how many rotated log files are kept and/or how long they are
/// retained before deletion. Both fields are optional; if both are `None`,
/// all rotated files are kept indefinitely.
///
/// # Examples
///
/// ```rust
/// use config::{RetentionPolicy, resolve_retention_policy};
///
/// // Keep at most 10 files
/// let p = resolve_retention_policy("10").unwrap();
/// assert_eq!(p.count, Some(10));
/// assert_eq!(p.seconds, None);
///
/// // Keep files for 30 days
/// let p = resolve_retention_policy("30 days").unwrap();
/// assert_eq!(p.count, None);
/// assert_eq!(p.seconds, Some(30 * 86400));
/// ```
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct RetentionPolicy {
    /// Maximum number of rotated files to keep.
    ///
    /// When `None`, there is no limit on the number of files retained.
    pub count: Option<u32>,
    /// Maximum age of rotated files in seconds.
    ///
    /// When `None`, files are not deleted based on age.
    pub seconds: Option<u64>,
}

/// Compression codec for rotated files.
///
/// Specifies the compression algorithm applied to rotated log files.
/// The codec determines both the file extension and the compression ratio.
///
/// # Supported Codecs
///
/// | Codec | Extension | Notes |
/// |---|---|---|
/// | `None` | `.log` | No compression |
/// | `Gzip` | `.gz` | Fast, good ratio |
/// | `Zip` | `.zip` | Archive format |
/// | `Bz2` | `.bz2` | Slow, high ratio |
/// | `Xz` | `.xz` | Slowest, best ratio |
/// | `Zstd` | `.zst` | Fast, excellent ratio |
///
/// # Examples
///
/// ```rust
/// use config::{CompressionCodec, resolve_compression_codec};
///
/// assert_eq!(CompressionCodec::Gzip.to_string(), "gzip");
/// assert_eq!(resolve_compression_codec("gz").unwrap(), CompressionCodec::Gzip);
/// assert_eq!(resolve_compression_codec("tar.gz").unwrap(), CompressionCodec::Gzip);
/// ```
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub enum CompressionCodec {
    /// No compression. Files are stored as plain text.
    #[default]
    None,
    /// Gzip compression. Good balance of speed and compression ratio.
    Gzip,
    /// Zip archive compression. Creates standard ZIP archives.
    Zip,
    /// Bzip2 compression. Slower but higher compression ratio than gzip.
    Bz2,
    /// XZ/LZMA compression. Best compression ratio but slowest.
    Xz,
    /// Zstandard compression. Excellent speed and ratio; recommended for most use cases.
    Zstd,
    /// Tar archive without compression.
    Tar,
}

/// Displays the codec name in lowercase (e.g., `"gzip"`, `"zstd"`).
impl std::fmt::Display for CompressionCodec {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::None => write!(f, "none"),
            Self::Gzip => write!(f, "gzip"),
            Self::Zip => write!(f, "zip"),
            Self::Bz2 => write!(f, "bz2"),
            Self::Xz => write!(f, "xz"),
            Self::Zstd => write!(f, "zstd"),
            Self::Tar => write!(f, "tar"),
        }
    }
}

/// Configuration shared by sink implementations.
///
/// Each sink (console, file, callback) is configured via this struct. The
/// defaults produce a sensible INFO-level console output with no rotation.
///
/// # Default Values
///
/// | Field | Default |
/// |---|---|
/// | `level` | `"INFO"` |
/// | `format` | `"{level} \| {message}"` |
/// | `colorize` | `None` (auto-detect) |
/// | `serialize` | `false` |
/// | `enqueue` | `Synchronous` |
/// | `rotation` | `Never` |
/// | `retention` | unlimited |
/// | `compression` | `None` |
/// | `append` | `true` |
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SinkConfig {
    /// Minimum accepted level name.
    ///
    /// Records below this level are filtered out. Case-insensitive.
    pub level: String,
    /// Output format template.
    ///
    /// Supports placeholder tokens like `{level}`, `{message}`, `{time}`, etc.
    /// See `TemplateFormatter` for the full token reference.
    pub format: String,
    /// Whether ANSI colors are emitted.
    ///
    /// - `None`: auto-detect (enabled for TTY, disabled otherwise)
    /// - `Some(true)`: always emit colors
    /// - `Some(false)`: never emit colors
    pub colorize: Option<bool>,
    /// Whether JSON output is emitted.
    ///
    /// When `true`, the sink uses `JsonFormatter` instead of `TemplateFormatter`.
    pub serialize: bool,
    /// Enqueue mode for this sink.
    ///
    /// Controls whether records are written synchronously or via a background thread.
    pub enqueue: EnqueueMode,
    /// Rotation policy.
    ///
    /// Determines when log files are rotated. Defaults to `Never`.
    pub rotation: RotationPolicy,
    /// Retention policy.
    ///
    /// Controls how many rotated files are kept and for how long.
    pub retention: RetentionPolicy,
    /// Compression codec.
    ///
    /// Applied to rotated files. Defaults to `None`.
    pub compression: CompressionCodec,
    /// Whether to append to existing files (`true`) or overwrite (`false`).
    ///
    /// When `false`, the file is truncated on open.
    pub append: bool,
}

/// Default configuration for a sink: INFO level, basic format, no rotation.
impl Default for SinkConfig {
    fn default() -> Self {
        Self {
            level: String::from("INFO"),
            format: String::from("{level} | {message}"),
            colorize: None,
            serialize: false,
            enqueue: EnqueueMode::Synchronous,
            rotation: RotationPolicy::Never,
            retention: RetentionPolicy::default(),
            compression: CompressionCodec::None,
            append: true,
        }
    }
}

/// Top-level logger configuration.
///
/// Contains the list of sink configurations and any logger names that should
/// be disabled by default.
///
/// # Examples
///
/// ```rust
/// use config::LoggerConfig;
///
/// let config = LoggerConfig::default();
/// assert!(config.sinks.is_empty());
/// assert!(config.disabled.is_empty());
/// ```
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct LoggerConfig {
    /// Sink configurations to install.
    ///
    /// Each entry defines a separate output destination with its own format,
    /// level filter, and rotation settings.
    pub sinks: Vec<SinkConfig>,
    /// Logger names disabled by default.
    ///
    /// Loggers matching these names will not produce output until explicitly
    /// enabled. Useful for suppressing noisy third-party loggers.
    pub disabled: Vec<String>,
}

/// Strips `<tag>` color markup and converts to ANSI escape sequences.
///
/// # Examples
///
/// ```rust
/// use config::strip_ansi_markup;
///
/// let result = strip_ansi_markup("<red>hello</red>");
/// assert!(result.contains("\x1b[31m"));
/// assert!(result.contains("hello"));
/// ```
#[must_use]
pub fn strip_ansi_markup(text: &str) -> String {
    let mut result = text.to_owned();
    let tags = [
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "black",
        "bold",
        "dim",
        "underline",
        "blink",
        "italic",
        "strike",
        "reverse",
    ];
    for tag in &tags {
        let code = color::color_code(tag);
        if !code.is_empty() {
            let open = format!("<{tag}>");
            let close = format!("</{tag}>");
            result = result.replace(&open, &format!("\x1b[{code}m"));
            result = result.replace(&close, "\x1b[0m");
        }
    }
    // Strip any remaining unrecognized tags (skip < that starts a format spec like <8)
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

/// Parses a size string like "10 MB", "500 KB", "1 GiB" into bytes.
///
/// # Examples
///
/// ```rust
/// use config::parse_size;
///
/// assert_eq!(parse_size("10 MB"), 10_000_000);
/// assert_eq!(parse_size("1 KiB"), 1_024);
/// assert_eq!(parse_size("500"), 500);
/// ```
#[must_use]
pub fn parse_size(text: &str) -> u64 {
    let units: std::collections::HashMap<&str, u64> = [
        ("b", 1),
        ("kb", 1_000),
        ("kib", 1_024),
        ("mb", 1_000_000),
        ("mib", 1_048_576),
        ("gb", 1_000_000_000),
        ("gib", 1_073_741_824),
    ]
    .into_iter()
    .collect();
    let cleaned = text.replace(' ', "").to_lowercase();
    let number_part: String = cleaned.chars().take_while(char::is_ascii_digit).collect();
    let suffix = &cleaned[number_part.len()..];
    let suffix_str = if suffix.is_empty() { "b" } else { suffix };
    let number: u64 = number_part.parse().unwrap_or(0);
    number * units.get(suffix_str).unwrap_or(&1)
}

/// Reads environment variables with the `LOGLY_` prefix and returns config overrides.
///
/// Supported variables:
/// - `LOGLY_LEVEL` — default level
/// - `LOGLY_FORMAT` — default format
/// - `LOGLY_COLORIZE` — "YES"/"NO"
/// - `LOGLY_SERIALIZE` — "YES"/"NO"
/// - `LOGLY_BACKTRACE` — "YES"/"NO"
/// - `LOGLY_DIAGNOSE` — "YES"/"NO"
///
/// # Examples
///
/// ```rust
/// use config::env_config_overrides;
/// let overrides = env_config_overrides();
/// ```
#[must_use]
pub fn env_config_overrides() -> std::collections::HashMap<String, String> {
    let mut overrides = std::collections::HashMap::new();
    for (key, value) in std::env::vars() {
        if let Some(stripped) = key.strip_prefix("LOGLY_") {
            overrides.insert(stripped.to_lowercase(), value);
        }
    }
    overrides
}

/// Resolves a compression codec from a string, including common aliases.
///
/// # Errors
///
/// Returns `LoglyError::Config` if the codec string is not recognized.
///
/// # Examples
///
/// ```rust
/// use config::{resolve_compression_codec, CompressionCodec};
///
/// assert_eq!(resolve_compression_codec("gz").unwrap(), CompressionCodec::Gzip);
/// assert_eq!(resolve_compression_codec("tar.gz").unwrap(), CompressionCodec::Gzip);
/// ```
pub fn resolve_compression_codec(value: &str) -> LoglyResult<CompressionCodec> {
    let text = value.trim().to_lowercase();
    let aliases: std::collections::HashMap<&str, &str> = [
        ("gz", "gzip"),
        ("tar.gz", "gzip"),
        ("tgz", "gzip"),
        ("tar.bz2", "bz2"),
        ("tar.xz", "xz"),
    ]
    .into_iter()
    .collect();
    let normalized = aliases.get(text.as_str()).copied().unwrap_or(text.as_str());
    match normalized {
        "none" => Ok(CompressionCodec::None),
        "gzip" => Ok(CompressionCodec::Gzip),
        "zip" => Ok(CompressionCodec::Zip),
        "bz2" => Ok(CompressionCodec::Bz2),
        "xz" | "lzma" => Ok(CompressionCodec::Xz),
        "zstd" => Ok(CompressionCodec::Zstd),
        "tar" => Ok(CompressionCodec::Tar),
        _ => Err(LoglyError::Config(format!(
            "unsupported compression codec: {value}"
        ))),
    }
}

/// Resolves a rotation policy from a string specification.
///
/// # Errors
///
/// Returns `LoglyError::Config` if the specification is invalid.
///
/// # Examples
///
/// ```rust
/// use config::{resolve_rotation_policy, RotationPolicy};
///
/// assert_eq!(resolve_rotation_policy("daily").unwrap(), RotationPolicy::IntervalSeconds(86400));
/// assert_eq!(resolve_rotation_policy("10 MB").unwrap(), RotationPolicy::SizeBytes(10_000_000));
/// assert_eq!(resolve_rotation_policy("00:00").unwrap(), RotationPolicy::ClockRotation("00:00".to_owned()));
/// assert_eq!(resolve_rotation_policy("monday").unwrap(), RotationPolicy::WeekdayRotation(0));
/// ```
pub fn resolve_rotation_policy(value: &str) -> LoglyResult<RotationPolicy> {
    let text = value.trim().to_lowercase();
    match text.as_str() {
        "never" | "none" | "" => Ok(RotationPolicy::Never),
        "daily" | "day" => Ok(RotationPolicy::IntervalSeconds(86_400)),
        "hourly" | "hour" => Ok(RotationPolicy::IntervalSeconds(3_600)),
        "weekly" | "week" => Ok(RotationPolicy::IntervalSeconds(604_800)),
        "monthly" | "month" => Ok(RotationPolicy::IntervalSeconds(2_592_000)),
        "yearly" | "year" => Ok(RotationPolicy::IntervalSeconds(31_536_000)),
        "minutely" | "minute" => Ok(RotationPolicy::IntervalSeconds(60)),
        _ => {
            // Check for combined weekday+clock: "friday at 18:00", "monday at 03:30"
            if let Some(at_pos) = text.find(" at ") {
                let day_part = text[..at_pos].trim();
                let time_part = text[at_pos + 4..].trim();
                let weekdays = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ];
                if let Some(idx) = weekdays.iter().position(|&d| d == day_part) {
                    // Validate time part as HH:MM
                    if time_part.contains(':') && time_part.len() <= 5 {
                        let parts: Vec<&str> = time_part.split(':').collect();
                        if parts.len() == 2
                            && let (Ok(h), Ok(m)) =
                                (parts[0].parse::<u32>(), parts[1].parse::<u32>())
                            && h <= 23
                            && m <= 59
                        {
                            #[expect(
                                clippy::cast_possible_truncation,
                                reason = "weekday index is always 0..6"
                            )]
                            return Ok(RotationPolicy::WeekdayClockRotation(
                                idx as u8,
                                time_part.to_owned(),
                            ));
                        }
                    }
                }
            }
            // Check for quantity-based time rotation: "1 day", "12 hours", "30 minutes", "10 seconds", "1 week", "1 month"
            if let Some(secs) = parse_time_quantity(&text) {
                return Ok(RotationPolicy::IntervalSeconds(secs));
            }
            // Check for clock rotation (HH:MM)
            if text.contains(':') && text.len() <= 5 {
                let parts: Vec<&str> = text.split(':').collect();
                if parts.len() == 2
                    && let (Ok(h), Ok(m)) = (parts[0].parse::<u32>(), parts[1].parse::<u32>())
                    && h <= 23
                    && m <= 59
                {
                    return Ok(RotationPolicy::ClockRotation(value.trim().to_owned()));
                }
            }
            // Check for weekday rotation
            let weekdays = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ];
            for (i, day) in weekdays.iter().enumerate() {
                if text == *day {
                    #[expect(
                        clippy::cast_possible_truncation,
                        reason = "weekday index is always 0..6"
                    )]
                    let weekday = i as u8;
                    return Ok(RotationPolicy::WeekdayRotation(weekday));
                }
            }
            // Check for size-based rotation — only match if text looks like a size
            let has_size_suffix = text.ends_with("kb")
                || text.ends_with("mb")
                || text.ends_with("gb")
                || text.ends_with('b')
                || text.ends_with("kib")
                || text.ends_with("mib")
                || text.ends_with("gib");
            let bytes = parse_size(&text);
            if has_size_suffix && bytes > 0 {
                return Ok(RotationPolicy::SizeBytes(bytes));
            }
            // Also match pure numbers as bytes
            if let Ok(n) = text.parse::<u64>() {
                return Ok(RotationPolicy::SizeBytes(n));
            }
            Err(LoglyError::Config(format!(
                "invalid rotation specification: {value}"
            )))
        }
    }
}

/// Resolves a retention policy from a string specification.
///
/// # Errors
///
/// Returns `LoglyError::Config` if the specification is invalid.
///
/// # Examples
///
/// ```rust
/// use config::resolve_retention_policy;
///
/// assert_eq!(resolve_retention_policy("30 days").unwrap().seconds, Some(30 * 86400));
/// assert_eq!(resolve_retention_policy("10").unwrap().count, Some(10));
/// assert_eq!(resolve_retention_policy("5 minutes").unwrap().seconds, Some(300));
/// assert_eq!(resolve_retention_policy("30 seconds").unwrap().seconds, Some(30));
/// ```
pub fn resolve_retention_policy(value: &str) -> LoglyResult<RetentionPolicy> {
    let text = value.trim().to_lowercase();
    if let Ok(count) = text.parse::<u32>() {
        return Ok(RetentionPolicy {
            count: Some(count),
            seconds: None,
        });
    }
    // Extract the numeric prefix
    let num_str: String = text
        .chars()
        .take_while(|c| c.is_ascii_digit() || *c == '.')
        .collect();
    let num: u64 = num_str.parse().unwrap_or(0);
    // Try full word forms first (longest first to avoid suffix collisions)
    if text.ends_with(" years")
        || text.ends_with(" year")
        || text.ends_with(" yrs")
        || text.ends_with(" yr")
    {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 31_536_000),
        });
    }
    if text.ends_with(" months") || text.ends_with(" month") {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 2_592_000),
        });
    }
    if text.ends_with(" weeks") || text.ends_with(" week") {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 604_800),
        });
    }
    if text.ends_with(" minutes") || text.ends_with(" minute") {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 60),
        });
    }
    if text.ends_with(" days") || text.ends_with(" day") {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 86_400),
        });
    }
    if text.ends_with(" hours") || text.ends_with(" hour") {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 3_600),
        });
    }
    if text.ends_with(" seconds") || text.ends_with(" second") {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num),
        });
    }
    // Short abbreviations — only for compact forms like "30s", "5min", "2h", "7d", "2w"
    if text.ends_with("min") {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 60),
        });
    }
    if num > 0 && text.ends_with('w') {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 604_800),
        });
    }
    if num > 0 && text.ends_with('d') {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 86_400),
        });
    }
    if num > 0 && text.ends_with('h') {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num * 3_600),
        });
    }
    if num > 0 && text.ends_with('s') {
        return Ok(RetentionPolicy {
            count: None,
            seconds: Some(num),
        });
    }
    Err(LoglyError::Config(format!(
        "invalid retention specification: {value}"
    )))
}

/// Parses a time quantity string like "1 day", "12 hours", "30 minutes", "10 seconds", "1 week", "1 month" into seconds.
fn parse_time_quantity(text: &str) -> Option<u64> {
    let num_str: String = text
        .chars()
        .take_while(|c| c.is_ascii_digit() || *c == '.')
        .collect();
    let num: u64 = num_str.parse().ok()?;
    if num == 0 {
        return None;
    }
    let unit = text[num_str.len()..].trim();
    match unit {
        "second" | "seconds" | "sec" | "secs" => Some(num),
        "minute" | "minutes" | "min" | "mins" => Some(num * 60),
        "hour" | "hours" | "hr" | "hrs" => Some(num * 3_600),
        "day" | "days" => Some(num * 86_400),
        "week" | "weeks" | "wk" | "wks" => Some(num * 604_800),
        "month" | "months" => Some(num * 2_592_000),
        "year" | "years" | "yr" | "yrs" => Some(num * 31_536_000),
        _ => None,
    }
}

/// Parses a rotation policy to its string representation.
///
/// # Errors
/// Returns a `LoglyError` if parsing fails.
pub fn parse_rotation_to_str(value: &str) -> LoglyResult<String> {
    let text = value.trim().to_lowercase();
    if text.is_empty() || text == "never" || text == "none" {
        return Ok("never".to_owned());
    }
    if text == "daily" || text == "day" {
        return Ok("interval:86400".to_owned());
    }
    if text == "hourly" || text == "hour" {
        return Ok("interval:3600".to_owned());
    }
    if text == "weekly" || text == "week" {
        return Ok("interval:604800".to_owned());
    }
    if text == "monthly" || text == "month" {
        return Ok("interval:2592000".to_owned());
    }
    if text == "yearly" || text == "year" {
        return Ok("interval:31536000".to_owned());
    }
    if text == "minutely" || text == "minute" {
        return Ok("interval:60".to_owned());
    }
    // Check for quantity-based time rotation: "1 day", "12 hours", etc.
    if let Some(secs) = parse_time_quantity(&text) {
        return Ok(format!("interval:{secs}"));
    }
    // Check for combined weekday+clock: "friday at 18:00"
    if let Some(at_pos) = text.find(" at ") {
        let day_part = text[..at_pos].trim();
        let time_part = text[at_pos + 4..].trim();
        let weekdays = [
            ("monday", 0),
            ("tuesday", 1),
            ("wednesday", 2),
            ("thursday", 3),
            ("friday", 4),
            ("saturday", 5),
            ("sunday", 6),
        ];
        if let Some((_, val)) = weekdays.iter().find(|(d, _)| *d == day_part) {
            return Ok(format!("weekday_clock:{val}:{time_part}"));
        }
    }
    if text.contains(':') && text.len() <= 5 {
        return Ok(format!("clock:{}", value.trim()));
    }
    let weekdays = [
        ("monday", 0),
        ("tuesday", 1),
        ("wednesday", 2),
        ("thursday", 3),
        ("friday", 4),
        ("saturday", 5),
        ("sunday", 6),
    ];
    for (day, val) in weekdays {
        if text == day {
            return Ok(format!("weekday:{val}"));
        }
    }
    let bytes = parse_size(&text);
    if bytes > 0 {
        return Ok(format!("size:{bytes}"));
    }
    Err(LoglyError::Config(format!(
        "invalid rotation specification: {value}"
    )))
}

/// Parses a retention policy to its string representation.
///
/// # Errors
/// Returns a `LoglyError` if parsing fails.
pub fn parse_retention_to_str(value: &str) -> LoglyResult<String> {
    match resolve_retention_policy(value) {
        Ok(policy) => {
            let count_str = policy.count.map_or("None".to_owned(), |c| c.to_string());
            let seconds_str = policy.seconds.map_or("None".to_owned(), |s| s.to_string());
            Ok(format!("{count_str}:{seconds_str}"))
        }
        Err(e) => Err(e),
    }
}

/// Parses a compression policy to its string representation.
///
/// # Errors
/// Returns a `LoglyError` if parsing fails.
pub fn parse_compression_to_str(value: &str) -> LoglyResult<String> {
    match resolve_compression_codec(value) {
        Ok(codec) => Ok(codec.to_string()),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sink_config_defaults_are_sane() {
        let cfg = SinkConfig::default();
        assert_eq!(cfg.level, "INFO");
        assert!(!cfg.serialize);
        assert!(cfg.append);
        assert_eq!(cfg.rotation, RotationPolicy::Never);
        assert_eq!(cfg.compression, CompressionCodec::None);
    }

    #[test]
    fn enqueue_mode_default_is_synchronous() {
        assert_eq!(EnqueueMode::default(), EnqueueMode::Synchronous);
    }

    #[test]
    fn compression_codec_display() {
        assert_eq!(CompressionCodec::Gzip.to_string(), "gzip");
        assert_eq!(CompressionCodec::Zstd.to_string(), "zstd");
        assert_eq!(CompressionCodec::None.to_string(), "none");
    }

    #[test]
    fn rotation_policy_default_is_never() {
        assert_eq!(RotationPolicy::default(), RotationPolicy::Never);
    }

    #[test]
    fn resolve_rotation_clock_spec() {
        let policy = resolve_rotation_policy("00:00").unwrap();
        assert_eq!(policy, RotationPolicy::ClockRotation("00:00".to_owned()));
    }

    #[test]
    fn resolve_rotation_clock_spec_12_30() {
        let policy = resolve_rotation_policy("12:30").unwrap();
        assert_eq!(policy, RotationPolicy::ClockRotation("12:30".to_owned()));
    }

    #[test]
    fn resolve_rotation_weekday_monday() {
        let policy = resolve_rotation_policy("monday").unwrap();
        assert_eq!(policy, RotationPolicy::WeekdayRotation(0));
    }

    #[test]
    fn resolve_rotation_weekday_sunday() {
        let policy = resolve_rotation_policy("sunday").unwrap();
        assert_eq!(policy, RotationPolicy::WeekdayRotation(6));
    }

    #[test]
    fn resolve_rotation_invalid_clock() {
        let result = resolve_rotation_policy("25:00");
        assert!(result.is_err());
    }

    #[test]
    fn resolve_rotation_invalid_clock_format() {
        let result = resolve_rotation_policy("abc");
        assert!(result.is_err());
    }

    #[test]
    fn resolve_retention_seconds() {
        let policy = resolve_retention_policy("30 seconds").unwrap();
        assert_eq!(policy.seconds, Some(30));
        assert_eq!(policy.count, None);
    }

    #[test]
    fn resolve_retention_minutes() {
        let policy = resolve_retention_policy("5 minutes").unwrap();
        assert_eq!(policy.seconds, Some(300));
        assert_eq!(policy.count, None);
    }

    #[test]
    fn resolve_retention_hours() {
        let policy = resolve_retention_policy("2 hours").unwrap();
        assert_eq!(policy.seconds, Some(7200));
        assert_eq!(policy.count, None);
    }

    #[test]
    fn resolve_retention_days() {
        let policy = resolve_retention_policy("30 days").unwrap();
        assert_eq!(policy.seconds, Some(30 * 86400));
        assert_eq!(policy.count, None);
    }

    #[test]
    fn resolve_retention_weeks() {
        let policy = resolve_retention_policy("2 weeks").unwrap();
        assert_eq!(policy.seconds, Some(2 * 604_800));
        assert_eq!(policy.count, None);
    }

    #[test]
    fn resolve_retention_months() {
        let policy = resolve_retention_policy("3 months").unwrap();
        assert_eq!(policy.seconds, Some(3 * 2_592_000));
        assert_eq!(policy.count, None);
    }

    #[test]
    fn resolve_retention_count() {
        let policy = resolve_retention_policy("10").unwrap();
        assert_eq!(policy.count, Some(10));
        assert_eq!(policy.seconds, None);
    }

    #[test]
    fn resolve_retention_invalid() {
        let result = resolve_retention_policy("invalid");
        assert!(result.is_err());
    }

    #[test]
    fn resolve_retention_abbreviated_seconds() {
        let policy = resolve_retention_policy("30s").unwrap();
        assert_eq!(policy.seconds, Some(30));
    }

    #[test]
    fn resolve_retention_abbreviated_minutes() {
        let policy = resolve_retention_policy("5min").unwrap();
        assert_eq!(policy.seconds, Some(300));
    }

    #[test]
    fn resolve_retention_abbreviated_hours() {
        let policy = resolve_retention_policy("2h").unwrap();
        assert_eq!(policy.seconds, Some(7200));
    }

    #[test]
    fn resolve_retention_abbreviated_days() {
        let policy = resolve_retention_policy("7d").unwrap();
        assert_eq!(policy.seconds, Some(7 * 86400));
    }

    #[test]
    fn strip_ansi_markup_known_tag() {
        let result = strip_ansi_markup("<red>hello</red>");
        assert!(result.contains("\x1b[31m"));
        assert!(result.contains("hello"));
    }

    #[test]
    fn strip_ansi_markup_no_ansi() {
        assert_eq!(strip_ansi_markup("plain text"), "plain text");
    }

    #[test]
    fn strip_ansi_markup_nested_tags() {
        let result = strip_ansi_markup("<bold><red>x</red></bold>");
        assert!(result.contains("\x1b[1m"));
        assert!(result.contains("\x1b[31m"));
        assert!(result.contains('x'));
    }

    #[test]
    fn strip_ansi_markup_unknown_tag_stripped() {
        let result = strip_ansi_markup("<foobar>text</foobar>");
        assert_eq!(result, "text");
    }

    #[test]
    fn parse_size_ten_mb() {
        assert_eq!(parse_size("10 MB"), 10_000_000);
    }

    #[test]
    fn parse_size_five_hundred_kb() {
        assert_eq!(parse_size("500 KB"), 500_000);
    }

    #[test]
    fn parse_size_one_gib() {
        assert_eq!(parse_size("1 GiB"), 1_073_741_824);
    }

    #[test]
    fn parse_size_bare_number() {
        assert_eq!(parse_size("1024"), 1024);
    }

    #[test]
    fn parse_size_zero() {
        assert_eq!(parse_size("0"), 0);
    }

    #[test]
    fn parse_size_invalid_string() {
        assert_eq!(parse_size("abc"), 0);
    }

    #[test]
    fn resolve_compression_gz() {
        assert_eq!(
            resolve_compression_codec("gz").unwrap(),
            CompressionCodec::Gzip
        );
    }

    #[test]
    fn resolve_compression_gzip() {
        assert_eq!(
            resolve_compression_codec("gzip").unwrap(),
            CompressionCodec::Gzip
        );
    }

    #[test]
    fn resolve_compression_tgz() {
        assert_eq!(
            resolve_compression_codec("tgz").unwrap(),
            CompressionCodec::Gzip
        );
    }

    #[test]
    fn resolve_compression_zstd() {
        assert_eq!(
            resolve_compression_codec("zstd").unwrap(),
            CompressionCodec::Zstd
        );
    }

    #[test]
    fn resolve_compression_bz2() {
        assert_eq!(
            resolve_compression_codec("bz2").unwrap(),
            CompressionCodec::Bz2
        );
    }

    #[test]
    fn resolve_compression_xz() {
        assert_eq!(
            resolve_compression_codec("xz").unwrap(),
            CompressionCodec::Xz
        );
    }

    #[test]
    fn resolve_compression_zip() {
        assert_eq!(
            resolve_compression_codec("zip").unwrap(),
            CompressionCodec::Zip
        );
    }

    #[test]
    fn resolve_compression_none() {
        assert_eq!(
            resolve_compression_codec("none").unwrap(),
            CompressionCodec::None
        );
    }

    #[test]
    fn resolve_compression_off_errors() {
        assert!(resolve_compression_codec("off").is_err());
    }

    #[test]
    fn resolve_compression_invalid() {
        assert!(resolve_compression_codec("invalid").is_err());
    }

    #[test]
    fn resolve_rotation_size_10mb() {
        assert_eq!(
            resolve_rotation_policy("10 MB").unwrap(),
            RotationPolicy::SizeBytes(10_000_000)
        );
    }

    #[test]
    fn resolve_rotation_size_1gb() {
        assert_eq!(
            resolve_rotation_policy("1 GB").unwrap(),
            RotationPolicy::SizeBytes(1_000_000_000)
        );
    }

    #[test]
    fn resolve_rotation_daily() {
        assert_eq!(
            resolve_rotation_policy("daily").unwrap(),
            RotationPolicy::IntervalSeconds(86400)
        );
    }

    #[test]
    fn resolve_rotation_hourly() {
        assert_eq!(
            resolve_rotation_policy("hourly").unwrap(),
            RotationPolicy::IntervalSeconds(3600)
        );
    }

    #[test]
    fn resolve_rotation_weekly() {
        assert_eq!(
            resolve_rotation_policy("weekly").unwrap(),
            RotationPolicy::IntervalSeconds(604_800)
        );
    }

    #[test]
    fn resolve_retention_singular_second() {
        let policy = resolve_retention_policy("1 second").unwrap();
        assert_eq!(policy.seconds, Some(1));
    }

    #[test]
    fn resolve_retention_plural_seconds() {
        let policy = resolve_retention_policy("1 seconds").unwrap();
        assert_eq!(policy.seconds, Some(1));
    }

    #[test]
    fn resolve_retention_count_only_no_seconds() {
        let policy = resolve_retention_policy("5").unwrap();
        assert_eq!(policy.count, Some(5));
        assert_eq!(policy.seconds, None);
    }

    #[test]
    fn parse_compression_to_str_roundtrip() {
        let result = parse_compression_to_str("gzip").unwrap();
        assert_eq!(result, "gzip");
    }

    #[test]
    fn parse_compression_to_str_invalid() {
        assert!(parse_compression_to_str("invalid").is_err());
    }

    #[test]
    fn parse_retention_to_str_count() {
        let result = parse_retention_to_str("10").unwrap();
        assert_eq!(result, "10:None");
    }

    #[test]
    fn parse_retention_to_str_seconds() {
        let result = parse_retention_to_str("30 seconds").unwrap();
        assert_eq!(result, "None:30");
    }

    #[test]
    fn parse_retention_to_str_invalid() {
        assert!(parse_retention_to_str("invalid").is_err());
    }

    #[test]
    fn compression_codec_display_all_variants() {
        assert_eq!(CompressionCodec::None.to_string(), "none");
        assert_eq!(CompressionCodec::Gzip.to_string(), "gzip");
        assert_eq!(CompressionCodec::Zip.to_string(), "zip");
        assert_eq!(CompressionCodec::Bz2.to_string(), "bz2");
        assert_eq!(CompressionCodec::Xz.to_string(), "xz");
        assert_eq!(CompressionCodec::Zstd.to_string(), "zstd");
    }
}
