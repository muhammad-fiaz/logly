"""
Logly: A ready-to-go logging utility.

Copyright (c) 2025 Muhammad Fiaz

This file is part of Logly.

Logly is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published by
the Open Source Initiative.

You should have received a copy of the MIT License
along with Logly. If not, see <https://opensource.org/licenses/MIT>.
"""

import os
import logging
from colorama import Fore, Style, init
from datetime import datetime
import re
from typing import Optional
from pydantic import BaseModel, Field
from rich.console import Console

from logly import get_version, __version__, FilePathNotFoundException, FileAccessError, FileCreationError

init(autoreset=True)
console = Console()

class LoglyConfig(BaseModel):
    show_time: bool = Field(
        default=True, description="Whether to include timestamps in log messages"
    )
    color_enabled: bool = Field(default=True, description="Whether to enable colored output")
    logging_enabled: bool = Field(default=True, description="Whether logging is enabled")
    log_to_file_enabled: bool = Field(
        default=False, description="Whether to enable logging to a file"
    )
    default_file_path: Optional[str] = Field(default=None, description="Default path for log files")
    default_max_file_size: int = Field(
        default=100, description="Default maximum file size for log files (in MB)"
    )
    custom_format: str = Field(
        default="{timestamp} - {level}: {message}", description="Custom format for log messages"
    )
    display: bool = Field(default=True, description="Whether to display logs in the console")

class LogMessageConfig(BaseModel):
    level: str = Field(description="The log level (e.g., 'INFO', 'WARNING', 'ERROR', etc.)")
    key_or_value: str = Field(description="The key or message to log")
    value: Optional[str] = Field(default=None, description="Additional message value for the log")
    color: Optional[str] = Field(default=None, description="Color to use for the log message")
    log_to_file: bool = Field(default=True, description="Whether to log to a file")
    file_path: Optional[str] = Field(
        default=None, description="Path where the log file will be stored"
    )
    file_name: Optional[str] = Field(default=None, description="Custom log file name")
    max_file_size: Optional[int] = Field(
        default=None, description="Maximum file size before rolling over (in MB)"
    )
    auto: bool = Field(default=True, description="Automatically handle file rollover")
    show_time: Optional[bool] = Field(
        default=None, description="Whether to include timestamp in the log message"
    )
    color_enabled: Optional[bool] = Field(
        default=None, description="Whether to enable colored output"
    )
    custom_format: Optional[str] = Field(
        default=None, description="Custom format for the log message"
    )

