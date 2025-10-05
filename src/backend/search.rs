use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

/// Search options for log file searching
#[derive(Debug, Clone, Default)]
pub struct SearchOptions {
    pub case_sensitive: bool,
    pub first_only: bool,
    pub use_regex: bool,
    pub start_line: Option<usize>,
    pub end_line: Option<usize>,
    pub max_results: Option<usize>,
    pub context_before: Option<usize>,
    pub context_after: Option<usize>,
    pub level_filter: Option<String>,
    pub invert_match: bool,
}

/// Search result containing match information
#[derive(Debug, Clone)]
pub struct SearchResult {
    pub line_number: usize,
    pub content: String,
    pub matched_text: String,
    pub context_before: Vec<String>,
    pub context_after: Vec<String>,
}

/// Search a file for a pattern with advanced options
///
/// # Arguments
///
/// * `file_path` - Path to the log file
/// * `pattern` - Search pattern (string or regex)
/// * `options` - Search configuration options
///
/// # Returns
///
/// Vector of SearchResult objects, or empty vector if no matches
pub fn search_file<P: AsRef<Path>>(
    file_path: P,
    pattern: &str,
    options: &SearchOptions,
) -> Result<Vec<SearchResult>, std::io::Error> {
    let file = File::open(file_path)?;
    let reader = BufReader::new(file);
    let mut results = Vec::new();
    let mut all_lines: Vec<String> = Vec::new();

    // Read all lines first for context support
    for line in reader.lines() {
        all_lines.push(line?);
    }

    // Compile regex if needed
    let regex_matcher = if options.use_regex {
        match regex::Regex::new(pattern) {
            Ok(re) => Some(re),
            Err(_) => return Ok(results), // Invalid regex returns empty
        }
    } else {
        None
    };

    // Determine line range
    let start = options.start_line.unwrap_or(1);
    let end = options.end_line.unwrap_or(all_lines.len());

    // Search through lines
    for (idx, line) in all_lines.iter().enumerate() {
        let line_num = idx + 1;

        // Check line range filter
        if line_num < start || line_num > end {
            continue;
        }

        // Check level filter
        if let Some(ref level) = options.level_filter {
            let line_upper = line.to_uppercase();
            if !line_upper.contains(&level.to_uppercase()) {
                continue;
            }
        }

        // Check if line matches pattern
        let matches = if let Some(ref re) = regex_matcher {
            re.is_match(line)
        } else if options.case_sensitive {
            line.contains(pattern)
        } else {
            line.to_lowercase().contains(&pattern.to_lowercase())
        };

        // Apply invert_match (like grep -v)
        let should_include = if options.invert_match {
            !matches
        } else {
            matches
        };

        if should_include {
            // Extract matched text
            let matched_text = if let Some(ref re) = regex_matcher {
                re.find(line)
                    .map(|m| m.as_str().to_string())
                    .unwrap_or_else(|| pattern.to_string())
            } else {
                // For non-regex searches, find the actual substring in the line
                if options.case_sensitive {
                    // Case-sensitive: find exact match
                    line.find(pattern)
                        .map(|pos| &line[pos..pos + pattern.len()])
                        .unwrap_or(pattern)
                } else {
                    // Case-insensitive: find the match preserving original case
                    let pattern_lower = pattern.to_lowercase();
                    let line_lower = line.to_lowercase();
                    line_lower
                        .find(&pattern_lower)
                        .map(|pos| &line[pos..pos + pattern.len()])
                        .unwrap_or(pattern)
                }
                .to_string()
            };

            // Get context lines
            let context_before = if let Some(n) = options.context_before {
                let start_idx = idx.saturating_sub(n);
                all_lines[start_idx..idx].to_vec()
            } else {
                Vec::new()
            };

            let context_after = if let Some(n) = options.context_after {
                let end_idx = std::cmp::min(idx + 1 + n, all_lines.len());
                all_lines[idx + 1..end_idx].to_vec()
            } else {
                Vec::new()
            };

            results.push(SearchResult {
                line_number: line_num,
                content: line.clone(),
                matched_text,
                context_before,
                context_after,
            });

            // Check first_only
            if options.first_only {
                break;
            }

            // Check max_results
            if let Some(max) = options.max_results
                && results.len() >= max
            {
                break;
            }
        }
    }

    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn create_test_file(content: &[&str]) -> NamedTempFile {
        let mut file = NamedTempFile::new().unwrap();
        for line in content {
            writeln!(file, "{}", line).unwrap();
        }
        file.flush().unwrap();
        file
    }

    #[test]
    fn test_basic_search() {
        let file = create_test_file(&["error occurred", "info message", "another error"]);
        let options = SearchOptions::default();
        let results = search_file(file.path(), "error", &options).unwrap();

        assert_eq!(results.len(), 2);
        assert_eq!(results[0].line_number, 1);
        assert_eq!(results[1].line_number, 3);
    }

    #[test]
    fn test_case_sensitive() {
        let file = create_test_file(&["ERROR", "error", "Error"]);
        let mut options = SearchOptions::default();
        options.case_sensitive = true;

        let results = search_file(file.path(), "error", &options).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].line_number, 2);
    }

    #[test]
    fn test_first_only() {
        let file = create_test_file(&["match 1", "match 2", "match 3"]);
        let mut options = SearchOptions::default();
        options.first_only = true;

        let results = search_file(file.path(), "match", &options).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].line_number, 1);
    }

    #[test]
    fn test_regex_search() {
        let file = create_test_file(&["error: 123", "error: abc", "warning: 456"]);
        let mut options = SearchOptions::default();
        options.use_regex = true;

        let results = search_file(file.path(), r"error:\s+\d+", &options).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].line_number, 1);
    }

    #[test]
    fn test_line_range_filter() {
        let file = create_test_file(&["line 1", "line 2", "line 3", "line 4", "line 5"]);
        let mut options = SearchOptions::default();
        options.start_line = Some(2);
        options.end_line = Some(4);

        let results = search_file(file.path(), "line", &options).unwrap();
        assert_eq!(results.len(), 3);
        assert_eq!(results[0].line_number, 2);
        assert_eq!(results[2].line_number, 4);
    }

    #[test]
    fn test_max_results() {
        let file = create_test_file(&["match", "match", "match", "match"]);
        let mut options = SearchOptions::default();
        options.max_results = Some(2);

        let results = search_file(file.path(), "match", &options).unwrap();
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn test_context_lines() {
        let file = create_test_file(&["line 1", "line 2", "MATCH", "line 4", "line 5"]);
        let mut options = SearchOptions::default();
        options.context_before = Some(1);
        options.context_after = Some(1);

        let results = search_file(file.path(), "MATCH", &options).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].context_before.len(), 1);
        assert_eq!(results[0].context_after.len(), 1);
        assert_eq!(results[0].context_before[0], "line 2");
        assert_eq!(results[0].context_after[0], "line 4");
    }

    #[test]
    fn test_level_filter() {
        let file = create_test_file(&[
            "INFO: starting",
            "ERROR: failed",
            "INFO: continuing",
            "ERROR: crashed",
        ]);
        let mut options = SearchOptions::default();
        options.level_filter = Some("ERROR".to_string());

        let results = search_file(file.path(), ":", &options).unwrap();
        assert_eq!(results.len(), 2);
        assert_eq!(results[0].line_number, 2);
        assert_eq!(results[1].line_number, 4);
    }

    #[test]
    fn test_invert_match() {
        let file = create_test_file(&["error", "info", "warning", "error"]);
        let mut options = SearchOptions::default();
        options.invert_match = true;

        let results = search_file(file.path(), "error", &options).unwrap();
        assert_eq!(results.len(), 2);
        assert_eq!(results[0].content, "info");
        assert_eq!(results[1].content, "warning");
    }
}
