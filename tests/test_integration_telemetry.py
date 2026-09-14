from __future__ import annotations

from logly import Logger
from logly.integrations.http import HttpHandler
from logly.integrations.telemetry import HttpJsonSink, TelemetrySink


def test_telemetry_sink_receives_events() -> None:
    events: list[object] = []
    logger = Logger()

    logger.add(TelemetrySink(events.append), format="{level}:{message}")
    logger.warning("slow")

    assert events == [
        {"body": "WARNING:slow", "environment": None, "service.name": "logly"},
    ]


def test_http_json_sink_is_http_handler_compat() -> None:
    # Back-compat: telemetry.HttpJsonSink accepts legacy `endpoint` arg
    # and behaves like http.HttpHandler (write/flush/close, no raise).
    sink = HttpJsonSink("http://localhost:9/logs", timeout=0.1)
    assert isinstance(sink, HttpHandler)
    assert sink.url == "http://localhost:9/logs"
    assert sink.endpoint == "http://localhost:9/logs"
    sink.write("hello")
    sink.flush()
    sink.close()

    sink2 = HttpJsonSink(url="http://localhost:9/logs", timeout=0.1)
    assert sink2.url == "http://localhost:9/logs"
