# Time Formatting Feature - Issue #79

This document demonstrates the new time formatting feature added to Logly.

## Feature Description

Logly now supports custom time formatting patterns in templates, similar to Loguru. You can format timestamps using the `{time:FORMAT}` syntax.

## Supported Format Specifiers

- `YYYY`: 4-digit year (e.g., 2023)
- `YY`: 2-digit year (e.g., 23)
- `MM`: 2-digit month (01-12)
- `DD`: 2-digit day (01-31)
- `HH`: 2-digit hour in 24-hour format (00-23)
- `mm`: 2-digit minute (00-59)
- `ss`: 2-digit second (00-59)
- `SSS`: 3-digit millisecond (000-999)

## Usage Examples

### Basic Date Format
```python
from logly import Logger

logger = Logger(format="{time:YYYY-MM-DD} | {level} | {message}")
logger.info("This is a test")
# Output: 2023-01-15 | INFO | This is a test
```

### Full DateTime Format
```python
logger = Logger(format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}")
logger.info("This is a test")
# Output: 2023-01-15 12:34:56 [INFO] This is a test
```

### European Date Format
```python
logger = Logger(format="{time:DD/MM/YYYY} | {level} | {message}")
logger.info("This is a test")
# Output: 15/01/2023 | INFO | This is a test
```

### With Milliseconds
```python
logger = Logger(format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
logger.info("This is a test")
# Output: 2023-01-15 12:34:56.789 | This is a test
```

### Mixed Formatted and Raw
```python
logger = Logger(format="{time:YYYY-MM-DD} | {level} | ISO: {time}")
logger.info("This is a test")
# Output: 2023-01-15 | INFO | ISO: 2023-01-15T12:34:56Z
```

## Implementation Details

The feature is implemented in `src/format/template.rs`:

1. **Pattern Conversion**: Simple patterns (YYYY, MM, DD, etc.) are converted to chrono format specifiers (%Y, %m, %d, etc.)
2. **Timestamp Parsing**: RFC3339 timestamps are parsed and formatted according to the pattern
3. **Backward Compatibility**: The default `{time}` placeholder without a format continues to work as before

## Tests

Comprehensive tests have been added to verify the functionality:
- `test_time_format_yyyy_mm_dd`: Basic date format
- `test_time_format_full`: Full datetime format
- `test_time_format_dd_mm_yyyy`: European date format
- `test_time_format_with_milliseconds`: Millisecond precision
- `test_time_format_yy`: 2-digit year format
- `test_time_format_mixed_with_unformatted`: Mixed usage
- `test_convert_time_pattern`: Pattern conversion

All tests pass successfully and the code compiles without errors.
