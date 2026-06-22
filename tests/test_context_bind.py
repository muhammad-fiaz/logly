"""Tests for context binding (bind/contextualize/patch)."""

from __future__ import annotations

from logly import logger


class TestContextBind:
    """Tests for bind() context propagation."""

    def test_bind_adds_fields(self) -> None:
        """Bound fields should appear in log output."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        bound = logger.bind(service="api")
        sink_id = bound.add(capture, format="{extra[service]} | {message}")
        bound.info("bound test")
        bound.remove(sink_id)
        assert len(messages) >= 1
        assert "api" in messages[0]

    def test_bind_multiple_fields(self) -> None:
        """Multiple bound fields should all appear."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        bound = logger.bind(service="api", version="1.0")
        sink_id = bound.add(
            capture,
            format="{extra[service]}:{extra[version]} | {message}",
        )
        bound.info("multi-bind")
        bound.remove(sink_id)
        assert len(messages) >= 1
        assert "api:1.0" in messages[0]

    def test_bind_does_not_mutate_parent(self) -> None:
        """Binding on a clone should not affect the parent logger."""
        messages_parent = []
        messages_child = []

        def capture_parent(msg: str) -> None:
            messages_parent.append(msg)

        def capture_child(msg: str) -> None:
            messages_child.append(msg)

        sink_p = logger.add(capture_parent, format="{message}")
        child = logger.bind(service="api")
        sink_c = child.add(capture_child, format="{extra[service]} | {message}")

        logger.info("parent message")
        child.info("child message")

        logger.remove(sink_p)
        child.remove(sink_c)

        assert any("parent message" in m for m in messages_parent)
        assert any("api" in m for m in messages_child)

    def test_contextualize(self) -> None:
        """Contextualize should bind values within the scope."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(
            capture,
            format="{extra[request_id]} | {message}",
        )
        with logger.contextualize(request_id="abc-123"):
            logger.info("scoped message")
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "abc-123" in messages[0]

    def test_contextualize_restores_after_scope(self) -> None:
        """Context should be restored after contextualize scope exits."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(
            capture,
            format="{extra.get('request_id', 'none')} | {message}",
        )
        with logger.contextualize(request_id="in-scope"):
            logger.info("inside scope")
        logger.info("outside scope")
        logger.remove(sink_id)
        assert len(messages) >= 2
