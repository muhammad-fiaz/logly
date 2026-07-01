"""Typer integration for Logly.

Provides ``typer_echo`` that routes Typer CLI output through Logly.

Requires ``typer``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[typer]

    # Option 2: pip
    pip install "logly[typer]"

    # Option 3: uv without extras
    uv add typer

    # Option 4: pip without extras
    pip install typer
"""

from __future__ import annotations

from typing import Any

from logly import logger

_IMPORT_MSG = (  # pragma: no cover
    "typer is required for Logly Typer integration.\n"
    "Install with one of:\n"
    "  uv add logly[typer]       # recommended\n"
    "  pip install logly[typer]\n"
    "  uv add typer\n"
    "  pip install typer"
)  # pragma: no cover


def typer_echo(
    message: Any = None,
    file: Any = None,
    nl: bool = True,
    err: bool = False,
    color: bool | None = None,
    **kwargs: Any,
) -> None:
    """Log a message via Logly instead of Typer's default echo.

    This function replaces ``typer.echo`` to route all CLI output
    through Logly's logging system.

    Usage::

        import typer
        from logly.integrations.typer import typer_echo

        typer.echo = typer_echo

        app = typer.Typer()

        @app.command()
        def cli():
            typer.echo("This goes through Logly")

    Args:
        message: Message to log.
        file: Ignored - kept for ``typer.echo`` compatibility.
        nl: Whether to append a newline (used for level selection).
        err: Whether this is an error message.
        color: Ignored - kept for ``typer.echo`` compatibility.
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
