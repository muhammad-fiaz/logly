"""
Tests for .txt file logging functionality in Logly.
"""

import os
import time

import pytest

import logly


class TestTxtFileBasics:
    """Test basic .txt file logging functionality."""

    def setup_method(self):
        """Setup for each test - create logger and cleanup."""
        self.logger = logly.PyLogger(auto_update_check=False)
        self.test_files = []

    def teardown_method(self):
        """Cleanup after each test."""
        self.logger._reset_for_tests()
        for filepath in self.test_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    def test_basic_txt_logging(self):
        """Test basic logging to .txt file."""
        filepath = "test_basic.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath, async_write=False)  # Synchronous for immediate write
        assert sink_id is not None

        self.logger.info("Hello from txt file")
        self.logger.warning("Warning message")
        self.logger.error("Error message")

        # Verify file exists
        assert os.path.exists(filepath)

        # Read content
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
            assert "Hello from txt file" in content
            assert "Warning message" in content
            assert "Error message" in content

    def test_txt_with_rotation_daily(self):
        """Test .txt file with daily rotation."""
        filepath = "logs/daily_app.txt"
        self.test_files.append(filepath)
        os.makedirs("logs", exist_ok=True)

        sink_id = self.logger.add(filepath, rotation="daily", date_enabled=True)

        assert sink_id is not None
        self.logger.info("Daily rotation test")

        # Verify file created
        assert os.path.exists(filepath) or any(
            "daily_app" in f for f in os.listdir("logs") if f.endswith(".txt")
        )

    def test_txt_with_rotation_size(self):
        """Test .txt file with size-based rotation."""
        filepath = "logs/size_app.txt"
        self.test_files.append(filepath)
        os.makedirs("logs", exist_ok=True)

        self.logger.add(
            filepath,
            rotation="1 KB",  # Rotate at 1KB
        )

        # Write enough data to trigger rotation
        for i in range(50):
            self.logger.info(f"Message {i} - " + "x" * 100)

        # Check if rotation occurred (multiple files)
        log_files = [f for f in os.listdir("logs") if "size_app" in f and f.endswith(".txt")]
        # May have rotated files
        assert len(log_files) >= 1

    def test_txt_with_retention(self):
        """Test .txt file with retention policy."""
        filepath = "logs/retention_app.txt"
        self.test_files.append(filepath)
        os.makedirs("logs", exist_ok=True)

        self.logger.add(
            filepath,
            rotation="100B",
            retention=3,  # Keep only 3 files
        )

        # Write enough to create multiple rotated files
        for i in range(100):
            self.logger.info(f"Retention test message {i}")

        # Verify file exists
        assert os.path.exists(filepath) or any(
            "retention_app" in f for f in os.listdir("logs") if f.endswith(".txt")
        )

    def test_txt_with_async_write(self):
        """Test .txt file with async writing."""
        filepath = "logs/async_app.txt"
        self.test_files.append(filepath)
        os.makedirs("logs", exist_ok=True)

        self.logger.add(filepath, async_write=True)

        # Write multiple messages quickly
        for i in range(10):
            self.logger.info(f"Async message {i}")

        # Wait a bit for async writes
        time.sleep(0.5)

        # Verify file exists
        assert os.path.exists(filepath)

    def test_txt_complete_configuration(self):
        """Test .txt file with all configuration options."""
        filepath = "logs/complete_app.txt"
        self.test_files.append(filepath)
        os.makedirs("logs", exist_ok=True)

        sink_id = self.logger.add(
            filepath, rotation="daily", retention=7, date_enabled=True, async_write=True
        )

        assert sink_id is not None

        # Log some messages
        self.logger.info("Complete configuration test")
        self.logger.debug("Debug message")
        self.logger.warning("Warning message")

        time.sleep(0.5)  # Wait for async writes

        # Verify file exists
        assert os.path.exists(filepath) or any(
            "complete_app" in f for f in os.listdir("logs") if f.endswith(".txt")
        )


