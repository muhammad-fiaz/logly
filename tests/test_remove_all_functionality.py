"""Test remove_all() functionality and removed sink error handling."""

from pathlib import Path
import pytest
from logly import logger


def read_log(path: Path) -> str:
    """Read log file content."""
    assert path.exists()
    return path.read_text()


def test_remove_all_basic(tmp_path: Path):
    """Test basic remove_all() functionality."""
    logger._inner._reset_for_tests()

    # Add multiple sinks
    p1 = tmp_path / "app1.log"
    p2 = tmp_path / "app2.log"
    p3 = tmp_path / "app3.log"

    logger.add(str(p1))
    logger.add(str(p2))
    logger.add(str(p3))

    logger.configure(level="INFO", color=False, console=False)
    logger.info("before remove_all")
    logger.complete()

    # Verify files were created and contain data
    assert p1.exists()
    assert p2.exists()
    assert p3.exists()
    assert "before remove_all" in read_log(p1)
    assert "before remove_all" in read_log(p2)
    assert "before remove_all" in read_log(p3)

    # Remove all sinks
    count = logger.remove_all()
    assert count == 3, f"Expected to remove 3 sinks, got {count}"

    # Log after removal - should not write to any file
    logger.info("after remove_all")
    logger.complete()

    # Files should still exist but not contain new message
    content1 = read_log(p1)
    content2 = read_log(p2)
    content3 = read_log(p3)

    assert "after remove_all" not in content1
    assert "after remove_all" not in content2
    assert "after remove_all" not in content3


def test_remove_all_returns_count(tmp_path: Path):
    """Test that remove_all() returns the correct count of removed sinks."""
    logger._inner._reset_for_tests()

    # Test with no sinks
    count = logger.remove_all()
    assert count == 0, "Should return 0 when no sinks exist"

    # Test with 1 sink
    p1 = tmp_path / "test1.log"
    logger.add(str(p1))
    count = logger.remove_all()
    assert count == 1, "Should return 1 when 1 sink exists"

    # Test with multiple sinks
    p2 = tmp_path / "test2.log"
    p3 = tmp_path / "test3.log"
    p4 = tmp_path / "test4.log"
    p5 = tmp_path / "test5.log"

    logger.add(str(p2))
    logger.add(str(p3))
    logger.add(str(p4))
    logger.add(str(p5))

    count = logger.remove_all()
    assert count == 4, "Should return 4 when 4 sinks exist"


def test_remove_all_multiple_times(tmp_path: Path):
    """Test calling remove_all() multiple times."""
    logger._inner._reset_for_tests()

    p = tmp_path / "multi.log"
    logger.add(str(p))
    logger.add(str(p))

    # First call should remove sinks
    count1 = logger.remove_all()
    assert count1 == 2

    # Second call should return 0
    count2 = logger.remove_all()
    assert count2 == 0

    # Third call should also return 0
    count3 = logger.remove_all()
    assert count3 == 0


def test_remove_all_with_mixed_sinks(tmp_path: Path):
    """Test remove_all() with different types of sinks."""
    logger._inner._reset_for_tests()

    # Add file sinks with different configurations
    p1 = tmp_path / "sync.log"
    p2 = tmp_path / "async.log"
    p3 = tmp_path / "json.log"

    logger.add(str(p1), async_write=False)  # noqa: F841
    logger.add(str(p2), async_write=True)  # noqa: F841
    logger.add(str(p3), json=True)  # noqa: F841

    logger.configure(level="INFO", color=False, console=False)
    logger.info("test message")
    logger.complete()

    # Verify all files exist
    assert p1.exists()
    assert p2.exists()
    assert p3.exists()

    # Remove all sinks
    count = logger.remove_all()
    assert count == 3


def test_remove_all_then_add_new_sinks(tmp_path: Path):
    """Test adding new sinks after remove_all()."""
    logger._inner._reset_for_tests()

    # Add initial sinks
    p1 = tmp_path / "old1.log"
    p2 = tmp_path / "old2.log"

    logger.add(str(p1))
    logger.add(str(p2))
    logger.configure(level="INFO", color=False, console=False)

    logger.info("old message")
    logger.complete()

    # Remove all sinks
    count = logger.remove_all()
    assert count == 2

    # Add new sinks
    p3 = tmp_path / "new1.log"
    p4 = tmp_path / "new2.log"

    logger.add(str(p3))
    logger.add(str(p4))

    logger.info("new message")
    logger.complete()

    # Old files should not contain new message
    assert "new message" not in read_log(p1)
    assert "new message" not in read_log(p2)

    # New files should contain new message
    assert p3.exists()
    assert p4.exists()
    assert "new message" in read_log(p3)
    assert "new message" in read_log(p4)


