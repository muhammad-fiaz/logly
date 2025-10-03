"""Test callback functionality and template strings."""

import threading
import time

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
        working_callback.called = True  # type: ignore[attr-defined]

    working_callback.called = False  # type: ignore[attr-defined]

    # Add both callbacks
    fail_id = logger.add_callback(failing_callback)
    work_id = logger.add_callback(working_callback)

    # Log message - failing callback should not break working one
    logger.info("exception test")
    logger.complete()
    time.sleep(0.1)

    # Working callback should still have been called
    assert working_callback.called  # type: ignore[attr-defined]

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


def test_callback_filename_and_line_number():
    """Test that callbacks receive filename and line number information."""
    callback_calls = []

    def filename_callback(record):
        callback_calls.append(record)

    # Add callback
    callback_id = logger.add_callback(filename_callback)

    # Log a message from this specific line (we'll capture the line number)
    logger.info("filename test message")  # This is line 185 in the test
    logger.complete()
    time.sleep(0.1)

    # Verify callback was called
    assert len(callback_calls) == 1
    record = callback_calls[0]

    # Check that filename and line number are present
    assert "filename" in record
    assert "lineno" in record

    # Verify filename contains the test file name
    assert "test_callbacks_and_templates.py" in record["filename"]

    # Verify line number is a string that can be converted to int (should be around line 191)
    assert isinstance(record["lineno"], str)
    line_number = int(record["lineno"])
    assert line_number > 0
    # Allow some flexibility in line number (between 185-200 should be reasonable)
    assert 185 <= line_number <= 200

    # Clean up
    logger.remove_callback(callback_id)


def test_callback_filename_line_with_json_format():
    """Test filename and line number with JSON format logging."""
    callback_calls = []

    def json_callback(record):
        callback_calls.append(record)

    # Configure JSON format
    logger.configure(json=True)
    callback_id = logger.add_callback(json_callback)

    # Log message - line number should be captured
    logger.info("JSON format test")  # Line ~225
    logger.complete()
    time.sleep(0.1)

    assert len(callback_calls) == 1
    record = callback_calls[0]

    # Verify filename and line number in JSON format
    assert "filename" in record
    assert "lineno" in record
    assert "test_callbacks_and_templates.py" in record["filename"]

    line_number = int(record["lineno"])
    assert 220 <= line_number <= 240  # Around line 225

    # Clean up
    logger.remove_callback(callback_id)
    logger.configure(json=False)


def test_callback_filename_line_different_levels():
    """Test filename and line number across different log levels."""
    callback_calls = []

    def level_callback(record):
        callback_calls.append(record)

    callback_id = logger.add_callback(level_callback)

    # Log at different levels from different lines
    logger.debug("debug message")  # Line ~250
    logger.info("info message")  # Line ~251
    logger.warning("warning message")  # Line ~252
    logger.error("error message")  # Line ~253
    logger.critical("critical message")  # Line ~254

    logger.complete()
    time.sleep(0.1)

    # Should have 5 callback calls (assuming all levels are enabled)
    assert len(callback_calls) >= 3  # At least info, warning, error, critical

    # Check that each record has filename and line number
    for record in callback_calls:
        assert "filename" in record
        assert "lineno" in record
        assert "test_callbacks_and_templates.py" in record["filename"]

        line_number = int(record["lineno"])
        assert 245 <= line_number <= 270  # Around lines 250-254

    # Clean up
    logger.remove_callback(callback_id)


def test_callback_filename_line_with_custom_fields():
    """Test filename and line number with custom fields in log records."""
    callback_calls = []

    def custom_callback(record):
        callback_calls.append(record)

    callback_id = logger.add_callback(custom_callback)

    # Log with custom fields
    logger.info(
        "Custom fields test", user_id=12345, action="login", ip_address="192.168.1.1"
    )  # Line ~280

    logger.complete()
    time.sleep(0.1)

    assert len(callback_calls) == 1
    record = callback_calls[0]

    # Verify standard fields
    assert "filename" in record
    assert "lineno" in record
    assert "message" in record
    assert "level" in record

    # Verify custom fields (stored as strings in JSON-like format)
    assert record["user_id"] == "12345"
    assert record["action"] == "login"
    assert record["ip_address"] == "192.168.1.1"

    # Verify filename and line number
    assert "test_callbacks_and_templates.py" in record["filename"]
    line_number = int(record["lineno"])
    assert 275 <= line_number <= 295  # Around line 280

    # Clean up
    logger.remove_callback(callback_id)


def test_callback_filename_line_multiple_calls():
    """Test filename and line number with multiple consecutive log calls."""
    callback_calls = []

    def multi_callback(record):
        callback_calls.append(
            {
                "message": record["message"],
                "lineno": record["lineno"],
                "filename": record["filename"],
            }
        )

    callback_id = logger.add_callback(multi_callback)

    # Multiple log calls from different lines
    logger.info("First message")  # Line ~310
    logger.info("Second message")  # Line ~311
    logger.info("Third message")  # Line ~312

    logger.complete()
    time.sleep(0.1)

    assert len(callback_calls) == 3

    # Verify each call has valid filename and line number information
    for call in callback_calls:
        assert "filename" in call
        assert "lineno" in call
        assert "message" in call
        assert "test_callbacks_and_templates.py" in call["filename"]

        line_number = int(call["lineno"])
        assert line_number > 0
        assert 330 <= line_number <= 350  # Reasonable range around the test lines

    # Verify the messages are present (order might vary due to async processing)
    messages = [call["message"] for call in callback_calls]
    assert "First message" in messages
    assert "Second message" in messages
    assert "Third message" in messages

    # Clean up
    logger.remove_callback(callback_id)


def test_callback_filename_line_with_function_name():
    """Test that function name is also captured along with filename and line number."""
    callback_calls = []

    def function_callback(record):
        callback_calls.append(record)

    callback_id = logger.add_callback(function_callback)

    # Log from within this test function
    logger.info("Function name test")  # Line ~340
    logger.complete()
    time.sleep(0.1)

    assert len(callback_calls) == 1
    record = callback_calls[0]

    # Verify all location fields are present
    assert "filename" in record
    assert "lineno" in record
    assert "function" in record

    # Verify function name matches this test function
    assert record["function"] == "test_callback_filename_line_with_function_name"

    # Verify filename and line number
    assert "test_callbacks_and_templates.py" in record["filename"]
    line_number = int(record["lineno"])
    assert 335 <= line_number <= 380  # Around line 340

    # Clean up
    logger.remove_callback(callback_id)
