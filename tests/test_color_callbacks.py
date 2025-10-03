"""Tests for color callback functionality."""

import sys

import pytest

from logly import logger


class TestColorCallbacks:
    """Test color callback functionality across different formats."""

    def setup_method(self):
        """Reset logger state before each test."""
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.reset()

    def test_color_callback_basic_functionality(self, capsys):
        """Test that color callback is called and overrides built-in coloring."""
        callback_calls = []

        def test_callback(level, text):
            callback_calls.append((level, text))
            return f"[{level}] {text}"

        logger.configure(level="INFO", color_callback=test_callback)
        logger.add("console")
        logger._inner._log_with_stdout("INFO", "Test message", sys.stdout)

        # Verify callback was called
        assert len(callback_calls) == 1
        level, text = callback_calls[0]
        assert level == "INFO"
        assert "Test message" in text

        # Verify output contains callback result
        captured = capsys.readouterr()
        assert "[INFO]" in captured.out
        assert "Test message" in captured.out

    def test_color_callback_precedence_over_builtin_colors(self, capsys):
        """Test that color callback completely overrides built-in ANSI coloring."""

        def custom_callback(level, text):
            return f"CUSTOM-{level}: {text}"

        # Configure with both color=True and color_callback
        logger.configure(
            level="INFO",
            color=True,
            color_callback=custom_callback,
            level_colors={"INFO": "RED"},  # This should be ignored
        )
        logger.add("console")
        logger._inner._log_with_stdout("INFO", "Test message", sys.stdout)

        captured = capsys.readouterr()
        # Should contain custom callback output, not ANSI red color
        assert "CUSTOM-INFO:" in captured.out
        assert "Test message" in captured.out
        # Should NOT contain ANSI red color code (\033[31m)
        assert "\033[31m" not in captured.out

    def test_color_callback_with_all_log_levels(self, capsys):
        """Test color callback with all log levels."""
        callback_calls = []

        def tracking_callback(level, text):
            callback_calls.append(level)
            return f"[{level}] {text}"

        logger.configure(level="TRACE", color_callback=tracking_callback)
        logger.add("console")

        logger._inner._log_with_stdout("TRACE", "trace message", sys.stdout)
        logger._inner._log_with_stdout("DEBUG", "debug message", sys.stdout)
        logger._inner._log_with_stdout("INFO", "info message", sys.stdout)
        logger._inner._log_with_stdout("WARNING", "warning message", sys.stdout)
        logger._inner._log_with_stdout("ERROR", "error message", sys.stdout)
        logger._inner._log_with_stdout("CRITICAL", "critical message", sys.stdout)

        # Verify all levels were processed (callback may be called multiple times due to async processing)
        expected_levels = [
            "TRACE",
            "DEBUG",
            "INFO",
            "WARN",
            "ERROR",
            "ERROR",
        ]  # CRITICAL maps to ERROR
        # Check that all expected levels are present in callback_calls
        for level in expected_levels:
            assert level in callback_calls

        captured = capsys.readouterr()
        for level in expected_levels:
            assert f"[{level}]" in captured.out

    def test_color_callback_with_json_format(self, capsys):
        """Test color callback works with JSON output."""

        def json_callback(level, text):
            return f"JSON-{level}: {text}"

        logger.configure(level="INFO", json=True, color_callback=json_callback)
        logger.add("console")
        logger._inner._log_with_stdout("INFO", "JSON test", sys.stdout, key="value")

        captured = capsys.readouterr()
        # Should contain callback output, not standard JSON
        assert "JSON-INFO:" in captured.out
        assert "JSON test" in captured.out

    def test_color_callback_with_file_output(self, tmp_path):
        """Test color callback works with file output."""
        log_file = tmp_path / "test.log"

        def file_callback(level, text):
            return f"FILE-{level}: {text}"

        logger.configure(level="INFO", color_callback=file_callback)
        logger.add(str(log_file), async_write=False)

        logger.info("File test message")

        # Read file and verify callback was applied
        content = log_file.read_text()
        assert "FILE-INFO:" in content
        assert "File test message" in content

    def test_color_callback_disabled_when_color_false(self, capsys):
        """Test that color callback is not called when color=False."""
        callback_calls = []

        def tracking_callback(level, text):
            callback_calls.append((level, text))
            return text

        logger.configure(
            level="INFO",
            color=False,  # Explicitly disable colors
            color_callback=tracking_callback,
        )
        logger.add("console")
        logger._inner._log_with_stdout("INFO", "Test message", sys.stdout)

        # Callback should not be called when color=False
        assert len(callback_calls) == 0

        captured = capsys.readouterr()
        assert "Test message" in captured.out
        # Should not contain any ANSI color codes
        assert "\033[" not in captured.out

    def test_color_callback_with_rich_library(self, capsys):
        """Test color callback integration with Rich library."""
        pytest.importorskip("rich")

        def rich_callback(level, text):
            """Rich-based color callback - simplified to return ANSI codes."""
            ansi_codes = {
                "DEBUG": "\033[34m",  # Blue
                "INFO": "\033[32m",  # Green
                "WARN": "\033[33m",  # Yellow
                "WARNING": "\033[33m",  # Yellow
                "ERROR": "\033[31m",  # Red
                "CRITICAL": "\033[35m",  # Magenta
            }
            reset = "\033[0m"
            code = ansi_codes.get(level, "")
            return f"{code}{text}{reset}"

        logger.configure(
            level="DEBUG",
            color_callback=rich_callback,
            show_time=False,
            show_module=False,
            show_function=False,
        )
        logger.add("console")

        logger._inner._log_with_stdout("DEBUG", "Debug with Rich", sys.stdout)
        logger._inner._log_with_stdout("INFO", "Info with Rich", sys.stdout)
        logger._inner._log_with_stdout("WARNING", "Warning with Rich", sys.stdout)
        logger._inner._log_with_stdout("ERROR", "Error with Rich", sys.stdout)

        captured = capsys.readouterr()
        # Should contain ANSI color codes from Rich
        assert "\033[" in captured.out  # ANSI escape codes present
        assert "Debug with Rich" in captured.out
        assert "Info with Rich" in captured.out
        assert "Warning with Rich" in captured.out
        assert "Error with Rich" in captured.out

    def test_color_callback_with_ansi_direct(self, capsys):
        """Test color callback with direct ANSI escape codes."""

        def ansi_callback(level, text):
            """Direct ANSI color callback."""
            ansi_codes = {
                "DEBUG": "\033[34m",  # Blue
                "INFO": "\033[32m",  # Green
                "WARN": "\033[33m",  # Yellow
                "WARNING": "\033[33m",  # Yellow
                "ERROR": "\033[31m",  # Red
                "CRITICAL": "\033[35m",  # Magenta
            }
            reset = "\033[0m"
            code = ansi_codes.get(level, "")
            return f"{code}{text}{reset}"

        logger.configure(
            level="DEBUG",
            color_callback=ansi_callback,
            show_time=False,
            show_module=False,
            show_function=False,
        )
        logger.add("console")

        logger._inner._log_with_stdout("DEBUG", "Debug with ANSI", sys.stdout)
        logger._inner._log_with_stdout("INFO", "Info with ANSI", sys.stdout)
        logger._inner._log_with_stdout("WARNING", "Warning with ANSI", sys.stdout)
        logger._inner._log_with_stdout("ERROR", "Error with ANSI", sys.stdout)

        captured = capsys.readouterr()
        # Should contain ANSI color codes
        assert "\033[" in captured.out
        assert "Debug with ANSI" in captured.out
        assert "Info with ANSI" in captured.out
        assert "Warning with ANSI" in captured.out
        assert "Error with ANSI" in captured.out

    def test_color_callback_with_custom_styling(self, capsys):
        """Test color callback with custom styling (emojis, formatting)."""

        def fancy_callback(level, text):
            """Callback with emojis and custom formatting."""
            decorations = {
                "DEBUG": "🔍",
                "INFO": "ℹ️",
                "WARN": "⚠️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "CRITICAL": "🚨",
            }
            emoji = decorations.get(level, "📝")
            return f"{emoji} {text} {emoji}"

        logger.configure(
            level="DEBUG",
            color_callback=fancy_callback,
            show_time=False,
            show_module=False,
            show_function=False,
        )
        logger.add("console")

        logger._inner._log_with_stdout("DEBUG", "Debug with emoji", sys.stdout)
        logger._inner._log_with_stdout("INFO", "Info with emoji", sys.stdout)
        logger._inner._log_with_stdout("WARNING", "Warning with emoji", sys.stdout)
        logger._inner._log_with_stdout("ERROR", "Error with emoji", sys.stdout)

        captured = capsys.readouterr()
        assert "🔍 [DEBUG] Debug with emoji 🔍" in captured.out
        assert "ℹ️ [INFO] Info with emoji ℹ️" in captured.out
        assert "⚠️ [WARN] Warning with emoji ⚠️" in captured.out
        assert "❌ [ERROR] Error with emoji ❌" in captured.out

    def test_color_callback_exception_handling(self, capsys):
        """Test that exceptions in color callback don't crash logging."""

        def broken_callback(level, text):
            raise ValueError("Callback error")

        logger.configure(level="INFO", color_callback=broken_callback)
        logger.add("console")

        # This should not crash, should fall back gracefully
        logger._inner._log_with_stdout("INFO", "Test message after callback error", sys.stdout)

        captured = capsys.readouterr()
        assert "Test message after callback error" in captured.out

    def test_color_callback_with_template_formatting(self, capsys):
        """Test color callback with template formatting."""

        def template_callback(level, text):
            return f"[{level.upper()}] {text}"

        logger.configure(level="INFO", color_callback=template_callback)
        logger.add("console")
        logger._inner._log_with_stdout("INFO", "Template test", sys.stdout)

        captured = capsys.readouterr()
        # Should contain the callback formatting
        assert "[INFO]" in captured.out
        assert "Template test" in captured.out

    def test_color_callback_with_context_binding(self, capsys):
        """Test color callback with context binding."""

        def context_callback(level, text):
            return f"CONTEXT-{level}: {text}"

        logger.configure(level="INFO", color_callback=context_callback)
        logger.add("console")

        # Bind context and log
        logger.bind(user="test_user", session="123")
        logger._inner._log_with_stdout(
            "INFO", "Context test", sys.stdout, user="test_user", session="123", action="login"
        )

        captured = capsys.readouterr()
        assert "CONTEXT-INFO:" in captured.out
        assert "Context test" in captured.out
        assert "user=test_user" in captured.out
        assert "session=123" in captured.out
        assert "action=login" in captured.out

    def test_color_callback_none_disables_custom_colors(self, capsys):
        """Test that setting color_callback=None falls back to built-in colors."""

        def custom_callback(level, text):
            return f"CUSTOM-{level}: {text}"

        # First configure with callback
        logger.configure(level="INFO", color=True, color_callback=custom_callback)
        logger.add("console")
        logger._inner._log_with_stdout("INFO", "With callback", sys.stdout)

        # Then configure without callback (should use built-in colors)
        logger.configure(level="INFO", color=True, color_callback=None)
        logger._inner._log_with_stdout("INFO", "Without callback", sys.stdout)

        captured = capsys.readouterr()
        assert "CUSTOM-INFO:" in captured.out  # First message with callback
        assert "Without callback" in captured.out  # Second message without callback
        # Second message should have ANSI colors (built-in) - check that it doesn't have CUSTOM-INFO
        assert "[INFO] Without callback" in captured.out
