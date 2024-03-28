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
    - [Explanation](#explanation)
5. [Set Default Path](#set-default-path)
6. [Color Options](#color-options)
    - [Default Color Options](#default-color-options)
    - [Custom Color Options](#custom-color-options)
7. [Tips & Tricks](#tips--tricks)
8. [Contributing](#contributing)
9. [Code of Conduct](#code-of-conduct)
10. [License](#license)
11. [Support the Project](#support-the-project)
12. [Happy Coding](#happy-coding)


## Features

- Easy-to-use logging for Python applications.
- Customizable log levels and formatting.
- Customizable log colors.
- Log to file and/or console.
- Log to file with automatic file rotation.
- Log to file with automatic file size management.
- Log to file with automatic file deletion.
- Log to file with automatic deletion and rewriting of the file when it reaches max_file_size. 
- Open Source: Logly is an open-source project, and we welcome contributions from the community.
- Community Support: Join a community of developers using Logly for their logging needs.
- many more features!

## Getting Started

## Installation

```bash
pip install logly
```

## Usage

```python
# Import Logly
from logly import Logly

# Create a Logly instance
logly = Logly()
# logly = Logly(show_time=False)  # Include timestamps in log messages default is  true, and you can set it to false will not show the time in all log messages

# Start logging will store the log in text file
logly.start_logging() #make sure to include this or else the log will only display without storing it

logly.info("hello this is log")
logly.info("hello this is log", color=logly.COLOR.RED) # with custom color

# Log messages with different levels and colors
logly.info("Key1", "Value1", color=logly.COLOR.CYAN)
logly.warn("Key2", "Value2", color=logly.COLOR.YELLOW)
logly.error("Key3", "Value3", color=logly.COLOR.RED)
logly.debug("Key4", "Value4", color=logly.COLOR.BLUE)
logly.critical("Key5", "Value5", color=logly.COLOR.CRITICAL)
logly.fatal("Key6", "Value6", color=logly.COLOR.CRITICAL)
logly.trace("Key7", "Value7", color=logly.COLOR.BLUE)
logly.log("Key8", "Value8", color=logly.COLOR.WHITE)

# Stop logging (messages will be displayed but not logged in file after this point)
logly.stop_logging()

# Log more messages after stopping logging (messages will be displayed but not logged in file after this point)
logly.info("AnotherKey1", "AnotherValue1", color=logly.COLOR.CYAN)
logly.warn("AnotherKey2", "AnotherValue2", color=logly.COLOR.YELLOW)
logly.error("AnotherKey3", "AnotherValue3", color=logly.COLOR.RED)


logly.info("hello this is log", color=logly.COLOR.RED,show_time=False) # with custom color and without time

# Start logging again
logly.start_logging() 

# Set the default file path and max file size
logly.set_default_file_path("log.txt") # Set the default file path is "log.txt" if you want to set the file path where you want to save the log file.
logly.set_default_max_file_size(50) # set default max file size is 50 MB

# Log messages with default settings (using default file path and max file size)
logly.info("DefaultKey1", "DefaultValue1")
logly.warn("DefaultKey2", "DefaultValue2")
logly.error("DefaultKey3", "DefaultValue3", log_to_file=False)

#The DEFAULT FILE SIZE IS 100 MB in the txt file
# Log messages with custom file path and max file size(optional)
logly.info("CustomKey1", "CustomValue1", file_path="path/c.txt", max_file_size=25) # max_file_size is in MB and create a new file when the file size reaches max_file_size
logly.warn("CustomKey2", "CustomValue2", file_path="path/c.txt", max_file_size=25,auto=True) # auto=True will automatically delete the file data when it reaches max_file_size

# Access color constants directly
logly.info("Accessing color directly", "DirectColorValue", color=logly.COLOR.RED)

# Disable color
logly.color_enabled = False
logly.info("ColorDisabledKey", "ColorDisabledValue", color=logly.COLOR.RED)
logly.info("ColorDisabledKey1", "ColorDisabledValue1", color=logly.COLOR.RED,color_enabled=True) # This will enable the color for this one log message
logly.color_enabled = True
# this will enable the color again
logly.info("ColorDisabledKey1", "ColorDisabledValue1", color=logly.COLOR.RED,color_enabled=False) # this will disable the color for this one log message


# Display logged messages (this will display all the messages logged so far)
print("Logged Messages:")
for message in logly.logged_messages:
    print(message)

```
## Explanation:

1. Import the `Logly` class from the `logly` module.
2. Create an instance of `Logly`.
3. Start logging using the `start_logging()` method.
4. Log messages with various levels (info, warn, error, debug, critical, fatal, trace) and colors.
5. Stop logging using the `stop_logging()` method.
6. Log additional messages after stopping logging.
7. Start logging again.
8. Log messages with default settings, custom file path, and max file size.
9. Access color constants directly.
10. Display logged messages.
11. enable/disable timestamp support
12. enable/disable color for log support

for more information, check the [repository](https://github.com/muhammad-fiaz/logly)

## Set the Default Path

If you encounter an error related to the default file path, you can use the following code snippet to set the default path:

```python3
import os
from logly import Logly

logly = Logly()
logly.start_logging()

# Set the default file path and maximum file size
logly.set_default_max_file_size(50)
logger = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logly.set_default_file_path(logger)
```
This will set the default file path, and you can customize it according to your requirements.

if you want to set the default path for the log file, you can use the following code snippet

```python3
from logly import Logly
logly = Logly()
logly.set_default_file_path("log.txt")
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
[XXXX-XX-XX XX:XX: XX] INFo: msg: hello this is logly

```

## Contributing
Contributions are welcome! Before contributing, please read our [Contributing Guidelines](CONTRIBUTING.md) to ensure a smooth and collaborative development process.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) to understand the standards of behavior we expect from contributors and users of this project.

## License
This project is licensed under the [MIT License](). See [LICENSE](LICENSE) for more details.

## Support the Project
<br>
<div align="center">

_Support the Project by Becoming a Sponsor on GitHub_

[![Sponsor muhammad-fiaz](https://img.shields.io/badge/Sponsor-%231EAEDB.svg?&style=for-the-badge&logo=GitHub-Sponsors&logoColor=white)](https://github.com/sponsors/muhammad-fiaz)


</div>



## Happy Coding
