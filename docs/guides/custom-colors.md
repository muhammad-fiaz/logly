---
title: Custom Colors
description: Guide to customizing log level colors with ANSI, RGB, hex, 256-color, compound styles, and Rich-style markup.
---

# Custom Colors

Logly provides a comprehensive color system supporting named colors, raw ANSI codes, 256-color values, RGB/hex colors, compound styles, background colors, and Rich-style markup tags.

## Color Formats Supported

### Named Colors

Standard ANSI color names:

```python
from logly import logger

logger.level("AUDIT", no=35, color="red")
logger.level("METRIC", no=15, color="cyan")
logger.level("TRACE", no=5, color="dim")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("AUDIT", "red audit message")
logger.log("METRIC", "cyan metric message")
```

Available named colors:
- `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
- `bright_black`, `bright_red`, `bright_green`, `bright_yellow`, `bright_blue`, `bright_magenta`, `bright_cyan`, `bright_white`

### Bright/High-Intensity Colors

Use bright variants for higher-contrast output:

```python
from logly import logger

logger.level("TRACE", no=5, color="bright_black")
logger.level("DEBUG", no=10, color="bright_blue")
logger.level("INFO", no=20, color="bright_green")
logger.level("NOTICE", no=25, color="bright_cyan")
logger.level("SUCCESS", no=30, color="bright_green")
logger.level("WARNING", no=40, color="bright_yellow")
logger.level("ERROR", no=50, color="bright_red")
logger.level("FAIL", no=55, color="bright_magenta")
logger.level("CRITICAL", no=60, color="bright_white")
logger.add("stderr", level="TRACE", colorize=True)
logger.trace("dim trace")
logger.debug("bright blue debug")
logger.info("bright green info")
logger.error("bright red error")
```

### Text Styles

Apply formatting styles to text:

```python
from logly import logger

logger.level("TRACE", no=5, color="dim")
logger.level("DEBUG", no=10, color="bold")
logger.level("WARNING", no=40, color="underline")
logger.level("ERROR", no=50, color="italic")
logger.add("stderr", level="TRACE", colorize=True)
logger.trace("dimmed text")
logger.debug("bold text")
logger.warning("underlined text")
logger.error("italic text")
```

Available styles:
- `dim`, `bold`, `italic`, `underline`, `blink`, `reverse`, `strike`

### Compound Styles (Underscore-Separated)

Combine foreground color with style using underscore syntax:

```python
from logly import logger

logger.level("TRACE", no=5, color="dim_cyan")
logger.level("DEBUG", no=10, color="bold_blue")
logger.level("INFO", no=20, color="bold_green")
logger.level("NOTICE", no=25, color="italic_cyan")
logger.level("SUCCESS", no=30, color="bold_green")
logger.level("WARNING", no=40, color="bold_yellow")
logger.level("ERROR", no=50, color="bold_red")
logger.level("FAIL", no=55, color="bold_magenta")
logger.level("CRITICAL", no=60, color="bold_white")
logger.add("stderr", level="TRACE", colorize=True)
logger.trace("dim cyan trace")
logger.debug("bold blue debug")
logger.error("bold red error")
logger.critical("bold white critical")
```

### Compound Styles (Space-Separated)

Use space-separated tokens for more flexibility:

```python
from logly import logger

logger.level("TRACE", no=5, color="dim cyan")
logger.level("DEBUG", no=10, color="bold blue")
logger.level("INFO", no=20, color="italic green")
logger.level("WARNING", no=40, color="underline yellow")
logger.level("ERROR", no=50, color="bold red")
logger.add("stderr", level="TRACE", colorize=True)
logger.trace("dim cyan trace")
logger.warning("underline yellow warning")
```

### Background Colors

Add background colors with `bg_` or `on_` prefix:

```python
from logly import logger

logger.level("INFO", no=20, color="bg_blue")
logger.level("WARNING", no=40, color="on_yellow")
logger.level("ERROR", no=50, color="bg_red")
logger.add("stderr", level="TRACE", colorize=True)
logger.info("blue background")
logger.warning("yellow background")
logger.error("red background")
```

Background color prefixes:
- `bg_red`, `bg_green`, `bg_blue`, etc.
- `on_red`, `on_green`, `on_blue`, etc.
- `bg_bright_red`, `on_bright_cyan`, etc.

### Compound Styles with Background

Combine foreground, style, and background:

```python
from logly import logger

logger.level("INFO", no=20, color="bold green on black")
logger.level("WARNING", no=40, color="bold yellow on blue")
logger.level("ERROR", no=50, color="bold red on white")
logger.add("stderr", level="TRACE", colorize=True)
logger.info("bold green on black")
logger.warning("bold yellow on blue")
logger.error("bold red on white")
```

Also works with `on_` and `bg_` as single tokens:

```python
logger.level("INFO", no=20, color="bold green on_black")
logger.level("WARNING", no=40, color="bold yellow on_blue")
```

### Raw ANSI SGR Codes

Pass raw SGR codes directly:

```python
from logly import logger

