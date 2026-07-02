//! Native formatters for Logly records.
//!
//! Provides a template formatter with placeholder tokens (including brace-style
//! format specs like `{level:<8}`), a structured JSON formatter, and the
//! [`Formatter`] trait for custom formatters.
//!
//! # Formatter Types
//!
//! - [`TemplateFormatter`]: Placeholder-based formatting with alignment support
//! - [`JsonFormatter`]: Structured JSON output with optional pretty-printing
//! - [`CustomFormatter`]: Closure-based formatting for arbitrary logic
//!
//! # Available Tokens (`TemplateFormatter`)
//!
//! | Token | Description |
//! |---|---|
//! | `{time}` | Formatted timestamp |
//! | `{level}` | Level name |
//! | `{level_no}` | Numeric priority |
//! | `{level_icon}` | Level icon/emoji |
//! | `{message}` | Log message |
//! | `{name}` | Logger name |
//! | `{file}` | Source file path |
//! | `{line}` | Source line number |
//! | `{function}` | Function name |
//! | `{module}` | Module name |
//! | `{thread}` | Thread name |
//! | `{process}` | Process ID |
//! | `{extra[key]}` | Bound context value (bracket syntax) |
//! | `{extra.key}` | Bound context value (dot syntax) |

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use chrono::{DateTime, Local};
use error::LoglyResult;
use record::LogRecord;
use std::collections::BTreeMap;

/// Renders a record into sink-ready text.
///
/// All formatters implement this trait, which is the interface between the
/// logging engine and output sinks. Formatters must be `Send + Sync` to
/// support concurrent logging.
///
/// # Implementors
///
/// - [`TemplateFormatter`]
/// - [`JsonFormatter`]
/// - [`CustomFormatter<F>`]
pub trait Formatter: Send + Sync {
    /// Formats one record.
    ///
    /// # Errors
    ///
    /// Implementations return an error when rendering fails (e.g., template
    /// syntax errors, I/O failures).
    fn format(&self, record: &LogRecord) -> LoglyResult<String>;
}

/// Placeholder-based formatter with full Python-style format spec support.
///
/// Supports:
/// - `{time}`, `{time:FORMAT}` — formatted timestamp
/// - `{level}`, `{level:<8}`, `{level:>8}` — level name with alignment
/// - `{message}` — log message
/// - `{name}` — logger name
/// - `{file}` — source file path
/// - `{line}` — source line number
/// - `{function}` — function name
/// - `{thread}` — thread name
/// - `{process}` — process ID
/// - `{extra[key]}`, `{extra.key}` — bound context value
///
/// Format specs follow Python's `str.format()` mini-language:
/// - `<` left-align, `>` right-align, `^` center
/// - Width: `{level:<8}` pads to 8 chars
/// - Fill: `{level:*<8}` pads with `*`
///
/// # Examples
///
/// ```rust
/// use format::{TemplateFormatter, Formatter};
/// use levels::LogLevel;
/// use record::LogRecord;
///
/// let fmt = TemplateFormatter::new("{level:<8} | {message}");
/// let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "started").build();
/// let output = fmt.format(&record).unwrap();
/// assert_eq!(output, "INFO     | started");
/// ```
#[derive(Clone, Debug)]
pub struct TemplateFormatter {
    template: String,
    timestamp_format: String,
}

impl TemplateFormatter {
    /// Creates a template formatter with the given template string.
    ///
    /// The default timestamp format is `"%Y-%m-%d %H:%M:%S"`.
    #[must_use]
    pub fn new(template: impl Into<String>) -> Self {
        Self {
            template: template.into(),
            timestamp_format: String::from("%Y-%m-%d %H:%M:%S"),
        }
    }

    /// Sets the timestamp format string (strftime-style).
    ///
    /// Supports both strftime tokens (`%Y`, `%m`, `%d`) and brace-style
    /// tokens (`YYYY`, `MM`, `DD`). See [`convert_time_tokens`] for the
    /// full token reference.
    #[must_use]
    pub fn with_timestamp_format(mut self, format: impl Into<String>) -> Self {
        self.timestamp_format = format.into();
        self
    }
}

impl Default for TemplateFormatter {
    fn default() -> Self {
        Self::new("{level} | {message}")
    }
}

