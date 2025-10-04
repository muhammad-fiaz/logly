"""
Tests for all new Logly features:
- Sink management: sink_count, list_sinks, sink_info, all_sinks_info
- File operations: delete, delete_all
- Log reading: read, read_all
- Console operations: clear
"""

import os

from logly import logger


class TestSinkManagement:
    """Tests for sink management features"""

    def setup_method(self):
        """Clean up before each test"""
        logger.remove_all()
        self.cleanup_files()

    def teardown_method(self):
        """Clean up after each test"""
        logger.remove_all()
        self.cleanup_files()

    def cleanup_files(self):
        """Remove test log files"""
        test_files = [
            "test_sink_count.log",
            "test_list_1.log",
            "test_list_2.log",
            "test_info.log",
            "test_all_info_1.log",
            "test_all_info_2.log",
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_sink_count_empty(self):
        """Test sink_count returns 0 when no sinks"""
        count = logger.sink_count()
        assert count == 0, "Should have 0 sinks initially"

    def test_sink_count_after_add(self):
        """Test sink_count returns correct count after adding sinks"""
        logger.add("test_sink_count.log", async_write=False)
        count = logger.sink_count()
        assert count == 1, "Should have 1 sink after adding"

    def test_sink_count_multiple(self):
        """Test sink_count with multiple sinks"""
        logger.add("test_list_1.log", async_write=False)
        logger.add("test_list_2.log", async_write=False)
        count = logger.sink_count()
        assert count == 2, "Should have 2 sinks"

    def test_list_sinks_empty(self):
        """Test list_sinks returns empty list when no sinks"""
        sinks = logger.list_sinks()
        assert len(sinks) == 0, "Should have empty sink list initially"

    def test_list_sinks_returns_ids(self):
        """Test list_sinks returns correct sink IDs"""
        id1 = logger.add("test_list_1.log", async_write=False)
        id2 = logger.add("test_list_2.log", async_write=False)

        sinks = logger.list_sinks()
        assert len(sinks) == 2, "Should have 2 sink IDs"
        assert id1 in sinks, "Should contain first ID"
        assert id2 in sinks, "Should contain second ID"

    def test_sink_info_valid_id(self):
        """Test sink_info returns info for valid sink ID"""
        id = logger.add("test_info.log", rotation="daily", async_write=False)

        info = logger.sink_info(id)
        assert info is not None, "Should return info for valid ID"
        assert "path" in info, "Should have 'path' key"
        assert info["path"] == "test_info.log"

    def test_sink_info_invalid_id(self):
        """Test sink_info returns None for invalid ID"""
        info = logger.sink_info(99999)
        assert info is None, "Should return None for invalid ID"

    def test_all_sinks_info(self):
        """Test all_sinks_info returns info for all sinks"""
        id1 = logger.add("test_all_info_1.log", rotation="daily", async_write=False)
        id2 = logger.add("test_all_info_2.log", rotation="hourly", async_write=False)

        all_info = logger.all_sinks_info()
        assert len(all_info) == 2, "Should return info for all sinks"

        # Extract IDs from info
        ids = [int(info["id"]) for info in all_info if "id" in info]
        assert id1 in ids, "Should contain first sink ID"
        assert id2 in ids, "Should contain second sink ID"


class TestFileOperations:
    """Tests for file operation features"""

    def setup_method(self):
        """Clean up before each test"""
        logger.remove_all()
        self.cleanup_files()

    def teardown_method(self):
        """Clean up after each test"""
        logger.remove_all()
        self.cleanup_files()

    def cleanup_files(self):
        """Remove test log files"""
        test_files = [
            "test_delete.log",
            "test_delete_keeps.log",
            "test_del_all_1.log",
            "test_del_all_2.log",
            "test_del_all_3.log",
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_delete_existing_file(self):
        """Test delete removes existing log file"""
        id = logger.add("test_delete.log", async_write=False)
        logger.info("Test message")

        assert os.path.exists("test_delete.log"), "File should exist before delete"

        result = logger.delete(id)
        assert result, "Delete should return True for existing file"
        assert not os.path.exists("test_delete.log"), "File should not exist after delete"

    def test_delete_invalid_sink(self):
        """Test delete returns False for invalid sink ID"""
        result = logger.delete(99999)
        assert not result, "Delete should return False for invalid sink ID"

    def test_delete_keeps_sink_active(self):
        """Test delete keeps sink active after file deletion"""
        sink_id = logger.add("test_delete_keeps.log", async_write=False)
        logger.info("Before delete")

        logger.delete(sink_id)

        # Sink should still be active
        count = logger.sink_count()
        assert count == 1, "Sink should still be active after file deletion"

        # Should be able to log again (file will be recreated)
        logger.info("After delete")
        # Note: File may not exist immediately if async writing is enabled
        # The important thing is the sink is still active

    def test_delete_all_multiple_files(self):
        """Test delete_all removes all log files"""
        logger.add("test_del_all_1.log", async_write=False)
        logger.add("test_del_all_2.log", async_write=False)
        logger.add("test_del_all_3.log", async_write=False)

        logger.info("Creating files")

        count = logger.delete_all()
        assert count == 3, "Should delete all 3 files"

        assert not os.path.exists("test_del_all_1.log"), "File 1 should be deleted"
        assert not os.path.exists("test_del_all_2.log"), "File 2 should be deleted"
        assert not os.path.exists("test_del_all_3.log"), "File 3 should be deleted"

    def test_delete_all_keeps_sinks_active(self):
        """Test delete_all keeps sinks active"""
        logger.add("test_del_all_1.log", async_write=False)
        logger.add("test_del_all_2.log", async_write=False)

        logger.info("Before delete_all")
        logger.delete_all()

        # Sinks should still be active
        count = logger.sink_count()
        assert count == 2, "Sinks should still be active after delete_all"


class TestLogReading:
    """Tests for log reading features"""

    def setup_method(self):
        """Clean up before each test"""
        logger.remove_all()
        self.cleanup_files()

    def teardown_method(self):
        """Clean up after each test"""
        logger.remove_all()
        self.cleanup_files()

    def cleanup_files(self):
        """Remove test log files"""
        test_files = [
            "test_read.log",
            "test_read_multiple.log",
            "test_read_all_1.log",
            "test_read_all_2.log",
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_read_valid_sink(self):
        """Test read returns content for valid sink"""
        id = logger.add("test_read.log", async_write=False)
        logger.info("Test log message")

        content = logger.read(id)
        assert content is not None, "Should return content for valid sink"
        assert "Test log message" in content, "Content should contain logged message"

    def test_read_invalid_sink(self):
        """Test read returns None for invalid sink ID"""
        content = logger.read(99999)
        assert content is None, "Should return None for invalid sink ID"

    def test_read_multiple_messages(self):
        """Test read returns all messages from file"""
        id = logger.add("test_read_multiple.log", async_write=False)
        logger.info("First message")
        logger.info("Second message")
        logger.info("Third message")

        content = logger.read(id)
        assert content is not None, "Should return content"
        assert "First message" in content, "Should contain first message"
        assert "Second message" in content, "Should contain second message"
        assert "Third message" in content, "Should contain third message"

    def test_read_all_multiple_sinks(self):
        """Test read_all returns content from all sinks"""
        id1 = logger.add("test_read_all_1.log", async_write=False)
        id2 = logger.add("test_read_all_2.log", async_write=False)

        logger.info("Message to both sinks")

        all_logs = logger.read_all()
        assert len(all_logs) == 2, "Should return content for all sinks"
        assert id1 in all_logs, "Should contain first sink"
        assert id2 in all_logs, "Should contain second sink"

    def test_read_preserves_file(self):
        """Test read does not delete or modify the file"""
        id = logger.add("test_read.log", async_write=False)
        logger.info("Test message")

        # Read the file
        logger.read(id)

        # File should still exist
        assert os.path.exists("test_read.log"), "File should still exist after reading"

        # Should be able to read again
        content = logger.read(id)
        assert content is not None, "Should be able to read file again"


class TestConsoleOperations:
    """Tests for console operation features"""

    def setup_method(self):
        """Clean up before each test"""
        logger.remove_all()

    def teardown_method(self):
        """Clean up after each test"""
        logger.remove_all()

    def test_clear_executes_without_error(self):
        """Test clear executes without raising an error"""
        try:
            logger.clear()
            success = True
        except Exception:
            success = False

        assert success, "Clear should execute without error"

    def test_clear_multiple_times(self):
        """Test clear can be called multiple times"""
        try:
            logger.clear()
            logger.clear()
            logger.clear()
            success = True
        except Exception:
            success = False

        assert success, "Should be able to clear multiple times"

    def test_clear_does_not_affect_sinks(self):
        """Test clear does not affect sink count"""
        logger.add("test_clear.log", async_write=False)

        count_before = logger.sink_count()
        logger.clear()
        count_after = logger.sink_count()

        assert count_before == count_after, "Clear should not affect sink count"

        if os.path.exists("test_clear.log"):
            os.remove("test_clear.log")

    def test_clear_does_not_delete_files(self):
        """Test clear does not delete log files"""
        logger.add("test_clear.log", async_write=False)
        logger.info("Test message")

        logger.clear()

        # File should still exist
        assert os.path.exists("test_clear.log"), "Clear should not delete log files"

        if os.path.exists("test_clear.log"):
            os.remove("test_clear.log")


class TestAdvancedFileOperations:
    """Tests for advanced file operations: file_size, file_metadata, read_lines, line_count, read_json"""

    def setup_method(self):
        """Clean up before each test"""
        logger.remove_all()
        self.cleanup_files()

    def teardown_method(self):
        """Clean up after each test"""
        logger.remove_all()
        self.cleanup_files()

    def cleanup_files(self):
        """Remove test log files"""
        test_files = [
            "test_file_size.log",
            "test_metadata.log",
            "test_read_lines.log",
            "test_line_count.log",
            "test_json.log",
            "test_json_ndjson.log",
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_file_size_exists(self):
        """Test file_size returns size for existing file"""
        sink_id = logger.add("test_file_size.log", async_write=False)
        logger.info("Test message for file size")

        size = logger.file_size(sink_id)
        assert size is not None, "File size should not be None"
        assert size > 0, f"File size should be positive, got {size}"

    def test_file_size_nonexistent_sink(self):
        """Test file_size returns None for non-existent sink"""
        size = logger.file_size(99999)
        assert size is None, "File size should be None for non-existent sink"

    def test_file_metadata_complete(self):
        """Test file_metadata returns all expected fields"""
        sink_id = logger.add("test_metadata.log", async_write=False)
        logger.info("Test message for metadata")

        metadata = logger.file_metadata(sink_id)
        assert metadata is not None, "Metadata should not be None"
        assert "size" in metadata, "Metadata should contain 'size'"
        assert "path" in metadata, "Metadata should contain 'path'"
        assert "created" in metadata, "Metadata should contain 'created'"
        assert "modified" in metadata, "Metadata should contain 'modified'"

        # Verify size is numeric
        assert int(metadata["size"]) > 0, "Size should be positive"

        # Verify path ends with filename
        assert metadata["path"].endswith("test_metadata.log"), (
            f"Path should end with filename, got {metadata['path']}"
        )

    def test_file_metadata_nonexistent_sink(self):
        """Test file_metadata returns None for non-existent sink"""
        metadata = logger.file_metadata(99999)
        assert metadata is None, "Metadata should be None for non-existent sink"

    def test_read_lines_first_n(self):
        """Test reading first N lines"""
        sink_id = logger.add("test_read_lines.log", async_write=False)

        # Write 10 lines
        for i in range(10):
            logger.info(f"Line {i + 1}")

        # Read first 3 lines
        lines = logger.read_lines(sink_id, 1, 3)
        assert lines is not None, "Lines should not be None"
        line_list = lines.split("\n")
        assert len(line_list) == 3, f"Should have 3 lines, got {len(line_list)}"
        assert "Line 1" in line_list[0], f"First line should contain 'Line 1', got {line_list[0]}"

    def test_read_lines_last_n(self):
        """Test reading last N lines using negative indices"""
        sink_id = logger.add("test_read_lines.log", async_write=False)

        # Write 10 lines
        for i in range(10):
            logger.info(f"Line {i + 1}")

        # Read last 2 lines
        lines = logger.read_lines(sink_id, -2, -1)
        assert lines is not None, "Lines should not be None"
        line_list = lines.split("\n")
        assert len(line_list) == 2, f"Should have 2 lines, got {len(line_list)}"
        assert "Line 9" in line_list[0] or "Line 10" in line_list[0], (
            "Should contain Line 9 or Line 10"
        )

    def test_read_lines_middle_range(self):
        """Test reading a middle range of lines"""
        sink_id = logger.add("test_read_lines.log", async_write=False)

        # Write 10 lines
        for i in range(10):
            logger.info(f"Line {i + 1}")

        # Read lines 5-7
        lines = logger.read_lines(sink_id, 5, 7)
        assert lines is not None, "Lines should not be None"
        line_list = lines.split("\n")
        assert len(line_list) == 3, f"Should have 3 lines, got {len(line_list)}"

    def test_read_lines_nonexistent_sink(self):
        """Test read_lines returns None for non-existent sink"""
        lines = logger.read_lines(99999, 1, 10)
        assert lines is None, "Lines should be None for non-existent sink"

    def test_line_count_accurate(self):
        """Test line_count returns accurate count"""
        sink_id = logger.add("test_line_count.log", async_write=False)

        # Write exactly 5 lines
        for i in range(5):
            logger.info(f"Message {i + 1}")

        count = logger.line_count(sink_id)
        assert count is not None, "Count should not be None"
        assert count == 5, f"Should have exactly 5 lines, got {count}"

    def test_line_count_zero(self):
        """Test line_count for empty file"""
        sink_id = logger.add("test_line_count.log", async_write=False)
        # Don't write anything

        # File might not exist yet or be empty
        count = logger.line_count(sink_id)
        # Either None (file doesn't exist) or 0 (empty file)
        assert count is None or count == 0, f"Empty file should have 0 or None lines, got {count}"

    def test_line_count_nonexistent_sink(self):
        """Test line_count returns None for non-existent sink"""
        count = logger.line_count(99999)
        assert count is None, "Count should be None for non-existent sink"

    def test_read_json_compact(self):
        """Test reading JSON logs in compact format"""
        import time

        sink_id = logger.add("test_json.log", format="json", async_write=False)
        logger.info("Test message", user="alice", action="login")
        time.sleep(0.1)  # Give async write time to complete

        json_content = logger.read_json(sink_id, pretty=False)
        assert json_content is not None, "JSON content should not be None"
        # Content should be a string (even if not valid JSON)
        assert isinstance(json_content, str), "JSON content should be a string"
        assert len(json_content) > 0, "JSON content should not be empty"

    def test_read_json_pretty(self):
        """Test reading JSON logs in pretty format"""
        import time

        sink_id = logger.add("test_json.log", format="json", async_write=False)
        logger.info("Test message", user="bob", action="logout")
        time.sleep(0.1)  # Give async write time to complete

        json_content = logger.read_json(sink_id, pretty=True)
        assert json_content is not None, "JSON content should not be None"
        assert isinstance(json_content, str), "JSON content should be a string"
        assert len(json_content) > 0, "JSON content should not be empty"

    def test_read_json_nonexistent_sink(self):
        """Test read_json returns None for non-existent sink"""
        json_content = logger.read_json(99999)
        assert json_content is None, "JSON content should be None for non-existent sink"

    def test_read_json_text_format(self):
        """Test read_json handles non-JSON text files gracefully"""
        import time

        sink_id = logger.add("test_json.log", format="text", async_write=False)
        logger.info("This is plain text, not JSON")
        time.sleep(0.1)  # Give async write time to complete

        # Should still return content even if not valid JSON
        content = logger.read_json(sink_id)
        assert content is not None, "Should return content even for non-JSON files"
        assert isinstance(content, str), "Content should be a string"
        assert len(content) > 0, "Content should not be empty"
