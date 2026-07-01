"""Click integration example.

Shows how to replace ``click.echo`` with Logly's ``click_echo``
so all CLI output is routed through Logly.
"""

from __future__ import annotations

import click

from logly import logger
from logly.integrations.click import click_echo

# Replace Click's default echo with Logly-backed version
click.echo = click_echo


@click.command()
@click.option("--name", default="world", help="Name to greet.")
def cli(name: str) -> None:
    """Simple CLI that greets a user."""
    logger.info("CLI invoked with name={}", name)
    click.echo(f"Hello, {name}!")
    logger.success("CLI completed")


if __name__ == "__main__":
    cli()
