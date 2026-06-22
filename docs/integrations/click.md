---
title: Click
description: Route Click CLI output through Logly.
---

# Click

`click_echo` replaces `click.echo` to route all CLI output through Logly's logging system.

## Installation

This integration requires the `click` package.

::: code-group

```bash [uv]
uv add logly[click]
```

```bash [pip]
pip install "logly[click]"
```

```bash [uv (without extras)]
uv add click
```

```bash [pip (without extras)]
pip install click
```

:::

::: warning Missing Dependency
If `click` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'click'
```
:::

## Usage

```python
import click
from logly.integrations.click import click_echo

click.echo = click_echo

@click.command()
def cli():
    click.echo("This goes through Logly")
```

## Function Signature

`click_echo` has the same signature as `click.echo` as a drop-in alternative:

| Argument | Type | Description |
|----------|------|-------------|
| `message` | `Any` | Message to log |
| `file` | `Any` | Ignored (kept for compatibility) |
| `nl` | `bool` | Whether to append a newline |
| `err` | `bool` | Whether this is an error message (maps to WARNING level) |
| `color` | `bool \| None` | Ignored (kept for compatibility) |

## Tips

- Messages sent with `err=True` are logged at `WARNING` level; all others at `INFO`.
- Assign `click.echo = click_echo` early in your CLI entry point, before any commands run.

## Full Example

```python
import click
from logly import logger
from logly.integrations.click import click_echo

click.echo = click_echo

logger.add("cli.log", level="INFO")

@click.command()
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(name):
    click.echo(f"Hello, {name}!")
    click.echo("Done!", err=True)

if __name__ == "__main__":
    hello()
```
