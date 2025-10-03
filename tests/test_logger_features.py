"""Test logger features and functionality."""

from pathlib import Path

import pytest

from logly import logger


def read_log(path: Path) -> str:
    """Read log file content."""
    assert path.exists()
    return path.read_text()


def test_bind_and_contextualize(tmp_path: Path):
    """Test binding context and contextualize functionality."""
    p = tmp_path / "bind.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    bound = logger.bind(request_id="r1")
    bound.info("started")

    with bound.contextualize(step=1):
        bound.debug("step")

    logger.complete()
    content = read_log(p)
    assert "started" in content
    assert "request_id=r1" in content
    assert "step=1" in content


def test_enable_disable(tmp_path: Path):
    """Test enable/disable functionality."""
    p = tmp_path / "enable.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    logger.disable()
    logger.info("should_not_appear")
    logger.enable()
    logger.info("should_appear")
    logger.complete()

    content = read_log(p)
    assert "should_appear" in content
    assert "should_not_appear" not in content


def test_level_mapping(tmp_path: Path):
    """Test custom level mapping functionality."""
    p = tmp_path / "level.log"
    logger.add(str(p))
    logger.level("NOTICE", "info")
    logger.configure(level="INFO", color=False)

    logger.log("NOTICE", "notice message")
    logger.complete()

    content = read_log(p)
    assert "notice message" in content


def test_catch_decorator_and_context_manager(tmp_path: Path):
    """Test catch decorator and context manager functionality."""
    p = tmp_path / "catch.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    @logger.catch(reraise=False)
    def will_raise():
        raise RuntimeError("fail")

    # decorator should suppress (reraise=False)
    will_raise()

    # context manager: reraise=False suppresses
    with logger.catch(reraise=False):  # type: ignore[attr-defined]
        raise ValueError("bad")

    # context manager: reraise=True should re-raise
    with pytest.raises(ZeroDivisionError):
        with logger.catch(reraise=True):  # type: ignore[attr-defined]
            _ = 1 / 0

    logger.complete()
    content = read_log(p)
    # both exceptions should be logged
    assert "RuntimeError" in content or "fail" in content
    assert "ValueError" in content or "bad" in content


def test_exception_logs_traceback(tmp_path: Path):
    """Test exception logging with traceback."""
    p = tmp_path / "exc.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    try:
        _ = 1 / 0
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("caught")

    logger.complete()
    content = read_log(p)
    assert "ZeroDivisionError" in content or "division" in content


def test_remove_and_complete_noop(tmp_path: Path):
    """Test remove handler and complete functionality."""
    p = tmp_path / "rm.log"
    handler_id = logger.add(str(p))
    logger.configure(level="INFO", color=False)

    # Log before removal
    logger.info("before remove")
    logger.complete()
    content = read_log(p)
    assert "before remove" in content

    # Remove sink
    ok = logger.remove(handler_id)
    assert ok is True

    # Log after removal - should not appear in file
    logger.info("after remove")
    logger.complete()

    # Content should still only have the first message
    content = read_log(p)
    assert "before remove" in content
    assert "after remove" not in content


def test_all_log_levels(tmp_path: Path):
    """Test all log levels including trace and critical."""
    p = tmp_path / "levels.log"
    logger.add(str(p))
    logger.configure(level="TRACE", color=False)  # Set to TRACE to capture all levels

    logger.trace("trace message", level="TRACE")
    logger.debug("debug message", level="DEBUG")
    logger.info("info message", level="INFO")
    logger.warning("warning message", level="WARNING")
    logger.error("error message", level="ERROR")
    logger.critical("critical message", level="CRITICAL")
    logger.success("success message", level="SUCCESS")
    logger.complete()

    content = read_log(p)
    assert "trace message" in content
    assert "debug message" in content
    assert "info message" in content
    assert "warning message" in content
    assert "error message" in content
    assert "critical message" in content
    assert "success message" in content


def test_log_levels_with_formatting(tmp_path: Path):
    """Test log levels with string formatting."""
    p = tmp_path / "format.log"
    logger.add(str(p))
    logger.configure(level="TRACE", color=False)

    logger.trace("trace %s %d", "formatted", 42, extra="data")
    logger.critical("critical %s", "formatted", code=500)
    logger.success("success %s", "operation", result="ok")
    logger.complete()

    content = read_log(p)
    assert "trace formatted 42" in content
    assert "extra=data" in content
    assert "critical formatted" in content
    assert "code=500" in content
    assert "success operation" in content
    assert "result=ok" in content


