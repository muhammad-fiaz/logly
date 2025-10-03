#!/usr/bin/env python3
"""
Format Placeholders Example

This example demonstrates Logly's template string formatting with placeholders,
including filename and line number information.

Features demonstrated:
- Custom format strings with placeholders
- Filename and line number placeholders
- Case-insensitive placeholders
- Extra field placeholders
- Template control over output
"""

from logly import logger


def helper_function():
    """A helper function to demonstrate function name in logs."""
    logger.info("Called from helper function", action="process_data")


def main():
    # Reset logger to clean state
    logger.reset()
    
    # Configure logger with filename and line number enabled
    logger.configure(
        level="INFO",
        color=True,
        show_filename=True,
        show_lineno=True
    )

    # Example 1: Basic format with time, level, and message
    logger.add("console", format="{time} [{level}] {message}")
    logger.info("Application started")
    logger.warning("This is a warning message")

    # Example 2: Format with filename and line number
    logger.add("console", format="{level}: {filename}:{lineno} - {message}")
    logger.info("Debug message with location info")
    logger.error("Error with location info")

    # Example 3: Detailed format with module and function
    logger.add("console", format="[{level}] {time} | {module}:{function}:{lineno} | {message}")
    logger.info("Detailed logging format")

    # Example 4: Format with extra fields
    logger.add("console", format="{time} | {level} | {message} | user={user} | action={action}")
    logger.info("User action performed", user="alice", action="login", session_id="abc123")

    # Example 5: Using {extra} to include all remaining fields
    logger.add("console", format="[{level}] {message} | {extra}")
    logger.info("All extra fields included", user="bob", action="logout", duration="5.2s")

    # Call a function to demonstrate function name in logs
    helper_function()

    # Example 6: Case-insensitive placeholders
    logger.add("console", format="{TIME} | {LEVEL} | {MESSAGE} | {FILENAME}:{LINENO}")
    logger.info("Case insensitive placeholders work too")

    # Clean up
    logger.complete()


if __name__ == "__main__":
    main()