logger.level("RAW_GREEN", no=27, color="1;32")
logger.level("RAW_RED", no=28, color="31")
logger.level("RAW_BOLD", no=29, color="1")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("RAW_GREEN", "raw ANSI green")
logger.log("RAW_RED", "raw ANSI red")
logger.log("RAW_BOLD", "raw ANSI bold")
```

### 256-Color

Use 256-color palette values:

```python
from logly import logger

logger.level("COLOR_208", no=33, color="color(208)")
logger.level("COLOR_196", no=34, color="color(196)")
logger.level("COLOR_82", no=35, color="color(82)")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("COLOR_208", "orange (color 208)")
logger.log("COLOR_196", "bright red (color 196)")
logger.log("COLOR_82", "bright green (color 82)")
```

### RGB Colors

Use RGB triplets for exact color control:

```python
from logly import logger

logger.level("ORANGE", no=33, color="rgb(255, 128, 0)")
logger.level("PURPLE", no=34, color="rgb(128, 0, 255)")
logger.level("TEAL", no=35, color="rgb(0, 255, 255)")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("ORANGE", "exact orange RGB")
logger.log("PURPLE", "exact purple RGB")
logger.log("TEAL", "exact teal RGB")
```

### Hex Colors

Use hex color codes:

```python
from logly import logger

logger.level("CORAL", no=33, color="#ff7f50")
logger.level("LAVENDER", no=34, color="#e6e6fa")
logger.level("GOLD", no=35, color="#ffd700")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("CORAL", "coral hex color")
logger.log("LAVENDER", "lavender hex color")
logger.log("GOLD", "gold hex color")
```

### Background RGB and Hex

Apply background colors using RGB or hex:

```python
from logly import logger

logger.level("INFO", no=20, color="bg_rgb(0, 0, 128)")
logger.level("WARNING", no=40, color="bg#ffff00")
logger.level("ERROR", no=50, color="on_rgb(255, 0, 0)")
logger.add("stderr", level="TRACE", colorize=True)
logger.info("navy background")
logger.warning("yellow background")
logger.error("red background")
```

### Background 256-Color

Use 256-color palette for backgrounds:

```python
from logly import logger

logger.level("INFO", no=20, color="bg_color(196)")
logger.level("WARNING", no=40, color="bgcolor(226)")
logger.add("stderr", level="TRACE", colorize=True)
logger.info("red background (256-color)")
logger.warning("yellow background (256-color)")
```

## Color Disabling

### Global Color Disable

Disable colors globally for a sink:

```python
from logly import logger

sink_id = logger.add(
    "no-color.log",
    format="{level} | {message}",
    colorize=False,  # explicitly disable colors
)
logger.error("No ANSI codes in output")
logger.complete()
logger.remove(sink_id)
```

### Per-Sink Color Control

Different sinks can have different color settings:

```python
from logly import logger

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

# Auto-detect: stderr/stdout get colors if TTY, files don't
logger.add("stderr")  # colorize=None (auto)
logger.add("app.log")  # colorize=None (auto, off for files)
```

## Rich-Style Markup in Format Strings

Use `<tag>` syntax in format strings for inline coloring:

```python
from logly import logger

sink_id = logger.add(
    "stderr",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
    colorize=True,
)
logger.info("<bold>Important</bold> message with <green>colors</green>")
logger.complete()
logger.remove(sink_id)
```

Supported Rich-style tags:
- Colors: `<red>`, `<green>`, `<blue>`, `<yellow>`, `<cyan>`, `<magenta>`, `<white>`, `<black>`
- Bright: `<bright_red>`, `<bright_green>`, `<bright_blue>`, etc.
- Styles: `<bold>`, `<dim>`, `<italic>`, `<underline>`, `<strike>`, `<reverse>`, `<blink>`
- Background: `<bg_red>`, `<bg_green>`, `<bg_blue>`, etc.

### Stripping Tags When Colors Disabled

When `colorize=False`, Rich-style tags are automatically stripped:

```python
from logly import logger

sink_id = logger.add(
    "plain.log",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level>",
    colorize=False,  # tags stripped, no ANSI codes
)
logger.info("<bold>This renders as plain text</bold>")
logger.complete()
logger.remove(sink_id)
```

## Highlight and Underline

### Highlight Text

Use `reverse` style for highlight effect:

```python
from logly import logger

logger.level("HIGHLIGHT", no=35, color="reverse")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("HIGHLIGHT", "highlighted text")
```

Or combine with colors:

```python
from logly import logger

logger.level("HIGHLIGHT", no=35, color="bold reverse")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("HIGHLIGHT", "bold highlighted text")
```

### Underline Text

Use the `underline` style:

```python
from logly import logger

logger.level("UNDERLINE", no=35, color="underline")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("UNDERLINE", "underlined text")
```

Combine underline with colors:

```python
from logly import logger

logger.level("UNDERLINE", no=35, color="underline red")
logger.add("stderr", level="TRACE", colorize=True)
logger.log("UNDERLINE", "underlined red text")
```

### Using Rich-Style Tags

Use `<underline>` and `<reverse>` tags in format strings:

```python
from logly import logger

sink_id = logger.add(
    "stderr",
    format="<underline>{level}</underline> | {message}",
    colorize=True,
)
logger.info("Underlined level name")
logger.complete()
logger.remove(sink_id)
```

## Complete Color Example

```python
from logly import logger

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

# Add console sink with colors
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
