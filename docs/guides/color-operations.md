---
title: Color Operations & Performance
description: Efficient color operations and ANSI processing in Logly
---

# Color Operations & Performance

Logly provides a comprehensive color system for styled log output. This guide covers all color operations, ANSI processing, and performance optimization techniques.

## Named Colors

Logly supports standard ANSI color names for foreground and background styling:

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

# Standard named colors
logger.level("CUSTOM_RED", no=31, color="red")
logger.level("CUSTOM_GREEN", no=32, color="green")
logger.level("CUSTOM_BLUE", no=33, color="blue")
logger.level("CUSTOM_YELLOW", no=34, color="yellow")
logger.level("CUSTOM_CYAN", no=35, color="cyan")
logger.level("CUSTOM_MAGENTA", no=36, color="magenta")

logger.log("CUSTOM_RED", "Red message")
logger.log("CUSTOM_GREEN", "Green message")
logger.log("CUSTOM_BLUE", "Blue message")
```

Available named colors:
- `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`

## Bright Colors

Bright variants provide higher-contrast output for better visibility:

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("BRIGHT_RED", no=31, color="bright_red")
logger.level("BRIGHT_GREEN", no=32, color="bright_green")
logger.level("BRIGHT_BLUE", no=33, color="bright_blue")
logger.level("BRIGHT_YELLOW", no=34, color="bright_yellow")
logger.level("BRIGHT_CYAN", no=35, color="bright_cyan")
logger.level("BRIGHT_MAGENTA", no=36, color="bright_magenta")

logger.log("BRIGHT_RED", "Bright red message")
logger.log("BRIGHT_GREEN", "Bright green message")
```

Available bright colors:
- `bright_black`, `bright_red`, `bright_green`, `bright_yellow`, `bright_blue`, `bright_magenta`, `bright_cyan`, `bright_white`

## Compound Styles

Combine foreground color with text styles using underscore or space syntax:

### Underscore-Separated

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("TRACE", no=5, color="dim_cyan")
logger.level("DEBUG", no=10, color="bold_blue")
logger.level("INFO", no=20, color="bold_green")
logger.level("NOTICE", no=25, color="italic_cyan")
logger.level("SUCCESS", no=30, color="bold_green")
logger.level("WARNING", no=40, color="bold_yellow")
logger.level("ERROR", no=50, color="bold_red")
logger.level("FAIL", no=55, color="bold_magenta")
logger.level("CRITICAL", no=60, color="bold_white")

logger.trace("dim cyan trace")
logger.debug("bold blue debug")
logger.error("bold red error")
logger.critical("bold white critical")
```

### Space-Separated

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("TRACE", no=5, color="dim cyan")
logger.level("DEBUG", no=10, color="bold blue")
logger.level("INFO", no=20, color="italic green")
logger.level("WARNING", no=40, color="underline yellow")
logger.level("ERROR", no=50, color="bold red")

logger.trace("dim cyan trace")
logger.warning("underline yellow warning")
```

Available text styles:
- `dim`, `bold`, `italic`, `underline`, `blink`, `reverse`, `strike`

## Background Colors

### Named Background Colors

Use `bg_` or `on_` prefix for background colors:

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("INFO", no=20, color="bg_blue")
logger.level("WARNING", no=40, color="on_yellow")
logger.level("ERROR", no=50, color="bg_red")

logger.info("blue background")
logger.warning("yellow background")
logger.error("red background")
```

Available background prefixes:
- `bg_red`, `bg_green`, `bg_blue`, `bg_yellow`, `bg_cyan`, `bg_magenta`, `bg_white`, `bg_black`
- `on_red`, `on_green`, `on_blue`, `on_yellow`, `on_cyan`, `on_magenta`, `on_white`, `on_black`
- `bg_bright_red`, `on_bright_cyan`, etc.

### RGB Background Colors

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("INFO", no=20, color="bg_rgb(0, 0, 128)")
logger.level("WARNING", no=40, color="on_rgb(255, 165, 0)")
logger.level("ERROR", no=50, color="on_rgb(255, 0, 0)")

logger.info("navy background")
logger.warning("orange background")
logger.error("red background")
```

