// Test module for Logly file operations features
// These tests verify the core functionality of new file operation methods

mod txt_format_tests;

#[cfg(test)]
mod file_ops_tests {
    use std::fs;
    use std::io::Write;
    use std::path::PathBuf;

    #[test]
    fn test_file_size_calculation() {
        // Create a test file with known content
        let test_file = "test_size_calc.log";
        let test_content = b"Hello World!\nThis is a test.\n";
        let mut file = fs::File::create(test_file).unwrap();
        file.write_all(test_content).unwrap();
        file.flush().unwrap();
        drop(file);

        // Verify file size
        let metadata = fs::metadata(test_file).unwrap();
        let size = metadata.len();
        assert_eq!(
            size,
            test_content.len() as u64,
            "File size should match content length"
        );

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_file_metadata_fields() {
        // Create a test file
        let test_file = "test_metadata_fields.log";
        let mut file = fs::File::create(test_file).unwrap();
        file.write_all(b"Test content for metadata\n").unwrap();
        file.flush().unwrap();
        drop(file);

        // Get metadata
        let metadata = fs::metadata(test_file).unwrap();

        // Verify we can access all required fields
        assert!(metadata.len() > 0, "File size should be positive");
        assert!(metadata.created().is_ok(), "Should have created time");
        assert!(metadata.modified().is_ok(), "Should have modified time");

        // Verify path exists
        let path = PathBuf::from(test_file);
        assert!(path.exists(), "Path should exist");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_read_lines_from_file() {
        // Create file with multiple lines
        let test_file = "test_read_lines.log";
        let mut file = fs::File::create(test_file).unwrap();
        for i in 1..=10 {
            writeln!(file, "Line {}", i).unwrap();
        }
        file.flush().unwrap();
        drop(file);

        // Read and verify lines
        let content = fs::read_to_string(test_file).unwrap();
        let lines: Vec<&str> = content.lines().collect();
        assert_eq!(lines.len(), 10, "Should have exactly 10 lines");
        assert!(
            lines[0].contains("Line 1"),
            "First line should contain 'Line 1'"
        );
        assert!(
            lines[9].contains("Line 10"),
            "Last line should contain 'Line 10'"
        );

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_line_slice_extraction() {
        // Create file with multiple lines
        let test_file = "test_line_slice.log";
        let mut file = fs::File::create(test_file).unwrap();
        for i in 1..=10 {
            writeln!(file, "Line {}", i).unwrap();
        }
        file.flush().unwrap();
        drop(file);

        // Read all lines
        let content = fs::read_to_string(test_file).unwrap();
        let all_lines: Vec<&str> = content.lines().collect();

        // Test slicing - first 3 lines
        let first_three: Vec<&str> = all_lines[0..3].to_vec();
        assert_eq!(first_three.len(), 3, "Should have 3 lines");

        // Test slicing - last 2 lines
        let total = all_lines.len();
        let last_two: Vec<&str> = all_lines[total - 2..total].to_vec();
        assert_eq!(last_two.len(), 2, "Should have 2 lines");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_line_count_accuracy() {
        // Create file with known number of lines
        let test_file = "test_line_count.log";
        let mut file = fs::File::create(test_file).unwrap();
        let expected_count = 7;
        for i in 1..=expected_count {
            writeln!(file, "Message {}", i).unwrap();
        }
        file.flush().unwrap();
        drop(file);

        // Count lines
        let content = fs::read_to_string(test_file).unwrap();
        let count = content.lines().count();
        assert_eq!(
            count, expected_count,
            "Should have exactly {} lines",
            expected_count
        );

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_json_parsing() {
        // Create a JSON file
        let test_file = "test_json_parse.log";
        let mut file = fs::File::create(test_file).unwrap();
        let json_str = r#"{"level":"INFO","message":"test message","user":"alice"}"#;
        write!(file, "{}", json_str).unwrap();
        file.flush().unwrap();
        drop(file);

        // Read and parse JSON
        let content = fs::read_to_string(test_file).unwrap();
        let parsed: Result<serde_json::Value, _> = serde_json::from_str(content.trim());
        assert!(parsed.is_ok(), "Should parse as valid JSON");

        let json = parsed.unwrap();
        assert_eq!(json["level"], "INFO", "Level should be INFO");
        assert_eq!(json["message"], "test message", "Message should match");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_ndjson_parsing() {
        // Create NDJSON file (newline-delimited JSON)
        let test_file = "test_ndjson_parse.log";
        let mut file = fs::File::create(test_file).unwrap();
        writeln!(file, r#"{{"level":"INFO","message":"first"}}"#).unwrap();
        writeln!(file, r#"{{"level":"WARN","message":"second"}}"#).unwrap();
        writeln!(file, r#"{{"level":"ERROR","message":"third"}}"#).unwrap();
        file.flush().unwrap();
        drop(file);

        // Read and parse NDJSON
        let content = fs::read_to_string(test_file).unwrap();
        let lines: Vec<&str> = content.lines().collect();
        assert_eq!(lines.len(), 3, "Should have 3 JSON lines");

        // Parse each line as JSON
        for line in lines {
            let parsed: Result<serde_json::Value, _> = serde_json::from_str(line);
            assert!(parsed.is_ok(), "Each line should be valid JSON");
        }

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_json_pretty_formatting() {
        // Create a JSON structure
        let json_obj = serde_json::json!({
            "level": "INFO",
            "message": "test",
            "metadata": {
                "user": "alice",
                "action": "login"
            }
        });

        // Test compact formatting
        let compact = serde_json::to_string(&json_obj).unwrap();
        assert!(
            !compact.contains("\n"),
            "Compact JSON should not have newlines"
        );

        // Test pretty formatting
        let pretty = serde_json::to_string_pretty(&json_obj).unwrap();
        assert!(pretty.contains("\n"), "Pretty JSON should have newlines");
        assert!(pretty.len() > compact.len(), "Pretty JSON should be longer");
    }

    #[test]
    fn test_empty_file_handling() {
        // Create an empty file
        let test_file = "test_empty_file.log";
        let mut file = fs::File::create(test_file).unwrap();
        file.flush().unwrap();
        drop(file);

        // Verify empty file
        let metadata = fs::metadata(test_file).unwrap();
        assert_eq!(metadata.len(), 0, "Empty file should have size 0");

        let content = fs::read_to_string(test_file).unwrap();
        assert_eq!(content.len(), 0, "Empty file should have no content");
        assert_eq!(content.lines().count(), 0, "Empty file should have 0 lines");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_file_not_found_handling() {
        // Try to read non-existent file
        let test_file = "absolutely_nonexistent_file.log";
        let result = fs::read_to_string(test_file);
        assert!(result.is_err(), "Should fail to read non-existent file");

        // Try to get metadata of non-existent file
        let metadata_result = fs::metadata(test_file);
        assert!(
            metadata_result.is_err(),
            "Should fail to get metadata of non-existent file"
        );
    }
}
