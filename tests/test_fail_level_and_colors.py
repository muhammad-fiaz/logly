"""
Comprehensive tests for FAIL level and default color mapping.

Tests the new FAIL level functionality and default color mapping
introduced in v0.1.5.
"""

import pytest

from logly import logger


class TestFailLevel:
    """Tests for the FAIL log level."""

    def setup_method(self):
        """Reset logger before each test."""
        logger.remove_all()
        logger.configure(auto_sink=False)

    def teardown_method(self):
        """Clean up after each test."""
        logger.complete()

    def test_fail_method_exists(self):
        """Test that fail() method exists on logger."""
        assert hasattr(logger, "fail")
        assert callable(logger.fail)

    def test_fail_to_file(self, tmp_path):
        """Test fail() writes to file."""
        log_file = tmp_path / "test.log"
        logger.add(str(log_file))

        logger.fail("Test failure")
        logger.complete()

        content = log_file.read_text()
        assert "[FAIL]" in content
        assert "Test failure" in content

    def test_fail_with_context(self, tmp_path):
        """Test fail() with context fields."""
        log_file = tmp_path / "test.log"
        logger.add(str(log_file))

        logger.fail("Auth failed", user="alice", attempts=3)
        logger.complete()

        content = log_file.read_text()
        assert "[FAIL]" in content
        assert "Auth failed" in content
        assert "user=alice" in content
        assert "attempts=3" in content

    def test_fail_with_bound_context(self, tmp_path):
        """Test fail() with bound context."""
        log_file = tmp_path / "test.log"
        logger.add(str(log_file))

        bound_logger = logger.bind(session_id="sess_123")
        bound_logger.fail("Operation timeout", operation="database_query")
        logger.complete()

        content = log_file.read_text()
        assert "[FAIL]" in content
        assert "session_id=sess_123" in content
        assert "operation=database_query" in content

    def test_fail_multiple_calls(self, tmp_path):
        """Test multiple fail() calls."""
        log_file = tmp_path / "test.log"
        logger.add(str(log_file))

        logger.fail("Failure 1", code=1001)
        logger.fail("Failure 2", code=1002)
        logger.fail("Failure 3", code=1003)
        logger.complete()

        content = log_file.read_text()
        assert content.count("[FAIL]") == 3
        assert "code=1001" in content
        assert "code=1002" in content
        assert "code=1003" in content


class TestFailLevelSemantics:
    """Tests for FAIL vs ERROR semantic differences."""

    def setup_method(self):
        """Reset logger before each test."""
        logger.remove_all()
        logger.configure(auto_sink=False)

    def teardown_method(self):
        """Clean up after each test."""
        logger.complete()

    def test_fail_vs_error_display(self, tmp_path):
        """Test that FAIL and ERROR display differently."""
        log_file = tmp_path / "test.log"
        logger.add(str(log_file))

        logger.fail("Expected failure")
        logger.error("Unexpected error")
        logger.complete()

        content = log_file.read_text()
        assert "[FAIL]" in content
        assert "[ERROR]" in content
        assert "Expected failure" in content
        assert "Unexpected error" in content

    def test_fail_use_cases(self, tmp_path):
        """Test typical FAIL level use cases."""
        log_file = tmp_path / "test.log"
        logger.add(str(log_file))

        # Authentication failure
        logger.fail("Login failed", user="alice", reason="invalid_password")

        # Payment failure
        logger.fail("Payment declined", transaction_id="txn_123", reason="insufficient_funds")

        # Validation failure
        logger.fail("Validation failed", field="email", rule="email_format")

        # Authorization failure
        logger.fail("Access denied", endpoint="/api/admin", status=403)

        logger.complete()

        content = log_file.read_text()
        assert content.count("[FAIL]") == 4
        assert "Login failed" in content
        assert "Payment declined" in content
        assert "Validation failed" in content
        assert "Access denied" in content