def test_disabled_logger_early_returns(tmp_path: Path):
    """Test that disabled logger methods return early without logging."""
    p = tmp_path / "disabled.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    # Disable logger
    logger.disable()

    # These should all return early and not log
    logger.trace("trace_disabled_msg")
    logger.debug("debug_disabled_msg")
    logger.info("info_disabled_msg")
    logger.warning("warning_disabled_msg")
    logger.error("error_disabled_msg")
    logger.critical("critical_disabled_msg")
    logger.success("success_disabled_msg")

    # Re-enable and log something to verify file is still valid
    logger.enable()
    logger.info("enabled_again")
    logger.complete()

    content = read_log(p)
    # Only the enabled message should appear
    assert "enabled_again" in content
    assert "disabled_msg" not in content


def test_caller_info_exceptions(tmp_path: Path):
    """Test exception handling in caller info augmentation."""
    p = tmp_path / "caller.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    # This should work normally
    logger.info("normal message", explicit_module="test")

    # The exception handling in _add_caller_info is hard to trigger directly
    # since it depends on introspection, but we can verify it doesn't break logging
    logger.info("another message")
    logger.complete()

    content = read_log(p)
    assert "normal message" in content
    assert "explicit_module=test" in content
    assert "another message" in content


def test_log_method_disabled(tmp_path: Path):
    """Test log() method early return when disabled."""
    p = tmp_path / "log_disabled.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    logger.disable()
    logger.log("INFO", "should_not_log")
    logger.enable()
    logger.log("INFO", "should_log")
    logger.complete()

    content = read_log(p)
    assert "should_log" in content
    assert "should_not_log" not in content


def test_custom_level_colors(tmp_path: Path):
    """Test custom color configuration for log levels."""
    p = tmp_path / "colors.log"
    logger.add(str(p))

    # Configure with custom colors
    custom_colors = {
        "INFO": "34",  # Blue
        "WARNING": "35",  # Magenta
        "ERROR": "36",  # Cyan
    }
    logger.configure(level="INFO", level_colors=custom_colors)

    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.complete()

    content = read_log(p)
    assert "info message" in content
    assert "warning message" in content
    assert "error message" in content


def test_default_colors_vs_custom_colors(tmp_path: Path):
    """Test that custom colors override defaults."""
    p = tmp_path / "color_test.log"
    logger.add(str(p))

    # First configure with defaults
    logger.configure(level="INFO", color=True)
    logger.info("default color info")

    # Then configure with custom colors
    custom_colors = {"INFO": "31"}  # Red
    logger.configure(level="INFO", level_colors=custom_colors)
    logger.info("custom color info")

    logger.complete()

    content = read_log(p)
    assert "default color info" in content
    assert "custom color info" in content


def test_color_names(tmp_path: Path):
    """Test custom color configuration using color names instead of ANSI codes."""
    p = tmp_path / "color_names.log"
    logger.add(str(p))

    # Configure with custom colors using color names
    custom_colors = {"INFO": "GREEN", "WARNING": "YELLOW", "ERROR": "RED"}
    logger.configure(level="INFO", level_colors=custom_colors)

    logger.info("info message with green")
    logger.warning("warning message with yellow")
    logger.error("error message with red")

    logger.complete()

    content = read_log(p)
    assert "info message with green" in content
    assert "warning message with yellow" in content
    assert "error message with red" in content


def test_show_time_configuration(tmp_path: Path):
    """Test console time display control."""
    p = tmp_path / "time_test.log"
    logger.add(str(p))

    # Configure with timestamps enabled (default)
    logger.configure(level="INFO", show_time=True)
    logger.info("message with timestamp")

    # Configure with timestamps disabled
    logger.configure(level="INFO", show_time=False)
    logger.info("message without timestamp")

    logger.complete()

    content = read_log(p)
    assert "message with timestamp" in content
    assert "message without timestamp" in content


def test_show_module_function_configuration(tmp_path: Path):
    """Test console module and function display control."""
    p = tmp_path / "module_function_test.log"
    logger.add(str(p))

    # Configure with module and function info enabled (default)
    logger.configure(level="INFO", show_module=True, show_function=True)
    logger.info("message with module and function")

    # Configure with module and function info disabled
    logger.configure(level="INFO", show_module=False, show_function=False)
    logger.info("message without module and function")

    # Configure with only module disabled
    logger.configure(level="INFO", show_module=False, show_function=True)
    logger.info("message without module but with function")

    # Configure with only function disabled
    logger.configure(level="INFO", show_module=True, show_function=False)
    logger.info("message with module but without function")

    logger.complete()

    content = read_log(p)
    assert "message with module and function" in content
    assert "message without module and function" in content
    assert "message without module but with function" in content
    assert "message with module but without function" in content