/// Parses a Python-style format spec like `<8`, `>10`, `^12`, `*^20`.
///
/// # Arguments
///
/// * `spec` - The format specification string (without surrounding `{}`)
///
/// # Returns
///
/// A tuple of `(alignment, width, fill_char)`:
/// - `alignment`: `<` (left), `>` (right), or `^` (center)
/// - `width`: Target width in characters
/// - `fill_char`: Character used for padding (default: space)
fn parse_format_spec(spec: &str) -> (char, usize, char) {
    if spec.is_empty() {
        return ('<', 0, ' ');
    }

    let mut fill_char = ' ';
    let mut align = '<';
    let rest;

    // Check for fill + align pattern: [fill][align][width]
    let first = spec.as_bytes()[0];
    let second_opt = spec.as_bytes().get(1).copied();

    match (first, second_opt) {
        // fill_char + align: e.g. "*^" or " >"
        (_, Some(b'<' | b'>' | b'^'))
            if first != b'<' && first != b'>' && first != b'^' && !first.is_ascii_digit() =>
        {
            fill_char = first as char;
            align = second_opt.unwrap() as char;
            rest = &spec[2..];
        }
        // align + width: e.g. "<8", ">10"
        (b'<' | b'>' | b'^', _) => {
            align = first as char;
            rest = &spec[1..];
        }
        // width only: e.g. "8"
        _ => {
            rest = spec;
        }
    }

    let width = rest.parse().unwrap_or(0);
    (align, width, fill_char)
}

/// Applies a format spec to a value string.
///
/// Pads the value according to the alignment, width, and fill character.
/// If the value is already wider than the target width, it is returned unchanged.
fn apply_format_spec(value: &str, spec: &str) -> String {
    if spec.is_empty() {
        return value.to_owned();
    }
    let (align, width, fill) = parse_format_spec(spec);
    if width == 0 {
        return value.to_owned();
    }
    let len = value.len();
    if len >= width {
        return value.to_owned();
    }
    let padding = width - len;
    let pad_str: String = std::iter::repeat_n(fill, padding).collect();
    match align {
        '>' => format!("{pad_str}{value}"),
        '^' => {
            let left = padding / 2;
            let right = padding - left;
            let left_pad: String = std::iter::repeat_n(fill, left).collect();
            let right_pad: String = std::iter::repeat_n(fill, right).collect();
            format!("{left_pad}{value}{right_pad}")
        }
        _ => format!("{value}{pad_str}"), // '<' is default
    }
}

/// Resolves a token name to its value from a log record.
///
/// # Supported Tokens
///
/// - `time` — formatted timestamp
/// - `level` — level name
/// - `level_no` — numeric priority
/// - `level_icon` — level icon/emoji
/// - `message` — log message
/// - `name` — logger name
/// - `file` — source file path
/// - `line` — source line number
/// - `column` — always empty (reserved)
/// - `function` — function name
/// - `module` — module name
/// - `thread` — thread name
/// - `process` — process ID
/// - `exception` — exception text
/// - `file_line` / `file_line_col` — `file:line` combined
/// - `filename` — basename of the source file
/// - `function_location` — `function (file:line)` or `file:line`
/// - `extra[key]` / `extra.key` — bound context value
fn resolve_token<'a>(
    name: &'a str,
    record: &'a LogRecord,
    timestamp_format: &'a str,
) -> Option<String> {
    match name {
        "time" => Some(format_timestamp(record, timestamp_format)),
        "level" => Some(record.level.name().to_owned()),
        "level_no" => Some(record.level.priority().to_string()),
        "level_icon" => Some(record.level.icon().unwrap_or("").to_owned()),
        "message" => Some(record.message.clone()),
        "name" => Some(record.name.clone()),
        "file" => Some(record.file.as_deref().unwrap_or("").to_owned()),
        "line" => Some(record.line.map_or_else(String::new, |l| l.to_string())),
        "column" => Some(String::new()),
        "function" => Some(record.function.as_deref().unwrap_or("").to_owned()),
        "module" => Some(record.module.as_deref().unwrap_or("").to_owned()),
        "thread" => Some(record.thread_name.as_deref().unwrap_or("").to_owned()),
        "process" => Some(record.process_id.to_string()),
        "exception" => Some(record.exception.clone().unwrap_or_default()),
        "file_line" | "file_line_col" => {
            let file = record.file.as_deref()?;
            match record.line {
                Some(l) => Some(format!("{file}:{l}")),
                None => Some(file.to_owned()),
            }
        }
        "filename" => {
            let file = record.file.as_deref()?;
            Some(
                std::path::Path::new(file)
                    .file_name()
                    .and_then(|n| n.to_str())
                    .unwrap_or(file)
                    .to_owned(),
            )
        }
        "function_location" => {
            let func = record.function.as_deref().unwrap_or("");
            let file = record.file.as_deref().unwrap_or("");
            match record.line {
                Some(l) => {
                    if func.is_empty() {
                        Some(format!("{file}:{l}"))
                    } else {
                        Some(format!("{func} ({file}:{l})"))
                    }
                }
                None => {
                    if func.is_empty() {
                        None
                    } else {
                        Some(func.to_owned())
                    }
                }
            }
        }
        _ if name.starts_with("extra[") && name.ends_with(']') => {
            let key = &name[6..name.len() - 1];
            record.extra.get(key).cloned()
        }
        _ if name.starts_with("extra.") => {
            let key = &name[6..];
            record.extra.get(key).cloned()
        }
        _ => None,
    }
}

