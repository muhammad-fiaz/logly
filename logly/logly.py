import os
from colorama import Fore, Style, init
from datetime import datetime
import re

from logly.exception import FilePathNotFoundException, FileAccessError, FileCreationError, LoglyException

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
    }

    # Define color constants
    class COLOR:
        BLUE = Fore.BLUE
        CYAN = Fore.CYAN
        YELLOW = Fore.YELLOW
        RED = Fore.RED
        CRITICAL = f"{Fore.RED}{Style.BRIGHT}"
        WHITE = Fore.WHITE

    DEFAULT_MAX_FILE_SIZE_MB = 100  # 100MB

    def __init__(self):
        """
        Initialize a Logly instance.

        Attributes:
        - logging_enabled (bool): Flag indicating whether logging is enabled.
        - log_to_file_enabled (bool): Flag indicating whether logging to a file is enabled.
        - logged_messages (list): List to store logged messages.
        - default_file_path (str): Default file path for logging.
        - default_max_file_size (int): Default maximum file size for logging.
        """
        self.logging_enabled = False
        self.log_to_file_enabled = True
        self.logged_messages = []
        self.default_file_path = None
        self.default_max_file_size = self.DEFAULT_MAX_FILE_SIZE_MB

    def start_logging(self):
        """
        Enable logging.
        """
        self.logging_enabled = True

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
        Remove ANSI color codes from text.

        Parameters:
        - text (str): Input text with color codes.

        Returns:
        - str: Text with color codes removed.
        """
        return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

    def _log(self, level, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
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
        """
        color = color or self.COLOR_MAP.get(level, self.COLOR.BLUE)
        log_message = f"[{self.get_current_datetime()}] {level}: {color}{key}: {value}{Style.RESET_ALL}"

        # Log to console
        print(log_message)

        if self.log_to_file_enabled and log_to_file:
            try:
                # Remove color codes before storing in the log file
                log_message_without_color = self.remove_color_codes(log_message)

                # Determine the file path and name
                if file_path is None:
                    file_path = self.default_file_path or os.path.join(os.getcwd(), "log.txt")  # Default file path and name in the project root
                elif file_name:
                    file_path = os.path.join(os.getcwd(), f"{file_name}.txt")  # Use the provided file name in the project root

                # Create the directories if they don't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Check if the file path exists
                if not os.path.exists(os.path.dirname(file_path)):
                    raise FilePathNotFoundException(f"The specified file path does not exist: {os.path.dirname(file_path)}")

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

                # Open the file in append mode, creating it if it doesn't exist
                with open(file_path, "a" if file_exists else "w") as log_file:
                    log_file.write(log_message_without_color + "\n")

                self.logged_messages.append(log_message + "\n")

            except (FileNotFoundError, PermissionError) as e:
                raise FileAccessError(f"Error accessing the log file: {e}")
            except Exception as e:
                raise FileCreationError(f"Error creating or writing to the log file: {e}")

    def log_function(self, level, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a message with exception handling.

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
        """
        try:
            self._log(level, key, value, color, log_to_file, file_path, file_name, max_file_size, auto)
        except LoglyException as e:
            print(f"LoglyException: {e}")

    def info(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a message with the INFO level.

        Parameters:
        - key (str): The key associated with the log message.
        - value (str): The value of the log message.
        - color (str): ANSI color code for the log message.
        - log_to_file (bool): Whether to log to a file.
        - file_path (str): File path for logging.
        - file_name (str): File name for logging.
        - max_file_size (int): Maximum file size for logging.
        - auto (bool): Whether to auto-delete log file data when the size limit is reached.
        """
        self.log_function("INFO", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)

    def warn(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a message with the WARNING level.

        Parameters:
        - key (str): The key associated with the log message.
        - value (str): The value of the log message.
        - color (str): ANSI color code for the log message.
        - log_to_file (bool): Whether to log to a file.
        - file_path (str): File path for logging.
        - file_name (str): File name for logging.
        - max_file_size (int): Maximum file size for logging.
        - auto (bool): Whether to auto-delete log file data when the size limit is reached.
        """
        self.log_function("WARNING", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)

    def error(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a message with the ERROR level.

        Parameters:
        - key (str): The key associated with the log message.
        - value (str): The value of the log message.
        - color (str): ANSI color code for the log message.
        - log_to_file (bool): Whether to log to a file.
        - file_path (str): File path for logging.
        - file_name (str): File name for logging.
        - max_file_size (int): Maximum file size for logging.
        - auto (bool): Whether to auto-delete log file data when the size limit is reached.
        """
        self.log_function("ERROR", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)

    def debug(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a message with the DEBUG level.

        Parameters:
        - key (str): The key associated with the log message.
        - value (str): The value of the log message.
        - color (str): ANSI color code for the log message.
        - log_to_file (bool): Whether to log to a file.
        - file_path (str): File path for logging.
        - file_name (str): File name for logging.
        - max_file_size (int): Maximum file size for logging.
        - auto (bool): Whether to auto-delete log file data when the size limit is reached.
        """
        self.log_function("DEBUG", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)

    def critical(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a critical message.

        Parameters:
        - key (str): The key for the log entry.
        - value (str): The value for the log entry.
        - color (str, optional): The color of the log entry. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): The path to the log file. Defaults to None.
        - file_name (str, optional): The name of the log file. Defaults to None.
        - max_file_size (int, optional): The maximum size of the log file in megabytes. Defaults to None.
        - auto (bool): Whether to auto-delete log file data when the size limit is reached.
        """
        self.log_function("CRITICAL", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)

    def fatal(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a fatal message.

        Parameters:
        - key (str): The key for the log entry.
        - value (str): The value for the log entry.
        - color (str, optional): The color of the log entry. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): The path to the log file. Defaults to None.
        - file_name (str, optional): The name of the log file. Defaults to None.
        - max_file_size (int, optional): The maximum size of the log file in megabytes. Defaults to None.
        - auto (bool): Whether to auto-delete log file data when the size limit is reached.
        """
        self.log_function("FATAL", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)

    def trace(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log a trace message.

        Parameters:
        - key (str): The key for the log entry.
        - value (str): The value for the log entry.
        - color (str, optional): The color of the log entry. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): The path to the log file. Defaults to None.
        - file_name (str, optional): The name of the log file. Defaults to None.
        - max_file_size (int, optional): The maximum size of the log file in megabytes. Defaults to None.
        - auto (bool, optional): Whether to automatically delete log file data if it reaches the file size limit
          and start storing again from scratch. Defaults to True.
        """
        self.log_function("TRACE", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)


    def log(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None, auto=True):
        """
        Log an info message.

        Parameters:
        - key (str): The key for the log entry.
        - value (str): The value for the log entry.
        - color (str, optional): The color of the log entry. Defaults to None.
        - log_to_file (bool, optional): Whether to log to a file. Defaults to True.
        - file_path (str, optional): The path to the log file. Defaults to None.
        - file_name (str, optional): The name of the log file. Defaults to None.
        - max_file_size (int, optional): The maximum size of the log file in megabytes. Defaults to None.
        - auto (bool, optional): Whether to automatically delete log file data if it reaches the file size limit
          and start storing again from scratch. Defaults to True.
        """
        self.log_function("LOG", key, value, color, log_to_file, file_path, file_name, max_file_size, auto)