def test_show_filename_lineno_configuration(tmp_path: Path):
    """Test console filename and lineno display control."""
    p = tmp_path / "filename_lineno_test.log"
    logger.add(str(p))

    # Configure with filename and lineno info enabled
    logger.configure(level="INFO", show_filename=True, show_lineno=True)
    logger.info("message with filename and lineno")

    # Configure with filename and lineno info disabled
    logger.configure(level="INFO", show_filename=False, show_lineno=False)
    logger.info("message without filename and lineno")

    # Configure with only filename disabled
    logger.configure(level="INFO", show_filename=False, show_lineno=True)
    logger.info("message without filename but with lineno")

    # Configure with only lineno disabled
    logger.configure(level="INFO", show_filename=True, show_lineno=False)
    logger.info("message with filename but without lineno")

    logger.complete()

    content = read_log(p)
    assert "message with filename and lineno" in content
    assert "message without filename and lineno" in content
    assert "message without filename but with lineno" in content
    assert "message with filename but without lineno" in content


def test_per_level_console_controls(tmp_path: Path):
    """Test per-level console output controls."""
    p = tmp_path / "console.log"
    logger.add(str(p))

    # Configure with per-level console settings
    logger.configure(
        level="DEBUG", console_levels={"DEBUG": True, "INFO": False, "WARN": True, "ERROR": True}
    )

    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warn message")
    logger.error("error message")
    logger.complete()

    # Check file output (should have all messages regardless of console settings)
    content = read_log(p)
    assert "debug message" in content
    assert "info message" in content
    assert "warn message" in content
    assert "error message" in content


def test_per_level_time_controls(tmp_path: Path):
    """Test per-level time display controls."""
    p = tmp_path / "time.log"
    logger.add(str(p))

    # Configure with per-level time settings
    logger.configure(
        level="DEBUG",
        show_time=False,  # Global default off
        time_levels={"DEBUG": True, "INFO": False, "WARN": True},
    )

    logger.debug("debug with time")
    logger.info("info without time")
    logger.warning("warn with time")
    logger.complete()

    # Check file output for timestamps
    content = read_log(p)
    import re

    timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

    # DEBUG and WARN should have timestamps in file, INFO should not
    assert re.search(timestamp_pattern + r".*debug with time", content), (
        "DEBUG should have timestamp in file"
    )
    assert re.search(r"\[INFO\] info without time", content) and not re.search(
        timestamp_pattern + r".*info without time", content
    ), "INFO should not have timestamp in file"
    assert re.search(timestamp_pattern + r".*warn with time", content), (
        "WARN should have timestamp in file"
    )


def test_per_level_color_controls(tmp_path: Path):
    """Test per-level color controls."""
    p = tmp_path / "color.log"
    logger.add(str(p))

    # Configure with per-level color settings
    logger.configure(
        level="DEBUG",
        color=True,  # Global default on
        color_levels={"DEBUG": False, "INFO": True, "WARN": False},
    )

    logger.debug("debug uncolored")
    logger.info("info colored")
    logger.warning("warn uncolored")
    logger.complete()

    # Check file output (colors don't affect file output)
    content = read_log(p)
    assert "debug uncolored" in content
    assert "info colored" in content
    assert "warn uncolored" in content


def test_per_level_storage_controls(tmp_path: Path):
    """Test per-level storage (file logging) controls."""
    p = tmp_path / "storage.log"
    logger.add(str(p))

    # Configure with per-level storage settings
    logger.configure(
        level="DEBUG", storage_levels={"DEBUG": True, "INFO": False, "WARN": True, "ERROR": True}
    )

    logger.debug("debug stored")
    logger.info("info not stored")
    logger.warning("warn stored")
    logger.error("error stored")
    logger.complete()

    # Check file output
    content = read_log(p)
    assert "debug stored" in content
    assert "info not stored" not in content  # Should not be in file
    assert "warn stored" in content
    assert "error stored" in content


def test_per_sink_custom_formatting(tmp_path: Path):
    """Test per-sink custom format strings."""
    file_log = tmp_path / "file.log"

    # Add console with default formatting
    logger.add("console")
    # Add file with custom format
    logger.add(str(file_log), format="{time} [{level}] {message} {extra}")
    logger.configure(level="INFO", color=False)

    logger.info("Test message", user="alice", action="login")
    logger.warning("Warning message", code=404, path="/api/users")
    logger.complete()

    # Check file has custom format
    content = read_log(file_log)
    lines = content.strip().split("\n")
    assert len(lines) == 2

    # First line should have RFC3339 timestamp, level, message, and extra fields
    first_line = lines[0]
    assert "[INFO]" in first_line
    assert "Test message" in first_line
    assert "user=alice" in first_line
    assert "action=login" in first_line
    # Should have RFC3339 timestamp format
    assert "T" in first_line and "+" in first_line

    # Second line should have warning
    second_line = lines[1]
    assert "[WARN]" in second_line
    assert "Warning message" in second_line
    assert "code=404" in second_line
    assert "path=/api/users" in second_line


