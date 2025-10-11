"""Test logger initialization and internal debug features."""

from pathlib import Path
from unittest.mock import patch

from logly import _LoggerProxy, logger
from logly._logly import PyLogger


def test_logger_with_provided_inner(tmp_path: Path):
    """Test creating logger with an existing PyLogger instance."""
    # Create a PyLogger instance directly
    py_logger = PyLogger(auto_update_check=False)

    # Create LoggerProxy with provided inner
    custom_logger = _LoggerProxy(inner=py_logger, auto_configure=True)

    # Test logging works
    log_file = tmp_path / "custom.log"
    custom_logger.add(str(log_file))
    custom_logger.info("Test with provided inner", status="success")
    custom_logger.complete()

    assert log_file.exists()
    content = log_file.read_text()
    assert "Test with provided inner" in content
    assert "success" in content


def test_logger_call_basic(tmp_path: Path):
    """Test logger() call with basic parameters."""
    # Create new logger instance
    new_logger = logger(auto_update_check=False)

    # Add a sink and log
    log_file = tmp_path / "app.log"
    new_logger.add(str(log_file))
    new_logger.info("Logger call test", operation="test_basic")
    new_logger.complete()

    # Check main log exists
    assert log_file.exists()
    content = log_file.read_text()
    assert "Logger call test" in content


def test_logger_init_with_none_inner(tmp_path: Path):
    """Test _LoggerProxy initialization with inner=None."""
    # Create logger with None inner (should create new PyLogger)
    new_logger = _LoggerProxy(
        inner=None,
        auto_update_check=False,
        auto_configure=True,
    )

    log_file = tmp_path / "none_inner.log"
    new_logger.add(str(log_file))
    new_logger.info("Logger created with inner=None")
    new_logger.complete()

    assert log_file.exists()
    content = log_file.read_text()
    assert "Logger created with inner=None" in content


def test_logger_call_without_auto_configure(tmp_path: Path):
    """Test logger() with auto_configure=False."""
    no_auto_logger = logger(
        auto_update_check=False,
        auto_configure=False,
    )

    # Manual configuration needed
    no_auto_logger.configure(level="INFO", color=False)

    log_file = tmp_path / "manual.log"
    no_auto_logger.add(str(log_file))
    no_auto_logger.info("Manual configuration test")
    no_auto_logger.complete()

    assert log_file.exists()
    content = log_file.read_text()
    assert "Manual configuration test" in content


def test_logger_multiple_instances(tmp_path: Path):
    """Test creating multiple logger instances."""
    logger1 = logger(auto_update_check=False)
    logger2 = logger(auto_update_check=False)

    log1 = tmp_path / "logger1.log"
    log2 = tmp_path / "logger2.log"

    logger1.add(str(log1))
    logger2.add(str(log2))

    logger1.info("From logger 1")
    logger2.info("From logger 2")

    logger1.complete()
    logger2.complete()

    assert log1.exists()
    assert log2.exists()
    assert "From logger 1" in log1.read_text()
    assert "From logger 2" in log2.read_text()


def test_logger_with_internal_debug(tmp_path: Path):
    """Test logger() with internal_debug enabled."""
    # Test internal debug parameters
    debug_logger = logger(
        auto_update_check=False,
        internal_debug=True,
        debug_log_path=str(tmp_path / "debug.log"),
    )

    # Add a sink and log
    log_file = tmp_path / "app.log"
    debug_logger.add(str(log_file))
    debug_logger.info("Testing internal debug mode")
    debug_logger.complete()

    # Verify main log exists
    assert log_file.exists()
    content = log_file.read_text()
    assert "Testing internal debug mode" in content


def test_logger_proxy_with_internal_debug_params(tmp_path: Path):
    """Test _LoggerProxy with internal_debug and debug_log_path parameters."""
    # Create logger with all internal debug parameters
    debug_logger = _LoggerProxy(
        inner=None,
        auto_update_check=False,
        auto_configure=True,
        internal_debug=True,
        debug_log_path=str(tmp_path / "internal_debug.log"),
    )

    log_file = tmp_path / "test.log"
    debug_logger.add(str(log_file))
    debug_logger.info("Test with internal debug parameters")
    debug_logger.complete()

    assert log_file.exists()
    content = log_file.read_text()
    assert "Test with internal debug parameters" in content


def test_logger_init_fallback_to_old_signature(tmp_path: Path):
    """Test _LoggerProxy fallback when PyLogger doesn't support new parameters."""

    # Create a mock PyLogger that raises TypeError for new signature
    def mock_pylogger_init(*args, **kwargs):
        # If called with new parameters, raise TypeError to simulate old Rust binary
        if "internal_debug" in kwargs or "debug_log_path" in kwargs:
            raise TypeError("PyLogger() got an unexpected keyword argument")
        # Otherwise return a real PyLogger with old signature
        return PyLogger(*args, **kwargs)

    with patch("logly.PyLogger", side_effect=mock_pylogger_init):
        # This should trigger the fallback in __init__
        fallback_logger = _LoggerProxy(
            inner=None,
            auto_update_check=False,
            auto_configure=True,
            internal_debug=True,  # This will cause TypeError
            debug_log_path="debug.log",
        )

        log_file = tmp_path / "fallback.log"
        fallback_logger.add(str(log_file))
        fallback_logger.info("Fallback test")
        fallback_logger.complete()

        assert log_file.exists()
        assert "Fallback test" in log_file.read_text()


def test_logger_call_fallback_to_old_signature(tmp_path: Path):
    """Test logger() call fallback when PyLogger doesn't support new parameters."""

    # Create a mock PyLogger that raises TypeError for new signature
    def mock_pylogger_init(*args, **kwargs):
        # If called with new parameters, raise TypeError to simulate old Rust binary
        if "internal_debug" in kwargs or "debug_log_path" in kwargs:
            raise TypeError("PyLogger() got an unexpected keyword argument")
        # Otherwise return a real PyLogger with old signature
        return PyLogger(*args, **kwargs)

    with patch("logly.PyLogger", side_effect=mock_pylogger_init):
        # This should trigger the fallback in __call__
        fallback_logger = logger(
            auto_update_check=False,
            internal_debug=True,  # This will cause TypeError
            debug_log_path="debug.log",
        )

        log_file = tmp_path / "call_fallback.log"
        fallback_logger.add(str(log_file))
        fallback_logger.info("Call fallback test")
        fallback_logger.complete()

        assert log_file.exists()
        assert "Call fallback test" in log_file.read_text()
