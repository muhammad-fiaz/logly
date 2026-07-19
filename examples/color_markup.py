"""Demonstrate Logly ANSI markup and explicit colors."""

from logly import logger

logger.remove()
logger.add("stderr", colorize=True, format="<level>{level}</level> | {message}")

logger.info("<g>Success</g> with <u>underline</u>")
logger.error("<fg #ff8800>Orange error</fg #ff8800>")
logger.info("<bg 24><white>256-color highlight</white></bg 24>")
logger.info(r"\<red> is literal markup")
