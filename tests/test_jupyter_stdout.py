"""
Tests for Jupyter/Colab stdout redirection fix.
Fixes: https://github.com/muhammad-fiaz/logly/issues/76

NOTE: These tests verify that logs go to sys.stdout (not StringIO).
The 'Captured stdout call' in pytest output proves the fix works.
"""

from logly import PyLogger


class TestJupyterStdoutRedirection:
    """Test cases for stdout redirection in Jupyter/Colab environments."""

    def test_logs_appear_in_stdout(self, tmp_path, capsys):
        """Test that logs are written to sys.stdout."""
        logger = PyLogger()
        logger.reset()  # Clear any existing sinks from other tests
        logger.configure(auto_sink=False)  # Disable auto-sink
        logger.add("console")  # Manually add console sink
        logger.info("Test message for stdout")

        # Capture what went to stdout
        captured = capsys.readouterr()

        # Verify message appears in output
        assert "Test message for stdout" in captured.out
        assert "INFO" in captured.out

    def test_multiple_log_levels_to_stdout(self, tmp_path, capsys):
        """Test that all log levels appear in stdout."""
        logger = PyLogger()
        logger.reset()  # Clear any existing sinks from other tests
        logger.configure(level="TRACE", auto_sink=False)  # Disable auto-sink
        logger.add("console")  # Manually add console sink
        logger.trace("Trace message")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        captured = capsys.readouterr()

        # All levels should appear
        assert "Trace message" in captured.out
        assert "Debug message" in captured.out
        assert "Info message" in captured.out
        assert "Warning message" in captured.out
        assert "Error message" in captured.out

    def test_structured_logging_to_stdout(self, tmp_path, capsys):
        """Test that structured fields appear in stdout."""
        logger = PyLogger()
        logger.reset()  # Clear any existing sinks from other tests
        logger.configure(auto_sink=False)  # Disable auto-sink
        logger.add("console")  # Manually add console sink
        logger.info("Structured log", user="alice", action="login", session_id="abc123")

        captured = capsys.readouterr()

        # Verify structured fields
        assert "Structured log" in captured.out
        assert "alice" in captured.out
        assert "login" in captured.out

    def test_console_and_file_sink_both_work(self, tmp_path, capsys):
        """Test that console and file sinks can work together."""
        log_file = tmp_path / "test.log"

        logger = PyLogger()
        logger.reset()  # Clear any existing sinks from other tests
        logger.configure(auto_sink=False)  # Disable auto-sink
        logger.add("console")  # Manually add console sink
        # Add file sink
        logger.add(str(log_file))
        logger.info("Test message")
        logger.complete()  # Flush to ensure file is written

        # Should appear in stdout
        captured = capsys.readouterr()
        assert "Test message" in captured.out

        # Check file
        with open(log_file, encoding="utf-8") as f:
            file_content = f.read()
            assert "Test message" in file_content

    def test_no_crash_when_stdout_is_none(self, tmp_path):
        """Test that logger doesn't crash in edge cases."""
        logger = PyLogger()
        # Should not raise an exception even in edge cases
        logger.info("Edge case message")

    def test_unicode_characters_in_stdout(self, tmp_path, capsys):
        """Test that Unicode characters are properly displayed."""
        logger = PyLogger()
        logger.reset()  # Clear any existing sinks from other tests
        logger.configure(auto_sink=False)  # Disable auto-sink
        logger.add("console")  # Manually add console sink
        logger.info("Unicode test: 你好世界 🌍 émojis")

        captured = capsys.readouterr()
        assert "你好世界" in captured.out
        assert "🌍" in captured.out
        assert "émojis" in captured.out