### Hex Background Colors

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("INFO", no=20, color="bg#000080")
logger.level("WARNING", no=40, color="on#ffa500")
logger.level("ERROR", no=50, color="on#ff0000")

logger.info("navy background")
logger.warning("orange background")
logger.error("red background")
```

### 256-Color Background

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("INFO", no=20, color="bg_color(196)")
logger.level("WARNING", no=40, color="bgcolor(226)")
logger.level("ERROR", no=50, color="on_color(160)")

logger.info("red background (256-color)")
logger.warning("yellow background (256-color)")
```

### Compound Styles with Background

Combine foreground, style, and background:

```python
from logly import logger

logger.remove()

logger.add("stderr", level="TRACE", colorize=True)

logger.level("INFO", no=20, color="bold green on black")
logger.level("WARNING", no=40, color="bold yellow on blue")
logger.level("ERROR", no=50, color="bold red on white")

logger.info("bold green on black")
logger.warning("bold yellow on blue")
logger.error("bold red on white")
```

## Rich-Style Markup Tags

Use `<tag>` syntax in format strings for inline coloring. These tags work directly in format strings and log messages.

### Color Tags

```python
from logly import logger

logger.remove()

logger.add(
    "stderr",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <level>{message}</level>",
    colorize=True,
)

logger.info("Colored output")
```

Supported color tags:
- `<red>`, `<green>`, `<blue>`, `<yellow>`, `<cyan>`, `<magenta>`, `<white>`, `<black>`
- `<bright_red>`, `<bright_green>`, `<bright_blue>`, `<bright_yellow>`, `<bright_cyan>`, `<bright_magenta>`, `<bright_white>`, `<bright_black>`

### Style Tags

```python
from logly import logger

logger.remove()

logger.add(
    "stderr",
    format="<bold>{level:<8}</bold> | <dim>{message}</dim>",
    colorize=True,
)

logger.info("Bold and dim text")
```

Supported style tags:
- `<bold>`, `<dim>`, `<italic>`, `<underline>`, `<blink>`, `<strike>`, `<reverse>`

### Background Tags

```python
from logly import logger

logger.remove()

logger.add(
    "stderr",
    format="<bg_red><white>{level:<8}</white></bg_red> | {message}",
    colorize=True,
)

logger.error("Error with red background")
```

Supported background tags:
- `<bg_red>`, `<bg_green>`, `<bg_blue>`, `<bg_yellow>`, `<bg_cyan>`, `<bg_magenta>`, `<bg_white>`, `<bg_black>`

### Combining Tags

Stack multiple tags for complex styling:

```python
from logly import logger

logger.remove()

logger.add(
    "stderr",
    format=(
        "<green><bold>{time:HH:mm:ss}</bold></green> | "
        "<red><bold>{level:<8}</bold></red> | "
        "<cyan>{message}</cyan>"
    ),
    colorize=True,
)

logger.info("Complex styled output")
```

### Level Tags

Use `<level>` to apply the level's configured color automatically:

```python
from logly import logger

logger.remove()

logger.add(
    "stderr",
    format="{time:HH:mm:ss} | <level>{level:<8}</level> | {message}",
    colorize=True,
)

logger.info("Green info")
logger.error("Red error")
logger.warning("Yellow warning")
```

## The `colorize()` Function

Use `colorize()` to apply ANSI colors to text programmatically:

```python
from logly import logger
from logly import colorize

logger.remove()

logger.add("stderr", colorize=True)

# Apply color to a string
red_text = colorize("Error occurred", "red")
bold_text = colorize("Important", "bold")
green_bold = colorize("Success", "bold green")

logger.info("{}", red_text)
logger.info("{}", bold_text)
logger.info("{}", green_bold)
```

### Colorize with Background

```python
from logly import colorize

# Foreground + background
error_msg = colorize("ERROR", "bold white on_red")
warning_msg = colorize("WARN", "bold black on_yellow")

print(f"{error_msg} Something failed")
print(f"{warning_msg} Something looks off")
```

## The `strip_rich_tags()` Function

Strip Rich-style markup tags from text, leaving only the content:

```python
from logly import logger
from logly import strip_rich_tags

logger.remove()

# Create a logger that strips tags for plain text output
logger.add(
    "plain.log",
    format="{time} | {level:<8} | {message}",
    colorize=False,
)

# Original message with tags
message = "<bold>Important</bold>: <red>check the logs</red>"

# Strip tags for plain text file
plain_text = strip_rich_tags(message)
logger.info("{}", plain_text)
# Output: Important: check the logs (no ANSI codes)
```

### Common Use Case

```python
from logly import logger
from logly import strip_rich_tags

logger.remove()

# Console with colors
logger.add(
    "stderr",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
    colorize=True,
)

# File without colors (tags automatically stripped when colorize=False)
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    colorize=False,
)

# Log message with Rich-style tags
logger.info("<bold>User</bold> <green>logged in</green>")
# Console: styled output with colors
# File: User logged in (plain text)
```

## The `paint_themed()` Function

Apply theme-aware coloring that adapts to the current color scheme:

```python
from logly import logger
from logly import paint_themed

logger.remove()

logger.add("stderr", colorize=True)

# Theme-aware coloring
success_msg = paint_themed("Operation completed", "success")
error_msg = paint_themed("Something failed", "error")
warning_msg = paint_themed("Check this", "warning")

logger.info("{}", success_msg)
logger.error("{}", error_msg)
logger.warning("{}", warning_msg)
```

### Custom Themes

```python
from logly import logger
from logly import paint_themed

logger.remove()

# Define custom theme
theme = {
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "cyan",
    "debug": "dim",
}

logger.add("stderr", colorize=True, theme=theme)

logger.info("{}", paint_themed("Success!", "success"))
logger.error("{}", paint_themed("Failed!", "error"))
```

## Color Caching and Performance

Logly caches color escape sequences for optimal performance. Understanding how caching works helps you write efficient color configurations.

### How Caching Works

```python
from logly import logger

logger.remove()

# Color values are cached after first use
# These calls reuse cached escape sequences
logger.add("stderr", colorize=True)
logger.level("CUSTOM", no=35, color="bold red on white")

# The escape sequence for "bold red on white" is computed once
# and reused for all subsequent log calls at this level
for i in range(10000):
    logger.log("CUSTOM", "Message {}", i)
```

### Performance Tips

```python
from logly import logger

logger.remove()

# Good: Reuse color strings (cached)
ERROR_STYLE = "bold red"
WARNING_STYLE = "yellow"
INFO_STYLE = "green"

logger.level("CUSTOM_ERROR", no=50, color=ERROR_STYLE)
logger.level("CUSTOM_WARNING", no=40, color=WARNING_STYLE)
logger.level("CUSTOM_INFO", no=20, color=INFO_STYLE)

# Good: Use named colors (faster parsing)
logger.level("LEVEL1", no=31, color="red")

# Avoid: Complex RGB colors in hot paths (more parsing overhead)
# Use only when exact color control is needed
logger.level("LEVEL2", no=32, color="rgb(255, 0, 0)")
```

### Performance Comparison

| Color Type | Parsing Speed | Use Case |
|------------|---------------|----------|
| Named colors | Fastest | Most log levels |
| Bright colors | Fast | High-contrast needs |
| Compound styles | Fast | Bold/italic combinations |
| 256-color | Medium | Extended palette |
| RGB/Hex | Slower | Exact color matching |

## Disabling Colors Globally

### Per-Sink Disable

```python
from logly import logger

logger.remove()

# Console gets colors
logger.add("stderr", colorize=True)

# File gets no colors
logger.add("app.log", colorize=False)

# Another file gets colors
logger.add("colored.log", colorize=True)

logger.error("This message goes to all three sinks")
logger.complete()
```

### Auto-Detection

When `colorize=None` (default), colors auto-detect based on sink type:

```python
from logly import logger

logger.remove()

# Auto-detect: stderr/stdout get colors if TTY, files don't
logger.add("stderr")  # colorize=None (auto)
logger.add("app.log")  # colorize=None (auto, off for files)
```

### Environment Variable

