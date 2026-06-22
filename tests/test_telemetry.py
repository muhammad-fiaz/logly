from __future__ import annotations

from logly import Logger
from logly.integrations.telemetry import TelemetrySink


def test_telemetry_sink_receives_events() -> None:
    events: list[object] = []
    logger = Logger()

    logger.add(TelemetrySink(events.append), format="{level}:{message}")
    logger.warning("slow")

    assert events == [
        {"body": "WARNING:slow", "environment": None, "service.name": "logly"},
    ]