/// Formats the template by replacing `{token}` and `{token:spec}` placeholders.
///
/// Supports escaped braces: `{{` produces a literal `{`, and `}}` produces a
/// literal `}`. Unknown tokens are preserved as-is (e.g., `{unknown}`).
fn format_template(template: &str, record: &LogRecord, timestamp_format: &str) -> String {
    let mut result = String::with_capacity(template.len());
    let mut chars = template.chars().peekable();

    while let Some(ch) = chars.next() {
        if ch == '{' {
            // Check for escaped brace: {{ -> {
            if chars.peek() == Some(&'{') {
                result.push('{');
                chars.next();
                continue;
            }

            // Read token name until } or :
            let mut token = String::new();
            let mut spec = String::new();
            let mut in_spec = false;

            for c in chars.by_ref() {
                if c == '}' {
                    break;
                } else if c == ':' && !in_spec {
                    in_spec = true;
                } else if in_spec {
                    spec.push(c);
                } else {
                    token.push(c);
                }
            }

            // Resolve token value
            let value = resolve_token(&token, record, timestamp_format)
                .unwrap_or_else(|| format!("{{{token}}}"));

            // Apply format spec
            if spec.is_empty() {
                result.push_str(&value);
            } else {
                result.push_str(&apply_format_spec(&value, &spec));
            }
        } else if ch == '}' {
            // Check for escaped brace: }} -> }
            if chars.peek() == Some(&'}') {
                result.push('}');
                chars.next();
            } else {
                result.push('}');
            }
        } else {
            result.push(ch);
        }
    }

    result
}

impl Formatter for TemplateFormatter {
    fn format(&self, record: &LogRecord) -> LoglyResult<String> {
        Ok(format_template(
            &self.template,
            record,
            &self.timestamp_format,
        ))
    }
}

/// Converts brace-style datetime tokens to strftime-style tokens.
///
/// Supports both brace-style (`YYYY`, `MM`, `DD`) and strftime-style (`%Y`,
/// `%m`, `%d`) tokens. Strftime tokens pass through unchanged.
///
/// # Token Reference
///
/// | Brace | Strftime | Description |
/// |---|---|---|
/// | `YYYY` | `%Y` | 4-digit year |
/// | `YY` | `%y` | 2-digit year |
/// | `MM` | `%m` | Month (01-12) |
/// | `DD` | `%d` | Day (01-31) |
/// | `HH` | `%H` | Hour 24h (00-23) |
/// | `hh` | `%I` | Hour 12h (01-12) |
/// | `mm` | `%M` | Minute (00-59) |
/// | `ss` | `%S` | Second (00-59) |
/// | `SSS` | `%.3f` | Milliseconds |
/// | `SS` | `%.2f` | Centiseconds |
/// | `S` | `%.f` | Sub-second |
/// | `A` | `%p` | AM/PM |
/// | `dddd` | `%A` | Full weekday name |
/// | `ddd` | `%a` | Short weekday name |
/// | `MMMM` | `%B` | Full month name |
/// | `MMM` | `%b` | Short month name |
///
/// # Examples
///
/// ```rust
/// use format::convert_time_tokens;
///
/// assert_eq!(convert_time_tokens("YYYY-MM-DD"), "%Y-%m-%d");
/// assert_eq!(convert_time_tokens("HH:mm:ss"), "%H:%M:%S");
/// assert_eq!(convert_time_tokens("%Y-%m-%d"), "%Y-%m-%d");
/// ```
#[must_use]
pub fn convert_time_tokens(format: &str) -> String {
    let mut result = String::with_capacity(format.len());
    let chars: Vec<char> = format.chars().collect();
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        if c == '%' {
            // Already strftime, pass through
            result.push(c);
            if i + 1 < chars.len() {
                result.push(chars[i + 1]);
                i += 2;
            } else {
                i += 1;
            }
            continue;
        }
        // Build a lookahead string from current position (up to 5 chars)
        let end = std::cmp::min(i + 5, chars.len());
        let collected: String = chars[i..end].iter().collect();
        // Match multi-character tokens (longest first)
        let skip = if collected.starts_with("dddd") {
            result.push_str("%A");
            4
        } else if collected.starts_with("MMMM") {
            result.push_str("%B");
            4
        } else if collected.starts_with("YYYY") {
            result.push_str("%Y");
            4
        } else if collected.starts_with("ddd") {
            result.push_str("%a");
            3
        } else if collected.starts_with("MMM") {
            result.push_str("%b");
            3
        } else if collected.starts_with("SSS") {
            result.push_str("%.3f");
            3
        } else if collected.starts_with("SS") {
            result.push_str("%.2f");
            2
        } else if collected.starts_with("YY") {
            result.push_str("%y");
            2
        } else if collected.starts_with("MM") {
            result.push_str("%m");
            2
        } else if collected.starts_with("DD") {
            result.push_str("%d");
            2
        } else if collected.starts_with("HH") {
            result.push_str("%H");
            2
        } else if collected.starts_with("hh") {
            result.push_str("%I");
            2
        } else if collected.starts_with("mm") {
            result.push_str("%M");
            2
        } else if collected.starts_with("ss") {
            result.push_str("%S");
            2
        } else if c == 'A' {
            result.push_str("%p");
            1
        } else if c == 'S' {
            result.push_str("%.f");
            1
        } else {
            result.push(c);
            1
        };
        i += skip;
    }
    result
}

