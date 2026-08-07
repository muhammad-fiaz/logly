---
title: Color markup
description: ANSI colors, styles, backgrounds, and escaping in Logly
---

# Color markup

Logly accepts markup in messages and format strings. A sink emits ANSI
sequences only when `colorize=True`; otherwise markup is removed.

## Colors and styles

Named colors are available as full names and short aliases:

```python
logger.info("<red>Error</red>")
logger.info("<g>Success</g>")
logger.info("<bold><u>Important</u></bold>")
```

Supported styles include `bold`, `dim`, `normal`, `italic`, `underline`,
`strike`, `reverse`, `blink`, and `hide` (aliases: `b`, `d`, `n`, `i`, `u`,
`s`, `v`, `l`, and `h`).

## Rich-style bracket syntax

Logly supports both `<tag>` (loguru-style) and `[tag]` (Rich-style) syntax:

```python
# Rich-style square brackets
logger.info("[red]Error[/red]")
logger.info("[bold]Important[/bold]")
logger.info("[bold red on white]Highlighted[/bold red on white]")

# Loguru-style angle brackets
logger.info("<red>Error</red>")
logger.info("<bold>Important</bold>")
```

### Rich-style features

```python
# Background colors with 'on' keyword
logger.info("[on red]White on red[/on red]")
logger.info("[bg blue]White on blue[/bg blue]")

# Compound styles
logger.info("[bold italic cyan]Bold italic cyan[/bold italic cyan]")
logger.info("[bold red on white]Bold red on white background[/bold red on white]")

# Hex colors
logger.info("[#ff8800]Orange text[/#ff8800]")
logger.info("[on #202020]White on dark[/on #202020]")

# RGB colors
logger.info("[rgb(255,128,0)]Orange text[/rgb(255,128,0)]")
logger.info("[on rgb(32,32,32)]White on dark[/on rgb(32,32,32)]")

# 256-color palette
logger.info("[color(208)]Orange text[/color(208)]")
logger.info("[on color(200)]White on pink[/on color(200)]")

# Negation (reset specific style)
logger.info("[bold][not bold]Not bold anymore[/not bold]")
```

## Comma-separated syntax (loguru-style)

For `<tag>` syntax, you can use commas to combine multiple styles:

```python
# Multiple styles with commas
logger.info("<bold, cyan>Bold cyan text</>")
logger.info("<b,c,>Same as above</>")

# Empty tokens are skipped
logger.info("<bold,,cyan>Bold cyan</>")

# Background via uppercase
logger.info("<RED>White on red</>")
logger.info("<LIGHT-RED>Bright white on bright red</>")
```

## 256-color and RGB values

Use `fg` and `bg` prefixes for explicit colors:

```python
logger.info("<fg 196>Bright red</fg 196>")
logger.info("<fg #ff8800>Orange</fg #ff8800>")
logger.info("<bg 24><white>Highlighted</white></bg 24>")
logger.info("<bg #202020><fg #00ff00>Green on dark</fg #00ff00></bg #202020>")
```

Palette indexes range from 0 to 255. Hex colors use six-digit `#RRGGBB`
values. Background names such as `<bg red>` and `<bg blue>` are supported.

## Level-aware formatting

Use `<level>` (or `<lvl>`) around a format token to apply the configured
color for the record's level:

```python
logger.add(
    "stderr",
    format="<green>{time}</green> | <level>{level}</level> | {message}",
    colorize=True,
)
```

Custom levels can provide their own color specification, including compound,
256-color, and RGB values.

When using the optional Rich integration, `RichSink` can be configured as a
sink for Rich console rendering while the same markup remains valid for the
standard console sink.

## Nesting and escaping

Tags can be nested. A short closing tag (`</>`) closes the current style.
Prefix a tag with a backslash to print it literally:

```python
logger.info("<bold><red>Error:</red></bold> connection failed")
logger.info(r"\<red> is printed literally")

# Rich-style escaping
logger.info(r"\[red] is printed literally")
```

The `strip_rich_tags()` helper removes markup and decodes common HTML entities
when preparing plain-text output.

## API Reference

```python
from logly import parse_rich_markup, strip_rich_tags

# Parse markup to ANSI
ansi_text = parse_rich_markup("<bold>hello</bold>", colorize=True)

# Strip tags to plain text
plain_text = strip_rich_tags("<bold>hello</bold>")
# Returns: "hello"
```
