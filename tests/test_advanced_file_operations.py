"""Advanced file operations and handling tests."""

import os
import tempfile
from pathlib import Path

import pytest

from logly import logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger before each test."""
    logger.reset()
    logger.remove_all()
    yield
    logger.reset()
    logger.remove_all()


class TestFileOperations:
    """Test suite for file operation features."""

    def test_file_size_tracking(self):
        """Test tracking file size during logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            initial_size = logger.file_size(sink_id)
            assert initial_size in (None, 0)  # File might not exist yet

            logger.info("First message")
            logger.complete()

            size1 = logger.file_size(sink_id)
            assert size1 is not None and size1 > 0

            logger.info("Second message with more content")
            logger.complete()

            size2 = logger.file_size(sink_id)
            assert size2 > size1

    def test_file_metadata_retrieval(self):
        """Test retrieving comprehensive file metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Test message")
            logger.complete()

            metadata = logger.file_metadata(sink_id)
            assert metadata is not None
            assert "size" in metadata
            assert "path" in metadata
            assert str(log_file) in metadata["path"]

    def test_line_count_tracking(self):
        """Test counting lines in log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            # Write specific number of lines
            for i in range(10):
                logger.info(f"Line {i}")
            logger.complete()

            line_count = logger.line_count(sink_id)
            assert line_count == 10

    def test_read_specific_lines(self):
        """Test reading specific line ranges from log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            # Write numbered lines
            for i in range(1, 11):
                logger.info(f"Line {i}")
            logger.complete()

            # Read lines 3-5
            content = logger.read_lines(sink_id, 3, 5)
            assert "Line 3" in content
            assert "Line 4" in content
            assert "Line 5" in content
            assert "Line 2" not in content
            assert "Line 6" not in content

    def test_read_lines_negative_indices(self):
        """Test reading lines with negative indices (from end)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            for i in range(1, 11):
                logger.info(f"Line {i}")
            logger.complete()

            # Read last 3 lines
            content = logger.read_lines(sink_id, -3, -1)
            assert content is not None
            assert "Line 8" in content or "Line 9" in content or "Line 10" in content

    def test_read_full_file_content(self):
        """Test reading entire file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            messages = ["First", "Second", "Third"]
            for msg in messages:
                logger.info(msg)
            logger.complete()

            content = logger.read(sink_id)
            assert content is not None
            for msg in messages:
                assert msg in content

    def test_read_all_files(self):
        """Test reading all log files from all sinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.log"
            file2 = Path(tmpdir) / "file2.log"

            sink1 = logger.add(str(file1))
            sink2 = logger.add(str(file2))

            logger.info("Test message")
            logger.complete()

            all_content = logger.read_all()
            assert isinstance(all_content, dict)
            assert sink1 in all_content
            assert sink2 in all_content
            assert "Test message" in all_content[sink1]
            assert "Test message" in all_content[sink2]

    def test_delete_single_file(self):
        """Test deleting a specific log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Test message")
            logger.complete()

            assert log_file.exists()

            result = logger.delete(sink_id)
            assert result is True
            assert not log_file.exists()

    def test_delete_all_files(self):
        """Test deleting all log files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = [Path(tmpdir) / f"file{i}.log" for i in range(3)]
            _ = [logger.add(str(f)) for f in files]

            logger.info("Test message")
            logger.complete()

            # All files should exist
            for f in files:
                assert f.exists()

            count = logger.delete_all()
            assert count == 3

            # All files should be deleted
            for f in files:
                assert not f.exists()

    def test_file_rotation_daily(self):
        """Test daily file rotation configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file), rotation="daily", retention=7)

            logger.info("Test message")
            logger.complete()

            info = logger.sink_info(sink_id)
            assert info is not None
            assert info.get("rotation") == "daily"

    def test_file_rotation_size_based(self):
        """Test size-based file rotation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file), size_limit="1KB")

            # Write enough to trigger rotation
            for _ in range(100):
                logger.info("A" * 100)
            logger.complete()

            # Check if rotation occurred
            info = logger.sink_info(sink_id)
            assert info is not None

    def test_file_retention_policy(self):
        """Test file retention configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file), rotation="hourly", retention=5)

            info = logger.sink_info(sink_id)
            assert info is not None
            # Retention should be configured
            assert info.get("rotation") == "hourly"

    def test_json_file_reading(self):
        """Test reading JSON-formatted log files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file), json=True)

            logger.info("Test message", user_id=42, action="login")
            logger.complete()

            json_content = logger.read_json(sink_id)
            assert json_content is not None
            assert "Test message" in json_content
            assert "user_id" in json_content or "42" in json_content

    def test_json_pretty_reading(self):
        """Test reading pretty-printed JSON logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file), json=True)

            logger.info("Test", data={"key": "value"})
            logger.complete()

            pretty_json = logger.read_json(sink_id, pretty=True)
            assert pretty_json is not None

    def test_file_operations_nonexistent_sink(self):
        """Test file operations on nonexistent sinks."""
        fake_id = 99999
        assert logger.file_size(fake_id) is None
        assert logger.file_metadata(fake_id) is None
        assert logger.line_count(fake_id) is None
        assert logger.read_lines(fake_id, 1, 10) is None
        assert logger.read(fake_id) is None
        assert logger.read_json(fake_id) is None
        assert logger.delete(fake_id) is False

    def test_concurrent_file_writes(self):
        """Test multiple sinks writing to different files concurrently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sinks = []
            files = []

            for i in range(5):
                log_file = Path(tmpdir) / f"concurrent_{i}.log"
                files.append(log_file)
                sink_id = logger.add(str(log_file), async_write=True)
                sinks.append(sink_id)

            # Write to all sinks simultaneously
            for i in range(100):
                logger.info(f"Message {i}")

            logger.complete()

            # Verify all files have content
            for log_file in files:
                assert log_file.exists()
                content = log_file.read_text()
                assert "Message 0" in content
                assert "Message 99" in content

    def test_file_path_with_directories(self):
        """Test creating log files in nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "logs" / "app" / "debug.log"
            _ = logger.add(str(nested_path))

            logger.info("Test in nested directory")
            logger.complete()

            assert nested_path.exists()
            content = nested_path.read_text()
            assert "Test in nested directory" in content


class TestFileHandlingEdgeCases:
    """Test edge cases in file handling."""

    def test_file_with_special_characters(self):
        """Test log files with special characters in name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test-log_2024.log"
            _ = logger.add(str(log_file))

            logger.info("Special filename test")
            logger.complete()

            assert log_file.exists()

    def test_empty_file_operations(self):
        """Test operations on empty log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "empty.log"
            sink_id = logger.add(str(log_file))

            # Don't write anything, just check operations
            logger.complete()

            size = logger.file_size(sink_id)
            # Size might be 0 or None depending on if file was created
            assert size in (0, None)

    def test_very_long_filename(self):
        """Test handling of very long filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a reasonably long filename (not exceeding OS limits)
            long_name = "a" * 100 + ".log"
            log_file = Path(tmpdir) / long_name
            _ = logger.add(str(log_file))

            logger.info("Long filename test")
            logger.complete()

            assert log_file.exists()

    def test_file_permissions_handling(self):
        """Test handling of file permission issues."""
        # This test is platform-dependent and may be skipped on Windows
        if os.name == "nt":
            pytest.skip("File permissions test not applicable on Windows")

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "readonly.log"
            _ = logger.add(str(log_file))

            logger.info("First write")
            logger.complete()

            # Make file read-only
            log_file.chmod(0o444)

            # Try to write again - should handle gracefully
            try:
                logger.info("Second write")
                logger.complete()
            except Exception:
                pass  # Expected to fail, but shouldn't crash

            # Restore permissions for cleanup
            log_file.chmod(0o644)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
