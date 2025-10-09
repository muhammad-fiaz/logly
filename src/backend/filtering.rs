/// Filters caller information fields from log record pairs.
///
/// This function removes caller-related fields (module, function, filename, lineno)
/// from the log record based on configuration flags. This allows fine-grained
/// control over which metadata appears in log output.
///
/// # Filtered Fields
///
/// - `module` - Removed if `show_module` is false
/// - `function` - Removed if `show_function` is false
/// - `filename` - Removed if `show_filename` is false
/// - `lineno` - Removed if `show_lineno` is false
///
/// All other fields pass through unchanged.
///
/// # Arguments
///
/// * `pairs` - The log record key-value pairs to filter
/// * `show_module` - Whether to include the module field
/// * `show_function` - Whether to include the function field
/// * `show_filename` - Whether to include the filename field
/// * `show_lineno` - Whether to include the line number field
///
/// # Returns
///
/// A new vector containing only the allowed fields
///
/// # Examples
///
/// ```rust
/// use logly::backend::filtering::filter_caller_info;
///
/// let pairs = vec![
///     ("module".to_string(), "main".to_string()),
///     ("function".to_string(), "run".to_string()),
///     ("message".to_string(), "Hello".to_string()),
/// ];
///
/// // Hide function but show module
/// let filtered = filter_caller_info(&pairs, true, false, true, true);
/// assert_eq!(filtered.len(), 2);  // module and message only
/// ```
#[allow(dead_code)]
pub fn filter_caller_info(
    pairs: &[(String, String)],
    show_module: bool,
    show_function: bool,
    show_filename: bool,
    show_lineno: bool,
) -> Vec<(String, String)> {
    pairs
        .iter()
        .filter(|(key, _)| match key.as_str() {
            "module" => show_module,
            "function" => show_function,
            "filename" => show_filename,
            "lineno" => show_lineno,
            _ => true, // Keep all other fields
        })
        .cloned()
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_filter_all_enabled() {
        let pairs = vec![
            ("module".to_string(), "test_module".to_string()),
            ("function".to_string(), "test_func".to_string()),
            ("filename".to_string(), "test.py".to_string()),
            ("lineno".to_string(), "42".to_string()),
            ("custom".to_string(), "value".to_string()),
        ];

        let result = filter_caller_info(&pairs, true, true, true, true);
        assert_eq!(result.len(), 5);
        assert!(result.contains(&("module".to_string(), "test_module".to_string())));
        assert!(result.contains(&("function".to_string(), "test_func".to_string())));
        assert!(result.contains(&("filename".to_string(), "test.py".to_string())));
        assert!(result.contains(&("lineno".to_string(), "42".to_string())));
        assert!(result.contains(&("custom".to_string(), "value".to_string())));
    }

    #[test]
    fn test_filter_module_disabled() {
        let pairs = vec![
            ("module".to_string(), "test_module".to_string()),
            ("function".to_string(), "test_func".to_string()),
            ("filename".to_string(), "test.py".to_string()),
            ("lineno".to_string(), "42".to_string()),
            ("custom".to_string(), "value".to_string()),
        ];

        let result = filter_caller_info(&pairs, false, true, true, true);
        assert_eq!(result.len(), 4);
        assert!(!result.iter().any(|(k, _)| k == "module"));
        assert!(result.contains(&("function".to_string(), "test_func".to_string())));
        assert!(result.contains(&("filename".to_string(), "test.py".to_string())));
        assert!(result.contains(&("lineno".to_string(), "42".to_string())));
        assert!(result.contains(&("custom".to_string(), "value".to_string())));
    }

    #[test]
    fn test_filter_function_disabled() {
        let pairs = vec![
            ("module".to_string(), "test_module".to_string()),
            ("function".to_string(), "test_func".to_string()),
            ("custom".to_string(), "value".to_string()),
        ];

        let result = filter_caller_info(&pairs, true, false, true, true);
        assert_eq!(result.len(), 2);
        assert!(result.contains(&("module".to_string(), "test_module".to_string())));
        assert!(!result.iter().any(|(k, _)| k == "function"));
        assert!(result.contains(&("custom".to_string(), "value".to_string())));
    }

    #[test]
    fn test_filter_all_disabled() {
        let pairs = vec![
            ("module".to_string(), "test_module".to_string()),
            ("function".to_string(), "test_func".to_string()),
            ("filename".to_string(), "test.py".to_string()),
            ("lineno".to_string(), "42".to_string()),
            ("custom".to_string(), "value".to_string()),
        ];

        let result = filter_caller_info(&pairs, false, false, false, false);
        assert_eq!(result.len(), 1);
        assert!(result.contains(&("custom".to_string(), "value".to_string())));
    }

    #[test]
    fn test_filter_preserves_custom_fields() {
        let pairs = vec![
            ("module".to_string(), "test".to_string()),
            ("user_id".to_string(), "123".to_string()),
            ("request_id".to_string(), "abc".to_string()),
        ];

        // Even with all caller info disabled, custom fields remain
        let result = filter_caller_info(&pairs, false, false, false, false);
        assert_eq!(result.len(), 2);
        assert!(result.contains(&("user_id".to_string(), "123".to_string())));
        assert!(result.contains(&("request_id".to_string(), "abc".to_string())));
    }
}