class TestTxtFileOperations:
    """Test file operations on .txt files."""

    def setup_method(self):
        """Setup for each test."""
        self.logger = logly.PyLogger(auto_update_check=False)
        self.test_files = []

    def teardown_method(self):
        """Cleanup after each test."""
        self.logger._reset_for_tests()
        for filepath in self.test_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    def test_txt_file_size(self):
        """Test file_size() on .txt file."""
        filepath = "test_size.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath, async_write=False)
        self.logger.info("Test message for size")

        size = self.logger.file_size(sink_id)
        assert size is not None
        assert size > 0

    def test_txt_file_metadata(self):
        """Test file_metadata() on .txt file."""
        filepath = "test_metadata.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath)
        self.logger.info("Metadata test message")

        metadata = self.logger.file_metadata(sink_id)
        assert metadata is not None
        assert "size" in metadata
        assert "path" in metadata
        assert "created" in metadata
        assert "modified" in metadata
        assert ".txt" in metadata["path"]

    def test_txt_read_lines(self):
        """Test read_lines() on .txt file."""
        filepath = "test_read_lines.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath, async_write=False)

        # Write multiple lines
        for i in range(1, 11):
            self.logger.info(f"Line {i}")

        # Read first 3 lines
        lines = self.logger.read_lines(sink_id, 1, 3)
        assert lines is not None
        assert "Line 1" in lines
        assert "Line 2" in lines
        assert "Line 3" in lines

        # Read last 2 lines using negative indices
        last_lines = self.logger.read_lines(sink_id, -2, -1)
        assert last_lines is not None
        assert "Line 9" in last_lines or "Line 10" in last_lines

    def test_txt_line_count(self):
        """Test line_count() on .txt file."""
        filepath = "test_line_count.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath, async_write=False)

        # Write known number of lines
        expected_count = 15
        for i in range(expected_count):
            self.logger.info(f"Message {i}")

        count = self.logger.line_count(sink_id)
        assert count is not None
        assert count == expected_count

    def test_txt_read_all(self):
        """Test read_all() on .txt file."""
        filepath = "test_read_all.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath, async_write=False)

        test_messages = ["First message", "Second message", "Third message"]
        for msg in test_messages:
            self.logger.info(msg)

        # Read all content using read_lines
        line_count = self.logger.line_count(sink_id)
        content = self.logger.read_lines(sink_id, 0, line_count) if line_count else ""
        assert content is not None
        for msg in test_messages:
            assert msg in content


class TestTxtExceptionHandling:
    """Test exception handling for .txt file operations."""

    def setup_method(self):
        """Setup for each test."""
        self.logger = logly.PyLogger(auto_update_check=False)
        self.test_files = []

    def teardown_method(self):
        """Cleanup after each test."""
        self.logger._reset_for_tests()
        for filepath in self.test_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    def test_invalid_sink_id_file_size(self):
        """Test file_size() with invalid sink ID."""
        result = self.logger.file_size(99999)
        assert result is None

    def test_invalid_sink_id_file_metadata(self):
        """Test file_metadata() with invalid sink ID."""
        result = self.logger.file_metadata(99999)
        assert result is None

    def test_invalid_sink_id_read_lines(self):
        """Test read_lines() with invalid sink ID."""
        result = self.logger.read_lines(99999, 1, 10)
        assert result is None

    def test_invalid_sink_id_line_count(self):
        """Test line_count() with invalid sink ID."""
        result = self.logger.line_count(99999)
        assert result is None

    def test_invalid_sink_id_read_json(self):
        """Test read_json() with invalid sink ID."""
        result = self.logger.read_json(99999)
        assert result is None

    def test_txt_read_lines_out_of_bounds(self):
        """Test read_lines() with out-of-bounds indices."""
        filepath = "test_bounds.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath)

        # Write only 5 lines
        for i in range(5):
            self.logger.info(f"Line {i}")

        # Request lines beyond file size (should clamp)
        lines = self.logger.read_lines(sink_id, 1, 100)
        assert lines is not None  # Should still return valid lines

        # Request with start > end (should handle gracefully)
        lines = self.logger.read_lines(sink_id, 10, 5)
        # Behavior depends on implementation

    def test_empty_txt_file_operations(self):
        """Test operations on empty .txt file."""
        filepath = "test_empty.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath)

        # Don't write anything, just check operations
        size = self.logger.file_size(sink_id)
        assert size is not None  # May be 0

        count = self.logger.line_count(sink_id)
        assert count is not None
        assert count == 0

        # Read all content using read_lines
        line_count = self.logger.line_count(sink_id)
        content = self.logger.read_lines(sink_id, 0, line_count) if line_count else None
        assert content is None or content == ""