```python
import os
from logly import logger

# Disable colors via environment variable
os.environ["NO_COLOR"] = "1"

logger.remove()
logger.add("stderr")  # Colors disabled by NO_COLOR
logger.info("No colors in output")
```

## Color in Network/File Sinks

### Network Sinks

When sending logs over the network, strip ANSI codes to avoid corrupting data:

```python
import json
import urllib.request
from logly import logger

def http_sink(message: str) -> None:
    # Strip ANSI codes before sending
    payload = json.dumps({"log": message}).encode("utf-8")
    request = urllib.request.Request(
        "https://logs.example.com/ingest",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(request, timeout=5)

logger.add(
    http_sink,
    level="INFO",
    enqueue=True,
    colorize=False,  # Disable colors for network sink
)
```

### File Sinks

Control colors per file:

```python
from logly import logger

logger.remove()

# Plain text file (no colors)
logger.add(
    "plain.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    colorize=False,
)

# Colored file (for terminals that support it)
logger.add(
    "colored.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    colorize=True,
)

logger.info("Goes to both files")
logger.complete()
```

### JSON Output

When `serialize=True`, colors are automatically stripped:

```python
from logly import logger

logger.remove()

logger.add("app.json", serialize=True, colorize=True)
logger.info("JSON output has no ANSI codes")
# Output: {"time": "...", "level": "INFO", "message": "JSON output has no ANSI codes"}
```

## Complete Examples

### Full Color Configuration

```python
from logly import logger

logger.remove()

# Configure all built-in levels with custom colors
logger.level("TRACE", no=5, color="dim cyan")
logger.level("DEBUG", no=10, color="blue")
logger.level("INFO", no=20, color="green")
logger.level("NOTICE", no=25, color="cyan")
logger.level("SUCCESS", no=30, color="bold green")
logger.level("WARNING", no=40, color="bold yellow")
logger.level("ERROR", no=50, color="bold red")
logger.level("FAIL", no=55, color="bold magenta")
logger.level("CRITICAL", no=60, color="bold red on white")
logger.level("FATAL", no=70, color="bold red on black")

# Register custom levels with colors
logger.level("AUDIT", no=35, color="rgb(255, 128, 0)")
logger.level("METRIC", no=15, color="color(208)")
logger.level("SECURITY", no=45, color="bold red")
logger.level("HIGHLIGHT", no=36, color="reverse")

# Console sink with colors
logger.add("stderr", level="TRACE", colorize=True)

# Test all levels
logger.trace("trace message")
logger.debug("debug message")
logger.info("info message")
logger.notice("notice message")
logger.success("success message")
logger.log("AUDIT", "audit message")
logger.log("METRIC", "metric message")
logger.warning("warning message")
logger.error("error message")
logger.fail("fail message")
logger.log("SECURITY", "security message")
logger.log("HIGHLIGHT", "highlighted message")
logger.critical("critical message")
logger.fatal("fatal message")

logger.complete()
```

### Multi-Sink Color Setup

```python
from logly import logger

logger.remove()

# Console with Rich-style markup
logger.add(
    "stderr",
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level><bold>{level:<8}</bold></level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# File without colors
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {filename}:{line} | {message}",
    colorize=False,
    rotation="daily",
    retention="30 days",
)

# JSON without colors
logger.add(
    "app.json",
    serialize=True,
    colorize=False,
)

logger.info("Message with <bold>Rich-style</bold> markup")
logger.complete()
```

### Performance-Optimized Colors

```python
from logly import logger

logger.remove()

# High-throughput: disable source capture, use simple colors
logger.add(
    "app.log",
    level="INFO",
    capture=False,
    enqueue=True,
    rotation="100 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
)

# Console with colors (cached escape sequences)
logger.add(
    "stderr",
    level="INFO",
    format="{time:HH:mm:ss} | <level>{level:<8}</level> | {message}",
    colorize=True,
)

# Pre-compute color strings (cached by Logly)
COLORS = {
    "info": "green",
    "warning": "yellow",
    "error": "bold red",
}

for i in range(100000):
    logger.info("Info message {}", i)
    if i % 10 == 0:
        logger.warning("Warning message {}", i)
    if i % 100 == 0:
        logger.error("Error message {}", i)

logger.complete()
```
