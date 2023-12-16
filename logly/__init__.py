from colorama import Fore, Style, init

init(autoreset=True)

COLOR_MAP = {
    "DEBUG": Fore.BLUE,
    "INFO": Fore.CYAN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": f"{Fore.RED}{Style.BRIGHT}",
}

# Create a logger at the module level
logger = None  # No need for the logging module in this case

# Define color constants
class COLOR:
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    CRITICAL = f"{Fore.RED}{Style.BRIGHT}"
    WHITE = Fore.WHITE  # Add this line

# Flag to determine whether logging is enabled or not
logging_enabled = False
log_to_file_enabled = True  # New flag to control file logging
logged_messages = []


def start_logging():
    global logging_enabled
    logging_enabled = True


def stop_logging():
    global logging_enabled
    logging_enabled = False


def disable_file_logging():
    global log_to_file_enabled
    log_to_file_enabled = False


def enable_file_logging():
    global log_to_file_enabled
    log_to_file_enabled = True


def _log(level, key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    color = color or COLOR_MAP.get(level, COLOR.BLUE)
    log_message = f"{color}{key}: {value}"

    # Log to console
    print(log_message)

    if log_to_file_enabled and log_to_file:  # Check the flag for file logging and log_to_file parameter
        # Log to file
        with open("log.txt", "a") as log_file:
            log_file.write(log_message + "\n")

        logged_messages.append(log_message + "\n")


def log_function(level, key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    _log(level, key, value, color, log_to_file)


def info(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("INFO", key, value, color, log_to_file)


def warn(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("WARNING", key, value, color, log_to_file)


def error(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("ERROR", key, value, color, log_to_file)


def debug(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("DEBUG", key, value, color, log_to_file)


def critical(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("CRITICAL", key, value, color, log_to_file)


def fatal(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("CRITICAL", key, value, color, log_to_file)


def trace(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("DEBUG", key, value, color, log_to_file)


def log(key, value, color=None, log_to_file=True):  # Updated to include log_to_file parameter
    log_function("INFO", key, value, color, log_to_file)


# Example usage:
start_logging()
info("example_key1", "example_value")
stop_logging()
info("example_key2", "example_value", log_to_file=True)  # This will store in log.txt even after stopping general logging

start_logging()
info("example_key3", "example_value")  # This will store in log.txt by default
info("example_key4", "example_value", log_to_file=False)  # This will not store in log.txt
# Stop logging will not store in log.txt, and it will not display in the console
print(logged_messages)
