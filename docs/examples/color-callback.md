---
title: Color Callback Examples - Logly Python Logging
description: Examples of using color callback functions for custom styling and external library integration.
keywords: python, logging, color, callback, rich, ansi, styling, examples, logly
---

# Color Callback Examples

Logly supports custom color callback functions that allow you to integrate with external styling libraries like Rich, colorama, or termcolor, or implement completely custom coloring logic.

## Basic Color Callback

The color callback function receives `(level: str, text: str)` and returns the styled text as a string.

```python
from logly import logger

def simple_color_callback(level, text):
    """Simple ANSI color callback."""
    colors = {
        "DEBUG": "\033[34m",      # Blue
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m"    # Magenta
    }
    reset = "\033[0m"
    color_code = colors.get(level, "")
    return f"{color_code}{text}{reset}"

# Configure with color callback
logger.configure(
    level="DEBUG",
    color_callback=simple_color_callback
)
logger.add("console")

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

## Rich Library Integration

Integrate with the Rich library for advanced terminal styling:

```python
import sys
from logly import logger

# Requires: pip install rich
try:
    from rich.console import Console
    from rich.text import Text

    console = Console(file=sys.stdout, force_terminal=True)

    def rich_color_callback(level, text):
        """Rich-based color callback with advanced styling."""
        # Create Rich Text object
        rich_text = Text(text)

        # Apply styling based on level
        if level == "DEBUG":
            rich_text.stylize("dim blue")
        elif level == "INFO":
            rich_text.stylize("green")
        elif level == "WARNING":
            rich_text.stylize("yellow bold")
        elif level == "ERROR":
            rich_text.stylize("red bold")
        elif level == "CRITICAL":
            rich_text.stylize("red on white bold")

        # Convert to ANSI and return
        with console.capture() as capture:
            console.print(rich_text, end="")
        return capture.get()

    logger.configure(
        level="DEBUG",
        color_callback=rich_color_callback
    )
    logger.add("console")

    logger.debug("Debug message with Rich styling")
    logger.info("Info message with Rich styling")
    logger.warning("Warning with bold styling")
    logger.error("Error with bold red styling")
    logger.critical("Critical with white background")

except ImportError:
    print("Rich library not installed. Install with: pip install rich")
```

## Custom Emoji Styling

Add emojis and custom formatting:

```python
from logly import logger

def emoji_color_callback(level, text):
    """Color callback with emojis and custom formatting."""
    styles = {
        "DEBUG": ("🐛", "\033[34m"),
        "INFO": ("ℹ️", "\033[32m"),
        "WARNING": ("⚠️", "\033[33m"),
        "ERROR": ("❌", "\033[31m"),
        "CRITICAL": ("🚨", "\033[35m")
    }

    emoji, color_code = styles.get(level, ("", ""))
    reset = "\033[0m"

    # Add emoji prefix and color
    return f"{color_code}{emoji} {text}{reset}"

logger.configure(
    level="DEBUG",
    color_callback=emoji_color_callback
)
logger.add("console")

logger.debug("Debug with bug emoji")
logger.info("Info with info emoji")
logger.warning("Warning with warning emoji")
logger.error("Error with cross mark")
logger.critical("Critical with alarm")
```

## File Output with Callbacks

Color callbacks work with file output too:

```python
from logly import logger

def file_color_callback(level, text):
    """Callback that adds level prefixes for file output."""
    return f"[{level}] {text}"

logger.configure(
    level="INFO",
    color_callback=file_color_callback
)

# Console output (no coloring applied)
logger.add("console")

# File output (callback applied)
logger.add("app.log")

logger.info("This message goes to both console and file")
logger.error("Error message with custom file formatting")
```

## Conditional Styling

Apply different styling based on conditions:

```python
from logly import logger
import os

def conditional_color_callback(level, text):
    """Apply colors only in interactive terminals."""
    # Only color if stdout is a TTY
    if not sys.stdout.isatty():
        return text  # No coloring for non-interactive output

    colors = {
        "DEBUG": "\033[34m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m"
    }

    color_code = colors.get(level, "")
    reset = "\033[0m"
    return f"{color_code}{text}{reset}"

logger.configure(
    level="DEBUG",
    color_callback=conditional_color_callback
)
logger.add("console")

logger.info("Colors only in interactive terminals")
```

## Integration with colorama

Use colorama for cross-platform color support:

```python
from logly import logger

# Requires: pip install colorama
try:
    import colorama
    from colorama import Fore, Back, Style

    colorama.init()  # Initialize colorama

    def colorama_callback(level, text):
        """Color callback using colorama."""
        if level == "DEBUG":
            return f"{Fore.BLUE}{text}{Style.RESET_ALL}"
        elif level == "INFO":
            return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
        elif level == "WARNING":
            return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
        elif level == "ERROR":
            return f"{Fore.RED}{text}{Style.RESET_ALL}"
        elif level == "CRITICAL":
            return f"{Back.RED}{Fore.WHITE}{text}{Style.RESET_ALL}"
        else:
            return text

    logger.configure(
        level="DEBUG",
        color_callback=colorama_callback
    )
    logger.add("console")

    logger.debug("Debug with colorama")
    logger.info("Info with colorama")
    logger.warning("Warning with colorama")
    logger.error("Error with colorama")
    logger.critical("Critical with colorama background")

except ImportError:
    print("colorama not installed. Install with: pip install colorama")
```

## Callback with Exception Handling

Handle exceptions in color callbacks gracefully:

```python
from logly import logger

def safe_color_callback(level, text):
    """Color callback with exception handling."""
    try:
        colors = {
            "DEBUG": "\033[34m",
            "INFO": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
            "CRITICAL": "\033[35m"
        }
        color_code = colors.get(level, "")
        reset = "\033[0m"
        return f"{color_code}{text}{reset}"
    except Exception as e:
        # Fallback to unstyled text on any error
        print(f"Color callback error: {e}", file=sys.stderr)
        return text

logger.configure(
    level="DEBUG",
    color_callback=safe_color_callback
)
logger.add("console")

logger.info("Message with safe color callback")
```