class TestTxtPerformance:
    """Test performance optimizations for .txt file operations."""

    def setup_method(self):
        """Setup for each test."""
        self.logger = logly.PyLogger(auto_update_check=False)
        self.test_files = []

    def teardown_method(self):
        """Cleanup after each test."""
        self.logger._reset_for_tests()
        for filepath in self.test_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    def test_async_write_performance(self):
        """Test async writing performance."""
        filepath = "test_async_perf.txt"
        self.test_files.append(filepath)

        # Test with async
        self.logger.add(filepath, async_write=True)

        start_time = time.time()
        for i in range(100):
            self.logger.info(f"Async message {i}")
        async_time = time.time() - start_time

        time.sleep(0.2)  # Wait for async writes to complete

        # Async should be fast (non-blocking)
        assert async_time < 1.0  # Should complete quickly

    def test_large_file_operations(self):
        """Test operations on larger .txt files."""
        filepath = "test_large.txt"
        self.test_files.append(filepath)

        sink_id = self.logger.add(filepath, async_write=False)  # Synchronous for immediate counting

        # Write 1000 lines
        for i in range(1000):
            self.logger.info(f"Message {i}")

        # Test file_size (should be fast - metadata only)
        start = time.time()
        _size = self.logger.file_size(sink_id)
        size_time = time.time() - start
        assert size_time < 1.0  # Should be fast

        # Test line_count (may be slower - reads file)
        start = time.time()
        count = self.logger.line_count(sink_id)
        _count_time = time.time() - start
        assert count == 1000
        # Line count may take longer for large files

        # Test read_lines with small range (should be efficient)
        start = time.time()
        lines = self.logger.read_lines(sink_id, 1, 10)
        _read_time = time.time() - start
        assert lines is not None


class TestTxtMultipleSinks:
    """Test multiple .txt file sinks simultaneously."""

    def setup_method(self):
        """Setup for each test."""
        self.logger = logly.PyLogger(auto_update_check=False)
        self.test_files = []

    def teardown_method(self):
        """Cleanup after each test."""
        self.logger._reset_for_tests()
        for filepath in self.test_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    def test_multiple_txt_sinks(self):
        """Test logging to multiple .txt files simultaneously."""
        files = ["test_multi_1.txt", "test_multi_2.txt", "test_multi_3.txt"]
        self.test_files.extend(files)

        sinks = []
        for filepath in files:
            sink_id = self.logger.add(filepath, async_write=False)
            sinks.append(sink_id)

        # Write to all sinks
        self.logger.info("Message to all sinks")

        # Verify all files
        for filepath in files:
            assert os.path.exists(filepath)
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
                assert "Message to all sinks" in content

    def test_txt_sinks_different_configs(self):
        """Test .txt sinks with different configurations."""
        self.test_files.extend(["test_sync.txt", "test_async.txt", "logs/test_rotated.txt"])
        os.makedirs("logs", exist_ok=True)

        self.logger.add("test_sync.txt", async_write=False)
        self.logger.add("test_async.txt", async_write=True)
        self.logger.add("logs/test_rotated.txt", rotation="1 KB", date_enabled=True)

        # Write to all
        for i in range(10):
            self.logger.info(f"Test message {i}")

        time.sleep(0.5)  # Wait for async

        # Verify all exist
        assert os.path.exists("test_sync.txt")
        assert os.path.exists("test_async.txt")
        assert os.path.exists("logs/test_rotated.txt") or any(
            "test_rotated" in f for f in os.listdir("logs") if f.endswith(".txt")
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
