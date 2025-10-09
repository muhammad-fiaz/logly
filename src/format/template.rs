use chrono::DateTime;
use regex::Regex;
use std::collections::HashMap;

/// Format a log message using a template string.
///
/// Supports placeholders like {time}, {level}, {message}, {module}, {function}.
/// Placeholders are case-insensitive and can include extra fields from the log record.
/// Extra fields that don't have placeholders are appended at the end.
///
/// Time formatting supports custom patterns using {time:FORMAT} syntax, where FORMAT
/// can include chrono format specifiers like:
/// - YYYY: 4-digit year
/// - YY: 2-digit year
/// - MM: 2-digit month
/// - DD: 2-digit day
/// - HH: 2-digit hour (24h)
/// - mm: 2-digit minute
/// - ss: 2-digit second
/// - SSS: 3-digit millisecond
///
/// Examples: {time:YYYY-MM-DD}, {time:YYYY-MM-DD HH:mm:ss}, {time:DD/MM/YYYY}
///
/// # Arguments
/// * `template` - Format string with placeholders (e.g., "{time} | {level} | {message}")
/// * `timestamp` - ISO 8601 timestamp
/// * `level` - Log level string
/// * `message` - Log message
/// * `extra_fields` - Additional key-value pairs from the log record
///
/// # Returns
/// Formatted string with placeholders replaced
/// Convert a simple format pattern to chrono format string
/// Supports patterns like YYYY-MM-DD HH:mm:ss
fn convert_time_pattern(pattern: &str) -> String {
    pattern
        .replace("YYYY", "%Y")
        .replace("YY", "%y")
        .replace("MM", "%m")
        .replace("DD", "%d")
        .replace("HH", "%H")
        .replace("mm", "%M")
        .replace("ss", "%S")
        .replace("SSS", "%3f")
}

/// Format a timestamp using a custom pattern
fn format_timestamp(timestamp: &str, pattern: &str) -> String {
    // Try to parse the ISO 8601 timestamp
    if let Ok(dt) = DateTime::parse_from_rfc3339(timestamp) {
        let chrono_pattern = convert_time_pattern(pattern);
        dt.format(&chrono_pattern).to_string()
    } else {
        // If parsing fails, return the original timestamp
        timestamp.to_string()
    }
}

pub fn format_with_template(
    template: &str,
    timestamp: &str,
    level: &str,
    message: &str,
    extra_fields: &[(String, String)],
) -> String {
    let mut result = template.to_string();

    // Create a map of all available fields
    let mut fields = HashMap::new();
    fields.insert("time".to_string(), timestamp.to_string());
    fields.insert("level".to_string(), level.to_string());
    fields.insert("message".to_string(), message.to_string());

    // Add extra fields
    for (key, value) in extra_fields {
        fields.insert(key.to_lowercase(), value.clone());
    }

    // Replace placeholders using regex
    // Matches {key} or {key:format} patterns (case-insensitive)
    let re = Regex::new(r"\{([^}:]+)(?::([^}]+))?\}").unwrap();
    result = re
        .replace_all(&result, |caps: &regex::Captures| {
            let key = caps[1].to_lowercase();
            let format_pattern = caps.get(2).map(|m| m.as_str());

            if key == "extra" {
                // Special handling for {extra} - format all extra fields
                let extra_parts: Vec<String> = extra_fields
                    .iter()
                    .map(|(k, v)| format!("{}={}", k, v))
                    .collect();
                extra_parts.join(" | ")
            } else if key == "time" && format_pattern.is_some() {
                // Handle time formatting with custom pattern
                format_timestamp(timestamp, format_pattern.unwrap())
            } else {
                fields
                    .get(&key)
                    .cloned()
                    .unwrap_or_else(|| format!("{{{}}}", &caps[0]))
            }
        })
        .to_string();

    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_formatting() {
        let template = "{time} | {level} | {message}";
        let result = format_with_template(
            template,
            "2023-01-01T12:00:00Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(result, "2023-01-01T12:00:00Z | INFO | Test message");
    }

    #[test]
    fn test_with_extra_fields() {
        let template = "{time} [{level}] {message} | module={module}";
        let extra = vec![("module".to_string(), "test_module".to_string())];
        let result = format_with_template(
            template,
            "2023-01-01T12:00:00Z",
            "INFO",
            "Test message",
            &extra,
        );
        assert_eq!(
            result,
            "2023-01-01T12:00:00Z [INFO] Test message | module=test_module"
        );
    }

    #[test]
    fn test_case_insensitive() {
        let template = "{TIME} | {LEVEL} | {MESSAGE}";
        let result = format_with_template(
            template,
            "2023-01-01T12:00:00Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(result, "2023-01-01T12:00:00Z | INFO | Test message");
    }

    #[test]
    fn test_filename_lineno_in_template() {
        let template = "{time} [{level}] {message} | {filename}:{lineno}";
        let extra = vec![
            ("filename".to_string(), "/path/to/file.py".to_string()),
            ("lineno".to_string(), "42".to_string()),
        ];
        let result = format_with_template(
            template,
            "2023-01-01T12:00:00Z",
            "INFO",
            "Test message",
            &extra,
        );
        assert_eq!(
            result,
            "2023-01-01T12:00:00Z [INFO] Test message | /path/to/file.py:42"
        );
    }

    #[test]
    fn test_time_format_yyyy_mm_dd() {
        let template = "{time:YYYY-MM-DD} | {level} | {message}";
        let result = format_with_template(
            template,
            "2023-01-15T12:34:56Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(result, "2023-01-15 | INFO | Test message");
    }

    #[test]
    fn test_time_format_full() {
        let template = "{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}";
        let result = format_with_template(
            template,
            "2023-01-15T12:34:56Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(result, "2023-01-15 12:34:56 [INFO] Test message");
    }

    #[test]
    fn test_time_format_dd_mm_yyyy() {
        let template = "{time:DD/MM/YYYY} | {level} | {message}";
        let result = format_with_template(
            template,
            "2023-01-15T12:34:56Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(result, "15/01/2023 | INFO | Test message");
    }

    #[test]
    fn test_time_format_with_milliseconds() {
        let template = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}";
        let result = format_with_template(
            template,
            "2023-01-15T12:34:56.789Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(result, "2023-01-15 12:34:56.789 | Test message");
    }

    #[test]
    fn test_time_format_yy() {
        let template = "{time:YY-MM-DD} | {message}";
        let result = format_with_template(
            template,
            "2023-01-15T12:34:56Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(result, "23-01-15 | Test message");
    }

    #[test]
    fn test_time_format_mixed_with_unformatted() {
        let template = "{time:YYYY-MM-DD} | {level} | {message} | raw: {time}";
        let result = format_with_template(
            template,
            "2023-01-15T12:34:56Z",
            "INFO",
            "Test message",
            &[],
        );
        assert_eq!(
            result,
            "2023-01-15 | INFO | Test message | raw: 2023-01-15T12:34:56Z"
        );
    }

    #[test]
    fn test_convert_time_pattern() {
        assert_eq!(convert_time_pattern("YYYY-MM-DD"), "%Y-%m-%d");
        assert_eq!(
            convert_time_pattern("YYYY-MM-DD HH:mm:ss"),
            "%Y-%m-%d %H:%M:%S"
        );
        assert_eq!(convert_time_pattern("DD/MM/YY"), "%d/%m/%y");
        assert_eq!(convert_time_pattern("HH:mm:ss.SSS"), "%H:%M:%S.%3f");
    }
}
