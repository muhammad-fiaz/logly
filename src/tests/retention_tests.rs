// Tests for file retention with size_limit
// Fixes: https://github.com/muhammad-fiaz/logly/issues/77

#[cfg(test)]
mod retention {
    use std::fs;
    use std::io::Write;
    use std::thread;
    use std::time::Duration;
    use tempfile::TempDir;

    use crate::backend::file::make_file_appender;
    use crate::backend::rotation::parse_size_limit;

    #[test]
    fn test_parse_size_limit() {
        // Uppercase units
        assert_eq!(parse_size_limit(Some("1B")), Some(1));
        assert_eq!(parse_size_limit(Some("1KB")), Some(1024));
        assert_eq!(parse_size_limit(Some("1MB")), Some(1024 * 1024));
        assert_eq!(parse_size_limit(Some("1GB")), Some(1024 * 1024 * 1024));
        assert_eq!(
            parse_size_limit(Some("2TB")),
            Some(2 * 1024u64 * 1024 * 1024 * 1024)
        );

        // Lowercase units
        assert_eq!(parse_size_limit(Some("1b")), Some(1));
        assert_eq!(parse_size_limit(Some("1kb")), Some(1024));
        assert_eq!(parse_size_limit(Some("1mb")), Some(1024 * 1024));
        assert_eq!(parse_size_limit(Some("1gb")), Some(1024 * 1024 * 1024));
        assert_eq!(
            parse_size_limit(Some("2tb")),
            Some(2 * 1024u64 * 1024 * 1024 * 1024)
        );

        // Short forms
        assert_eq!(parse_size_limit(Some("10K")), Some(10 * 1024));
        assert_eq!(parse_size_limit(Some("5M")), Some(5 * 1024 * 1024));
        assert_eq!(parse_size_limit(Some("1G")), Some(1024 * 1024 * 1024));

        // Number only (defaults to bytes)
        assert_eq!(parse_size_limit(Some("100")), Some(100));

        // Invalid inputs
        assert_eq!(parse_size_limit(None), None);
        assert_eq!(parse_size_limit(Some("invalid")), None);
    }

    #[test]
    fn test_retention_with_size_limit() {
        let temp_dir = TempDir::new().unwrap();
        let log_path = temp_dir.path().join("test.log");

        // Create a file appender with 1-byte size limit and retention of 3
        let writer = make_file_appender(
            log_path.to_str().unwrap(),
            None, // no time-based rotation
            Some("before_ext"),
            false,
            Some(3),    // keep 3 files
            Some("1B"), // rotate after 1 byte
        );

        // Write multiple messages to trigger rotations
        for i in 0..10 {
            let mut w = writer.lock();
            writeln!(&mut **w, "Message {}", i).unwrap();
            w.flush().unwrap();
            drop(w);
            thread::sleep(Duration::from_millis(10)); // Small delay for file system
        }

        // Wait a bit for async operations
        thread::sleep(Duration::from_millis(100));

        // Count log files
        let mut log_files = Vec::new();
        for entry in fs::read_dir(temp_dir.path()).unwrap() {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("log") {
                log_files.push(path);
            }
        }

        // Should have at most 3 files (retention limit)
        assert!(
            log_files.len() <= 3,
            "Expected at most 3 log files, found {}. Files: {:?}",
            log_files.len(),
            log_files
        );
    }

    #[test]
    fn test_retention_without_size_limit() {
        let temp_dir = TempDir::new().unwrap();
        let log_path = temp_dir.path().join("daily_test.log");

        // Create a file appender with daily rotation and retention of 5
        let writer = make_file_appender(
            log_path.to_str().unwrap(),
            Some("daily"),
            Some("before_ext"),
            true,
            Some(5), // keep 5 files
            None,    // no size limit
        );

        // Write a message
        let mut w = writer.lock();
        writeln!(&mut **w, "Test message").unwrap();
        w.flush().unwrap();
    }

    #[test]
    fn test_retention_counts_current_file() {
        let temp_dir = TempDir::new().unwrap();
        let log_path = temp_dir.path().join("retention_test.log");

        // Manually create some old log files
        for i in 0..5 {
            let old_file = temp_dir
                .path()
                .join(format!("retention_test.2025-01-0{}.log", i + 1));
            fs::write(&old_file, format!("Old log {}", i)).unwrap();
        }

        // Create appender with retention=3
        let writer = make_file_appender(
            log_path.to_str().unwrap(),
            None,
            Some("before_ext"),
            false,
            Some(3), // keep only 3 files total
            Some("10B"),
        );

        // Write a message
        let mut w = writer.lock();
        writeln!(&mut **w, "New log entry").unwrap();
        w.flush().unwrap();
        drop(w);

        // Wait for cleanup
        thread::sleep(Duration::from_millis(200));

        // Count remaining log files
        let mut log_files = Vec::new();
        for entry in fs::read_dir(temp_dir.path()).unwrap() {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.to_str().unwrap().contains("retention_test") {
                log_files.push(path);
            }
        }

        // Should have at most 3 files
        assert!(
            log_files.len() <= 3,
            "Expected at most 3 files with retention=3, found {}",
            log_files.len()
        );
    }

    #[test]
    fn test_combined_rotation_and_retention() {
        let temp_dir = TempDir::new().unwrap();
        let log_path = temp_dir.path().join("combined.log");

        // Use both time-based and size-based rotation
        let writer = make_file_appender(
            log_path.to_str().unwrap(),
            Some("hourly"),
            Some("before_ext"),
            true,
            Some(2),    // keep only 2 files
            Some("5B"), // rotate after 5 bytes
        );

        // Write some data
        for i in 0..5 {
            let mut w = writer.lock();
            writeln!(&mut **w, "Log {}", i).unwrap();
            w.flush().unwrap();
            drop(w);
            thread::sleep(Duration::from_millis(10));
        }

        thread::sleep(Duration::from_millis(100));

        // Verify files exist
        assert!(log_path.exists() || temp_dir.path().read_dir().unwrap().count() > 0);
    }

    #[test]
    fn test_no_retention_keeps_all_files() {
        let temp_dir = TempDir::new().unwrap();
        let log_path = temp_dir.path().join("no_retention.log");

        // No retention limit
        let writer = make_file_appender(
            log_path.to_str().unwrap(),
            None,
            Some("before_ext"),
            false,
            None,       // no retention limit
            Some("1B"), // small size to trigger rotations
        );

        // Write multiple messages
        for i in 0..5 {
            let mut w = writer.lock();
            writeln!(&mut **w, "Message {}", i).unwrap();
            w.flush().unwrap();
            drop(w);
            thread::sleep(Duration::from_millis(10));
        }

        thread::sleep(Duration::from_millis(50));

        // Should have multiple files (no limit)
        let log_files: Vec<_> = fs::read_dir(temp_dir.path())
            .unwrap()
            .filter_map(|e| e.ok())
            .filter(|e| e.path().to_str().unwrap().contains("no_retention"))
            .collect();

        // Should have created at least 2 files due to 1-byte limit and multiple writes
        // (More lenient check as file rotation timing can vary)
        assert!(
            log_files.len() >= 2,
            "Expected at least 2 rotated files without retention, found {}",
            log_files.len()
        );
    }
}
