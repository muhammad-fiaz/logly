"""
Tests for the logly.compat module.

This module tests the compatibility layer with Python's standard logging module.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import logly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logly.compat import (
    getLogger, basicConfig, config, FileHandler, StreamHandler, Formatter,
    Logger, LoglyHandler, LoglyFormatter, LoglyFilter,
    DEBUG, INFO, WARNING, ERROR, CRITICAL
)


class TestCompat(unittest.TestCase):
    """Test the compatibility layer with Python's standard logging module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = os.path.join(self.temp_dir.name, "test.log")

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        self.temp_dir.cleanup()

    def test_basic_config(self):
        """Test basic configuration with basicConfig."""
        # Configure logging
        basicConfig(
            level=INFO,
            filename=self.log_file,
            format="%(levelname)s: %(message)s"
        )

        # Get a logger
        logger = getLogger("test_basic_config")

        # Log some messages
        logger.debug("Debug message")  # Should not appear
        logger.info("Info message")    # Should appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear
        logger.critical("Critical message")  # Should appear

        # Check that the log file exists and contains the expected messages
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertNotIn("DEBUG: Debug message", content)
            self.assertIn("INFO: Info message", content)
            self.assertIn("WARNING: Warning message", content)
            self.assertIn("ERROR: Error message", content)
            self.assertIn("CRITICAL: Critical message", content)

    def test_dict_config(self):
        """Test configuration with dictConfig."""
        # Configure logging
        config.dictConfig({
            'version': 1,
            'formatters': {
                'standard': {
                    'format': '%(levelname)s: %(message)s'
                },
            },
            'handlers': {
                'file': {
                    'class': 'logly.compat.FileHandler',
                    'level': 'DEBUG',
                    'formatter': 'standard',
                    'filename': self.log_file,
                    'mode': 'a',
                }
            },
            'loggers': {
                'test_dict_config': {
                    'handlers': ['file'],
                    'level': 'DEBUG',
                    'propagate': False
                },
            }
        })

        # Get a logger
        logger = getLogger("test_dict_config")

        # Log some messages
        logger.debug("Debug message")  # Should appear
        logger.info("Info message")    # Should appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear
        logger.critical("Critical message")  # Should appear

        # Check that the log file exists and contains the expected messages
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("DEBUG: Debug message", content)
            self.assertIn("INFO: Info message", content)
            self.assertIn("WARNING: Warning message", content)
            self.assertIn("ERROR: Error message", content)
            self.assertIn("CRITICAL: Critical message", content)

    def test_handlers(self):
        """Test configuration with handlers."""
        # Create a logger
        logger = getLogger("test_handlers")
        logger.setLevel(DEBUG)

        # Create a handler
        handler = FileHandler(self.log_file)
        handler.setLevel(DEBUG)

        # Create a formatter
        formatter = Formatter("%(levelname)s: %(message)s")

        # Add formatter to handler
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Log some messages
        logger.debug("Debug message")  # Should appear
        logger.info("Info message")    # Should appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear
        logger.critical("Critical message")  # Should appear

        # Check that the log file exists and contains the expected messages
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("DEBUG: Debug message", content)
            self.assertIn("INFO: Info message", content)
            self.assertIn("WARNING: Warning message", content)
            self.assertIn("ERROR: Error message", content)
            self.assertIn("CRITICAL: Critical message", content)

    def test_filter(self):
        """Test filters."""
        # Create a logger
        logger = getLogger("test_filter")
        logger.setLevel(DEBUG)

        # Create a handler
        handler = FileHandler(self.log_file)
        handler.setLevel(DEBUG)

        # Create a formatter
        formatter = Formatter("%(levelname)s: %(message)s")

        # Add formatter to handler
        handler.setFormatter(formatter)

        # Create a filter that only allows messages from loggers with names starting with "test_"
        filter = LoglyFilter("test_")
        handler.addFilter(filter)

        # Add handler to logger
        logger.addHandler(handler)

        # Log some messages
        logger.debug("Debug message")  # Should appear
        logger.info("Info message")    # Should appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear
        logger.critical("Critical message")  # Should appear

        # Check that the log file exists and contains the expected messages
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("DEBUG: Debug message", content)
            self.assertIn("INFO: Info message", content)
            self.assertIn("WARNING: Warning message", content)
            self.assertIn("ERROR: Error message", content)
            self.assertIn("CRITICAL: Critical message", content)

        # Create another logger with a name that doesn't start with "test_"
        other_logger = getLogger("other")
        other_logger.setLevel(DEBUG)
        other_logger.addHandler(handler)

        # Log some messages
        other_logger.debug("Other debug message")  # Should not appear
        other_logger.info("Other info message")    # Should not appear
        other_logger.warning("Other warning message")  # Should not appear
        other_logger.error("Other error message")  # Should not appear
        other_logger.critical("Other critical message")  # Should not appear

        # Check that the log file doesn't contain the messages from the other logger
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertNotIn("DEBUG: Other debug message", content)
            self.assertNotIn("INFO: Other info message", content)
            self.assertNotIn("WARNING: Other warning message", content)
            self.assertNotIn("ERROR: Other error message", content)
            self.assertNotIn("CRITICAL: Other critical message", content)

    def test_propagate(self):
        """Test logger propagation."""
        # Configure logging
        config.dictConfig({
            'version': 1,
            'formatters': {
                'standard': {
                    'format': '%(levelname)s: %(message)s'
                },
            },
            'handlers': {
                'file': {
                    'class': 'logly.compat.FileHandler',
                    'level': 'DEBUG',
                    'formatter': 'standard',
                    'filename': self.log_file,
                    'mode': 'a',
                }
            },
            'loggers': {
                'parent': {
                    'handlers': ['file'],
                    'level': 'DEBUG',
                    'propagate': False
                },
                'parent.child': {
                    'level': 'DEBUG',
                    'propagate': True
                },
            }
        })

        # Get loggers
        parent_logger = getLogger("parent")
        child_logger = getLogger("parent.child")

        # Log some messages
        parent_logger.debug("Parent debug message")  # Should appear
        child_logger.debug("Child debug message")    # Should appear (propagated to parent)

        # Check that the log file exists and contains the expected messages
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("DEBUG: Parent debug message", content)
            self.assertIn("DEBUG: Child debug message", content)

    def test_formatter(self):
        """Test formatters."""
        # Create a logger
        logger = getLogger("test_formatter")
        logger.setLevel(DEBUG)

        # Create a handler
        handler = FileHandler(self.log_file)
        handler.setLevel(DEBUG)

        # Create a formatter with a custom format
        formatter = Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        # Add formatter to handler
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Log a message
        logger.info("Info message")

        # Check that the log file exists and contains the expected message
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            # The message should include the timestamp, level, logger name, and message
            self.assertRegex(content, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \[INFO\] test_formatter: Info message")

    def test_exception(self):
        """Test logging exceptions."""
        # Configure logging
        basicConfig(
            level=INFO,
            filename=self.log_file,
            format="%(levelname)s: %(message)s"
        )

        # Get a logger
        logger = getLogger("test_exception")

        # Log an exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")

        # Check that the log file exists and contains the expected message
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("ERROR: Exception occurred", content)
            # The traceback should be included, but we can't easily check for it
            # since it will vary depending on the line numbers


if __name__ == "__main__":
    unittest.main()