"""Typer integration example.

Shows how to replace ``typer.echo`` with Logly's ``typer_echo``
so all CLI output is routed through Logly.
"""

from __future__ import annotations

import typer

from logly import logger
from logly.integrations.typer import typer_echo

# Replace Typer's default echo with Logly-backed version
typer.echo = typer_echo

app = typer.Typer()


@app.command()
def hello(name: str = typer.Option("world", help="Name to greet.")) -> None:
    """Greet someone."""
    logger.info("CLI invoked with name={}", name)
    typer.echo(f"Hello, {name}!")
    logger.success("CLI completed")


if __name__ == "__main__":
    app()
