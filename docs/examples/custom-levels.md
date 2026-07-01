---
title: Custom Log Levels
description: Register custom log levels with priorities and colors.
---

# Custom Log Levels

Define your own log levels beyond the built-in 10.

## Register a Custom Level

```python
from logly import logger

logger.level("AUDIT", no=35, color="magenta")
logger.level("METRIC", no=15, color="cyan")

logger.log("AUDIT", "User action recorded")
logger.log("METRIC", "Request latency: 42ms")
logger.complete()
```

## Custom Level with Named Colors

```python
from logly import logger

logger.level("SECURITY", no=45, color="bold red")
logger.level("VERBOSE", no=12, color="dim cyan")
logger.level("HIGHLIGHT", no=36, color="reverse")

logger.log("SECURITY", "Unauthorized access attempt")
logger.log("VERBOSE", "Verbose debug output")
logger.log("HIGHLIGHT", "Highlighted message")
logger.complete()
```

## Custom Level with RGB Colors

```python
from logly import logger

logger.level("ORANGE", no=33, color="rgb(255, 128, 0)")
logger.level("PURPLE", no=34, color="rgb(128, 0, 255)")
logger.level("TEAL", no=35, color="rgb(0, 200, 200)")

logger.log("ORANGE", "Orange RGB message")
logger.log("PURPLE", "Purple RGB message")
logger.log("TEAL", "Teal RGB message")
logger.complete()
```

## Custom Level with Hex Colors

```python
from logly import logger

logger.level("CORAL", no=33, color="#ff7f50")
logger.level("LAVENDER", no=34, color="#e6e6fa")
logger.level("GOLD", no=35, color="#ffd700")

logger.log("CORAL", "Coral hex color")
logger.log("LAVENDER", "Lavender hex color")
logger.log("GOLD", "Gold hex color")
logger.complete()
```

## Custom Level with 256-Color

```python
from logly import logger

logger.level("COLOR_208", no=33, color="color(208)")
logger.level("COLOR_196", no=34, color="color(196)")
logger.level("COLOR_82", no=35, color="color(82)")

logger.log("COLOR_208", "Orange 256-color")
logger.log("COLOR_196", "Bright red 256-color")
logger.log("COLOR_82", "Bright green 256-color")
logger.complete()
```

## Custom Level with Background Colors

```python
from logly import logger

logger.level("ON_RED", no=33, color="bold white on_red")
logger.level("ON_BLUE", no=34, color="bold white on_blue")
logger.level("BG_GREEN", no=35, color="bold black bg_green")

logger.log("ON_RED", "White on red background")
logger.log("ON_BLUE", "White on blue background")
logger.log("BG_GREEN", "Black on green background")
logger.complete()
```

## Custom Level with Raw ANSI

```python
from logly import logger

logger.level("RAW_GREEN", no=27, color="1;32")
logger.level("RAW_RED", no=28, color="31")
logger.level("RAW_BOLD", no=29, color="1")

logger.log("RAW_GREEN", "Raw ANSI green")
logger.log("RAW_RED", "Raw ANSI red")
logger.log("RAW_BOLD", "Raw ANSI bold")
logger.complete()
```

## Override Built-in Colors

```python
from logly import logger

logger.level("DEBUG", color="bright blue")
logger.level("WARNING", color="bold yellow")
logger.level("ERROR", color="bold red on white")

logger.debug("Custom blue debug")
logger.warning("Custom yellow warning")
logger.error("Custom red on white error")
logger.complete()
```

## Custom Level with Filters

```python
from logly import logger

logger.level("SECURITY", no=45, color="bold red")

sink_id = logger.add(
    "security.log",
    level="SECURITY",  # only SECURITY and above
    rotation="daily",
)

logger.log("SECURITY", "Unauthorized access attempt")
logger.complete()
logger.remove(sink_id)
```

## Custom Level with Enqueue

```python
from logly import logger

logger.level("AUDIT", no=35, color="bold magenta")

sink_id = logger.add(
    "audit.log",
    level="AUDIT",
    enqueue=True,  # async write via background worker
)

logger.log("AUDIT", "Async audit message")
logger.complete()
logger.remove(sink_id)
```

## Multiple Custom Levels

```python
from logly import logger

logger.level("TRACE", no=5, color="dim cyan")
logger.level("DEBUG", no=10, color="blue")
logger.level("INFO", no=20, color="green")
logger.level("NOTICE", no=25, color="cyan")
logger.level("SUCCESS", no=30, color="bold green")
logger.level("AUDIT", no=35, color="bold magenta")
logger.level("WARNING", no=40, color="bold yellow")
logger.level("ERROR", no=50, color="bold red")
logger.level("FAIL", no=55, color="bold magenta")
logger.level("CRITICAL", no=60, color="bold red on white")
logger.level("FATAL", no=70, color="bold red on black")

logger.add("stderr", level="TRACE", colorize=True)

logger.trace("trace")
logger.debug("debug")
logger.info("info")
logger.notice("notice")
logger.success("success")
logger.log("AUDIT", "audit")
logger.warning("warning")
logger.error("error")
logger.fail("fail")
logger.critical("critical")
logger.fatal("fatal")

logger.complete()
```

::: info
Level priority (`no`) determines filtering: lower values are more verbose. Set custom levels between existing ones (e.g., 15 between DEBUG=10 and INFO=20).
:::
