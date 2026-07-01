"""Click integration for Logly.

Provides ``click_echo`` that routes Click CLI output through Logly.

Requires ``click``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[click]

    # Option 2: pip
    pip install "logly[click]"

    # Option 3: uv without extras
    uv add click

    # Option 4: pip without extras
    pip install click
"""

from __future__ import annotations

from typing import Any

from logly import logger

_IMPORT_MSG = (  # pragma: no cover
    "click is required for Logly Click integration.\n"
    "Install with one of:\n"
    "  uv add logly[click]       # recommended\n"
    "  pip install logly[click]\n"
    "  uv add click\n"
    "  pip install click"
)  # pragma: no cover


def click_echo(
    message: Any = None,
    file: Any = None,
    nl: bool = True,
    err: bool = False,
    color: bool | None = None,
    **kwargs: Any,
) -> None:
    """Log a message via Logly instead of Click's default echo.

    This function replaces ``click.echo`` to route all CLI output
    through Logly's logging system.

    Usage::

        import click
        from logly.integrations.click import click_echo

        click.echo = click_echo

        @click.command()
        def cli():
            click.echo("This goes through Logly")

    Args:
        message: Message to log.
        file: Ignored - kept for ``click.echo`` compatibility.
        nl: Whether to append a newline (used for level selection).
        err: Whether this is an error message.
        color: Ignored - kept for ``click.echo`` compatibility.
        **kwargs: Additional keyword arguments (ignored).
    """
    if message is None:
        return

    msg = str(message)
    level = "WARNING" if err else "INFO"

    try:
        logger.log(level, msg)
    except Exception:
        pass
