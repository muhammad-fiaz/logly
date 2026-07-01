"""Starlette integration example.

Demonstrates how to add ``LoglyMiddleware`` to a Starlette ASGI application
for request context logging with ``request_id``, timing, etc.

Run with::

    uvicorn examples.starlette_integration:app --reload
"""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from logly import logger
from logly.integrations.starlette import LoglyMiddleware


async def homepage(request: Request) -> JSONResponse:
    """Handle GET /."""
    logger.info("Homepage requested")
    return JSONResponse({"message": "Hello from Logly + Starlette"})


async def greet(request: Request) -> JSONResponse:
    """Handle GET /greet/{name}."""
    name = request.path_params["name"]
    logger.info("Greeting user {}", name)
    return JSONResponse({"greeting": f"Hello, {name}!"})


app = Starlette(
    routes=[
        Route("/", homepage),
        Route("/greet/{name}", greet),
    ],
)
app.add_middleware(LoglyMiddleware)