def test_per_sink_format_with_extra_placeholder(tmp_path: Path):
    """Test {extra} placeholder in custom format strings."""
    log_file = tmp_path / "extra.log"

    logger.add(str(log_file), format="{level}: {message} | {extra}")
    logger.configure(level="INFO", color=False)

    logger.info("Simple message")
    logger.warning("Message with extras", key1="value1", key2="value2")
    logger.complete()

    content = read_log(log_file)
    lines = content.strip().split("\n")
    assert len(lines) == 2

    # First line: no extra fields, but module/function are always added
    assert "INFO: Simple message | module=" in lines[0]
    assert "function=" in lines[0]

    # Second line: with extra fields
    assert "WARN: Message with extras | key1=value1 | key2=value2" in lines[1]
    # Module and function should still be appended since they're not in the {extra} template
    assert "module=" in lines[1]
    assert "function=" in lines[1]


def test_per_sink_format_case_insensitive(tmp_path: Path):
    """Test that format placeholders are case-insensitive."""
    log_file = tmp_path / "case.log"

    logger.add(str(log_file), format="{TIME} | {LEVEL} | {MESSAGE}")
    logger.configure(level="INFO", color=False)

    logger.info("Case test message")
    logger.complete()

    content = read_log(log_file)
    # Should work with uppercase placeholders: "timestamp | INFO | Case test message"
    # Extra fields are not automatically appended for custom templates
    assert " | INFO | Case test message" in content
    assert "module=" not in content
    assert "function=" not in content
    # Should have RFC3339 timestamp
    assert "T" in content and "+" in content


def test_per_sink_format_mixed_placeholders(tmp_path: Path):
    """Test mixing different placeholder types in format strings."""
    log_file = tmp_path / "mixed.log"

    logger.add(str(log_file), format="[{level}] {time} - {message} | user={user} | {extra}")
    logger.configure(level="INFO", color=False)

    bound_logger = logger.bind(user="testuser")
    bound_logger.info("Mixed format test", action="click", button="submit")
    logger.complete()

    content = read_log(log_file)
    line = content.strip()

    # Should contain all expected elements
    assert "[INFO]" in line
    assert "Mixed format test" in line
    assert "user=testuser" in line
    assert "action=click" in line
    assert "button=submit" in line
    # Should have timestamp
    assert "T" in line and "+" in line


def test_per_sink_format_backward_compatibility(tmp_path: Path):
    """Test that sinks without custom format still work with default formatting."""
    log_file = tmp_path / "compat.log"

    # Add sink without format (should use default)
    logger.add(str(log_file))
    logger.configure(level="INFO", color=False, show_time=False)

    logger.info("Compatibility test", extra_field="value")
    logger.complete()

    content = read_log(log_file)
    # Should have default format: [LEVEL] message | extra
    assert "[INFO] Compatibility test | extra_field=value" in content


def test_per_sink_format_with_filters(tmp_path: Path):
    """Test custom format combined with filters."""
    logger.reset()  # Reset to clean state
    info_log = tmp_path / "info.log"
    error_log = tmp_path / "error.log"

    logger.add(str(info_log), format="{level}: {message}", filter_min_level="INFO")
    logger.add(
        str(error_log), format="ERROR - {time} - {message} | {extra}", filter_min_level="ERROR"
    )
    logger.configure(level="DEBUG", color=False)

    logger.debug("Debug message")  # Should not appear in either
    logger.info("Info message")  # Should appear in info.log
    logger.error("Error message", code=500)  # Should appear in error.log
    logger.complete()

    # Check info log
    info_content = read_log(info_log)
    assert "INFO: Info message" in info_content
    assert "Debug message" not in info_content
    assert "Error message" not in info_content

    # Check error log
    error_content = read_log(error_log)
    assert "ERROR -" in error_content
    assert "Error message" in error_content
    assert "code=500" in error_content
    assert "Debug message" not in error_content
    assert "Info message" not in error_content


def test_per_sink_format_filename_lineno_placeholders(tmp_path: Path):
    """Test {filename} and {lineno} placeholders in custom format strings."""
    log_file = tmp_path / "filename_lineno.log"

    logger.add(str(log_file), format="{level}: {filename}:{lineno} - {message}")
    logger.configure(level="INFO", color=False, show_filename=True, show_lineno=True)

    logger.info("Test message with filename and lineno")
    logger.complete()

    content = read_log(log_file)
    # The format should include the actual filename and line number
    assert "INFO:" in content
    assert "test_logger_features.py:" in content
    assert "- Test message with filename and lineno" in content
