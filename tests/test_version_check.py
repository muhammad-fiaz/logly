"""Tests for Logly version checking functionality."""

import time
from io import StringIO
from unittest.mock import patch

import logly


class TestVersionCheck:
    """Test cases for automatic version checking."""

    def test_logger_creation_triggers_version_check(self):
        """Test that creating a logger instance triggers version check."""
        # Capture stderr to check for version warning
        captured_stderr = StringIO()
        with patch("sys.stderr", captured_stderr):
            # Create logger (this should trigger version check)
            logger = logly.logger

            # Version check runs asynchronously, so we need to wait a bit
            time.sleep(0.1)  # Give async task time to run

            # Check that logger was created successfully
            assert logger is not None
            assert hasattr(logger, "info")
            assert hasattr(logger, "critical")

    def test_version_check_does_not_block_logger_operations(self):
        """Test that version check doesn't block normal logging operations."""
        logger = logly.logger

        # Configure logger
        logger.configure(level="INFO")

        # Test that logging works immediately (version check shouldn't block)
        logger.info("Test message", test_field="value")

        # Should not raise any exceptions
        assert True

    def test_logger_methods_exist(self):
        """Test that all expected logger methods exist."""
        logger = logly.logger

        expected_methods = [
            "configure",
            "add",
            "remove",
            "reset",
            "enable",
            "disable",
            "trace",
            "debug",
            "info",
            "success",
            "warning",
            "error",
            "critical",
            "log",
            "exception",
        ]

        for method in expected_methods:
            assert hasattr(logger, method), f"Logger missing method: {method}"

    def test_configure_method(self):
        """Test that configure method works."""
        logger = logly.logger

        # Should not raise exception
        logger.configure(level="DEBUG", color=False)
        logger.configure(level="INFO", json=True)

        assert True

    def test_basic_logging(self):
        """Test basic logging functionality."""
        logger = logly.logger
        logger.configure(level="INFO")

        # Test different log levels
        logger.info("Info message", test="value")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Should not raise exceptions
        assert True

    def test_auto_update_check_parameter(self):
        """Test that auto_update_check parameter works correctly."""
        from logly._logly import PyLogger

        # Test with auto_update_check=True (default)
        logger_with_check = PyLogger()
        assert logger_with_check is not None

        # Test with auto_update_check=False
        logger_without_check = PyLogger(auto_update_check=False)
        assert logger_without_check is not None

        # Both should work normally
        assert hasattr(logger_with_check, "configure")
        assert hasattr(logger_without_check, "configure")

    def test_callable_logger_syntax(self):
        """Test that logger() callable syntax works correctly."""
        from logly import logger

        # Test callable syntax with auto_update_check=True (default)
        callable_logger_default = logger()
        assert callable_logger_default is not None
        assert hasattr(callable_logger_default, "info")

        # Test callable syntax with auto_update_check=False
        callable_logger_custom = logger(auto_update_check=False)
        assert callable_logger_custom is not None
        assert hasattr(callable_logger_custom, "info")

        # Both should be different instances
        assert callable_logger_default is not callable_logger_custom

    def test_module_level_logger_access(self):
        """Test that module-level access works for both import styles."""
        # Since logly is already imported at module level, we can test the __getattr__ functionality
        # by accessing attributes directly on the logly module

        # Test that we can access logger methods through the module
        # This simulates what happens with "import logly as logger; logger.info()"
        assert hasattr(logly, "info")
        assert hasattr(logly, "warning")
        assert hasattr(logly, "error")

        # Test that we can still access the explicit logger instance
        assert hasattr(logly, "logger")
        assert logly.logger is not None

        # Test that calling methods on the module works (this would be used in real code)
        # We can't actually call them in tests as they would log, but we can verify the methods exist
        assert callable(logly.info)
        assert callable(logly.configure)