def test_remove_all_clears_file_writers(tmp_path: Path):
    """Test that remove_all() properly clears file writers."""
    logger._inner._reset_for_tests()

    p1 = tmp_path / "writer1.log"
    p2 = tmp_path / "writer2.log"

    logger.add(str(p1))
    logger.add(str(p2))

    logger.configure(level="INFO", color=False, console=False)
    logger.info("before clear")
    logger.complete()

    # Remove all sinks
    logger.remove_all()

    # Try to log again - should not crash
    logger.info("after clear")
    logger.complete()

    # Old files should not have the new message
    content1 = read_log(p1)
    content2 = read_log(p2)
    assert "after clear" not in content1
    assert "after clear" not in content2


def test_remove_all_with_async_senders(tmp_path: Path):
    """Test that remove_all() properly clears async senders."""
    logger._inner._reset_for_tests()

    p1 = tmp_path / "async1.log"
    p2 = tmp_path / "async2.log"

    # Add async sinks
    logger.add(str(p1), async_write=True)
    logger.add(str(p2), async_write=True)

    logger.configure(level="INFO", color=False, console=False)
    logger.info("async message")
    logger.complete()

    assert p1.exists()
    assert p2.exists()

    # Remove all sinks
    count = logger.remove_all()
    assert count == 2

    # Log after removal - should not crash or write
    logger.info("post removal")
    logger.complete()

    # Files should not contain post-removal message
    content1 = read_log(p1)
    content2 = read_log(p2)
    assert "post removal" not in content1
    assert "post removal" not in content2


def test_remove_all_does_not_affect_callbacks(tmp_path: Path):
    """Test that remove_all() does not remove callbacks."""
    import time

    logger._inner._reset_for_tests()

    # Track callback invocations
    callback_called = []

    def test_callback(record):
        callback_called.append(record.get("message"))

    # Add callback and sinks
    callback_id = logger.add_callback(test_callback)

    p = tmp_path / "callback_test.log"
    logger.add(str(p))

    logger.configure(level="INFO", color=False, console=False)
    logger.info("with sink")
    logger.complete()
    time.sleep(0.1)  # Give callbacks time to execute

    # Remove all sinks
    logger.remove_all()

    # Callback should still work
    logger.info("without sink")
    logger.complete()
    time.sleep(0.1)  # Give callbacks time to execute

    # Callback should have been called both times
    assert len(callback_called) >= 2, (
        f"Expected at least 2 callbacks, got {len(callback_called)}: {callback_called}"
    )
    assert "with sink" in callback_called
    assert "without sink" in callback_called

    # File should only have first message
    content = read_log(p)
    assert "with sink" in content
    assert "without sink" not in content

    # Clean up callback
    logger.remove_callback(callback_id)


def test_remove_all_isolation(tmp_path: Path):
    """Test that remove_all() is properly isolated per logger instance."""
    logger._inner._reset_for_tests()

    # Create bound logger instances
    logger1 = logger.bind(instance="logger1")
    logger2 = logger.bind(instance="logger2")

    p1 = tmp_path / "logger1.log"
    p2 = tmp_path / "logger2.log"

    # Both loggers share the same underlying sinks
    logger.add(str(p1))
    logger.add(str(p2))

    logger.configure(level="INFO", color=False, console=False)

    logger1.info("message1")
    logger2.info("message2")
    logger.complete()

    # Both files should exist
    assert p1.exists()
    assert p2.exists()

    # Remove all sinks affects both logger instances
    count = logger.remove_all()
    assert count == 2

    # Neither logger should write after removal
    logger1.info("after_removal1")
    logger2.info("after_removal2")
    logger.complete()

    content1 = read_log(p1)
    content2 = read_log(p2)

    assert "after_removal1" not in content1
    assert "after_removal2" not in content2


