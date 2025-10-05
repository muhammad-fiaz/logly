"""Tests for auto-sink levels feature.

This test suite validates the automatic sink creation and management
for different log levels using the auto_sink_levels configuration.
"""

import pytest

from logly import logger


class TestAutoSinkLevels:
    """Test automatic sink creation for different log levels."""

    def setup_method(self):
        """Reset logger before each test."""
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.complete()

    def test_basic_auto_sink_levels_string_paths(self, tmp_path):
        """Test basic auto-sink with simple string paths."""
        debug_log = tmp_path / "debug.log"
        info_log = tmp_path / "info.log"
        error_log = tmp_path / "error.log"

        logger.configure(
            level="DEBUG",
            auto_sink=False,  # Disable console for file testing
            auto_sink_levels={
                "DEBUG": str(debug_log),
                "INFO": str(info_log),
                "ERROR": str(error_log),
            },
        )

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.complete()

        # Check DEBUG log (should have all levels)
        debug_content = debug_log.read_text()
        assert "[DEBUG] Debug message" in debug_content
        assert "[INFO] Info message" in debug_content
        assert "[WARN] Warning message" in debug_content
        assert "[ERROR] Error message" in debug_content

        # Check INFO log (should have INFO and above)
        info_content = info_log.read_text()
        assert "[DEBUG] Debug message" not in info_content
        assert "[INFO] Info message" in info_content
        assert "[WARN] Warning message" in info_content
        assert "[ERROR] Error message" in info_content

        # Check ERROR log (should have ERROR and above)
        error_content = error_log.read_text()
        assert "[DEBUG] Debug message" not in error_content
        assert "[INFO] Info message" not in error_content
        assert "[WARN] Warning message" not in error_content
        assert "[ERROR] Error message" in error_content

    def test_auto_sink_levels_with_dict_config(self, tmp_path):
        """Test auto-sink with advanced dictionary configuration."""
        debug_log = tmp_path / "debug_rotating.log"
        warning_log = tmp_path / "warnings.log"
        error_log = tmp_path / "errors.json"

        logger.configure(
            level="DEBUG",
            auto_sink=False,
            auto_sink_levels={
                "DEBUG": {
                    "path": str(debug_log),
                    "rotation": "daily",
                    "retention": 7,
                    "date_enabled": True,
                },
                "WARNING": {
                    "path": str(warning_log),
                    "size_limit": "10MB",
                    "retention": 5,
                },
                "ERROR": {
                    "path": str(error_log),
                    "json": True,
                    "async_write": True,
                },
            },
        )

        logger.debug("Debug with rotation")
        logger.warning("Warning with size limit")
        logger.error("Error as JSON")
        logger.complete()

        # Verify files exist (debug log will have date suffix with date_enabled=True)
        debug_files = list(tmp_path.glob("debug_rotating*.log"))
        assert len(debug_files) > 0, "Debug log file should exist with date suffix"
        assert warning_log.exists()
        assert error_log.exists()

        # Verify content
        assert "Debug with rotation" in debug_files[0].read_text()
        assert "Warning with size limit" in warning_log.read_text()

        # JSON output should contain JSON structure
        error_content = error_log.read_text()
        assert '"level"' in error_content or '"message"' in error_content

    def test_auto_sink_levels_with_filters(self, tmp_path):
        """Test auto-sink with module and function filters."""
        info_log = tmp_path / "info_filtered.log"
        error_log = tmp_path / "error_filtered.log"

        logger.configure(
            level="DEBUG",
            auto_sink=False,
            auto_sink_levels={
                "INFO": {
                    "path": str(info_log),
                    "filter_module": "tests.test_auto_sink_levels",
                    "format": "{time} | {level} | {message}",
                },
                "ERROR": {
                    "path": str(error_log),
                    "filter_module": "tests.test_auto_sink_levels",
                },
            },
        )

        logger.info("Info from main")
        logger.error("Error from main")
        logger.complete()

        # Verify filtering worked
        info_content = info_log.read_text()
        error_content = error_log.read_text()

        assert "Info from main" in info_content
        assert "Error from main" in error_content

    def test_auto_sink_all_levels(self, tmp_path):
        """Test auto-sink for all 8 log levels."""
        levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL", "FAIL"]
        log_files = {level: tmp_path / f"{level.lower()}.log" for level in levels}

        logger.configure(
            level="TRACE",
            auto_sink=False,
            auto_sink_levels={level: str(log_files[level]) for level in levels},
        )

        logger.trace("Trace message")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.success("Success message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        logger.fail("Fail message")
        logger.complete()

        # Verify all files exist
        for level, log_file in log_files.items():
            assert log_file.exists(), f"{level} log file should exist"
            content = log_file.read_text()
            assert len(content) > 0, f"{level} log file should not be empty"

    def test_disable_auto_sink_levels(self, tmp_path):
        """Test that auto_sink_levels=None disables automatic sink creation."""
        logger.configure(level="INFO", auto_sink=False, auto_sink_levels=None)

        # Should not create any sinks
        sinks = logger.list_sinks()
        assert len(sinks) == 0, "No sinks should be created when auto_sink_levels=None"

    def test_auto_sink_levels_with_console(self, tmp_path):
        """Test auto-sink levels combined with console output."""
        info_log = tmp_path / "info.log"
        error_log = tmp_path / "error.log"

        logger.configure(
            level="INFO",
            auto_sink=True,  # Enable console
            auto_sink_levels={
                "INFO": str(info_log),
                "ERROR": str(error_log),
            },
        )

        logger.info("Info message")
        logger.error("Error message")
        logger.complete()

        # Should have console sink + 2 file sinks = 3 total
        # (Checking after logging but before complete)

        # Verify file sinks created
        assert info_log.exists()
        assert error_log.exists()
        assert "Info message" in info_log.read_text()
        assert "Error message" in error_log.read_text()

    def test_auto_sink_levels_precedence(self, tmp_path):
        """Test that manually added sinks coexist with auto-sinks."""
        auto_log = tmp_path / "auto.log"
        manual_log = tmp_path / "manual.log"

        logger.configure(
            level="INFO",
            auto_sink=False,
            auto_sink_levels={
                "INFO": str(auto_log),
            },
        )

        # Add manual sink
        logger.add(str(manual_log), filter_min_level="ERROR")

        logger.info("Info message")
        logger.error("Error message")
        logger.complete()

        # Auto-sink should have both messages
        auto_content = auto_log.read_text()
        assert "Info message" in auto_content
        assert "Error message" in auto_content

        # Manual sink should only have ERROR
        manual_content = manual_log.read_text()
        assert "Info message" not in manual_content
        assert "Error message" in manual_content

    def test_auto_sink_levels_empty_dict(self, tmp_path):
        """Test that empty auto_sink_levels dict creates no sinks."""
        logger.configure(level="INFO", auto_sink=False, auto_sink_levels={})

        sinks = logger.list_sinks()
        assert len(sinks) == 0, "No sinks should be created with empty auto_sink_levels"

    def test_auto_sink_levels_invalid_level(self, tmp_path):
        """Test error handling for invalid log level in auto_sink_levels."""
        invalid_log = tmp_path / "invalid.log"

        with pytest.raises((ValueError, KeyError)):
            logger.configure(
                level="INFO",
                auto_sink=False,
                auto_sink_levels={
                    "INVALID_LEVEL": str(invalid_log),
                },
            )


class TestAutoSinkLevelsEdgeCases:
    """Test edge cases and error conditions for auto-sink levels."""

    def setup_method(self):
        """Reset logger before each test."""
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.complete()

    def test_auto_sink_levels_with_retention(self, tmp_path):
        """Test that retention settings work with auto-sinks."""
        log_file = tmp_path / "retention.log"

        logger.configure(
            level="INFO",
            auto_sink=False,
            auto_sink_levels={
                "INFO": {
                    "path": str(log_file),
                    "rotation": "daily",
                    "retention": 3,
                }
            },
        )

        logger.info("Test message")
        logger.complete()

        assert log_file.exists()
        assert "Test message" in log_file.read_text()

    def test_auto_sink_levels_reconfigure(self, tmp_path):
        """Test reconfiguring auto-sink levels."""
        log1 = tmp_path / "log1.log"
        log2 = tmp_path / "log2.log"

        # First configuration
        logger.configure(level="INFO", auto_sink=False, auto_sink_levels={"INFO": str(log1)})
        logger.info("Message 1")

        # Reconfigure with different auto-sinks
        logger.configure(level="INFO", auto_sink=False, auto_sink_levels={"INFO": str(log2)})
        logger.info("Message 2")
        logger.complete()

        # Both logs should exist
        assert log1.exists()
        assert log2.exists()

    def test_auto_sink_levels_with_custom_format(self, tmp_path):
        """Test custom format strings with auto-sinks."""
        log_file = tmp_path / "custom_format.log"

        logger.configure(
            level="INFO",
            auto_sink=False,
            auto_sink_levels={
                "INFO": {
                    "path": str(log_file),
                    "format": "{level} - {message} - {module}",
                }
            },
        )

        logger.info("Custom format test")
        logger.complete()

        content = log_file.read_text()
        assert "INFO - Custom format test" in content
        assert "__main__" in content or "test_auto_sink_levels" in content
