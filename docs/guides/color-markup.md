---
title: Color Markup
description: ANSI color markup for styled log output
---

# Color Markup

Logly supports inline ANSI color markup in format strings. Wrap tags in angle brackets to style log output.

## Basic Usage

```python
from logly import logger

logger.add(
    "stderr",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <level>{message}</level>",
    colorize=True,
)
logger.info("Colored output")
```

## Color Tags

| Tag | Color |
|-----|-------|
| `<red>` | Red |
| `<green>` | Green |
| `<blue>` | Blue |
| `<yellow>` | Yellow |
| `<cyan>` | Cyan |
| `<magenta>` | Magenta |
| `<white>` | White |
| `<black>` | Black |

## Style Tags

| Tag | Effect |
|-----|--------|
| `<bold>` | Bold text |
| `<dim>` | Dim text |
| `<underline>` | Underlined text |
| `<italic>` | Italic text |
| `<blink>` | Blinking text |
| `<strike>` | Strikethrough text |
| `<reverse>` | Reverse video |

## Combining Tags

Stack multiple tags for complex styling:

```python
logger.add(
    "stderr",
    format="<green><bold>{time:HH:mm:ss}</bold></green> | <red><bold>{level:<8}</bold></red> | {message}",
    colorize=True,
)
```

## Level Tags

Use `<level>` to apply the level's configured color:

```python
from logly import logger

logger.add(
    "stderr",
    format="{time:HH:mm:ss} | <level>{level:<8}</level> | {message}",
    colorize=True,
)
```

The `<level>` tag automatically applies the color registered for each log level (e.g., green for INFO, red for ERROR).

### Custom Level Colors

```python
from logly import logger

logger.level("SECURITY", no=45, color="<red><bold>")

logger.add(
    "stderr",
    format="{time:HH:mm:ss} | <level>{level:<8}</level> | {message}",
    colorize=True,
)

logger.log("SECURITY", "Unauthorized access")
# SECURITY appears in bold red
```

## Background Colors

```python
logger.add(
    "stderr",
    format="<bg_red><white>{level:<8}</white></bg_red> | {message}",
    colorize=True,
)
```

| Tag | Background Color |
|-----|-----------------|
| `<bg_red>` | Red background |
| `<bg_green>` | Green background |
| `<bg_blue>` | Blue background |
| `<bg_yellow>` | Yellow background |
| `<bg_cyan>` | Cyan background |
| `<bg_magenta>` | Magenta background |
| `<bg_white>` | White background |
| `<bg_black>` | Black background |

## Escape Codes

Logly uses standard ANSI escape codes. The `colorize=True` parameter enables color rendering:

```python
from logly import logger

# Colors enabled (auto-detected for stderr)
logger.add("stderr", colorize=True)

# Colors forced on
logger.add("app.log", colorize=True)

# Colors forced off
logger.add("app.log", colorize=False)
```

## Rich Integration

If [Rich](https://github.com/Textualize/rich) is installed, Logly uses Rich's color engine for enhanced rendering:

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

logger.add(LoglyRichSink(), colorize=True)
```

## Common Patterns

### Compact Console Output

```python
logger.add(
    "stderr",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)
```

### Error Highlighting

```python
logger.add(
    "stderr",
    format="<green>{time:HH:mm:ss}</green> | <level><bold>{level:<8}</bold></level> | {message}",
    colorize=True,
)
```

### Minimal

```python
logger.add(
    "stderr",
    format="<level>{level:<8}</level> | {message}",
    colorize=True,
)
```
