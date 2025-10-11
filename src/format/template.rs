use chrono::{DateTime, Utc};
use regex::Regex;
use std::collections::HashMap;

/// Convert time format patterns to chrono format.
///
/// Supports custom time format specifications.
/// Feature added in v0.1.6.
///
/// See: https://github.com/muhammad-fiaz/logly/pull/80
/// See: https://github.com/muhammad-fiaz/logly/issues/79
///
/// # Supported Patterns
/// - **Years**: YYYY (2025), YY (25)
/// - **Months**: MMMM (October), MMM (Oct), MM (10)
/// - **Days**: dddd (Saturday), ddd (Sat), DD (11)
/// - **Hours**: HH (13 for 24h), hh (01 for 12h)
/// - **Minutes**: mm (51)
/// - **Seconds**: ss (37)
/// - **Fractional**: SSSSSS (microseconds), SSS (milliseconds), SS (centiseconds)
/// - **AM/PM**: A (AM/PM), a (am/pm)
/// - **Timezone**: ZZ (+00:00), Z (+0000), zz (UTC)
/// - **Unix**: X (timestamp)
///
/// # Examples
/// ```
/// use logly::format::template::loguru_to_chrono_format;
///
/// let pattern = loguru_to_chrono_format("YYYY-MM-DD HH:mm:ss");
/// assert_eq!(pattern, "%Y-%m-%d %H:%M:%S");
///
/// let pattern = loguru_to_chrono_format("YYYY-MM-DD");
/// assert_eq!(pattern, "%Y-%m-%d");
/// ```
///
/// # Important
/// The replacement order matters! Longer patterns must be replaced before shorter ones.
/// We avoid single-letter replacements (H, m, s, etc.) to prevent double-replacement issues.
fn loguru_to_chrono_format(loguru_format: &str) -> String {
    let mut result = loguru_format.to_string();

    // Year - longer patterns first
    result = result.replace("YYYY", "%Y");
    result = result.replace("YY", "%y");

    // Month - longer patterns first
    result = result.replace("MMMM", "%B"); // Full month name
    result = result.replace("MMM", "%b"); // Abbreviated month name
    result = result.replace("MM", "%m"); // Month as number

    // Day - longer patterns first
    result = result.replace("dddd", "%A"); // Full weekday name
    result = result.replace("ddd", "%a"); // Abbreviated weekday name
    result = result.replace("DD", "%d"); // Day of month

    // Hour - longer patterns first
    result = result.replace("HH", "%H"); // Hour (24-hour)
    result = result.replace("hh", "%I"); // Hour (12-hour)

    // Minute
    result = result.replace("mm", "%M"); // Minute

    // Fractional seconds - MUST come before "ss"
    result = result.replace("SSSSSS", "%6f"); // Microseconds
    result = result.replace("SSS", "%3f"); // Milliseconds
    result = result.replace("SS", "%2f"); // Centiseconds

    // Second
    result = result.replace("ss", "%S"); // Second

    // AM/PM
    result = result.replace("A", "%p"); // AM/PM
    result = result.replace("a", "%P"); // am/pm

    // Timezone - longer patterns first
    result = result.replace("ZZ", "%:z"); // Timezone offset with colon
    result = result.replace("zz", "%Z"); // Timezone name
    result = result.replace("Z", "%z"); // Timezone offset

    // Unix timestamp
    result = result.replace("X", "%s"); // Unix timestamp

    result
}

