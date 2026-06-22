---
title: Typer
description: Route Typer CLI output through Logly.
---

# Typer

`typer_echo` replaces `typer.echo` to route all CLI output through Logly's logging system.

## Installation

This integration requires the `typer` package.

::: code-group

```bash [uv]
uv add logly[typer]
```

```bash [pip]
pip install "logly[typer]"
```

```bash [uv (without extras)]
uv add typer
```

```bash [pip (without extras)]
pip install typer
```

:::

::: warning Missing Dependency
If `typer` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'typer'
```
:::

## Usage

```python
import typer
from logly.integrations.typer import typer_echo

typer.echo = typer_echo

app = typer.Typer()

@app.command()
def cli():
    typer.echo("This goes through Logly")
```

## Function Signature

`typer_echo` has the same signature as `typer.echo` as a drop-in alternative:

| Argument | Type | Description |
|----------|------|-------------|
| `message` | `Any` | Message to log |
| `file` | `Any` | Ignored (kept for compatibility) |
| `nl` | `bool` | Whether to append a newline |
| `err` | `bool` | Whether this is an error message (maps to WARNING level) |
| `color` | `bool \| None` | Ignored (kept for compatibility) |

## Tips

- Messages sent with `err=True` are logged at `WARNING` level; all others at `INFO`.
- Assign `typer.echo = typer_echo` early in your CLI entry point, before any commands run.

## Full Example

```python
import typer
from logly import logger
from logly.integrations.typer import typer_echo

typer.echo = typer_echo

app = typer.Typer()
logger.add("cli.log", level="INFO")

@app.command()
def greet(name: str):
    typer.echo(f"Hello, {name}!")
    typer.echo("Something went wrong", err=True)

if __name__ == "__main__":
    app()
```
