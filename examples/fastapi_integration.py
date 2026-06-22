"""FastAPI integration example."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from logly import logger
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)  # type: ignore[arg-type]


@app.get("/")
async def root() -> dict[str, Any]:
    logger.info("Root endpoint called")
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict[str, Any]:
    logger.info("Reading item {}", item_id)
    return {"item_id": item_id}


# Run with: uvicorn examples.fastapi_integration:app --reload
