use regex::Regex;
use std::collections::HashMap;

/// Format a log message using a template string.
///
/// Supports placeholders like {time}, {level}, {message}, {module}, {function}.
/// Placeholders are case-insensitive and can include extra fields from the log record.
/// Extra fields that don't have placeholders are appended at the end.
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
    // Matches {key} patterns (case-insensitive)
    let re = Regex::new(r"\{([^}]+)\}").unwrap();
    result = re
        .replace_all(&result, |caps: &regex::Captures| {
            let key = caps[1].to_lowercase();
            if key == "extra" {
                // Special handling for {extra} - format all extra fields
                let extra_parts: Vec<String> = extra_fields
                    .iter()
                    .map(|(k, v)| format!("{}={}", k, v))
                    .collect();
                extra_parts.join(" | ")
            } else {
                fields
                    .get(&key)
                    .cloned()
                    .unwrap_or_else(|| format!("{{{}}}", &caps[1]))
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
}
