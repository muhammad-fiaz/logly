"""Test logger initialization and internal debug features."""

from pathlib import Path
from logly import logger
from logly._logly import PyLogger


def test_logger_with_provided_inner(tmp_path: Path):
    """Test creating logger with an existing PyLogger instance."""
    # Create a PyLogger instance directly
    py_logger = PyLogger(auto_update_check=False)

    # Create LoggerProxy with provided inner
    from logly import _LoggerProxy

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
    from logly import _LoggerProxy

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
