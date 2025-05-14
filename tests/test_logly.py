import os
import tempfile
import json
from pathlib import Path
from logly import logger, init, configure, DEBUG, INFO, WARNING, ERROR, CRITICAL


def test_logger_levels():
    """Test that logger levels work correctly."""
    # Default level should be INFO
    assert logger.get_level() == INFO

    # Set level to DEBUG
    logger.set_level(DEBUG)
    assert logger.get_level() == DEBUG

    # Set level to ERROR
    logger.set_level(ERROR)
    assert logger.get_level() == ERROR

    # Set level by string
    logger.set_level("WARNING")
    assert logger.get_level() == WARNING

    # Set level by int
    logger.set_level(50)  # CRITICAL
    assert logger.get_level() == CRITICAL


def test_logger_enable_disable():
    """Test that logger can be enabled and disabled."""
    # Default should be enabled
    assert logger.is_enabled() == True

    # Disable
    logger.disable()
    assert logger.is_enabled() == False

    # Enable
    logger.enable()
    assert logger.is_enabled() == True


def test_file_logging():
    """Test that logger can write to a file."""
    # Create a temporary directory for log files
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test.log")

        # Configure logger to write to file
        configure(
            level=DEBUG,
            file_path=log_file,
            colored_output=False,
            format="{level}: {message}"
        )

        # Log some messages
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Check that file exists and contains the messages
        assert os.path.exists(log_file)

        with open(log_file, "r") as f:
            content = f.read()
            assert "DEBUG: Debug message" in content
            assert "INFO: Info message" in content
            assert "WARNING: Warning message" in content
            assert "ERROR: Error message" in content
            assert "CRITICAL: Critical message" in content


def test_log_rotation():
    """Test that log files are rotated correctly."""
    # Create a temporary directory for log files
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "rotation.log")

        # Configure logger with small max file size
        configure(
            level=DEBUG,
            file_path=log_file,
            max_file_size=100,  # Very small to trigger rotation
            max_backup_count=3,
            colored_output=False
        )

        # Write enough logs to trigger multiple rotations
        for i in range(20):
            logger.info(f"Message {i} with some padding to make it larger")

        # Check that we have the expected number of log files
        log_path = Path(log_file)
        log_dir = log_path.parent
        log_name = log_path.name

        # Should have main log file plus backups
        log_files = list(log_dir.glob(f"{log_name}*"))
        assert len(log_files) <= 4  # Main file + 3 backups

        # Check that .1, .2, .3 exist (or fewer if not enough data)
        for i in range(1, 4):
            backup = log_path.with_name(f"{log_name}.{i}")
            if backup.exists():
                with open(backup, "r") as f:
                    assert "Message" in f.read()


def test_json_logging():
    """Test structured JSON logging."""
    # Create a temporary directory for log files
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "json.log")

        # Configure logger
        configure(
            level=DEBUG,
            file_path=log_file,
            colored_output=False
        )

        # Log a JSON message
        test_data = {
            "user": "test_user",
            "action": "login",
            "status": "success",
            "metadata": {
                "ip": "127.0.0.1",
                "timestamp": 1625097600
            }
        }

        logger.json(INFO, test_data)

        # Check that file contains valid JSON
        with open(log_file, "r") as f:
            content = f.read()
            # The log line contains formatting, but should include our JSON
            assert "test_user" in content
            assert "127.0.0.1" in content


def test_init_function():
    """Test the init function for configuring the logger."""
    # Create a temporary directory for log files
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "init.log")

        # Initialize with custom settings
        custom_logger = init(
            level="ERROR",
            file_path=log_file,
            max_file_size=1024 * 1024,
            max_backup_count=2,
            colored_output=False,
            format="{level}: {message}"
        )

        # Check that settings were applied
        assert custom_logger.get_level() == ERROR

        # Log messages
        custom_logger.debug("Debug message")  # Should not be logged
        custom_logger.info("Info message")    # Should not be logged
        custom_logger.error("Error message")  # Should be logged

        # Check log file
        with open(log_file, "r") as f:
            content = f.read()
            assert "Debug message" not in content
            assert "Info message" not in content
            assert "ERROR: Error message" in content
