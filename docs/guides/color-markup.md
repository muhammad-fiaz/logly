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
```

The `strip_rich_tags()` helper removes markup and decodes common HTML entities
when preparing plain-text output.
