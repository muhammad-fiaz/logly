import os
from colorama import Fore, Style, init
from datetime import datetime
import re  # Add this line for color code removal

init(autoreset=True)

class Logly:
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
        WHITE = Fore.WHITE  # Add this line

    DEFAULT_MAX_FILE_SIZE_MB = 100  # 100MB

    def __init__(self):
        self.logging_enabled = False
        self.log_to_file_enabled = True
        self.logged_messages = []
        self.default_file_path = None
        self.default_max_file_size = self.DEFAULT_MAX_FILE_SIZE_MB

    def start_logging(self):
        self.logging_enabled = True

    def stop_logging(self):
        self.logging_enabled = False

    def disable_file_logging(self):
        self.log_to_file_enabled = False

    def enable_file_logging(self):
        self.log_to_file_enabled = True

    def set_default_file_path(self, file_path):
        self.default_file_path = file_path

    def set_default_max_file_size(self, max_file_size):
        self.default_max_file_size = max_file_size

    def get_current_datetime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def remove_color_codes(self, text):
        # Remove ANSI color codes from text
        return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

    def _log(self, level, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        color = color or self.COLOR_MAP.get(level, self.COLOR.BLUE)
        log_message = f"[{self.get_current_datetime()}] {level}: {color}{key}: {value}{Style.RESET_ALL}"

        # Log to console
        print(log_message)

        if self.log_to_file_enabled and log_to_file:
            # Remove color codes before storing in the log file
            log_message_without_color = self.remove_color_codes(log_message)

            # Determine the file path and name
            if file_path is None:
                file_path = self.default_file_path or os.path.join(os.getcwd(), "log.txt")  # Default file path and name in the project root
            elif file_name:
                file_path = os.path.join(os.getcwd(), f"{file_name}.txt")  # Use the provided file name in the project root

            # Set the default max_file_size if not provided
            max_file_size = max_file_size or self.default_max_file_size

            # Convert max_file_size to bytes
            max_file_size_bytes = max_file_size * 1024 * 1024

            # Check if the file exists
            file_exists = os.path.exists(file_path)

            # Check if the file size limit is reached
            if max_file_size and file_exists and os.path.getsize(file_path) >= max_file_size_bytes:
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

    def log_function(self, level, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self._log(level, key, value, color, log_to_file, file_path, file_name, max_file_size)

    def info(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("INFO", key, value, color, log_to_file, file_path, file_name, max_file_size)

    def warn(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("WARNING", key, value, color, log_to_file, file_path, file_name, max_file_size)

    def error(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("ERROR", key, value, color, log_to_file, file_path, file_name, max_file_size)

    def debug(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("DEBUG", key, value, color, log_to_file, file_path, file_name, max_file_size)

    def critical(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("CRITICAL", key, value, color, log_to_file, file_path, file_name, max_file_size)

    def fatal(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("CRITICAL", key, value, color, log_to_file, file_path, file_name, max_file_size)

    def trace(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("DEBUG", key, value, color, log_to_file, file_path, file_name, max_file_size)

    def log(self, key, value, color=None, log_to_file=True, file_path=None, file_name=None, max_file_size=None):
        self.log_function("INFO", key, value, color, log_to_file, file_path, file_name, max_file_size)
