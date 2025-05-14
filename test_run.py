from logly import (
    logger, init, configure,
    debug, info, warning, error, critical,
    set_level, enable, disable,
    DEBUG, INFO, WARNING, ERROR, CRITICAL
)
import os

# Clean previous logs (optional setup for test)
log_path = "logs/app.log"
# Commenting out to test append behavior
# if os.path.exists(log_path):
#     os.remove(log_path)

# Test: Initialization
init(
    level="DEBUG",
    file_path=log_path,
    max_file_size=1024 * 1024,  # 1MB
    max_backup_count=3,
    colored_output=True,
    format="{timestamp} [{level}] {message} ({file}:{line} - {function})",
    debug_config=False  # Don't show config debug messages
)

# Test: Global logging functions
debug("Test debug message from global")
info("Test info message from global")
warning("Test warning message from global")
error("Test error message from global")
critical("Test critical message from global")

# Test: Logger instance methods
logger.debug("Instance debug message", file=__file__, line=42, function="main")
logger.info("Instance info message", file=__file__, line=43, function="main")
logger.warning("Instance warning message", file=__file__, line=44, function="main")
logger.error("Instance error message", file=__file__, line=45, function="main")
logger.critical("Instance critical message", file=__file__, line=46, function="main")

# Test: Custom format for individual log messages
print("\n# Testing custom format for individual log messages")
logger.debug("Custom format debug message", file=__file__, line=42, function="main", 
             format="{timestamp} [{level}] {message} ({file}:{line} - {function})")
logger.info("Custom format info message", file=__file__, line=43, function="main", 
            format="CUSTOM FORMAT: {level} - {message}")
logger.warning("Custom format warning message", file=__file__, line=44, function="main", 
               format="{timestamp} :: {level} :: {message} :: {file}")
logger.error("Custom format error message", file=__file__, line=45, function="main", 
             format="ERROR: {message}")
logger.critical("Custom format critical message", file=__file__, line=46, function="main", 
                format="{level}: {message} at {timestamp}")

# Test: Custom colors for individual log messages
print("\n# Testing custom colors for individual log messages")
logger.debug("Debug message with custom color (red)", color="red")
logger.info("Info message with custom color (blue)", color="blue")
logger.warning("Warning message with custom color (green)", color="green")
logger.error("Error message with custom color (yellow)", color="yellow")
logger.critical("Critical message with custom color (magenta)", color="magenta")

# Test: Global functions with custom colors
print("\n# Testing global functions with custom colors")
debug("Global debug message with custom color (cyan)", color="cyan")
info("Global info message with custom color (red)", color="red")
warning("Global warning message with custom color (blue)", color="blue")
error("Global error message with custom color (green)", color="green")
critical("Global critical message with custom color (yellow)", color="yellow")

# Test: Structured JSON logging
logger.json(INFO, {"event": "user_login", "user": "admin", "status": "success"})

# Test: Level control
set_level(WARNING)
logger.debug("This debug should not appear")
logger.warning("This warning should appear")

# Test: Enable/Disable
disable()
logger.info("This log should be suppressed")

enable()
logger.info("This log should be visible again")

# Test: Reconfigure
configure(
    level="ERROR",
    file_path=log_path,
    max_file_size=1024 * 512,
    max_backup_count=1,
    colored_output=False,
    format="{timestamp} [{level}] {message}"
)

logger.info("This should not be logged")  # Below current level
logger.error("This should be logged after reconfigure")

# Test: Debug config messages
print("\n# Testing debug config messages")
configure(
    level="ERROR",
    file_path=log_path,
)

# This should show debug messages about configuration
print("\n# Reconfiguring with debug_config=True")
configure(
    level="WARNING",
    file_path=log_path,
)

print("All tests ran. Check logs/app.log for output.")