def test_remove_all_idempotent(tmp_path: Path):
    """Test that remove_all() is idempotent (safe to call multiple times)."""
    logger._inner._reset_for_tests()

    p = tmp_path / "idempotent.log"
    logger.add(str(p))

    # Call remove_all() 5 times
    for i in range(5):
        count = logger.remove_all()
        if i == 0:
            assert count == 1, "First call should remove 1 sink"
        else:
            assert count == 0, f"Call {i + 1} should remove 0 sinks"


def test_remove_all_with_rotation(tmp_path: Path):
    """Test remove_all() with sinks that have rotation enabled."""
    logger._inner._reset_for_tests()

    p1 = tmp_path / "rotate_daily.log"
    p2 = tmp_path / "rotate_hourly.log"

    logger.add(str(p1), rotation="daily")
    logger.add(str(p2), rotation="hourly")

    logger.configure(level="INFO", color=False, console=False)
    logger.info("rotation test")
    logger.complete()

    # Remove all sinks
    count = logger.remove_all()
    assert count == 2

    # Should not crash when trying to log
    logger.info("after rotation removal")
    logger.complete()


def test_remove_all_with_size_limit(tmp_path: Path):
    """Test remove_all() with sinks that have size limits."""
    logger._inner._reset_for_tests()

    p = tmp_path / "size_limit.log"
    logger.add(str(p), size_limit="1MB")

    logger.configure(level="INFO", color=False, console=False)
    logger.info("size limit test")
    logger.complete()

    # Remove all sinks
    count = logger.remove_all()
    assert count == 1


def test_remove_all_empty_state(tmp_path: Path):
    """Test remove_all() on a freshly initialized logger."""
    logger._inner._reset_for_tests()

    # Call remove_all() without adding any sinks
    count = logger.remove_all()
    assert count == 0, "Should return 0 when no sinks have been added"

    # Should not crash
    logger.info("test message")
    logger.complete()


def test_remove_specific_then_remove_all(tmp_path: Path):
    """Test remove() followed by remove_all()."""
    logger._inner._reset_for_tests()

    p1 = tmp_path / "test1.log"
    p2 = tmp_path / "test2.log"
    p3 = tmp_path / "test3.log"

    logger.add(str(p1))
    h2 = logger.add(str(p2))
    logger.add(str(p3))

    # Remove one specific sink
    result = logger.remove(h2)
    assert result is True

    # Now remove all remaining sinks
    count = logger.remove_all()
    assert count == 2, "Should have 2 remaining sinks"


def test_remove_all_then_remove_specific(tmp_path: Path):
    """Test remove_all() followed by remove() on non-existent sink."""
    logger._inner._reset_for_tests()

    p = tmp_path / "test.log"
    h = logger.add(str(p))

    # Remove all sinks
    count = logger.remove_all()
    assert count == 1

    # Try to remove the already-removed sink (should not crash)
    result = logger.remove(h)
    assert result is True, "remove() should return True for non-existent handler (no-op)"


def test_remove_all_thread_safety(tmp_path: Path):
    """Test remove_all() thread safety with concurrent logging."""
    import threading
    import time

    logger._inner._reset_for_tests()

    p = tmp_path / "concurrent.log"
    logger.add(str(p), async_write=True)
    logger.configure(level="INFO", color=False, console=False)

    stop_flag = threading.Event()

    def log_continuously():
        """Log messages continuously until stopped."""
        counter = 0
        while not stop_flag.is_set():
            logger.info(f"concurrent message {counter}")
            counter += 1
            time.sleep(0.001)

    # Start logging thread
    log_thread = threading.Thread(target=log_continuously)
    log_thread.start()

    # Let it log for a bit
    time.sleep(0.05)

    # Remove all sinks while logging is happening
    count = logger.remove_all()
    assert count == 1

    # Stop logging thread
    stop_flag.set()
    log_thread.join(timeout=2.0)

    logger.complete()

    # Should not crash
    assert True


def test_remove_all_performance(tmp_path: Path):
    """Test remove_all() performance with many sinks."""
    import time

    logger._inner._reset_for_tests()

    # Add many sinks
    num_sinks = 100
    for i in range(num_sinks):
        p = tmp_path / f"perf_{i}.log"
        logger.add(str(p))

    # Measure remove_all() time
    start = time.perf_counter()
    count = logger.remove_all()
    elapsed = time.perf_counter() - start

    assert count == num_sinks
    assert elapsed < 1.0, f"remove_all() took {elapsed:.3f}s, expected < 1.0s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
