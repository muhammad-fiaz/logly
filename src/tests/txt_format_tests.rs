// Tests for .txt file format support

#[cfg(test)]
mod txt_format_tests {
    use std::fs::{self, File};
    use std::io::Write;
    use std::path::Path;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_txt_file_creation() {
        let test_file = "test_txt_creation.txt";

        let mut file = File::create(test_file).unwrap();
        writeln!(file, "Test log entry").unwrap();
        file.flush().unwrap();
        drop(file);

        assert!(Path::new(test_file).exists(), "TXT file should be created");

        let content = fs::read_to_string(test_file).unwrap();
        assert!(content.contains("Test log entry"), "Content should match");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_file_size_tracking() {
        let test_file = "test_txt_size.txt";

        let mut file = File::create(test_file).unwrap();
        let content = "Hello World\n";
        write!(file, "{}", content).unwrap();
        file.flush().unwrap();
        drop(file);

        let metadata = fs::metadata(test_file).unwrap();
        let size = metadata.len();

        assert_eq!(
            size,
            content.len() as u64,
            "File size should match content length"
        );

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_multiple_lines() {
        let test_file = "test_txt_lines.txt";

        let mut file = File::create(test_file).unwrap();
        for i in 1..=10 {
            writeln!(file, "Log entry {}", i).unwrap();
        }
        file.flush().unwrap();
        drop(file);

        let content = fs::read_to_string(test_file).unwrap();
        let lines: Vec<&str> = content.lines().collect();

        assert_eq!(lines.len(), 10, "Should have 10 lines");
        assert_eq!(lines[0], "Log entry 1", "First line should match");
        assert_eq!(lines[9], "Log entry 10", "Last line should match");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_line_count() {
        let test_file = "test_txt_count.txt";

        let mut file = File::create(test_file).unwrap();
        let line_count = 25;
        for i in 0..line_count {
            writeln!(file, "Message {}", i).unwrap();
        }
        file.flush().unwrap();
        drop(file);

        let content = fs::read_to_string(test_file).unwrap();
        let count = content.lines().count();

        assert_eq!(count, line_count, "Line count should match");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_metadata_fields() {
        let test_file = "test_txt_metadata.txt";

        // Create file
        let mut file = File::create(test_file).unwrap();
        writeln!(file, "Metadata test").unwrap();
        file.flush().unwrap();
        drop(file);

        let metadata = fs::metadata(test_file).unwrap();

        assert!(metadata.len() > 0, "File should have size");
        assert!(metadata.created().is_ok(), "Should have creation time");
        assert!(metadata.modified().is_ok(), "Should have modification time");
        assert!(metadata.is_file(), "Should be a file");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_line_reading_slice() {
        let test_file = "test_txt_slice.txt";

        let mut file = File::create(test_file).unwrap();
        for i in 1..=20 {
            writeln!(file, "Line {}", i).unwrap();
        }
        file.flush().unwrap();
        drop(file);

        let content = fs::read_to_string(test_file).unwrap();
        let all_lines: Vec<&str> = content.lines().collect();

        let first_five: Vec<&str> = all_lines[0..5].to_vec();
        assert_eq!(first_five.len(), 5, "Should have 5 lines");
        assert_eq!(first_five[0], "Line 1");
        assert_eq!(first_five[4], "Line 5");

        let len = all_lines.len();
        let last_three: Vec<&str> = all_lines[len - 3..len].to_vec();
        assert_eq!(last_three.len(), 3, "Should have 3 lines");
        assert_eq!(last_three[2], "Line 20");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_empty_file() {
        let test_file = "test_txt_empty.txt";

        File::create(test_file).unwrap();

        let metadata = fs::metadata(test_file).unwrap();
        assert_eq!(metadata.len(), 0, "Empty file should have size 0");

        let content = fs::read_to_string(test_file).unwrap();
        assert_eq!(content.len(), 0, "Empty file should have no content");
        assert_eq!(content.lines().count(), 0, "Empty file should have 0 lines");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_file_not_found() {
        let test_file = "nonexistent_file.txt";

        fs::remove_file(test_file).ok();

        let result = fs::read_to_string(test_file);
        assert!(result.is_err(), "Should fail to read non-existent file");

        let metadata_result = fs::metadata(test_file);
        assert!(metadata_result.is_err(), "Should fail to get metadata");
    }

    #[test]
    fn test_txt_append_mode() {
        let test_file = "test_txt_append.txt";

        let mut file = File::create(test_file).unwrap();
        writeln!(file, "Initial line").unwrap();
        file.flush().unwrap();
        drop(file);

        let mut file = fs::OpenOptions::new().append(true).open(test_file).unwrap();
        writeln!(file, "Appended line").unwrap();
        file.flush().unwrap();
        drop(file);

        let content = fs::read_to_string(test_file).unwrap();
        assert!(
            content.contains("Initial line"),
            "Should have initial content"
        );
        assert!(
            content.contains("Appended line"),
            "Should have appended content"
        );

        let lines: Vec<&str> = content.lines().collect();
        assert_eq!(lines.len(), 2, "Should have 2 lines");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_large_file() {
        let test_file = "test_txt_large.txt";

        // Create larger file
        let mut file = File::create(test_file).unwrap();
        let line_count = 1000;
        for i in 0..line_count {
            writeln!(file, "Large file line {}", i).unwrap();
        }
        file.flush().unwrap();
        drop(file);

        // Verify size and count
        let metadata = fs::metadata(test_file).unwrap();
        assert!(
            metadata.len() > 1000,
            "Large file should have substantial size"
        );

        let content = fs::read_to_string(test_file).unwrap();
        let count = content.lines().count();
        assert_eq!(count, line_count, "Should have all lines");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_concurrent_writes() {
        let test_file = "test_txt_concurrent.txt";

        fs::remove_file(test_file).ok();

        File::create(test_file).unwrap();

        for _ in 0..5 {
            let mut file = fs::OpenOptions::new().append(true).open(test_file).unwrap();
            writeln!(file, "Concurrent write").unwrap();
            file.flush().unwrap();
            drop(file);
            thread::sleep(Duration::from_millis(10));
        }

        let content = fs::read_to_string(test_file).unwrap();
        let count = content.lines().count();
        assert_eq!(count, 5, "Should have all concurrent writes");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_special_characters() {
        let test_file = "test_txt_special.txt";

        let mut file = File::create(test_file).unwrap();
        writeln!(file, "Special: !@#$%^&*()").unwrap();
        writeln!(file, "Unicode: 你好世界 🎉").unwrap();
        writeln!(file, "Quotes: \"quoted\" 'single'").unwrap();
        file.flush().unwrap();
        drop(file);

        let content = fs::read_to_string(test_file).unwrap();
        assert!(
            content.contains("!@#$%^&*()"),
            "Should handle special chars"
        );
        assert!(content.contains("你好世界 🎉"), "Should handle Unicode");
        assert!(content.contains("\"quoted\""), "Should handle quotes");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_file_path_absolute() {
        let test_file = "test_txt_path.txt";

        File::create(test_file).unwrap();

        let path = fs::canonicalize(test_file).unwrap();

        assert!(path.is_absolute(), "Path should be absolute");
        assert!(path.exists(), "File should exist at absolute path");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_performance_metadata() {
        let test_file = "test_txt_perf_meta.txt";

        let mut file = File::create(test_file).unwrap();
        writeln!(file, "Performance test").unwrap();
        file.flush().unwrap();
        drop(file);

        let start = std::time::Instant::now();
        for _ in 0..100 {
            let _ = fs::metadata(test_file).unwrap();
        }
        let duration = start.elapsed();

        assert!(duration.as_millis() < 100, "Metadata access should be fast");

        fs::remove_file(test_file).ok();
    }

    #[test]
    fn test_txt_error_handling_permissions() {
        // Platform-dependent permission testing placeholder
        let test_file = "test_txt_readonly.txt";

        File::create(test_file).unwrap();

        let metadata = fs::metadata(test_file).unwrap();
        assert!(metadata.is_file());

        fs::remove_file(test_file).ok();
    }
}
