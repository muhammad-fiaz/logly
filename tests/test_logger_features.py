"""Test logger features and functionality."""

from pathlib import Path

import pytest

from logly import logger


def read_log(path: Path) -> str:
    """Read log file content."""
    assert path.exists()
    return path.read_text()


def test_add_configure_and_basic_logging(tmp_path: Path):
    """Test basic logging configuration and file output."""
    p = tmp_path / "basic.log"
    # add file before configure per MVP
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    logger.info("hello world", user="bob")
    logger.complete()

    content = read_log(p)
    assert "hello world" in content
    assert "user=bob" in content


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


def test_opt_returns_proxy_and_logs(tmp_path: Path):
    """Test opt() method returns proxy and logs correctly."""
    p = tmp_path / "opt.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    opt_logger = logger.opt(colors=False)
    opt_logger.info("opt message")
    logger.complete()

    content = read_log(p)
    assert "opt message" in content


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
    with logger.catch(reraise=False):
        raise ValueError("bad")

    # context manager: reraise=True should re-raise
    with pytest.raises(ZeroDivisionError):
        with logger.catch(reraise=True):
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
    """Test remove handler and complete noop functionality."""
    p = tmp_path / "rm.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    ok = logger.remove(0)
    assert ok is True
    logger.info("after remove")
    logger.complete()
    content = read_log(p)
    assert "after remove" in content


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


def test_template_string_processing_exceptions(tmp_path: Path):
    """Test exception handling in template string processing."""
    p = tmp_path / "template.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    # Test malformed template strings that should fall back gracefully
    logger.info("malformed {unclosed", key="value")  # Missing closing brace
    logger.info("bad {missing} format", other="data")  # Missing key in format
    logger.info("valid {key} format", key="value")  # Valid template

    logger.complete()
    content = read_log(p)
    # Should contain the messages, possibly with fallback formatting
    assert "malformed" in content
    assert "bad" in content
    assert "valid value format" in content


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
