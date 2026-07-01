"""Uvicorn integration example.

Routes Uvicorn access and error logs through Logly with structured formatting.
"""

from fastapi import FastAPI

from logly import logger
from logly.integrations.uvicorn import setup_uvicorn_logging

app = FastAPI()


@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    logger.debug("Health check passed")
    return {"status": "healthy"}


# Option 1: Setup logging in code before uvicorn.run()
setup_uvicorn_logging(level="INFO")

# Option 2: Pass log_config to uvicorn.run()
# uvicorn.run("examples.uvicorn_integration:app", log_config=get_log_config())

# Run with: uvicorn examples.uvicorn_integration:app --reload
