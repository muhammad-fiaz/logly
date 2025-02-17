<div align="center">

<img src="assets/logly_logo.png" alt="Sample Image">


# Logly

[![Run Tests](https://github.com/muhammad-fiaz/logly/actions/workflows/python-package.yaml/badge.svg)](https://github.com/muhammad-fiaz/logly/actions/workflows/python-package.yaml)
[![PyPI Version](https://img.shields.io/pypi/v/logly)](https://pypi.org/project/logly/)
[![Python Versions](https://img.shields.io/pypi/pyversions/logly)](https://pypi.org/project/logly/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/logly)](https://pypi.org/project/logly/)
[![Last Commit](https://img.shields.io/github/last-commit/muhammad-fiaz/logly)](https://github.com/muhammad-fiaz/logly)
[![GitHub Issues](https://img.shields.io/github/issues/muhammad-fiaz/logly)](https://github.com/muhammad-fiaz/logly/issues)
[![GitHub Stars](https://img.shields.io/github/stars/muhammad-fiaz/logly)](https://github.com/muhammad-fiaz/logly/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/muhammad-fiaz/logly)](https://github.com/muhammad-fiaz/logly/network)
[![Maintainer](https://img.shields.io/badge/Maintainer-muhammad--fiaz-blue)](https://github.com/muhammad-fiaz)
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor%20on%20GitHub-Become%20a%20Sponsor-blue)](https://github.com/sponsors/muhammad-fiaz)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Stability](https://img.shields.io/badge/Stability-Stable-green)](https://github.com/muhammad-fiaz/logly)
[![Follow me on GitHub](https://img.shields.io/github/followers/muhammad-fiaz?label=Follow&style=social)](https://github.com/muhammad-fiaz)

[![Join My Discord](https://img.shields.io/badge/Join%20My%20Discord-7289DA?style=for-the-badge&logo=discord)](https://discord.gg/cFnFdeFw)
[![Sponsor muhammad-fiaz](https://img.shields.io/badge/Sponsor-muhammad_fiaz-ff69b4?style=for-the-badge&logo=github)](https://github.com/sponsors/muhammad-fiaz)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F1F6MME1W)

</div>

Tired of writing custom logging code for your Python applications? 

Logly is a ready to go logging utility that provides an easy way to log messages with different levels, colors, and many custom options. It is designed to be flexible, allowing you to customize the log messages based on your application's needs. Logly supports logging to both the console and a file, and it comes with built-in color-coded log levels for better visibility.

if you like this project, make sure to star 🌟 it in the [repository](https://github.com/muhammad-fiaz/logly/) and if you want to contribute make sure to fork this repository❤✨.

## Table of Contents

1. [Introduction](#)
2. [Installation](#installation)
3. [Features](#features)
4. [Usage](#usage)
    - [Getting Started](#getting-started)
5. [Set Default Path](#set-default-path)
6. [Color Options](#color-options)
    - [Default Color Options](#default-color-options)
    - [Custom Color Options](#custom-color-options)
7. [Tips & Tricks](#tips--tricks)
8. [Contributing](#contributing)
9. [Code of Conduct](#code-of-conduct)
10. [License](#license)
11. [Support the Project](#support-the-project)
    - [Become a Sponsor on GitHub](#become-a-sponsor-on-github)
    - [Support via Ko-fi](#support-via-ko-fi)
12. [Happy Coding](#happy-coding)


## Features

- Support for multiple log levels: INFO, WARNING, ERROR, DEBUG, CRITICAL, FATAL, TRACE, and custom LOG levels.
- Colored output for console logs.
- Customizable log message formats.
- Logging to files with automatic file rollover.
- Control over console display and file logging.
- Easy configuration and usage.
- Open Source: Logly is an open-source project, and we welcome contributions from the community.
- Community Support: Join a community of developers using Logly for their logging needs.
- many more features!

## Getting Started

## Installation

To install the stable version of `logly`, use:
```bash
pip install logly
```

If you want to install the latest development version directly from GitHub, you can run:
```bash
pip install git+https://github.com/muhammad-fiaz/logly.git
```

## Usage
Once installed, you can use `logly` in your Python project for logging. Here is a basic example of how to set it up and use it:

```python
from logly import Logly, LoglyConfig
```

### Create a Logly Instance

You can create a Logly instance with default settings or customize the configuration:

#### Default Settings

```python
logly = Logly()
```

#### Custom Configuration

```python
config = LoglyConfig(display=True, log_to_file_enabled=True, default_file_path="logs/app.log")
logly = Logly(config=config)
```

### Start Logging

Enable logging to store logs in a text file and optionally display them in the console:

```python
# Start logging and display logs in the console
logly.start_logging()

# Start logging but do not display logs in the console
logly.start_logging(display=False)
```

### Stop Logging

Disable logging to a file and optionally stop displaying logs in the console:

```python
# Stop logging to file but continue displaying logs in the console
logly.stop_logging()

# Stop logging to file and stop displaying logs in the console
logly.stop_logging(display=False)
```

### Log Messages

Log messages with different levels and colors:

```python
logly.info("Application started successfully.")
logly.info("User logged in", color=Logly.COLOR.GREEN)  # with custom color

logly.info("Database connection established", "Connection details: host=db.local, port=5432", color=Logly.COLOR.CYAN)
logly.warn("API rate limit exceeded", "API request count exceeded 1000", color=Logly.COLOR.YELLOW)
logly.error("Database connection failed", "Unable to reach database at db.local", color=Logly.COLOR.RED)
logly.debug("User request details", "User requested resource /api/data", color=Logly.COLOR.BLUE)
logly.critical("Critical system failure", "Disk space usage exceeded 95%", color=Logly.COLOR.CRITICAL)
logly.fatal("Application crashed", "Unhandled exception in user module", color=Logly.COLOR.CRITICAL)
logly.trace("Debug trace", "Trace info: function call stack", color=Logly.COLOR.BLUE)
logly.log("System status", "All systems operational", color=Logly.COLOR.WHITE)
```

### Custom Log Format

You can customize the format of the log messages:

```python
config = LoglyConfig(custom_format="{timestamp} - {level} - {message}")
logly = Logly(config=config)
logly.start_logging()

logly.info("Custom format log message.")
```

### Disable File Logging

Disable logging to a file:

```python
logly.disable_file_logging()
```

### Enable File Logging

Enable logging to a file:

```python
logly.enable_file_logging()
```

### Set Default File Path

Set the default file path for log files:

```python
logly.set_default_file_path("logs/new_log.txt")
```

### Set Default Maximum File Size

Set the default maximum file size for log files:

```python
logly.set_default_max_file_size(50)  # 50 MB
```

## Example

```python
from logly import Logly, LoglyConfig

# Create a Logly instance with custom configuration
config = LoglyConfig(display=True, log_to_file_enabled=True, default_file_path="logs/app.log")
logly = Logly(config=config)

# Start logging to store the logs in a text file and display in console
logly.start_logging()

logly.info("Application started successfully.")
logly.info("User logged in", color=Logly.COLOR.GREEN)  # with custom color

# Log messages with different levels and colors
logly.info("Database connection established", "Connection details: host=db.local, port=5432", color=Logly.COLOR.CYAN)
logly.warn("API rate limit exceeded", "API request count exceeded 1000", color=Logly.COLOR.YELLOW)
logly.error("Database connection failed", "Unable to reach database at db.local", color=Logly.COLOR.RED)
logly.debug("User request details", "User requested resource /api/data", color=Logly.COLOR.BLUE)
logly.critical("Critical system failure", "Disk space usage exceeded 95%", color=Logly.COLOR.CRITICAL)
logly.fatal("Application crashed", "Unhandled exception in user module", color=Logly.COLOR.CRITICAL)
logly.trace("Debug trace", "Trace info: function call stack", color=Logly.COLOR.BLUE)
logly.log("System status", "All systems operational", color=Logly.COLOR.WHITE)

# Stop logging to file (messages will be displayed but not logged to file after this point)
logly.stop_logging()

# Log more messages after stopping logging to file (messages will be displayed but not logged in file)
logly.info("User session ended", "User logged out", color=Logly.COLOR.CYAN)
logly.warn("Low disk space", "Disk space is below 10%", color=Logly.COLOR.YELLOW)
logly.error("File not found", "Unable to find /config/settings.json", color=Logly.COLOR.RED)
```


if you faced an error like [`FileNotFoundError: [Errno 2] No such file or directory: 'log.txt'`](https://github.com/muhammad-fiaz/logly/issues/4) you can use the following code snippet to set the default path

```python3
import os
from logly import Logly

logly = Logly() # initialize the logly
logly.start_logging() # make sure to include this or else the log will only display without storing it

logly.set_default_max_file_size(50) # optional
logger = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt") # This will ensure the path location to create the log.txt on current directory
logly.set_default_file_path(logger)
```
for more information, check the [repository](https://github.com/muhammad-fiaz/logly).

## Color Options:

### Default Color Options:

| Level    | Color Code      |
| -------- | --------------- |
| INFO     | CYAN            |
| WARNING  | YELLOW          |
| ERROR    | RED             |
| DEBUG    | BLUE            |
| CRITICAL | BRIGHT RED      |
| TRACE    | BLUE            |
| DEFAULT  | WHITE           |

### Custom Color Options:

You can use any of the following color codes for custom coloring:

| NAME     | Color Code      |
|----------| --------------- |
| CYAN      | CYAN            |
| YELLOW   | YELLOW          |
|  RED       | RED             |
|  BLUE      | BLUE            |
| BRIGHT RED | CRITICAL     |
|WHITE   | WHITE           |
| GREEN       | Fore.GREEN    |


For example, you can use `color=logly.COLOR.RED` for the red color.

## Tips & Tricks
If you want to use logly in your project files without creating a new object in each Python file or class, you can create a file named logly.py. In this file, initialize logly and configure the defaults. Now, you can easily import and use it throughout your project:

`logly.py`
```python3
# logly.py in your root or custom path
# Import Logly

from logly import Logly
import os
logly = Logly()
logly.start_logging()

# Set the default file path and maximum file size
logly.set_default_max_file_size(50)
logger = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt") # This will ensure the path location to create the log.txt 
logly.set_default_file_path(logger)

# Start logging again
logly.start_logging()
```
you can now use the logly by


`main.py`
```python3
from logly import logly # make sure to import it some IDE may automatically import it on top

logly.info("msg","hello this is logly", color=logly.COLOR.RED) # with custom color of red

```
### output 
```
[XXXX-XX-XX XX:XX: XX] INFO: msg: hello this is logly

```

## Contributing
Contributions are welcome! Before contributing, please read our [Contributing Guidelines](CONTRIBUTING.md) to ensure a smooth and collaborative development process.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) to understand the standards of behavior we expect from contributors and users of this project.

## License
This project is licensed under the [MIT License](). See [LICENSE](LICENSE) for more details.


## Support the Project

<div align="center">

Your support helps improve Logly and enables us to continue adding more features and improvements. If you'd like to contribute and support the development of this project, consider becoming a sponsor on GitHub or Ko-fi.




### Become a Sponsor on GitHub
Support Logly directly on GitHub to help sustain ongoing development.

[![Sponsor muhammad-fiaz](https://img.shields.io/badge/Sponsor-%231EAEDB.svg?&style=for-the-badge&logo=GitHub-Sponsors&logoColor=white)](https://github.com/sponsors/muhammad-fiaz)

### Support via Ko-fi
If you prefer, you can also support the project via Ko-fi.

[![Support on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F1F6MME1W)


Thank you for supporting the project! 🙏

</div>

## Happy Coding