/// Formats a timestamp using the given format string.
///
/// Supports both brace-style tokens (`YYYY`, `MM`, `DD`, etc.) and
/// strftime-style tokens (`%Y`, `%m`, `%d`, etc.).
///
/// # Arguments
///
/// * `record` - The log record containing the timestamp
/// * `format` - Format string (brace-style or strftime-style)
///
/// # Examples
///
/// ```rust
/// use format::format_timestamp;
/// use levels::LogLevel;
/// use record::LogRecord;
///
/// let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "test").build();
/// let ts = format_timestamp(&record, "YYYY-MM-DD");
/// assert!(ts.contains('-'));
/// ```
#[must_use]
pub fn format_timestamp(record: &LogRecord, format: &str) -> String {
    let duration = record
        .timestamp
        .duration_since(std::time::SystemTime::UNIX_EPOCH)
        .unwrap_or_default();
    let secs = duration.as_secs().cast_signed();
    let nsecs = duration.subsec_nanos();
    let dt: DateTime<Local> = DateTime::from_timestamp(secs, nsecs)
        .unwrap_or_default()
        .into();
    let strftime_fmt = convert_time_tokens(format);
    dt.format(&strftime_fmt).to_string()
}

/// Minimal JSON formatter for structured sinks.
///
/// Produces a single-line JSON object with all record fields. Supports
/// pretty-printing, key sorting, ASCII escaping, and custom separators.
///
/// # Configuration
///
/// - [`JsonFormatter::new()`]: Compact single-line output
/// - [`JsonFormatter::pretty()`]: Pretty-printed with 4-space indent
/// - `.with_indent(n)`: Custom indentation width
/// - `.with_sort_keys(true)`: Alphabetical key ordering
/// - `.with_ensure_ascii(true)`: Escape non-ASCII characters
/// - `.with_separators(item, key)`: Custom separators
///
/// # Examples
///
/// ```rust
/// use format::{Formatter, JsonFormatter};
/// use levels::LogLevel;
/// use record::LogRecord;
///
/// let fmt = JsonFormatter::new();
/// let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "test")
///     .build();
/// let output = fmt.format(&record).unwrap();
/// assert!(output.contains("\"level\":\"INFO\""));
/// ```
#[derive(Clone, Debug)]
pub struct JsonFormatter {
    pretty: bool,
    indent: usize,
    sort_keys: bool,
    ensure_ascii: bool,
    separators: Option<(String, String)>,
}

impl JsonFormatter {
    /// Creates a compact JSON formatter.
    ///
    /// Output is a single line with no extra whitespace.
    #[must_use]
    pub fn new() -> Self {
        Self {
            pretty: false,
            indent: 4,
            sort_keys: false,
            ensure_ascii: false,
            separators: None,
        }
    }

    /// Creates a pretty-printed JSON formatter.
    ///
    /// Output is indented with 4 spaces by default.
    #[must_use]
    pub fn pretty() -> Self {
        Self {
            pretty: true,
            indent: 4,
            sort_keys: false,
            ensure_ascii: false,
            separators: None,
        }
    }

    /// Sets the indentation level for pretty printing.
    #[must_use]
    pub fn with_indent(mut self, indent: usize) -> Self {
        self.indent = indent;
        self
    }

    /// Sets whether to sort keys alphabetically.
    #[must_use]
    pub fn with_sort_keys(mut self, sort_keys: bool) -> Self {
        self.sort_keys = sort_keys;
        self
    }

    /// Sets whether to escape non-ASCII characters.
    #[must_use]
    pub fn with_ensure_ascii(mut self, ensure_ascii: bool) -> Self {
        self.ensure_ascii = ensure_ascii;
        self
    }

    /// Sets custom separators as (`item_separator`, `key_separator`).
    #[must_use]
    pub fn with_separators(mut self, item_sep: String, key_sep: String) -> Self {
        self.separators = Some((item_sep, key_sep));
        self
    }
}

impl Default for JsonFormatter {
    fn default() -> Self {
        Self::new()
    }
}

