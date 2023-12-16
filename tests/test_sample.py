# test_logly_integration.py
import os
import pytest

from logly import Logly
from logly import exception

@pytest.fixture
def logly_instance():
    """
    Fixture to create and return a Logly instance for testing.

    Returns:
    - Logly: A Logly instance with logging started.
    """
    logly = Logly()
    logly.start_logging()
    return logly

def test_logly_integration(logly_instance):
    """
    Test the integration of Logly by logging messages with different levels and colors.

    Parameters:
    - logly_instance (Logly): The Logly instance created by the fixture.
    """
    # Log messages with different levels and colors
    logly_instance.info("Key1", "Value1", color=logly_instance.COLOR.CYAN)
    logly_instance.warn("Key2", "Value2", color=logly_instance.COLOR.YELLOW)
    logly_instance.error("Key3", "Value3", color=logly_instance.COLOR.RED)
    logly_instance.debug("Key4", "Value4", color=logly_instance.COLOR.BLUE)
    logly_instance.critical("Key5", "Value5", color=logly_instance.COLOR.CRITICAL)
    logly_instance.fatal("Key6", "Value6", color=logly_instance.COLOR.CRITICAL)
    logly_instance.trace("Key7", "Value7", color=logly_instance.COLOR.BLUE)
    logly_instance.log("Key8", "Value8", color=logly_instance.COLOR.WHITE)

    # Stop logging
    logly_instance.stop_logging()

    # Log more messages after stopping logging (these won't be displayed or logged)
    logly_instance.info("AnotherKey1", "AnotherValue1", color=logly_instance.COLOR.CYAN)
    logly_instance.warn("AnotherKey2", "AnotherValue2", color=logly_instance.COLOR.YELLOW)
    logly_instance.error("AnotherKey3", "AnotherValue3", color=logly_instance.COLOR.RED)

    # Start logging again
    logly_instance.start_logging()

    # Log messages with default settings (using default file path and max file size)
    logly_instance.info("DefaultKey1", "DefaultValue1")
    logly_instance.warn("DefaultKey2", "DefaultValue2")
    logly_instance.error("DefaultKey3", "DefaultValue3", log_to_file=False)

    # Log messages with custom file path and max file size
    logly_instance.info("CustomKey1", "CustomValue1", file_path="path/log.txt", max_file_size=25)
    logly_instance.warn("CustomKey2", "CustomValue2", file_path="path/log.txt",auto=True, max_file_size=25)

    # Access color constants directly
    logly_instance.info("Accessing color directly", "DirectColorValue", color=logly_instance.COLOR.RED)

    # Display logged messages
    for message in logly_instance.logged_messages:
        print(message)
