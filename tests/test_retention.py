"""
Tests for file retention with size_limit.
Fixes: https://github.com/muhammad-fiaz/logly/issues/77
"""

import time

from logly import PyLogger


class TestRetentionFunctionality:
    """Test cases for log file retention behavior."""

    def test_retention_with_size_limit(self, tmp_path):
        """Test that retention limits the number of files correctly."""
        log_file = tmp_path / "retention_test.log"

        # Create logger with 1-byte size limit and retention of 3
        logger = PyLogger()
        logger.add(str(log_file), size_limit="1B", retention=3)

        # Write many messages to trigger rotations
        for i in range(20):
            logger.info(f"Message {i}")
            time.sleep(0.01)  # Small delay for file system

        # Wait for file operations to complete
        time.sleep(0.2)

        # Count log files
        log_files = list(tmp_path.glob("retention_test*.log"))

        # Should have at most 3 files (retention limit)
        # Fixes: https://github.com/muhammad-fiaz/logly/issues/77
        assert len(log_files) <= 3, (
            f"Expected at most 3 log files with retention=3, "
            f"found {len(log_files)}: {[f.name for f in log_files]}"
        )

    def test_retention_extreme_case(self, tmp_path):
        """Test retention with 1-byte files and retention=3."""
        log_file = tmp_path / "extreme.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="1B", retention=3)

        # Write multiple single-character messages
        for i in range(10):
            logger.info(str(i))
            time.sleep(0.01)

        time.sleep(0.2)

        # Count files
        log_files = list(tmp_path.glob("extreme*.log"))

        # Should strictly honor retention=3
        assert len(log_files) <= 3, (
            f"Extreme case: Expected at most 3 files, found {len(log_files)}"
        )

    def test_retention_with_rotation(self, tmp_path):
        """Test retention works with time-based rotation."""
        log_file = tmp_path / "rotated.log"

        logger = PyLogger()
        logger.add(str(log_file), rotation="100 KB", retention=5)

        # Write some logs
        for i in range(10):
            logger.info(f"Rotated message {i}")

        time.sleep(0.1)

        # At least one file should exist
        log_files = list(tmp_path.glob("rotated*.log"))
        assert len(log_files) >= 1, "Should have created at least one log file"

        # Should not exceed retention limit
        assert len(log_files) <= 5, (
            f"With retention=5, should not exceed 5 files, found {len(log_files)}"
        )

    def test_no_retention_keeps_files(self, tmp_path):
        """Test that without retention, multiple files can exist."""
        log_file = tmp_path / "no_retention.log"

        logger = PyLogger()
        logger.add(
            str(log_file),
            size_limit="100B",  # Larger size to be more realistic
            # No retention parameter
        )

        # Write enough data to potentially trigger rotation
        for i in range(50):
            logger.info(f"Message number {i} with some content")
            time.sleep(0.01)

        time.sleep(0.2)

        # Should have at least one file
        log_files = list(tmp_path.glob("no_retention*.log"))
        assert len(log_files) >= 1, (
            f"Should have created at least one log file, found {len(log_files)}"
        )

    def test_retention_with_existing_files(self, tmp_path):
        """Test that retention works with pre-existing files."""
        log_file = tmp_path / "existing_test.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="50B", retention=3)

        # Write logs
        for i in range(10):
            logger.info(f"Log entry {i}")
            time.sleep(0.02)

        time.sleep(0.3)

        # Count all files matching the pattern
        all_files = list(tmp_path.glob("existing_test*.log"))

        # Should respect retention limit
        assert len(all_files) <= 3, (
            f"Retention=3 should limit total files to 3, found {len(all_files)}"
        )

    def test_retention_with_multiple_loggers(self, tmp_path):
        """Test that multiple loggers respect their own retention limits."""
        log_file_a = tmp_path / "logger_a.log"
        log_file_b = tmp_path / "logger_b.log"

        logger_a = PyLogger()
        logger_a.add(str(log_file_a), size_limit="1B", retention=2)

        logger_b = PyLogger()
        logger_b.add(str(log_file_b), size_limit="1B", retention=4)

        # Write to both loggers
        for i in range(10):
            logger_a.info(str(i))
            logger_b.info(str(i))
            time.sleep(0.01)

        time.sleep(0.2)

        # Check retention for logger A
        files_a = list(tmp_path.glob("logger_a*.log"))
        assert len(files_a) <= 2, f"Logger A: Expected ≤2 files, found {len(files_a)}"

        # Check retention for logger B
        files_b = list(tmp_path.glob("logger_b*.log"))
        assert len(files_b) <= 4, f"Logger B: Expected ≤4 files, found {len(files_b)}"

    def test_retention_basic_behavior(self, tmp_path):
        """Test basic retention behavior."""
        log_file = tmp_path / "basic_retention.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="50B", retention=3)

        # Write multiple logs
        for i in range(15):
            logger.info(f"Log entry number {i}")
            time.sleep(0.02)

        time.sleep(0.3)
        logger.complete()

        # Get remaining files
        log_files = list(tmp_path.glob("basic_retention*.log"))

        # Should have at most 3 files
        assert len(log_files) <= 3, (
            f"Expected at most 3 files with retention=3, found {len(log_files)}"
        )

        # Verify we have some log content
        total_content = 0
        for log_path in log_files:
            total_content += len(log_path.read_text())

        assert total_content > 0, "Log files should have content"
