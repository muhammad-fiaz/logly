from logly import Logly

# Create a Logly instance
logly = Logly()

# Start logging
logly.start_logging()

# Set default file path and max file size
logly.set_default_file_path("../c.txt")
logly.set_default_max_file_size(50)

# Log messages with different levels and colors
logly.info("Key1", "Value1", color=logly.COLOR.CYAN)
logly.warn("Key2", "Value2", color=logly.COLOR.YELLOW)
logly.error("Key3", "Value3", color=logly.COLOR.RED)
logly.debug("Key4", "Value4", color=logly.COLOR.BLUE)
logly.critical("Key5", "Value5", color=logly.COLOR.CRITICAL)
logly.fatal("Key6", "Value6", color=logly.COLOR.CRITICAL)
logly.trace("Key7", "Value7", color=logly.COLOR.BLUE)
logly.log("Key8", "Value8", color=logly.COLOR.WHITE)

# Stop logging (no messages will be displayed or logged after this point)
logly.stop_logging()

# Log more messages after stopping logging (these won't be displayed or logged)
logly.info("AnotherKey1", "AnotherValue1", color=logly.COLOR.CYAN)
logly.warn("AnotherKey2", "AnotherValue2", color=logly.COLOR.YELLOW)
logly.error("AnotherKey3", "AnotherValue3", color=logly.COLOR.RED)

# Start logging again
logly.start_logging()

# Log messages with default settings (using default file path and max file size)
logly.info("DefaultKey1", "DefaultValue1")
logly.warn("DefaultKey2", "DefaultValue2")
logly.error("DefaultKey3", "DefaultValue3" ,log_to_file=False)

# Log messages with custom file path and max file size
logly.info("CustomKey1", "CustomValue1", file_path="path/c.txt", max_file_size=25)
logly.warn("CustomKey2", "CustomValue2", file_path="path/c.txt", max_file_size=25)

# Access color constants directly
logly.info("Accessing color directly", "DirectColorValue", color=logly.COLOR.RED)

# Display logged messages
print("Logged Messages:")
for message in logly.logged_messages:
    print(message)
