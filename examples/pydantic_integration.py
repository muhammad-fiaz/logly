"""Pydantic integration example.

Demonstrates how to route Pydantic validation and application logs
through Logly using ``PydanticLogHandler``.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, ValidationError

from logly import logger
from logly.integrations.pydantic import PydanticLogHandler


class User(BaseModel):
    """Simple Pydantic model."""

    name: str
    age: int


def main() -> None:
    """Set up logging and trigger a validation error."""
    # Attach Logly handler to the root logger
    handler = PydanticLogHandler()
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)

    logger.info("Starting Pydantic integration demo")

    # Valid data
    user = User(name="Alice", age=30)
    logger.info("Created user: {}", user)

    # Invalid data – triggers validation error
    try:
        User(name="Bob", age="not_a_number")
    except ValidationError as exc:
        logger.error("Validation failed: {}", exc.errors())

    logger.success("Demo completed")


if __name__ == "__main__":
    main()
