---
title: Color Markup
description: Use ANSI colors, styles, 256-color values, and RGB values in Logly output.
---

# Color Markup

This example writes colored records to the terminal. Set `colorize=True` for
ANSI-capable output; markup is removed for plain-text sinks.

```python
from logly import logger

logger.remove()
logger.add(
    "stderr",
    colorize=True,
    format="<level>{level}</level> | {message}",
)

logger.info("<bold><cyan>Readable structured output</cyan></bold>")
logger.success("<g>Success</g> with <u>underline</u>")
logger.info("<fg #00ffcc>True-color text</fg #00ffcc>")
logger.warning("<bg 24><white>256-color highlight</white></bg 24>")
logger.info(r"\\<red> is printed literally")
```

Example output (ANSI escape sequences omitted):

```text
INFO | Readable structured output
SUCCESS | Success with underline
INFO | True-color text
WARNING | 256-color highlight
INFO | <red> is printed literally
```
