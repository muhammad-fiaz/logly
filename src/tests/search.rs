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
fn test_basic_string_search() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["error occurred", "info message", "another error"]);
    let options = SearchOptions::default();
    let results = search_file(file.path(), "error", &options).unwrap();

    assert_eq!(results.len(), 2);
    assert_eq!(results[0].line_number, 1);
    assert_eq!(results[1].line_number, 3);
}

#[test]
fn test_case_sensitive_search() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["ERROR", "error", "Error"]);
    let mut options = SearchOptions::default();
    options.case_sensitive = true;

    let results = search_file(file.path(), "error", &options).unwrap();
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].line_number, 2);
}

#[test]
fn test_first_only_mode() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["match 1", "match 2", "match 3"]);
    let mut options = SearchOptions::default();
    options.first_only = true;

    let results = search_file(file.path(), "match", &options).unwrap();
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].line_number, 1);
}

#[test]
fn test_regex_pattern_search() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["error: 123", "error: abc", "warning: 456"]);
    let mut options = SearchOptions::default();
    options.use_regex = true;

    let results = search_file(file.path(), r"error:\s+\d+", &options).unwrap();
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].line_number, 1);
}

#[test]
fn test_line_range_filtering() {
    use crate::backend::{SearchOptions, search_file};

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
fn test_max_results_limit() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["match", "match", "match", "match"]);
    let mut options = SearchOptions::default();
    options.max_results = Some(2);

    let results = search_file(file.path(), "match", &options).unwrap();
    assert_eq!(results.len(), 2);
}

#[test]
fn test_context_lines_before_and_after() {
    use crate::backend::{SearchOptions, search_file};

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
fn test_log_level_filtering() {
    use crate::backend::{SearchOptions, search_file};

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
fn test_invert_match_mode() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["error", "info", "warning", "error"]);
    let mut options = SearchOptions::default();
    options.invert_match = true;

    let results = search_file(file.path(), "error", &options).unwrap();
    assert_eq!(results.len(), 2);
    assert_eq!(results[0].content, "info");
    assert_eq!(results[1].content, "warning");
}

#[test]
fn test_unicode_content_support() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["日本語エラー", "English error", "Español error"]);
    let options = SearchOptions::default();

    let results = search_file(file.path(), "error", &options).unwrap();
    assert_eq!(results.len(), 2);
}

#[test]
fn test_special_characters_in_pattern() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["Error: [Connection] failed (timeout)"]);
    let options = SearchOptions::default();

    let results = search_file(file.path(), "[Connection]", &options).unwrap();
    assert_eq!(results.len(), 1);
}

#[test]
fn test_empty_file_handling() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&[]);
    let options = SearchOptions::default();

    let results = search_file(file.path(), "anything", &options).unwrap();
    assert_eq!(results.len(), 0);
}

#[test]
fn test_no_matches_found() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&["line 1", "line 2", "line 3"]);
    let options = SearchOptions::default();

    let results = search_file(file.path(), "nonexistent", &options).unwrap();
    assert_eq!(results.len(), 0);
}

#[test]
fn test_large_file_performance() {
    use crate::backend::{SearchOptions, search_file};
    use std::time::Instant;

    // Create file with 10,000 lines
    let mut lines = Vec::new();
    for i in 0..10000 {
        lines.push(format!("Line number {}", i));
    }
    let line_refs: Vec<&str> = lines.iter().map(|s| s.as_str()).collect();
    let file = create_test_file(&line_refs);

    let mut options = SearchOptions::default();
    options.first_only = true;

    let start = Instant::now();
    let results = search_file(file.path(), "Line", &options).unwrap();
    let duration = start.elapsed();

    assert_eq!(results.len(), 1);
    assert!(
        duration.as_millis() < 100,
        "Search took too long: {:?}",
        duration
    );
}

#[test]
fn test_combined_filters() {
    use crate::backend::{SearchOptions, search_file};

    let file = create_test_file(&[
        "ERROR: line 1",
        "INFO: line 2",
        "ERROR: line 3",
        "ERROR: line 4",
        "INFO: line 5",
        "ERROR: line 6",
    ]);

    let mut options = SearchOptions::default();
    options.level_filter = Some("ERROR".to_string());
    options.start_line = Some(2);
    options.end_line = Some(5);
    options.max_results = Some(2);

    let results = search_file(file.path(), "line", &options).unwrap();
    assert_eq!(results.len(), 2);
    assert_eq!(results[0].line_number, 3);
    assert_eq!(results[1].line_number, 4);
}
