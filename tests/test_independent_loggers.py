from __future__ import annotations

from logly import Logger


def test_independent_logger_instances_have_separate_sinks() -> None:
    left_messages: list[str] = []
    right_messages: list[str] = []

    left = Logger()
    right = Logger()

    left.add(left_messages.append, level="TRACE", format="left:{message}")
    right.add(right_messages.append, level="TRACE", format="right:{message}")

    left.info("only left")
    right.info("only right")
    left.complete()
    right.complete()

    assert left_messages == ["left:only left\n"]
    assert right_messages == ["right:only right\n"]


def test_bound_logger_view_shares_parent_sinks() -> None:
    messages: list[str] = []
    logger = Logger()

    logger.add(messages.append, level="TRACE", format="{extra[component]}:{message}")
    worker = logger.bind(component="worker")

    worker.info("started")
    logger.complete()

    assert messages == ["worker:started\n"]
