#!/usr/bin/env python3
"""
Color Callback Examples

This example demonstrates how to use custom color callback functions with Logly
to integrate with external styling libraries or implement custom coloring logic.

Features demonstrated:
- Basic ANSI color callbacks
- Rich library integration
- Custom emoji styling
- File output with callbacks
- Exception handling in callbacks
- Conditional styling
"""

import sys
from logly import logger


def basic_ansi_callback():
    """Demonstrate basic ANSI color callback."""
    print("\n=== Basic ANSI Color Callback ===")

    def ansi_callback(level, text):
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

    logger.reset()
    logger.configure(level="DEBUG", color_callback=ansi_callback)
    logger.add("console")

    logger.debug("Debug message with blue color")
    logger.info("Info message with green color")
    logger.warning("Warning message with yellow color")
    logger.error("Error message with red color")
    logger.critical("Critical message with magenta color")


def rich_integration_callback():
    """Demonstrate Rich library integration."""
    print("\n=== Rich Library Integration ===")

    try:
        from rich.console import Console
        from rich.text import Text

        console = Console(file=sys.stdout, force_terminal=True)

        def rich_callback(level, text):
            """Rich-based color callback with advanced styling."""
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

        logger.reset()
        logger.configure(level="DEBUG", color_callback=rich_callback)
        logger.add("console")

        logger.debug("Debug with Rich dim blue styling")
        logger.info("Info with Rich green styling")
        logger.warning("Warning with Rich bold yellow styling")
        logger.error("Error with Rich bold red styling")
        logger.critical("Critical with Rich white background")

    except ImportError:
        print("Rich library not installed. Install with: pip install rich")


def emoji_styling_callback():
    """Demonstrate custom emoji styling."""
    print("\n=== Custom Emoji Styling ===")

    def emoji_callback(level, text):
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
        return f"{color_code}{emoji} {text}{reset}"

    logger.reset()
    logger.configure(level="DEBUG", color_callback=emoji_callback)
    logger.add("console")

    logger.debug("Debug with bug emoji")
    logger.info("Info with info emoji")
    logger.warning("Warning with warning emoji")
    logger.error("Error with cross mark emoji")
    logger.critical("Critical with alarm emoji")


def file_output_callback():
    """Demonstrate color callbacks with file output."""
    print("\n=== File Output with Callbacks ===")

    import tempfile
    import os

    def file_callback(level, text):
        """Callback that adds level prefixes for file output."""
        return f"[{level}] {text}"

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False) as f:
        log_file = f.name

    try:
        logger.reset()
        logger.configure(level="INFO", color_callback=file_callback)
        logger.add(log_file, async_write=False)  # Synchronous for immediate reading

        logger.info("This message goes to file with custom formatting")
        logger.error("Error message with custom file formatting")

        # Read and display file contents
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("File contents:")
            print(content)

    finally:
        # Clean up
        if os.path.exists(log_file):
            os.unlink(log_file)


def conditional_styling_callback():
    """Demonstrate conditional styling based on environment."""
    print("\n=== Conditional Styling ===")

    def conditional_callback(level, text):
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

    logger.reset()
    logger.configure(level="DEBUG", color_callback=conditional_callback)
    logger.add("console")

    print(f"Is TTY: {sys.stdout.isatty()}")
    logger.info("Colors only in interactive terminals")
    logger.warning("This warning will be colored if in TTY")


def exception_handling_callback():
    """Demonstrate exception handling in callbacks."""
    print("\n=== Exception Handling in Callbacks ===")

    def safe_callback(level, text):
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
        except (ValueError, TypeError) as e:
            # Fallback to unstyled text on any error
            print(f"Color callback error: {e}", file=sys.stderr)
            return text

    logger.reset()
    logger.configure(level="DEBUG", color_callback=safe_callback)
    logger.add("console")

    logger.info("Message with safe color callback")
    logger.error("Error message with safe callback")


def colorama_integration_callback():
    """Demonstrate colorama integration."""
    print("\n=== Colorama Integration ===")

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

        logger.reset()
        logger.configure(level="DEBUG", color_callback=colorama_callback)
        logger.add("console")

        logger.debug("Debug with colorama")
        logger.info("Info with colorama")
        logger.warning("Warning with colorama")
        logger.error("Error with colorama")
        logger.critical("Critical with colorama background")

    except ImportError:
        print("colorama not installed. Install with: pip install colorama")


def main():
    """Run all color callback examples."""
    print("Logly Color Callback Examples")
    print("=" * 40)

    basic_ansi_callback()
    rich_integration_callback()
    emoji_styling_callback()
    file_output_callback()
    conditional_styling_callback()
    exception_handling_callback()
    colorama_integration_callback()

    print("\n=== Examples Complete ===")
    print("All color callback examples have been demonstrated!")


if __name__ == "__main__":
    main()