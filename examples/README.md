# Logly Examples

These are some examples to play around with Logly functionality. Each example demonstrates different features and use cases of the Logly logging library.

Note: I added a docstring/comments above each example file for better clarity :)

## Features Demonstrated

- **Basic Setup**: Console and file logging, configuration options
- **Advanced Features**: Custom colors, callbacks, structured logging
- **Production Ready**: File rotation, JSON output, error handling
- **Version Management**: Automatic version checking (can be disabled)

!!! tip "Disabling Auto-Update Checks"
    All examples use the default logger which includes automatic version checking. For environments without network access, create loggers with:
    
    ```python
    from logly import logger
    custom_logger = logger(auto_update_check=False)  # Recommended
    # or
    from logly import PyLogger
    custom_logger = PyLogger(auto_update_check=False)
    ```

## Available Examples

- `basic_console.py` - Basic console logging setup
- `color_callback.py` - Custom color callbacks
- `file_rotation.py` - File logging with rotation
- `format_placeholders.py` - Custom format placeholders
- `json_logging.py` - JSON formatted logging

## Running Examples

To run any example:

```bash
cd examples
python basic_console.py
```


Feel free to modify these examples to experiment with Logly's capabilities!