impl Formatter for JsonFormatter {
    fn format(&self, record: &LogRecord) -> LoglyResult<String> {
        let mut fields = BTreeMap::new();
        fields.insert("level".to_owned(), escape_json(record.level.name()));
        fields.insert("message".to_owned(), escape_json(&record.message));
        fields.insert("name".to_owned(), escape_json(&record.name));
        fields.insert("process".to_owned(), record.process_id.to_string());

        let timestamp = format_timestamp(record, "%Y-%m-%dT%H:%M:%S%.3f%z");
        fields.insert("time".to_owned(), escape_json(&timestamp));

        if let Some(ref file) = record.file {
            fields.insert("file".to_owned(), escape_json(file));
        }
        if let Some(line) = record.line {
            fields.insert("line".to_owned(), line.to_string());
        }
        if let Some(ref function) = record.function {
            fields.insert("function".to_owned(), escape_json(function));
        }
        if let Some(ref thread) = record.thread_name {
            fields.insert("thread".to_owned(), escape_json(thread));
        }
        if !record.extra.is_empty() {
            let extra: BTreeMap<_, _> = record
                .extra
                .iter()
                .map(|(k, v)| (k.clone(), escape_json(v)))
                .collect();
            let extra_str = if self.pretty {
                format_btree_pretty_with_opts(&extra, self.indent, &self.separators)
            } else {
                format_btree_compact(&extra)
            };
            fields.insert("extra".to_owned(), extra_str);
        }
        if let Some(ref exc) = record.exception {
            fields.insert("exception".to_owned(), escape_json(exc));
        }

        if self.pretty {
            Ok(format_btree_pretty_with_opts(
                &fields,
                self.indent,
                &self.separators,
            ))
        } else {
            Ok(format_btree_compact(&fields))
        }
    }
}

/// A custom formatter that wraps a Rust closure.
///
/// Useful for plugging in arbitrary formatting logic from the Rust side.
/// The closure receives a `&LogRecord` and returns the formatted string.
///
/// # Examples
///
/// ```rust
/// use format::{CustomFormatter, Formatter};
/// use levels::LogLevel;
/// use record::LogRecord;
///
/// let fmt = CustomFormatter::new(|record| {
///     Ok(format!("[{}] {}", record.level, record.message))
/// });
/// let record = LogRecord::builder(LogLevel::new("INFO", 20, None), "hello").build();
/// let output = fmt.format(&record).unwrap();
/// assert_eq!(output, "[INFO] hello");
/// ```
pub struct CustomFormatter<F>
where
    F: Fn(&LogRecord) -> LoglyResult<String> + Send + Sync,
{
    func: F,
}

impl<F> CustomFormatter<F>
where
    F: Fn(&LogRecord) -> LoglyResult<String> + Send + Sync,
{
    /// Creates a custom formatter from a closure.
    pub fn new(func: F) -> Self {
        Self { func }
    }
}

impl<F> Formatter for CustomFormatter<F>
where
    F: Fn(&LogRecord) -> LoglyResult<String> + Send + Sync,
{
    fn format(&self, record: &LogRecord) -> LoglyResult<String> {
        (self.func)(record)
    }
}

/// Parses a log file line-by-line, yielding each non-empty line as a [`LogEntry`].
///
/// Without a pattern, every line is yielded. With a pattern, only lines
/// containing the pattern substring are returned. Each entry extracts
/// `key=value` pairs from whitespace-separated tokens.
///
/// # Arguments
///
/// * `path` - Path to the log file
/// * `pattern` - Optional substring filter; only matching lines are included
///
/// # Errors
///
/// Returns an error if the file cannot be read.
pub fn parse_log_file(path: &std::path::Path, pattern: Option<&str>) -> LoglyResult<Vec<LogEntry>> {
    let content = std::fs::read_to_string(path).map_err(|e| {
        error::LoglyError::Formatter(format!("failed to read {}: {e}", path.display()))
    })?;
    let mut entries = Vec::new();
    for line in content.lines() {
        if line.is_empty() {
            continue;
        }
        if let Some(pat) = pattern
            && !line.contains(pat)
        {
            continue;
        }
        let mut groups = BTreeMap::new();
        for part in line.split_whitespace() {
            if let Some((key, value)) = part.split_once('=') {
                groups.insert(key.to_owned(), value.to_owned());
            }
        }
        entries.push(LogEntry {
            message: line.to_owned(),
            groups,
        });
    }
    Ok(entries)
}

/// A parsed log entry with its message and extracted key-value groups.
///
/// Key-value pairs are extracted from whitespace-separated `key=value` tokens
/// in the log line.
#[derive(Clone, Debug)]
pub struct LogEntry {
    /// The raw log line.
    pub message: String,
    /// Extracted key=value pairs.
    pub groups: BTreeMap<String, String>,
}

