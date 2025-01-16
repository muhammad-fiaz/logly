# logly.py
# Path: logly/logly.py
"""
Logly: A ready to go logging utility.

Copyright (c) 2023 Muhammad Fiaz

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

from logly.exception import FilePathNotFoundException, FileAccessError, FileCreationError

init(autoreset=True)

class Logly:
    """
    Logly: A ready-to-go logging utility.

    This class provides methods to log messages with different levels of severity,
    including INFO, WARNING, ERROR, DEBUG, CRITICAL, and custom LOG levels. It supports
    colored output and logging to files with automatic file rollover.

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
        "LOG": Fore.GREEN  # Added "LOG" level color
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

    def __init__(self, show_time=True, color_enabled=None):
        """
          Initialize the Logly instance.

          This constructor sets up the initial state of the Logly logger, including
          logging preferences, file paths, and color settings.

          Parameters:
          -----------
          show_time : bool, optional
              Whether to include timestamps in log messages (default is True).
          color_enabled : bool, optional
              Whether to enable colored output. If None, uses the default color setting.

          Attributes:
          -----------
          logging_enabled : bool
              Flag to enable/disable logging.
          log_to_file_enabled : bool
              Flag to enable/disable logging to a file.
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
          logger : logging.Logger
              Python's built-in logger instance.

          Returns:
          --------
          None
          """
        self.logging_enabled = False
        self.log_to_file_enabled = True
        self.logged_messages = []
        self.default_file_path = None
        self.default_max_file_size = self.DEFAULT_MAX_FILE_SIZE_MB
        self.show_time = show_time
        self.color_enabled = color_enabled if color_enabled is not None else self.DEFAULT_COLOR_ENABLED  # Use the provided value or default
        self.default_color_enabled = self.color_enabled  # Store the default color state

        # Disable default logging setup for this logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Ensure there are no default handlers that duplicate the log messages
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')  # Format only the message, no additional time or level
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def start_logging(self):
        """
        Enable logging.
        """
        self.logging_enabled = True
        self.color_enabled = self.default_color_enabled  # Use the stored default color state

    def stop_logging(self):
        """
        Disable logging.
        """
        self.logging_enabled = False

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
        return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

    def _log(self, level, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None,
             auto=True, show_time=None, color_enabled=None):
        """
        Internal method to handle logging operations.

        This method processes the log message, applies formatting, and handles both console and file logging.

        Args:
            level (str): The log level (e.g., "INFO", "WARNING", "ERROR", etc.).
            key (str): The key for the log message. If None, it's treated as an empty string.
            value (str): The main content of the log message.
            color (str, optional): The color to use for the log message. If None, a default color is used based on the log level.
            log_to_file (bool, optional): Whether to log the message to a file. Defaults to True.
            file_path (str, optional): The path where the log file will be stored. If None, uses the default path.
            file_name (str, optional): The name of the log file. If provided, it overrides the file_path.
            max_file_size (int, optional): The maximum size of the log file in MB before rolling over.
            auto (bool, optional): If True, automatically handles file rollover when max_file_size is reached. Defaults to True.
            show_time (bool, optional): Whether to include a timestamp in the log message. If None, uses the instance's default.
            color_enabled (bool, optional): Whether to enable colored output. If None, uses the instance's default.

        Returns:
            str: The formatted log message with color codes removed.

        Raises:
            FilePathNotFoundException: If the specified file path does not exist.
            FileAccessError: If there's an error accessing the log file.
            FileCreationError: If there's an error creating or writing to the log file.
        """
        color_enabled = color_enabled if color_enabled is not None else self.color_enabled
        if show_time is None:
            show_time = self.show_time

        timestamp = "" if not show_time else self.get_current_datetime()
        if key is None:
            key = "" # Set key to empty string if it is None
        else:
            key = f"{key}:"
        if color_enabled and show_time:
            color = color or self.COLOR_MAP.get(level, self.COLOR.BLUE)
            log_message = f"{color}[{timestamp}] - {level}: {key} {value}{Style.RESET_ALL}"
        elif color_enabled and not show_time:
            color = color or self.COLOR_MAP.get(level, self.COLOR.BLUE)
            log_message = f"{color} {level}: {key} {value}{Style.RESET_ALL}"
        elif not color_enabled and show_time:
            log_message = f"[{timestamp}] - {level}: {key} {value}"
        else:
            log_message = f"{level}: {key} {value}"

        # Log to console using logging library
        if level == "INFO":
            self.logger.info(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        elif level == "DEBUG":
            self.logger.debug(log_message)
        elif level == "CRITICAL":
            self.logger.critical(log_message)
        else:
            self.logger.log(logging.NOTSET, log_message)

        if self.log_to_file_enabled and log_to_file:
            try:
                log_message_without_color = self.remove_color_codes(log_message)

                if file_path is None:
                    file_path = self.default_file_path or os.path.join(os.getcwd(), "log.txt")
                elif file_name:
                    file_path = os.path.join(os.getcwd(), f"{file_name}.txt")

                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                if not os.path.exists(os.path.dirname(file_path)):
                    raise FilePathNotFoundException(f"The specified file path does not exist: {os.path.dirname(file_path)}")

                max_file_size = max_file_size or self.default_max_file_size
                max_file_size_bytes = max_file_size * 1024 * 1024

                file_exists = os.path.exists(file_path)

                if max_file_size and file_exists and os.path.getsize(file_path) >= max_file_size_bytes:
                    if auto:
                        with open(file_path, 'w'):
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

    def log_function(self, level, key_or_value, value=None, color=None, log_to_file=True, file_path=None,
                     file_name=None, max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
            General logging function that handles different log levels (INFO, WARNING, ERROR, etc.).

            Args:
                level (str): The log level (e.g., "INFO", "WARNING", "ERROR", etc.).
                key_or_value (str): The key or message to log.
                value (str, optional): Additional message value for the log.
                color (str, optional): Color to use for the log message.
                log_to_file (bool, optional): Whether to log to a file (default is True).
                file_path (str, optional): Path where the log file will be stored (default is None).
                file_name (str, optional): Custom log file name (default is None).
                max_file_size (int, optional): Maximum file size before rolling over (in MB).
                auto (bool, optional): Automatically handle file rollover (default is True).
                show_time (bool, optional): Whether to include timestamp in the log message (default is None).
                color_enabled (bool, optional): Whether to enable colored output (default is None).

            Returns:
                str: The log message with or without color, depending on the configuration.
            """
        if value is None:
            key = None
            value = key_or_value
        else:
            key = key_or_value

        return self._log(level, key, value, color, log_to_file, file_path, file_name, max_file_size, auto, show_time,
                         color_enabled)

    def info(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
             max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
           Logs an informational message.

           Args:
               key_or_value (str): The key or message to log.
               value (str, optional): Additional message value for the log.
               color (str, optional): Color to use for the log message.
               log_to_file (bool, optional): Whether to log to a file (default is True).
               file_path (str, optional): Path where the log file will be stored (default is None).
               file_name (str, optional): Custom log file name (default is None).
               max_file_size (int, optional): Maximum file size before rolling over (in MB).
               auto (bool, optional): Automatically handle file rollover (default is True).
               show_time (bool, optional): Whether to include timestamp in the log message (default is None).
               color_enabled (bool, optional): Whether to enable colored output (default is None).

           Returns:
               str: The log message with or without color, depending on the configuration.
           """
        return self.log_function("INFO", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                                 show_time, color_enabled)

    def warn(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
             max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Logs a warning message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.
            color (str, optional): Color to use for the log message.
            log_to_file (bool, optional): Whether to log to a file (default is True).
            file_path (str, optional): Path where the log file will be stored (default is None).
            file_name (str, optional): Custom log file name (default is None).
            max_file_size (int, optional): Maximum file size before rolling over (in MB).
            auto (bool, optional): Automatically handle file rollover (default is True).
            show_time (bool, optional): Whether to include timestamp in the log message (default is None).
            color_enabled (bool, optional): Whether to enable colored output (default is None).

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        return self.log_function("WARNING", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                                 show_time, color_enabled)

    def error(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Logs an error message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.
            color (str, optional): Color to use for the log message.
            log_to_file (bool, optional): Whether to log to a file (default is True).
            file_path (str, optional): Path where the log file will be stored (default is None).
            file_name (str, optional): Custom log file name (default is None).
            max_file_size (int, optional): Maximum file size before rolling over (in MB).
            auto (bool, optional): Automatically handle file rollover (default is True).
            show_time (bool, optional): Whether to include timestamp in the log message (default is None).
            color_enabled (bool, optional): Whether to enable colored output (default is None).

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        return self.log_function("ERROR", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                                 show_time, color_enabled)

    def debug(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Logs a debug message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.
            color (str, optional): Color to use for the log message.
            log_to_file (bool, optional): Whether to log to a file (default is True).
            file_path (str, optional): Path where the log file will be stored (default is None).
            file_name (str, optional): Custom log file name (default is None).
            max_file_size (int, optional): Maximum file size before rolling over (in MB).
            auto (bool, optional): Automatically handle file rollover (default is True).
            show_time (bool, optional): Whether to include timestamp in the log message (default is None).
            color_enabled (bool, optional): Whether to enable colored output (default is None).

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        return self.log_function("DEBUG", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                                 show_time, color_enabled)

    def critical(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
                 max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
             Logs a critical message.

             Args:
                 key_or_value (str): The key or message to log.
                 value (str, optional): Additional message value for the log.
                 color (str, optional): Color to use for the log message.
                 log_to_file (bool, optional): Whether to log to a file (default is True).
                 file_path (str, optional): Path where the log file will be stored (default is None).
                 file_name (str, optional): Custom log file name (default is None).
                 max_file_size (int, optional): Maximum file size before rolling over (in MB).
                 auto (bool, optional): Automatically handle file rollover (default is True).
                 show_time (bool, optional): Whether to include timestamp in the log message (default is None).
                 color_enabled (bool, optional): Whether to enable colored output (default is None).

             Returns:
                 str: The log message with or without color, depending on the configuration.
             """
        return self.log_function("CRITICAL", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size,
                                 auto, show_time, color_enabled)

    def fatal(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Logs a fatal error message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.
            color (str, optional): Color to use for the log message.
            log_to_file (bool, optional): Whether to log to a file (default is True).
            file_path (str, optional): Path where the log file will be stored (default is None).
            file_name (str, optional): Custom log file name (default is None).
            max_file_size (int, optional): Maximum file size before rolling over (in MB).
            auto (bool, optional): Automatically handle file rollover (default is True).
            show_time (bool, optional): Whether to include timestamp in the log message (default is None).
            color_enabled (bool, optional): Whether to enable colored output (default is None).

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        return self.log_function("FATAL", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                                 show_time, color_enabled)

    def trace(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Logs a trace message.

        Args:
            key_or_value (str): The key or message to log.
            value (str, optional): Additional message value for the log.
            color (str, optional): Color to use for the log message.
            log_to_file (bool, optional): Whether to log to a file (default is True).
            file_path (str, optional): Path where the log file will be stored (default is None).
            file_name (str, optional): Custom log file name (default is None).
            max_file_size (int, optional): Maximum file size before rolling over (in MB).
            auto (bool, optional): Automatically handle file rollover (default is True).
            show_time (bool, optional): Whether to include timestamp in the log message (default is None).
            color_enabled (bool, optional): Whether to enable colored output (default is None).

        Returns:
            str: The log message with or without color, depending on the configuration.
        """
        return self.log_function("TRACE", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                                 show_time, color_enabled)

    def log(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
            max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
               Logs a general message.

               Args:
                   key_or_value (str): The key or message to log.
                   value (str, optional): Additional message value for the log.
                   color (str, optional): Color to use for the log message.
                   log_to_file (bool, optional): Whether to log to a file (default is True).
                   file_path (str, optional): Path where the log file will be stored (default is None).
                   file_name (str, optional): Custom log file name (default is None).
                   max_file_size (int, optional): Maximum file size before rolling over (in MB).
                   auto (bool, optional): Automatically handle file rollover (default is True).
                   show_time (bool, optional): Whether to include timestamp in the log message (default is None).
                   color_enabled (bool, optional): Whether to enable colored output (default is None).

               Returns:
                   str: The log message with or without color, depending on the configuration.
               """
        return self.log_function("LOG", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                                 show_time, color_enabled)
