"""Tests for opt(depth=N) and opt(capture=True/False)."""

from __future__ import annotations

from logly import Logger


def test_depth_zero_same_frame() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}|{function}")
    logger.opt(depth=0).info("zero depth")
    logger.remove(sink_id)
    assert "test_depth_zero_same_frame" in messages[0]


def test_depth_one_skips_frame() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}|{function}")
    logger.opt(depth=1).info("one depth")
    logger.remove(sink_id)
    # Should skip the current frame and show the caller of the caller
    assert len(messages) == 1


def test_depth_two_skips_two_frames() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}|{function}")
    logger.opt(depth=2).info("two depth")
    logger.remove(sink_id)
    assert len(messages) == 1


def test_capture_true_includes_caller() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}|{function}")
    logger.opt(capture=True).info("captured")
    logger.remove(sink_id)
    assert len(messages) == 1
    assert "captured" in messages[0]


def test_capture_false_skips_caller_info() -> None:
    logger = Logger()
    messages: list[str] = []

    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
    logger.opt(capture=False).info("no capture")
    logger.remove(sink_id)
    assert len(messages) == 1


def test_depth_does_not_mutate_parent() -> None:
    logger = Logger()
    messages1: list[str] = []
    messages2: list[str] = []

    sink_id1 = logger.add(
        lambda m: messages1.append(m), level="DEBUG", format="{message}|{function}"
    )
    sink_id2 = logger.add(
        lambda m: messages2.append(m), level="DEBUG", format="{message}|{function}"
    )
    logger.opt(depth=2).info("depth view")
    logger.info("normal view")
    logger.remove(sink_id1)
    logger.remove(sink_id2)
    assert len(messages1) == 2
    assert len(messages2) == 2
    assert "test_depth_does_not_mutate_parent" in messages1[1]
    assert "test_depth_does_not_mutate_parent" in messages2[1]
