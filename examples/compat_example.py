"""
Example script demonstrating the use of logly's compatibility layer with Python's standard logging module.

This script shows how to use logly with code that expects the standard logging module.
"""

import os
import sys
import logging
import tempfile

# Add the parent directory to the path so we can import logly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from logly.compat instead of logging
from logly.compat import getLogger, basicConfig, config, FileHandler, StreamHandler, Formatter

# Basic configuration
print("Basic configuration example:")
# Create a temporary log file
with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp:
    log_file = temp.name
    print(f"Logging to {log_file}")

    # Configure logging with basicConfig
    basicConfig(
        level="INFO",
        filename=log_file,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Get a logger
    logger = getLogger("example")

    # Log some messages
    logger.debug("This debug message should not appear")
    logger.info("This info message should appear")
    logger.warning("This warning message should appear")
    logger.error("This error message should appear")
    logger.critical("This critical message should appear")

    # Read the log file
    with open(log_file, 'r') as f:
        print("\nLog file contents:")
        print(f.read())

    # Clean up
    os.unlink(log_file)

# Advanced configuration with dictConfig
print("\nAdvanced configuration example with dictConfig:")
# Create a temporary log file
with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp:
    log_file = temp.name
    print(f"Logging to {log_file}")

    # Configure logging with dictConfig
    config.dictConfig({
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'simple': {
                'format': '%(levelname)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logly.compat.StreamHandler',
                'level': 'WARNING',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logly.compat.FileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': log_file,
                'mode': 'a',
            }
        },
        'loggers': {
            'example': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        }
    })

    # Get a logger
    logger = getLogger("example")

    # Log some messages
    logger.debug("This debug message should appear in the file but not console")
    logger.info("This info message should appear in the file but not console")
    logger.warning("This warning message should appear in both file and console")
    logger.error("This error message should appear in both file and console")
    logger.critical("This critical message should appear in both file and console")

    # Read the log file
    with open(log_file, 'r') as f:
        print("\nLog file contents:")
        print(f.read())

    # Clean up
    os.unlink(log_file)

# Using loggers with handlers
print("\nUsing loggers with handlers example:")
# Create a temporary log file
with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp:
    log_file = temp.name
    print(f"Logging to {log_file}")

    # Create a logger
    logger = getLogger("example_handlers")
    logger.setLevel("DEBUG")

    # Create handlers
    console_handler = StreamHandler(sys.stdout)
    console_handler.setLevel("WARNING")
    file_handler = FileHandler(log_file)
    file_handler.setLevel("DEBUG")

    # Create formatters
    console_formatter = Formatter("%(levelname)s: %(message)s")
    file_formatter = Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Add formatters to handlers
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log some messages
    logger.debug("This debug message should appear in the file but not console")
    logger.info("This info message should appear in the file but not console")
    logger.warning("This warning message should appear in both file and console")
    logger.error("This error message should appear in both file and console")
    logger.critical("This critical message should appear in both file and console")

    # Read the log file
    with open(log_file, 'r') as f:
        print("\nLog file contents:")
        print(f.read())

    # Clean up
    os.unlink(log_file)

print("\nAll examples completed successfully!")