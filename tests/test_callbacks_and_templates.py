"""Test callback functionality and template strings."""

import time
import threading
from pathlib import Path

import pytest

from logly import logger


def test_add_remove_callback():
    """Test adding and removing callbacks."""
    callback_calls = []

    def test_callback(record):
        callback_calls.append(record)

    # Add callback
    callback_id = logger.add_callback(test_callback)
    assert isinstance(callback_id, int)
    assert callback_id >= 0

    # Log a message - callback should be called
    logger.info("test message", test_field="value")
    logger.complete()  # Ensure callbacks complete

    # Wait a bit for async callback
    time.sleep(0.1)

    # Check callback was called
    assert len(callback_calls) == 1
    record = callback_calls[0]
    assert record["message"] == "test message"
    assert record["level"] == "INFO"
    assert record["test_field"] == "value"
    assert "timestamp" in record

    # Remove callback
    success = logger.remove_callback(callback_id)
    assert success is True

    # Log another message - callback should not be called
    callback_calls.clear()
    logger.info("another message")
    logger.complete()
    time.sleep(0.1)

    assert len(callback_calls) == 0

    # Try to remove non-existent callback
    success = logger.remove_callback(999)
    assert success is False


def test_multiple_callbacks():
    """Test multiple callbacks can be registered."""
    calls = []

    def callback1(record):
        calls.append(f"cb1: {record['message']}")

    def callback2(record):
        calls.append(f"cb2: {record['message']}")

    # Add both callbacks
    id1 = logger.add_callback(callback1)
    id2 = logger.add_callback(callback2)

    # Log message
    logger.info("multi callback test")
    logger.complete()
    time.sleep(0.1)

    # Both should have been called
    assert len(calls) == 2
    assert "cb1: multi callback test" in calls
    assert "cb2: multi callback test" in calls

    # Remove one callback
    logger.remove_callback(id1)
    calls.clear()

    # Log again - only second callback should fire
    logger.info("single callback test")
    logger.complete()
    time.sleep(0.1)

    assert len(calls) == 1
    assert "cb2: single callback test" in calls

    # Clean up
    logger.remove_callback(id2)


def test_callback_exception_handling():
    """Test that callback exceptions don't break logging."""

    def failing_callback(record):
        raise ValueError("Callback failed")

    def working_callback(record):
        working_callback.called = True

    working_callback.called = False

    # Add both callbacks
    fail_id = logger.add_callback(failing_callback)
    work_id = logger.add_callback(working_callback)

    # Log message - failing callback should not break working one
    logger.info("exception test")
    logger.complete()
    time.sleep(0.1)

    # Working callback should still have been called
    assert working_callback.called

    # Clean up
    logger.remove_callback(fail_id)
    logger.remove_callback(work_id)


def test_callback_with_context():
    """Test callbacks receive bound context."""
    records = []

    def context_callback(record):
        records.append(record)

    callback_id = logger.add_callback(context_callback)

    # Bind some context
    bound_logger = logger.bind(user="alice", session="s123")

    # Log with additional context
    bound_logger.info("context test", action="login")
    logger.complete()
    time.sleep(0.1)

    # Check callback received all context
    assert len(records) == 1
    record = records[0]
    assert record["user"] == "alice"
    assert record["session"] == "s123"
    assert record["action"] == "login"
    assert record["message"] == "context test"

    logger.remove_callback(callback_id)


def test_template_strings():
    """Test template string functionality."""
    # This would test template strings if implemented
    # For now, just ensure basic logging still works
    logger.info("template test {name}", name="value")
    logger.complete()


def test_callback_threading():
    """Test that callbacks run in background threads."""
    thread_ids = []

    def thread_callback(record):
        thread_ids.append(threading.current_thread().ident)

    callback_id = logger.add_callback(thread_callback)

    # Get main thread ID
    main_thread = threading.current_thread().ident

    logger.info("thread test")
    logger.complete()
    time.sleep(0.1)

    # Callback should have run in a different thread
    assert len(thread_ids) == 1
    assert thread_ids[0] != main_thread

    logger.remove_callback(callback_id)
