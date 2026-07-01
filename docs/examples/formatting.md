---
title: Formatting
description: Customize log output with format tokens, templates, colors, and callable formatters.
---

# Formatting

Control exactly how log records appear using format strings, tokens, colors, and callable formatters.

## Format Tokens

```python
from logly import logger

sink_id = logger.add(
    "formatted.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
)
logger.info("Detailed format")
logger.complete()
logger.remove(sink_id)
```

Available tokens:

| Token | Description | Example |
|-------|-------------|---------|
| `{time}` | Timestamp | `{time:YYYY-MM-DD HH:mm:ss}` |
| `{time:FORMAT}` | Formatted timestamp | `{time:HH:mm:ss.SSS}` |
| `{level}` | Level name | `{level}` |
| `{level:<8}` | Level name padded | `{level:<8}` |
| `{level_no}` | Numeric priority | `{level_no}` |
| `{message}` | Log message | `{message}` |
| `{name}` | Logger name | `{name}` |
| `{file}` | Source file path | `{file}` |
| `{filename}` | Source filename only | `{filename}` |
| `{line}` | Line number | `{line}` |
| `{function}` | Function name | `{function}` |
| `{module}` | Module name | `{module}` |
| `{thread}` | Thread name | `{thread}` |
| `{process}` | Process ID | `{process}` |
| `{extra[key]}` | Extra context value | `{extra[user]}` |
| `{extra.key}` | Extra context (dot) | `{extra.user}` |
| `{exception}` | Exception text | `{exception}` |
| `{file_line}` | File:line | `{file_line}` |
| `{function_location}` | Function (file:line) | `{function_location}` |

## Time Format Tokens

Use brace-style tokens for timestamps:

```python
from logly import logger

sink_id = logger.add(
    "time.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS}",
)
logger.info("Timestamped message")
logger.complete()
logger.remove(sink_id)
```

Brace-style tokens: `YYYY`, `YY`, `MM`, `DD`, `HH`, `hh`, `mm`, `ss`, `SSS`, `SS`, `S`, `A`, `ddd`, `dddd`, `MMMM`, `MMM`

Strftime tokens also work: `%Y`, `%m`, `%d`, `%H`, `%M`, `%S`, `%.f`

## Alignment and Padding

```python
from logly import logger

sink_id = logger.add(
    "aligned.log",
    format="{time:HH:mm:ss} | {level:<10} | {message:<30}",
)
logger.info("Left-aligned level")
logger.warning("Right-aligned {level:>10}")
logger.error("Center-aligned {level:^10}")
logger.complete()
logger.remove(sink_id)
```

Alignment operators:
- `{level:<8}` left-align to 8 chars
- `{level:>8}` right-align to 8 chars
- `{level:^8}` center-align to 8 chars
- `{level:*<8}` left-align with `*` fill

## Callable Formatter

```python
from logly import logger

def custom_fmt(record):
    return f"[{record['time'].timestamp():.3f}] {record['level']}: {record['message']}"

sink_id = logger.add("custom.log", format=custom_fmt)
logger.info("Callable formatter active")
logger.complete()
logger.remove(sink_id)
```

## Color Markup in Format Strings

Use Rich-style `<tag>` syntax for inline coloring:

```python
from logly import logger

sink_id = logger.add(
    "stderr",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
    colorize=True,
)
logger.info("<bold>Important</bold> message")
logger.warning("<yellow>Warning</yellow> with <underline>underline</underline>")
logger.complete()
logger.remove(sink_id)
```

Available tags:
- Colors: `<red>`, `<green>`, `<blue>`, `<yellow>`, `<cyan>`, `<magenta>`, `<white>`
- Bright: `<bright_red>`, `<bright_green>`, `<bright_blue>`, etc.
- Styles: `<bold>`, `<dim>`, `<italic>`, `<underline>`, `<strike>`, `<reverse>`
- Background: `<bg_red>`, `<bg_green>`, `<bg_blue>`, etc.

## Combined Level and Message Coloring

```python
from logly import logger

sink_id = logger.add(
    "stderr",
    format="<level>{level:<8}</level> | <level>{message}</level>",
    colorize=True,
)
logger.info("Green info message")
logger.error("Red error message")
logger.warning("Yellow warning message")
logger.complete()
logger.remove(sink_id)
```

## Pretty JSON Format

```python
from logly import logger

sink_id = logger.add(
    "structured.log",
    serialize=True,
    pretty_json=True,
)
logger.info("Structured JSON output")
logger.complete()
logger.remove(sink_id)
```

With custom options:

```python
from logly import logger, PrettyJsonConfig

config = PrettyJsonConfig(indent=2, sort_keys=True)
sink_id = logger.add(
    "structured.log",
    serialize=True,
    pretty_json=config,
)
logger.info("Custom pretty JSON")
logger.complete()
logger.remove(sink_id)
```

## Compact JSON Format

```python
from logly import logger

sink_id = logger.add(
    "compact.log",
    serialize=True,
)
logger.info("Compact JSON output")
logger.complete()
logger.remove(sink_id)
```

## Multiple Format Tokens

```python
from logly import logger

sink_id = logger.add(
    "full.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {thread} | {process} | {message}",
)
logger.info("Full format with all tokens")
logger.complete()
logger.remove(sink_id)
```
