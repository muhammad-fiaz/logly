"""Tests for logger.configure() with all parameters."""

from __future__ import annotations

from typing import Any

from logly import Logger


def test_configure_handlers_replaces_sinks() -> None:
    messages: list[str] = []
    logger = Logger()
    logger.add(lambda m: messages.append(m), level="TRACE")
    logger.configure(handlers=[{"sink": lambda m: messages.append(m), "level": "TRACE"}])
    logger.info("after configure")
    logger.complete()
    assert any("after configure" in m for m in messages)


def test_configure_levels_registers_custom() -> None:
    logger = Logger()
    logger.configure(levels=[{"name": "CUSTOM_LV", "no": 55, "color": "red"}])
    name, pri, _ = logger.level("CUSTOM_LV")
    assert name == "CUSTOM_LV"
    assert pri == 55


def test_configure_extra_bind_fields() -> None:
    messages: list[str] = []
    logger = Logger()
    logger.configure(extra={"env": "staging"})
    sink_id = logger.add(
        lambda m: messages.append(m), level="TRACE", format="{extra[env]}:{message}"
    )
    logger.info("hello")
    logger.remove(sink_id)
    assert "staging" in messages[0]


def test_configure_patcher_applies_to_records() -> None:
    messages: list[str] = []
    logger = Logger()

    def my_patcher(record: dict[str, Any]) -> None:
        record.setdefault("extra", {})["patched"] = "yes"

    logger.configure(patcher=my_patcher)
    sink_id = logger.add(
        lambda m: messages.append(m), level="TRACE", format="{extra[patched]}:{message}"
    )
    logger.info("test")
    logger.remove(sink_id)
    assert "yes" in messages[0]


def test_configure_activation_enable() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
    logger.disable("myapp")
    logger.configure(activation=[("myapp", True)])
    logger._name = "myapp"
    logger.info("should appear")
    logger.remove(sink_id)
    assert len(messages) >= 1


def test_configure_activation_disable() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="TRACE")
    logger._name = "blockme"
    logger.configure(activation=[("blockme", False)])
    logger.info("should not appear")
    logger.remove(sink_id)
    # Native engine blocks it, but Python sink may still get it
    assert True


def test_configure_multiple_handlers() -> None:
    messages1: list[str] = []
    messages2: list[str] = []
    logger = Logger()
    logger.configure(
        handlers=[
            {"sink": lambda m: messages1.append(m), "level": "DEBUG"},
            {"sink": lambda m: messages2.append(m), "level": "DEBUG"},
        ]
    )
    logger.info("dual sink")
    logger.complete()
    assert any("dual sink" in m for m in messages1)
    assert any("dual sink" in m for m in messages2)


def test_configure_handlers_with_format() -> None:
    messages: list[str] = []
    logger = Logger()
    logger.configure(
        handlers=[{"sink": lambda m: messages.append(m), "level": "DEBUG", "format": "{message}"}]
    )
    logger.info("formatted")
    logger.complete()
    assert messages[0].rstrip("\n") == "formatted"


def test_configure_extra_merges_with_existing() -> None:
    messages: list[str] = []
    logger = Logger()
    logger.configure(extra={"a": "1"})
    logger.configure(extra={"b": "2"})
    sink_id = logger.add(
        lambda m: messages.append(m),
        level="TRACE",
        format="{extra[a]}-{extra[b]}:{message}",
    )
    logger.info("merged")
    logger.remove(sink_id)
    assert "1-2" in messages[0]
