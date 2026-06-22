"""Tests for serialize=True on add()."""

from __future__ import annotations

import json

from logly import Logger


def test_serialize_json_output(tmp_path) -> None:
    logger = Logger()
    log_file = tmp_path / "json.log"
    sink_id = logger.add(log_file, level="DEBUG", format="{message}", serialize=True)
    logger.info("json test")
    logger.complete()
    logger.remove(sink_id)
    content = log_file.read_text(encoding="utf-8").strip()
    data = json.loads(content)
    assert isinstance(data, dict)
    assert "message" in data


def test_serialize_contains_message() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(
        lambda m: messages.append(m), level="DEBUG", format="{message}", serialize=True
    )
    logger.info("serialized msg")
    logger.remove(sink_id)
    # serialize=True with callable sink may still produce JSON
    assert len(messages) >= 1


def test_serialize_with_extra_fields(tmp_path) -> None:
    logger = Logger()
    log_file = tmp_path / "extra.json"
    sink_id = logger.add(log_file, level="DEBUG", format="{message}", serialize=True)
    bound = logger.bind(service="api")
    bound._name = "myapp"
    bound.info("extra test")
    logger.complete()
    logger.remove(sink_id)
    content = log_file.read_text(encoding="utf-8").strip()
    data = json.loads(content)
    assert "extra" in data


def test_serialize_with_file_handler(tmp_path) -> None:
    logger = Logger()
    log_file = tmp_path / "serialize.log"
    sink_id = logger.add(log_file, level="DEBUG", format="{level}:{message}", serialize=True)
    logger.warning("warning json")
    logger.complete()
    logger.remove(sink_id)
    content = log_file.read_text(encoding="utf-8").strip()
    data = json.loads(content)
    assert data["level"] == "WARNING"


def test_serialize_false_produces_plain_text(tmp_path) -> None:
    logger = Logger()
    log_file = tmp_path / "plain.log"
    sink_id = logger.add(log_file, level="DEBUG", format="{message}", serialize=False)
    logger.info("plain text")
    logger.complete()
    logger.remove(sink_id)
    content = log_file.read_text(encoding="utf-8").strip()
    assert content == "plain text"