class Logly:
    """
    Logly: A ready-to-go logging utility.

    This class provides methods to log messages with different levels of severity,
    including INFO, WARNING, ERROR, DEBUG, CRITICAL, FATAL, TRACE, and custom LOG levels.
    It supports colored output and logging to files with automatic file rollover.

    Attributes:
    -----------
    COLOR_MAP : dict
        A mapping of log levels to their respective colors.
    DEFAULT_MAX_FILE_SIZE_MB : int
        The default maximum file size for log files in megabytes.
    DEFAULT_COLOR_ENABLED : bool
        The default setting for enabling colored output.
    """

    COLOR_MAP = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.CYAN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": f"{Fore.RED}{Style.BRIGHT}",
        "FATAL": f"{Fore.RED}{Style.BRIGHT}",
        "TRACE": Fore.BLUE,
        "LOG": Fore.GREEN,  # Added "LOG" level color
    }

    # Define color constants
    class COLOR:
        """
        A class to define color constants for log messages.
        """

        BLUE = Fore.BLUE
        CYAN = Fore.CYAN
        YELLOW = Fore.YELLOW
        RED = Fore.RED
        CRITICAL = f"{Fore.RED}{Style.BRIGHT}"
        WHITE = Fore.WHITE
        GREEN = Fore.GREEN  # Added "LOG" level color

    DEFAULT_MAX_FILE_SIZE_MB = 100  # 100MB
    DEFAULT_COLOR_ENABLED = True  # Add a class attribute for controlling default Colorama behavior

    def __init__(self, config: LoglyConfig = None):
        """
        Initialize the Logly instance.

        This constructor sets up the initial state of the Logly logger, including
        logging preferences, file paths, and color settings.

        Parameters:
        -----------
        config : LoglyConfig
            Configuration parameters for Logly.

        Attributes:
        -----------
        logging_enabled : bool
            Flag to enable/disable logging.
        log_to_file_enabled : bool
            Flag to enable/disable logging to a file.
        display_logs : bool
            Flag to enable/disable displaying logs in the console.
        logged_messages : list
            List to store logged messages.
        default_file_path : str or None
            Default path for log files.
        default_max_file_size : int
            Default maximum file size for log files.
        show_time : bool
            Whether to show timestamps in log messages.
        color_enabled : bool
            Whether color output is enabled.
        default_color_enabled : bool
            Default setting for color output.
        custom_format : str
            Default custom format for log messages.
        logger : logging.Logger
            Python's built-in logger instance.

        Returns:
        --------
        None
        """
        if config is None:
            config = LoglyConfig()

        self.logging_enabled = config.logging_enabled
        self.log_to_file_enabled = config.log_to_file_enabled
        self.display_logs = config.display
        self.logged_messages = []
        self.default_file_path = config.default_file_path
        self.default_max_file_size = config.default_max_file_size
        self.show_time = config.show_time
        self.color_enabled = (
            config.color_enabled if config.color_enabled is not None else self.DEFAULT_COLOR_ENABLED
        )  # Use the provided value or default
        self.default_color_enabled = self.color_enabled  # Store the default color state
        self.custom_format = config.custom_format

        get_version(__version__)

        # Disable default logging setup for this logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Ensure there are no default handlers that duplicate the log messages
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(message)s"
            )  # Format only the message, no additional time or level
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def start_logging(self, display=True):
        """
        Enable logging.

        Parameters:
        - display (bool): Whether to display logs in the console. Default is True.
        """
        self.logging_enabled = True
        self.display_logs = display
        self.color_enabled = self.default_color_enabled  # Use the stored default color state
        self.logger.disabled = not display

    def stop_logging(self, display=True):
        """
        Disable logging to a file.

        Parameters:
        - display (bool): Whether to display logs in the console. Default is True.
        """
        self.log_to_file_enabled = False
        self.display_logs = display
        self.logger.disabled = not display

    def disable_file_logging(self):
        """
        Disable logging to a file.
        """
        self.log_to_file_enabled = False

    def enable_file_logging(self):
        """
        Enable logging to a file.
        """
        self.log_to_file_enabled = True

    def set_default_file_path(self, file_path):
        """
        Set the default file path.

        Parameters:
        - file_path (str): The default file path.
        """
        self.default_file_path = file_path

    def set_default_max_file_size(self, max_file_size):
        """
        Set the default maximum file size.

        Parameters:
        - max_file_size (int): The default maximum file size.
        """
        self.default_max_file_size = max_file_size

    def update_settings(self, config: LoglyConfig):
        """
        Update the logger settings.

        Parameters:
        - config (LoglyConfig): New configuration parameters for Logly.
        """
        self.logging_enabled = config.logging_enabled
        self.log_to_file_enabled = config.log_to_file_enabled
        self.default_file_path = config.default_file_path
        self.default_max_file_size = config.default_max_file_size
        self.show_time = config.show_time
        self.color_enabled = (
            config.color_enabled if config.color_enabled is not None else self.DEFAULT_COLOR_ENABLED
        )
        self.default_color_enabled = self.color_enabled
        self.custom_format = config.custom_format
        self.display_logs = config.display

    def get_current_datetime(self):
        """
        Get the current date and time as a formatted string.

        Returns:
        - str: Formatted date and time string.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def remove_color_codes(self, text):
        """
        Remove ANSI color codes from a text.

        Parameters:
        - text (str): Input text with color codes.

        Returns:
        - str: Text with color codes removed.
        """
        return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)

    def _log(self, config: LogMessageConfig):
        """
        Internal method to handle logging operations.

        This method processes the log message, applies formatting, and handles both console and file logging.

        Args:
            config (LogMessageConfig): Configuration parameters for the log message.

        Returns:
            str: The formatted log message with color codes removed.

        Raises:
            FilePathNotFoundException: If the specified file path does not exist.
            FileAccessError: If there's an error accessing the log file.
            FileCreationError: If there's an error creating or writing to the log file.
        """
        color_enabled = (
            config.color_enabled if config.color_enabled is not None else self.color_enabled
        )
        show_time = config.show_time if config.show_time is not None else self.show_time

        timestamp = "" if not show_time else self.get_current_datetime()
        key = config.key_or_value if config.key_or_value is not None else ""
        message = f"{key}" if config.value is None else f"{key}: {config.value}"
        color = config.color or self.COLOR_MAP.get(config.level, self.COLOR.BLUE)

        # Use custom format if provided, otherwise use default format
        custom_format = config.custom_format if config.custom_format else self.custom_format
        log_message = custom_format.format(timestamp=timestamp, level=config.level, message=message)

        if color_enabled:
            log_message = f"{color}{log_message}{Style.RESET_ALL}"

        # Log to console using logging library
        if self.display_logs:
            if config.level == "INFO":
                self.logger.info(log_message)
            elif config.level == "WARNING":
                self.logger.warning(log_message)
            elif config.level == "ERROR":
                self.logger.error(log_message)
            elif config.level == "DEBUG":
                self.logger.debug(log_message)
            elif config.level == "CRITICAL":
                self.logger.critical(log_message)
            elif config.level == "FATAL":
                self.logger.fatal(log_message)
            elif config.level == "TRACE":
                self.logger.log(logging.NOTSET, log_message)
            else:
                self.logger.log(logging.NOTSET, log_message)

        if self.log_to_file_enabled and config.log_to_file:
            try:
                log_message_without_color = self.remove_color_codes(log_message)
                # Encode emojis properly
                log_message_without_color = log_message_without_color.encode(
                    "utf-8", "replace"
                ).decode()

                file_path = (
                    config.file_path
                    or self.default_file_path
                    or os.path.join(os.getcwd(), "log.txt")
                )
                if config.file_name:
                    file_path = os.path.join(os.getcwd(), f"{config.file_name}.txt")

                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                if not os.path.exists(os.path.dirname(file_path)):
                    raise FilePathNotFoundException(
                        f"The specified file path does not exist: {os.path.dirname(file_path)}"
                    )

                max_file_size = config.max_file_size or self.default_max_file_size
                max_file_size_bytes = max_file_size * 1024 * 1024

                file_exists = os.path.exists(file_path)

                if (
                    max_file_size
                    and file_exists
                    and os.path.getsize(file_path) >= max_file_size_bytes
                ):
                    if config.auto:
                        with open(file_path, "w"):
                            pass
                    else:
                        file_base, file_ext = os.path.splitext(file_path)
                        count = 1
                        while os.path.exists(f"{file_base}_{count}{file_ext}"):
                            count += 1
                        file_path = f"{file_base}_{count}{file_ext}"

                with open(file_path, "a" if file_exists else "w") as log_file:
                    log_file.write(log_message_without_color + "\n")

                self.logged_messages.append(log_message + "\n")

            except (FileNotFoundError, PermissionError) as e:
                raise FileAccessError(f"Error accessing the log file: {e}")
            except Exception as e:
                raise FileCreationError(f"Error creating or writing to the log file: {e}")

        return self.remove_color_codes(log_message)  # Return log message without color formatting

    def log_function(self, config: LogMessageConfig):
        """
        General logging function that handles different log levels (INFO, WARNING, ERROR, etc.).

        Args:
            config (LogMessageConfig): Configuration parameters for the log message.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        return self._log(config)

    def info(self, key_or_value, value=None, **kwargs):
        """
        Logs an informational message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(level="INFO", key_or_value=key_or_value, value=value, **kwargs)
        return self.log_function(config)

    def warn(self, key_or_value, value=None, **kwargs):
        """
        Logs a warning message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(level="WARNING", key_or_value=key_or_value, value=value, **kwargs)
        return self.log_function(config)

    def error(self, key_or_value, value=None, **kwargs):
        """
        Logs an error message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(level="ERROR", key_or_value=key_or_value, value=value, **kwargs)
        return self.log_function(config)

    def debug(self, key_or_value, value=None, **kwargs):
        """
        Logs a debug message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(level="DEBUG", key_or_value=key_or_value, value=value, **kwargs)
        return self.log_function(config)

    def critical(self, key_or_value, value=None, **kwargs):
        """
        Logs a critical message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(
            level="CRITICAL", key_or_value=key_or_value, value=value, **kwargs
        )
        return self.log_function(config)

    def fatal(self, key_or_value, value=None, **kwargs):
        """
        Logs a fatal error message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(level="FATAL", key_or_value=key_or_value, value=value, **kwargs)
        return self.log_function(config)

    def trace(self, key_or_value, value=None, **kwargs):
        """
        Logs a trace message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(level="TRACE", key_or_value=key_or_value, value=value, **kwargs)
        return self.log_function(config)

    def log(self, key_or_value, value=None, **kwargs):
        """
        Logs a general message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        config = LogMessageConfig(level="LOG", key_or_value=key_or_value, value=value, **kwargs)
        return self.log_function(config)