/// Escapes a string for JSON output.
///
/// Wraps the string in double quotes and escapes special characters:
/// `"` → `\"`, `\` → `\\`, `\n`, `\r`, `\t`, and control characters
/// → `\uXXXX`.
///
/// # Examples
///
/// ```rust
/// use format::escape_json;
///
/// assert_eq!(escape_json("hello"), "\"hello\"");
/// assert_eq!(escape_json("say \"hi\""), "\"say \\\"hi\\\"\"");
/// assert_eq!(escape_json("a\nb"), "\"a\\nb\"");
/// ```
#[must_use]
pub fn escape_json(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c.is_control() => {
                use std::fmt::Write;
                let _ = write!(out, "\\u{:04x}", c as u32);
            }
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

/// Formats a `BTreeMap` as compact JSON.
///
/// Keys are escaped; values are inserted as-is (expected to be pre-escaped
/// or raw numbers/booleans).
///
/// # Examples
///
/// ```rust
/// use format::format_btree_compact;
/// use std::collections::BTreeMap;
///
/// let mut map = BTreeMap::new();
/// map.insert("a".to_owned(), "1".to_owned());
/// assert_eq!(format_btree_compact(&map), "{\"a\":1}");
/// ```
#[must_use]
pub fn format_btree_compact(map: &BTreeMap<String, String>) -> String {
    let mut out = String::from("{");
    for (i, (k, v)) in map.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        out.push_str(&escape_json(k));
        out.push(':');
        // Values are already escaped or are raw numbers/booleans
        out.push_str(v);
    }
    out.push('}');
    out
}

/// Formats a `BTreeMap` as pretty-printed JSON.
///
/// Uses 4-space indentation and default separators.
#[must_use]
pub fn format_btree_pretty(map: &BTreeMap<String, String>) -> String {
    format_btree_pretty_with_opts(map, 4, &None)
}

