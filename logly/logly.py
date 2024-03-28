# logly.py
# # Path: logly/logly.py
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
from colorama import Fore, Style, init
from datetime import datetime
import re

from logly.exception import FilePathNotFoundException, FileAccessError, FileCreationError

init(autoreset=True)


class Logly:
    """
    Logly: A simple logging utility.

    Attributes:
    - COLOR_MAP (dict): Mapping of log levels to color codes.
    - COLOR (class): Color constants for log messages.
    - DEFAULT_MAX_FILE_SIZE_MB (int): Default maximum file size in megabytes.

    Methods:
    - __init__: Initialize Logly instance.
    - start_logging: Enable logging.
    - stop_logging: Disable logging.
    - disable_file_logging: Disable logging to a file.
    - enable_file_logging: Enable logging to a file.
    - set_default_file_path: Set default file path.
    - set_default_max_file_size: Set default maximum file size.
    - get_current_datetime: Get current date and time as a formatted string.
    - remove_color_codes: Remove ANSI color codes from text.
    - _log: Internal method to log a message.
    - log_function: Log a message with exception handling.
    - info, warn, error, debug, critical, fatal, trace: Log messages with different levels.
    - log: Log a message with the INFO level.
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
        Initialize a Logly instance.

        Attributes:
        - logging_enabled (bool): Flag indicating whether logging is enabled.
        - log_to_file_enabled (bool): Flag indicating whether logging to a file is enabled.
        - logged_messages (list): List to store logged messages.
        - default_file_path (str): Default file path for logging.
        - default_max_file_size (int): Default maximum file size for logging.
        - show_time (bool): Flag indicating whether to include timestamps in log messages.
        """
        self.logging_enabled = False
        self.log_to_file_enabled = True
        self.logged_messages = []
        self.default_file_path = None
        self.default_max_file_size = self.DEFAULT_MAX_FILE_SIZE_MB
        self.show_time = show_time
        self.color_enabled = color_enabled if color_enabled is not None else self.DEFAULT_COLOR_ENABLED  # Use the provided value or default
        self.default_color_enabled = self.color_enabled  # Store the default color state

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
        Internal method to log a message.

        Parameters:
        - level (str): Log level (e.g., "INFO", "ERROR").
        - key (str): The key associated with the log message.
        - value (str): The value of the log message.
        - color (str): ANSI color code for the log message.
        - log_to_file (bool): Whether to log to a file.
        - file_path (str): File path for logging.
        - file_name (str): File name for logging.
        - max_file_size (int): Maximum file size for logging.
        - auto (bool): Whether to auto-delete log file data when the size limit is reached.
        - show_time (bool): Whether to include timestamps in the log message.
        - color_enabled (bool): Whether to enable color in the log message.

        """
        color_enabled = color_enabled if color_enabled is not None else self.color_enabled  # Use the provided value or default
        if show_time is None:
            show_time = self.show_time

        timestamp = "" if not show_time else self.get_current_datetime()

        if color_enabled and show_time:
            # Apply color if both color and time are enabled
            color = color or self.COLOR_MAP.get(level, self.COLOR.BLUE)
            log_message = f"[{timestamp}] {level}: {color}{key}: {value}{Style.RESET_ALL}"
        elif color_enabled and not show_time:
            # Apply color if only color is enabled
            color = color or self.COLOR_MAP.get(level, self.COLOR.BLUE)
            log_message = f" {level}: {color}{key}: {value}{Style.RESET_ALL}"
        elif not color_enabled and show_time:
            # Do not apply color, but include timestamp if only time is enabled
            log_message = f"[{timestamp}] {level}: {key}: {value}"
        else:
            # Do not apply color or timestamp if neither is enabled
            log_message = f"{level}: {key}: {value}"

        # Log to console
        print(log_message)

        if self.log_to_file_enabled and log_to_file:
            try:
                # Remove color codes before storing in the log file
                log_message_without_color = self.remove_color_codes(log_message)

                # Determine the file path and name
                if file_path is None:
                    file_path = self.default_file_path or os.path.join(os.getcwd(),
                                                                       "log.txt")  # Default file path and name in the project root
                elif file_name:
                    file_path = os.path.join(os.getcwd(),
                                             f"{file_name}.txt")  # Use the provided file name in the project root

                # Create the directories if they don't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Check if the file path exists
                if not os.path.exists(os.path.dirname(file_path)):
                    raise FilePathNotFoundException(
                        f"The specified file path does not exist: {os.path.dirname(file_path)}")

                # Set the default max_file_size if not provided
                max_file_size = max_file_size or self.default_max_file_size

                # Convert max_file_size to bytes
                max_file_size_bytes = max_file_size * 1024 * 1024

                # Check if the file exists
                file_exists = os.path.exists(file_path)

                # Check if the file size limit is reached
                if max_file_size and file_exists and os.path.getsize(file_path) >= max_file_size_bytes:
                    if auto:
                        # Auto-delete log file data by truncating the file
                        with open(file_path, 'w'):
                            pass
                    else:
                        # Find the next available file name with a number appended
                        file_base, file_ext = os.path.splitext(file_path)
                        count = 1
                        while os.path.exists(f"{file_base}_{count}{file_ext}"):
                            count += 1
                        file_path = f"{file_base}_{count}{file_ext}"

                # Open the file in appended mode, creating it if it doesn't exist
                with open(file_path, "a" if file_exists else "w") as log_file:
                    log_file.write(log_message_without_color + "\n")

                self.logged_messages.append(log_message + "\n")

            except (FileNotFoundError, PermissionError) as e:
                raise FileAccessError(f"Error accessing the log file: {e}")
            except Exception as e:
                raise FileCreationError(f"Error creating or writing to the log file: {e}")

    def log_function(self, level, key_or_value, value=None, color=None, log_to_file=True, file_path=None,
                     file_name=None, max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a message with exception handling.

        Parameters:
        - level (str): Log level (e.g., "INFO", "ERROR").
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        if value is None:
            # If only one parameter is provided, consider it as the value, and set key to None
            key = None
            value = key_or_value
        else:
            # If two parameters are provided, consider the first as the key and the second as the value
            key = key_or_value

        self._log(level, key, value, color, log_to_file, file_path, file_name, max_file_size, auto, show_time,
                  color_enabled)

    def info(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
             max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a message with the INFO level.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("INFO", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                          show_time, color_enabled)

    def warn(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
             max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a message with the WARNING level.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("WARNING", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                          show_time, color_enabled)

    def error(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a message with the ERROR level.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("ERROR", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                          show_time, color_enabled)

    def debug(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a message with the DEBUG level.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("DEBUG", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                          show_time, color_enabled)

    def critical(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
                 max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a critical message.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("CRITICAL", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size,
                          auto,
                          show_time, color_enabled)

    def fatal(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a fatal message.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("FATAL", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                          show_time, color_enabled)

    def trace(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
              max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log a trace message.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("TRACE", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                          show_time, color_enabled)

    def log(self, key_or_value, value=None, color=None, log_to_file=True, file_path=None, file_name=None,
            max_file_size=None, auto=True, show_time=None, color_enabled=None):
        """
        Log an info message.

        Parameters:
        - key_or_value (str): If a second parameter (value) is provided, this is considered as the key.
                             If no second parameter is provided, this is considered as the value, and the key is set to None.
        - value (str, optional): The value of the log message. Defaults to None.
        - color (str, optional): ANSI color code for the log message. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): File path for logging. Defaults to None.
        - file_name (str, optional): File name for logging. Defaults to None.
        - max_file_size (int, optional): Maximum file size for logging. Defaults to None.
        - auto (bool, optional): Whether to auto-delete log file data when the size limit is reached. Defaults to True.
        - show_time (bool, optional): Whether to include timestamps in the log message. Defaults to None.
        """
        self.log_function("LOG", key_or_value, value, color, log_to_file, file_path, file_name, max_file_size, auto,
                          show_time, color_enabled)