/// Format a log message using a template string.
///
/// Supports placeholders like {time}, {level}, {message}, {module}, {function}.
/// Placeholders are case-insensitive and can include extra fields from the log record.
///
/// See: https://github.com/muhammad-fiaz/logly/pull/80
/// See: https://github.com/muhammad-fiaz/logly/issues/79
///
/// # Time Format Specifications (v0.1.6+)
/// Time placeholders support custom format specs using {time:FORMAT} syntax.
///
/// Supported time format patterns:
/// - **Date**: YYYY-MM-DD, DD/MM/YYYY, YY-MM-DD
/// - **Time**: HH:mm:ss, hh:mm:ss A (12-hour with AM/PM)
/// - **DateTime**: YYYY-MM-DD HH:mm:ss, YYYY-MM-DDTHH:mm:ss
/// - **Milliseconds**: YYYY-MM-DD HH:mm:ss.SSS
/// - **Month names**: YYYY-MMM-DD (2025-Oct-11), YYYY-MMMM-DD (2025-October-11)
/// - **Weekday names**: dddd, DD MMMM YYYY (Saturday, 11 October 2025)
///
/// # Extra Fields
/// Use {extra} placeholder to explicitly include all extra fields.
/// Without {extra}, custom templates won't auto-append extra fields.
///
/// # Examples
/// ```
/// use chrono::Utc;
/// use logly::format::template::format_with_template;
///
/// let timestamp = Utc::now();
///
/// // Date only
/// let result = format_with_template(
///     "{time:YYYY-MM-DD} | {level} | {message}",
///     &timestamp,
///     "INFO",
///     "Hello",
///     &[]
/// );
///
/// // Full datetime with milliseconds
/// let result = format_with_template(
///     "{time:YYYY-MM-DD HH:mm:ss.SSS} [{level}] {message}",
///     &timestamp,
///     "ERROR",
///     "Something failed",
///     &[]
/// );
///
/// // With extra fields
/// let result = format_with_template(
///     "{time:HH:mm:ss} | {message} | {extra}",
///     &timestamp,
///     "DEBUG",
///     "Debug info",
///     &[("user".to_string(), "alice".to_string())]
/// );
/// ```
///
/// # Arguments
/// * `template` - Format string with placeholders (e.g., "{time} | {level} | {message}")
/// * `timestamp` - Timestamp as DateTime<Utc>
/// * `level` - Log level string
/// * `message` - Log message
/// * `extra_fields` - Additional key-value pairs from the log record
///
/// # Returns
/// Formatted string with placeholders replaced
pub fn format_with_template(
    template: &str,
    timestamp: &DateTime<Utc>,
    level: &str,
    message: &str,
    extra_fields: &[(String, String)],
) -> String {
    let result = template.to_string();

    // Create a map of all available fields
    let mut fields = HashMap::new();
    fields.insert(
        "time".to_string(),
        timestamp.format("%Y-%m-%d %H:%M:%S%.3f").to_string(),
    );
    fields.insert("level".to_string(), level.to_string());
    fields.insert("message".to_string(), message.to_string());

    // Add extra fields
    for (key, value) in extra_fields {
        fields.insert(key.to_lowercase(), value.clone());
    }

    // Replace placeholders using regex
    // Matches {key} or {key:format} patterns (case-insensitive)
    let re = Regex::new(r"\{([^:}]+)(?::([^}]*))?\}").unwrap();

    // Track which extra fields have been used in the template
    let mut used_fields = std::collections::HashSet::new();

    // Check if the template contains {extra} placeholder
    let has_extra_placeholder = template.to_lowercase().contains("{extra}");

    let result = re
        .replace_all(&result, |caps: &regex::Captures| {
            let key = caps[1].to_lowercase();
            let format_spec = caps.get(2).map(|m| m.as_str());

            if key == "time" {
                if let Some(format_str) = format_spec {
                    // Handle time formatting with custom format spec
                    // Convert format patterns to chrono format
                    let chrono_format = loguru_to_chrono_format(format_str);
                    timestamp.format(&chrono_format).to_string()
                } else {
                    // Default time format (RFC3339)
                    timestamp.to_rfc3339()
                }
            } else if key == "extra" {
                // Special handling for {extra} - format all extra fields
                let extra_parts: Vec<String> = extra_fields
                    .iter()
                    .filter(|(k, _)| !used_fields.contains(&k.to_lowercase()))
                    .map(|(k, v)| format!("{}={}", k, v))
                    .collect();
                extra_parts.join(" | ")
            } else {
                // Mark this field as used
                used_fields.insert(key.clone());
                fields
                    .get(&key)
                    .cloned()
                    .unwrap_or_else(|| format!("{{{}}}", &caps[1]))
            }
        })
        .to_string();

    // Only append unused extra fields if the template explicitly contained {extra}
    // If there's no {extra} placeholder, user doesn't want auto-appended fields
    if !has_extra_placeholder {
        // Don't append extra fields automatically - user must explicitly use {extra}
        result
    } else {
        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_formatting() {
        let template = "{time} | {level} | {message}";
        let timestamp = Utc::now();
        let result = format_with_template(template, &timestamp, "INFO", "Test message", &[]);
        // Check that the result contains the expected parts
        assert!(result.contains(" | INFO | Test message"));
    }

    #[test]
    fn test_with_extra_fields() {
        let template = "{time} [{level}] {message} | module={module}";
        let timestamp = Utc::now();
        let extra = vec![("module".to_string(), "test_module".to_string())];
        let result = format_with_template(template, &timestamp, "INFO", "Test message", &extra);
        // Check that the result contains the expected parts
        assert!(result.contains(" [INFO] Test message | module=test_module"));
    }

    #[test]
    fn test_case_insensitive() {
        let template = "{TIME} | {LEVEL} | {MESSAGE}";
        let timestamp = Utc::now();
        let result = format_with_template(template, &timestamp, "INFO", "Test message", &[]);
        // Check that the result contains the expected parts
        assert!(result.contains(" | INFO | Test message"));
    }

    #[test]
    fn test_extra_fields() {
        let template = "{time} [{level}] {message} | {filename}:{lineno}";
        let timestamp = Utc::now();
        let extra = vec![
            ("filename".to_string(), "/path/to/file.py".to_string()),
            ("lineno".to_string(), "42".to_string()),
        ];
        let result = format_with_template(template, &timestamp, "INFO", "Test message", &extra);
        // Check that the result contains the expected parts
        assert!(result.contains(" [INFO] Test message | /path/to/file.py:42"));
    }

    #[test]
    fn test_format_specs() {
        let template = "{time:YYYY-MM-DD} | {level} | {message}";
        let timestamp = Utc::now();
        let result = format_with_template(template, &timestamp, "INFO", "Test message", &[]);
        println!("Format spec result: '{}'", result);
        // Check that the result contains the expected parts
        assert!(result.contains(" | INFO | Test message"));
        // Check that the date is formatted correctly (should be YYYY-MM-DD format)
        let date_part = result.split(" | ").next().unwrap();
        println!("Date part: '{}'", date_part);
        assert!(date_part.len() == 10); // YYYY-MM-DD is 10 characters
        assert!(date_part.chars().nth(4) == Some('-'));
        assert!(date_part.chars().nth(7) == Some('-'));
    }

    #[test]
    fn test_time_format_specs() {
        // Test time formatting directly
        let template = "{time:HH:mm:ss}";
        let timestamp = Utc::now();
        let result = format_with_template(template, &timestamp, "INFO", "Test", &[]);
        println!("Time format result: '{}'", result);

        // Check that it has the HH:mm:ss structure
        let parts: Vec<&str> = result.split(':').collect();
        assert_eq!(parts.len(), 3, "Should have 3 colon-separated parts");
        assert!(!parts[0].is_empty(), "Hour should have at least 1 digit");
        assert!(!parts[1].is_empty(), "Minute should have at least 1 digit");
        assert!(!parts[2].is_empty(), "Second should have at least 1 digit");

        // Test what loguru_to_chrono_format produces
        let chrono_format = loguru_to_chrono_format("HH:mm:ss");
        println!("Converted format: '{}'", chrono_format);
        assert_eq!(chrono_format, "%H:%M:%S", "Should convert to chrono format");

        // Test the actual formatting
        let formatted = timestamp.format(&chrono_format).to_string();
        println!("Chrono formatted: '{}'", formatted);
    }

    #[test]
    fn test_regex_matching() {
        let re = Regex::new(r"\{([^:}]+)(?::([^}]*))?\}").unwrap();
        let template = "{time:YYYY-MM-DD}";
        let captures: Vec<_> = re.captures_iter(template).collect();
        println!("Regex captures: {:?}", captures);
        assert_eq!(captures.len(), 1);
        let cap = &captures[0];
        assert_eq!(cap.get(1).map(|m| m.as_str()), Some("time"));
        assert_eq!(cap.get(2).map(|m| m.as_str()), Some("YYYY-MM-DD"));
    }
}