/// Formats a `BTreeMap` as pretty-printed JSON with custom indentation and separators.
///
/// # Arguments
///
/// * `map` - The key-value pairs to format
/// * `indent` - Number of spaces per indentation level
/// * `separators` - Optional custom `(item_separator, key_separator)` pair;
///   defaults to `(",\n", ": ")`
#[must_use]
pub fn format_btree_pretty_with_opts(
    map: &BTreeMap<String, String>,
    indent: usize,
    separators: &Option<(String, String)>,
) -> String {
    if map.is_empty() {
        return "{}".to_owned();
    }
    let indent_str: String = " ".repeat(indent);
    let (item_sep, key_sep) = if let Some((item, key)) = separators {
        (item.clone(), key.clone())
    } else {
        (",\n".to_owned(), ": ".to_owned())
    };
    let mut out = String::from("{\n");
    for (i, (k, v)) in map.iter().enumerate() {
        if i > 0 {
            out.push_str(&item_sep);
        }
        out.push_str(&indent_str);
        out.push_str(&escape_json(k));
        out.push_str(&key_sep);
        out.push_str(v);
    }
    out.push('\n');
    out.push('}');
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use levels::LogLevel;

    fn info_record(message: &str) -> LogRecord {
        LogRecord::builder(LogLevel::new("INFO", 20, Some("green".to_owned())), message).build()
    }

    fn record_with_extra(message: &str, extra: BTreeMap<String, String>) -> LogRecord {
        let mut record = info_record(message);
        record.extra = extra;
        record
    }

    #[test]
    fn template_basic_tokens() {
        let fmt = TemplateFormatter::new("{level} | {message}");
        let record = info_record("hello world");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "INFO | hello world");
    }

    #[test]
    fn template_alignment_left() {
        let fmt = TemplateFormatter::new("{level:<8} | {message}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "INFO     | test");
    }

    #[test]
    fn template_alignment_right() {
        let fmt = TemplateFormatter::new("{level:>8} | {message}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "    INFO | test");
    }

    #[test]
    fn template_alignment_center() {
        let fmt = TemplateFormatter::new("{level:^8} | {message}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "  INFO   | test");
    }

    #[test]
    fn template_fill_char() {
        let fmt = TemplateFormatter::new("{level:*<8}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "INFO****");
    }

    #[test]
    fn template_extra_key() {
        let mut extra = BTreeMap::new();
        extra.insert("user".to_owned(), "alice".to_owned());
        let record = record_with_extra("msg", extra);
        let fmt = TemplateFormatter::new("{extra[user]} - {message}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "alice - msg");
    }

    #[test]
    fn template_extra_dot() {
        let mut extra = BTreeMap::new();
        extra.insert("env".to_owned(), "prod".to_owned());
        let record = record_with_extra("msg", extra);
        let fmt = TemplateFormatter::new("{extra.env}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "prod");
    }

    #[test]
    fn template_escaped_braces() {
        let fmt = TemplateFormatter::new("{{literal}} {level}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "{literal} INFO");
    }

    #[test]
    fn template_time_with_format() {
        let fmt = TemplateFormatter::new("{time:%H:%M:%S}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        // Should contain time in HH:MM:SS format
        assert!(output.contains(':'));
        assert!(!output.contains("{time"));
    }

    #[test]
    fn template_process() {
        let fmt = TemplateFormatter::new("{process}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        let pid = std::process::id();
        assert_eq!(output, pid.to_string());
    }

    #[test]
    fn template_line_number() {
        let mut record = info_record("test");
        record.line = Some(42);
        let fmt = TemplateFormatter::new("{line}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "42");
    }

    #[test]
    fn template_function_name() {
        let mut record = info_record("test");
        record.function = Some("my_func".to_owned());
        let fmt = TemplateFormatter::new("{function}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "my_func");
    }

    #[test]
    fn template_file_path() {
        let mut record = info_record("test");
        record.file = Some("/path/to/file.rs".to_owned());
        let fmt = TemplateFormatter::new("{file}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "/path/to/file.rs");
    }

    #[test]
    fn template_thread_name() {
        let mut record = info_record("test");
        record.thread_name = Some("main".to_owned());
        let fmt = TemplateFormatter::new("{thread}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "main");
    }

    #[test]
    fn template_unknown_token_preserved() {
        let fmt = TemplateFormatter::new("{unknown}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "{unknown}");
    }

    #[test]
    fn template_combined_format_spec() {
        let fmt = TemplateFormatter::new("{level:<8} | {message:<20} | {extra[key]}");
        let mut extra = BTreeMap::new();
        extra.insert("key".to_owned(), "val".to_owned());
        let record = record_with_extra("hello", extra);
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "INFO     | hello                | val");
    }

    #[test]
    fn template_level_no() {
        let fmt = TemplateFormatter::new("{level_no}");
        let record = info_record("test");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "20");
    }

    #[test]
    fn template_file_line() {
        let mut record = info_record("test");
        record.file = Some("src/main.rs".to_owned());
        record.line = Some(42);
        let fmt = TemplateFormatter::new("{file_line}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "src/main.rs:42");
    }

    #[test]
    fn template_filename() {
        let mut record = info_record("test");
        record.file = Some("/path/to/src/main.rs".to_owned());
        let fmt = TemplateFormatter::new("{filename}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "main.rs");
    }

    #[test]
    fn template_function_location() {
        let mut record = info_record("test");
        record.file = Some("src/lib.rs".to_owned());
        record.line = Some(10);
        record.function = Some("my_func".to_owned());
        let fmt = TemplateFormatter::new("{function_location}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "my_func (src/lib.rs:10)");
    }

    #[test]
    fn template_function_location_no_function() {
        let mut record = info_record("test");
        record.file = Some("src/lib.rs".to_owned());
        record.line = Some(10);
        let fmt = TemplateFormatter::new("{function_location}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "src/lib.rs:10");
    }

    #[test]
    fn template_source_location_combined() {
        let mut record = info_record("test");
        record.file = Some("src/main.rs".to_owned());
        record.line = Some(42);
        record.function = Some("main".to_owned());
        let fmt = TemplateFormatter::new("{function_location} {level} {message}");
        let output = fmt.format(&record).unwrap();
        assert_eq!(output, "main (src/main.rs:42) INFO test");
    }

    #[test]
    fn json_formatter_compact() {
        let fmt = JsonFormatter::new();
        let record = info_record("test msg");
        let output = fmt.format(&record).unwrap();
        assert!(output.contains("\"level\":\"INFO\""));
        assert!(output.contains("\"message\":\"test msg\""));
        assert!(!output.contains('\n'));
    }

    #[test]
    fn json_formatter_pretty() {
        let fmt = JsonFormatter::pretty();
        let record = info_record("test msg");
        let output = fmt.format(&record).unwrap();
        assert!(output.contains('\n'));
        assert!(output.contains("\"level\": \"INFO\""));
    }

    #[test]
    fn json_escape_special_chars() {
        let record = info_record("line1\nline2\ttab\"quote");
        let fmt = JsonFormatter::new();
        let output = fmt.format(&record).unwrap();
        assert!(output.contains("\\n"));
        assert!(output.contains("\\t"));
        assert!(output.contains("\\\""));
    }

    #[test]
    fn parse_format_spec_empty() {
        let (align, width, fill) = parse_format_spec("");
        assert_eq!(align, '<');
        assert_eq!(width, 0);
        assert_eq!(fill, ' ');
    }

    #[test]
    fn parse_format_spec_align_only() {
        let (align, width, fill) = parse_format_spec("<");
        assert_eq!(align, '<');
        assert_eq!(width, 0);
        assert_eq!(fill, ' ');
    }

    #[test]
    fn parse_format_spec_width_only() {
        let (align, width, fill) = parse_format_spec("8");
        assert_eq!(align, '<');
        assert_eq!(width, 8);
        assert_eq!(fill, ' ');
    }

    #[test]
    fn parse_format_spec_align_width() {
        let (align, width, fill) = parse_format_spec(">10");
        assert_eq!(align, '>');
        assert_eq!(width, 10);
        assert_eq!(fill, ' ');
    }

    #[test]
    fn parse_format_spec_fill_align_width() {
        let (align, width, fill) = parse_format_spec("*^20");
        assert_eq!(align, '^');
        assert_eq!(width, 20);
        assert_eq!(fill, '*');
    }

    #[test]
    fn apply_format_left() {
        let result = apply_format_spec("hi", "<6");
        assert_eq!(result, "hi    ");
    }

    #[test]
    fn apply_format_right() {
        let result = apply_format_spec("hi", ">6");
        assert_eq!(result, "    hi");
    }

    #[test]
    fn apply_format_center() {
        let result = apply_format_spec("hi", "^6");
        assert_eq!(result, "  hi  ");
    }

    #[test]
    fn apply_format_fill() {
        let result = apply_format_spec("hi", "*<6");
        assert_eq!(result, "hi****");
    }

    #[test]
    fn apply_format_no_width() {
        let result = apply_format_spec("hello", "");
        assert_eq!(result, "hello");
    }

    #[test]
    fn apply_format_already_wide() {
        let result = apply_format_spec("hello", "<3");
        assert_eq!(result, "hello");
    }

    #[test]
    fn escape_json_basic() {
        assert_eq!(escape_json("hello"), "\"hello\"");
    }

    #[test]
    fn escape_json_quotes() {
        assert_eq!(escape_json("say \"hi\""), "\"say \\\"hi\\\"\"");
    }

    #[test]
    fn escape_json_newline() {
        assert_eq!(escape_json("a\nb"), "\"a\\nb\"");
    }

    #[test]
    fn escape_json_empty() {
        assert_eq!(escape_json(""), "\"\"");
    }

    #[test]
    fn format_btree_empty() {
        let map = BTreeMap::new();
        assert_eq!(format_btree_compact(&map), "{}");
    }

    #[test]
    fn format_btree_single() {
        let mut map = BTreeMap::new();
        map.insert("key".to_owned(), "\"value\"".to_owned());
        assert_eq!(format_btree_compact(&map), "{\"key\":\"value\"}");
    }

    #[test]
    fn format_btree_multiple() {
        let mut map = BTreeMap::new();
        map.insert("a".to_owned(), "1".to_owned());
        map.insert("b".to_owned(), "2".to_owned());
        let result = format_btree_compact(&map);
        assert!(result.contains("\"a\":1"));
        assert!(result.contains("\"b\":2"));
    }

    #[test]
    fn format_timestamp_default() {
        let record = info_record("test");
        let ts = format_timestamp(&record, "%Y-%m-%d");
        assert!(!ts.is_empty());
        assert!(ts.contains('-'));
    }

    #[test]
    fn convert_time_tokens_yyyy_mm_dd() {
        let result = convert_time_tokens("YYYY-MM-DD");
        assert_eq!(result, "%Y-%m-%d");
    }

    #[test]
    fn convert_time_tokens_full_datetime() {
        let result = convert_time_tokens("YYYY-MM-DD HH:mm:ss");
        assert_eq!(result, "%Y-%m-%d %H:%M:%S");
    }

    #[test]
    fn convert_time_tokens_with_millis() {
        let result = convert_time_tokens("YYYY-MM-DD HH:mm:ss.SSS");
        assert_eq!(result, "%Y-%m-%d %H:%M:%S.%.3f");
    }

    #[test]
    fn convert_time_tokens_12h() {
        let result = convert_time_tokens("hh:mm A");
        assert_eq!(result, "%I:%M %p");
    }

    #[test]
    fn convert_time_tokens_strftime_passthrough() {
        let result = convert_time_tokens("%Y-%m-%d %H:%M:%S");
        assert_eq!(result, "%Y-%m-%d %H:%M:%S");
    }

    #[test]
    fn convert_time_tokens_mixed() {
        let result = convert_time_tokens("YYYY-%m-%d");
        assert_eq!(result, "%Y-%m-%d");
    }

    #[test]
    fn convert_time_tokens_weekday() {
        let result = convert_time_tokens("dddd, MMMM DD");
        assert_eq!(result, "%A, %B %d");
    }

    #[test]
    fn convert_time_tokens_short_weekday() {
        let result = convert_time_tokens("ddd MMM DD YYYY");
        assert_eq!(result, "%a %b %d %Y");
    }

    #[test]
    fn convert_time_tokens_yy() {
        let result = convert_time_tokens("YY-MM-DD");
        assert_eq!(result, "%y-%m-%d");
    }

    #[test]
    fn format_timestamp_brace_style() {
        let record = info_record("test");
        let ts = format_timestamp(&record, "YYYY-MM-DD");
        assert!(!ts.is_empty());
        assert!(ts.contains('-'));
        // Should be 4-digit year
        let year_str = ts.split('-').next().unwrap();
        assert_eq!(year_str.len(), 4);
    }

    #[test]
    fn format_timestamp_brace_with_millis() {
        let record = info_record("test");
        let ts = format_timestamp(&record, "YYYY-MM-DD HH:mm:ss.SSS");
        assert!(!ts.is_empty());
        // Should contain a dot before milliseconds
        assert!(ts.contains('.'));
    }
}