class TestDefaultColorMapping:
    """Tests for default color mapping."""

    def setup_method(self):
        """Reset logger before each test."""
        logger.remove_all()
        logger.configure(auto_sink=False)

    def teardown_method(self):
        """Clean up after each test."""
        logger.complete()

    def test_all_levels_work(self, tmp_path):
        """Test that all 8 levels work correctly."""
        log_file = tmp_path / "test.log"
        logger.configure(color=True)
        logger.add(str(log_file))

        logger.trace("Trace")
        logger.debug("Debug")
        logger.info("Info")
        logger.success("Success")
        logger.warning("Warning")
        logger.error("Error")
        logger.critical("Critical")
        logger.fail("Fail")

        logger.complete()

        content = log_file.read_text()

        # All levels should appear
        assert "[TRACE]" in content
        assert "[DEBUG]" in content
        assert "[INFO]" in content
        # SUCCESS maps to INFO level internally
        assert content.count("[INFO]") >= 2  # Both info() and success()
        assert "[WARN]" in content
        assert "[ERROR]" in content
        assert "[CRITICAL]" in content
        assert "[FAIL]" in content


class TestColorConfiguration:
    """Tests for color configuration options."""

    def setup_method(self):
        """Reset logger before each test."""
        logger.remove_all()
        logger.configure(auto_sink=False)

    def teardown_method(self):
        """Clean up after each test."""
        logger.complete()

    def test_configure_with_color_names(self, tmp_path):
        """Test configuring colors with color names."""
        log_file = tmp_path / "test.log"
        logger.configure(
            color=True,
            level_colors={
                "TRACE": "CYAN",
                "DEBUG": "BLUE",
                "INFO": "WHITE",
                "SUCCESS": "GREEN",
                "WARNING": "YELLOW",
                "ERROR": "RED",
                "CRITICAL": "BRIGHT_RED",
                "FAIL": "MAGENTA",
            },
        )
        logger.add(str(log_file))

        logger.trace("Trace")
        logger.fail("Fail")
        logger.complete()

        content = log_file.read_text()
        assert "[TRACE]" in content
        assert "[FAIL]" in content

    def test_configure_with_ansi_codes(self, tmp_path):
        """Test configuring colors with ANSI codes."""
        log_file = tmp_path / "test.log"
        logger.configure(
            color=True,
            level_colors={
                "INFO": "37",  # White
                "FAIL": "35",  # Magenta
            },
        )
        logger.add(str(log_file))

        logger.info("Info")
        logger.fail("Fail")
        logger.complete()

        content = log_file.read_text()
        assert "[INFO]" in content
        assert "[FAIL]" in content


class TestBackwardCompatibility:
    """Tests to ensure no breaking changes."""

    def setup_method(self):
        """Reset logger before each test."""
        logger.remove_all()
        logger.configure(auto_sink=False)

    def teardown_method(self):
        """Clean up after each test."""
        logger.complete()

    def test_existing_levels_still_work(self, tmp_path):
        """Test that all existing levels still work."""
        log_file = tmp_path / "test.log"
        logger.add(str(log_file))

        logger.trace("Trace")
        logger.debug("Debug")
        logger.info("Info")
        logger.success("Success")
        logger.warning("Warning")
        logger.error("Error")
        logger.critical("Critical")
        logger.complete()

        content = log_file.read_text()
        assert "[TRACE]" in content
        assert "[DEBUG]" in content
        assert "[INFO]" in content
        assert "[WARN]" in content
        assert "[ERROR]" in content
        assert "[CRITICAL]" in content

    def test_custom_colors_still_work(self, tmp_path):
        """Test that custom color configuration still works."""
        log_file = tmp_path / "test.log"
        logger.configure(color=True, level_colors={"INFO": "BRIGHT_CYAN", "ERROR": "BRIGHT_RED"})
        logger.add(str(log_file))

        logger.info("Info")
        logger.error("Error")
        logger.complete()

        content = log_file.read_text()
        assert "[INFO]" in content
        assert "[ERROR]" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
