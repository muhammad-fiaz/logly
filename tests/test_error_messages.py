"""
Test error handling and error messages.

This module tests that error messages include the GitHub issue tracker link
and that validation works correctly for all parameters.
"""

import pytest

from logly import PyLogger


class TestErrorMessages:
    """Test error message formatting and GitHub issue tracker links."""

    def setup_method(self):
        """Reset logger before each test."""
        self.logger = PyLogger(auto_update_check=False)
        self.logger.configure(level="INFO", console=False)

    def test_invalid_level_error_message(self):
        """Test that invalid level includes GitHub issue tracker link."""
        with pytest.raises(ValueError) as exc_info:
            self.logger.configure(level="INVALID_LEVEL")

        error_msg = str(exc_info.value)
        assert "Invalid log level: 'INVALID_LEVEL'" in error_msg
        assert "https://github.com/muhammad-fiaz/logly" in error_msg
        assert (
            "Valid levels are: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL" in error_msg
        )

    def test_invalid_rotation_error_message(self):
        """Test that invalid rotation includes GitHub issue tracker link."""
        with pytest.raises(ValueError) as exc_info:
            self.logger.add("test.log", rotation="invalid_rotation")

        error_msg = str(exc_info.value)
        assert "Invalid rotation policy" in error_msg
        assert "https://github.com/muhammad-fiaz/logly" in error_msg

    def test_invalid_size_limit_error_message(self):
        """Test that invalid size limit includes GitHub issue tracker link."""
        with pytest.raises(ValueError) as exc_info:
            self.logger.add("test.log", size_limit="invalid_size")

        error_msg = str(exc_info.value)
        assert "Invalid size limit" in error_msg
        assert "https://github.com/muhammad-fiaz/logly" in error_msg
        # Updated to match new error message format
        assert "Supported formats:" in error_msg or "Expected format:" in error_msg

    def test_valid_levels_accepted(self):
        """Test that all valid log levels are accepted."""
        valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            # Should not raise any error
            self.logger.configure(level=level, console=False)

    def test_valid_rotations_accepted(self):
        """Test that all valid rotation policies are accepted."""
        import os
        import tempfile

        valid_rotations = ["daily", "hourly", "minutely"]
        for rotation in valid_rotations:
            with tempfile.TemporaryDirectory() as tmpdir:
                log_file = os.path.join(tmpdir, f"test_{rotation}.log")
                # Should not raise any error
                handler_id = self.logger.add(log_file, rotation=rotation, async_write=False)
                self.logger.remove(handler_id)

    def test_valid_size_limits_accepted(self):
        """Test that all valid size limit formats are accepted."""
        import os
        import tempfile

        valid_sizes = ["500B", "1KB", "5KB", "10MB", "1GB"]
        for size in valid_sizes:
            with tempfile.TemporaryDirectory() as tmpdir:
                log_file = os.path.join(tmpdir, "test_size.log")
                # Should not raise any error
                handler_id = self.logger.add(log_file, size_limit=size, async_write=False)
                self.logger.remove(handler_id)

    def test_case_insensitive_levels(self):
        """Test that log levels are case-insensitive."""
        # Should accept lowercase, uppercase, and mixed case
        for level in ["info", "INFO", "Info"]:
            self.logger.configure(level=level, console=False)

    def test_case_insensitive_rotations(self):
        """Test that rotation policies are case-insensitive."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            for rotation in ["daily", "DAILY", "Daily"]:
                log_file = os.path.join(tmpdir, f"test_{rotation}.log")
                handler_id = self.logger.add(log_file, rotation=rotation, async_write=False)
                self.logger.remove(handler_id)

    def test_size_limit_with_spaces(self):
        """Test that size limits with spaces are handled correctly."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test_size.log")
            # Should handle spaces around size value
            handler_id = self.logger.add(log_file, size_limit=" 10MB ", async_write=False)
            self.logger.remove(handler_id)
