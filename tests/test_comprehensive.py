"""Comprehensive feature verification test."""

from __future__ import annotations

from typing import Any

from logly import Logger, __version__
from logly._logly import (
    HttpJsonSink,
    SyslogSink,
    TcpSink,
    UdpSink,
    format_exception_text,
    inspect_level,
    list_levels,
    parse_compression_str,
    parse_retention_str,
    parse_rotation_str,
    register_custom_level,
    render_message,
    resolve_level_name,
)
from logly.models import PrettyJsonConfig


def test_exports() -> None:
    """Test all exports exist."""
    assert __version__
    assert len(list_levels()) >= 10


def test_custom_levels() -> None:
    """Test custom levels with various colors."""
    register_custom_level("AUDIT", 35, "rgb(255, 128, 0)")
    register_custom_level("SECURITY", 45, "#ff0066")
    register_custom_level("METRIC", 15, "bright_cyan")
    register_custom_level("HIGHLIGHT", 36, "bold red on white")

    assert inspect_level("AUDIT") == ("AUDIT", 35, "rgb(255, 128, 0)", None)
    assert inspect_level("SECURITY") == ("SECURITY", 45, "#ff0066", None)
    assert inspect_level("METRIC") == ("METRIC", 15, "bright_cyan", None)
    assert inspect_level("HIGHLIGHT") == ("HIGHLIGHT", 36, "bold red on white", None)


def test_parse_functions() -> None:
    """Test parse rotation, retention, compression."""
    assert parse_rotation_str("10 MB")
    assert parse_retention_str("30 days")
    assert parse_compression_str("gzip")


def test_render_message() -> None:
    """Test render_message."""
    result = render_message("Hello {}", ["world"])
    assert result == "Hello world"


def test_resolve_level_name() -> None:
    """Test resolve_level_name."""
    result = resolve_level_name("20")
    assert result == "INFO"


def test_format_exception() -> None:
    """Test format_exception_text."""
    try:
        _ = 1 / 0
    except Exception as e:
        text = format_exception_text(e)
        assert text is not None

        backtrace = format_exception_text(e, True)
        assert backtrace is not None


def test_color_features() -> None:
    """Test all color features."""
    messages: list[str] = []
    local_logger = Logger()

    local_logger.level("RED", no=33, color="red")
    local_logger.level("GREEN", no=34, color="green")
    local_logger.level("BLUE", no=35, color="blue")
    local_logger.level("BRIGHT_RED", no=36, color="bright_red")
    local_logger.level("BRIGHT_GREEN", no=37, color="bright_green")
    local_logger.level("BOLD_RED", no=38, color="bold red")
    local_logger.level("DIM_CYAN", no=39, color="dim cyan")
    local_logger.level("BG_RED", no=40, color="bg_red")
    local_logger.level("ON_BLUE", no=41, color="on_blue")
    local_logger.level("ORANGE", no=42, color="rgb(255, 128, 0)")
    local_logger.level("CORAL", no=43, color="#ff7f50")
    local_logger.level("COLOR_208", no=44, color="color(208)")
    local_logger.level("RAW", no=45, color="1;32")

    sink_id = local_logger.add(
        messages.append, level="TRACE", colorize=True, format="{level}:{message}"
    )
    local_logger.log("RED", "red test")
    local_logger.log("GREEN", "green test")
    local_logger.log("BOLD_RED", "bold red test")
    local_logger.log("BG_RED", "bg red test")
    local_logger.log("ORANGE", "orange rgb test")
    local_logger.log("CORAL", "coral hex test")
    local_logger.log("COLOR_208", "208 color test")
    local_logger.log("RAW", "raw ansi test")
    local_logger.remove(sink_id)

    has_colors = any("\x1b[" in m for m in messages)
    assert has_colors, "Expected ANSI escape codes in colored output"
    assert len(messages) >= 8


def test_color_disable() -> None:
    """Test color disabling."""
    no_color_messages: list[str] = []
    local_logger = Logger()
    local_logger.level("RED", no=33, color="red")

    sink_id = local_logger.add(
        no_color_messages.append,
        level="TRACE",
        colorize=False,
        format="{level}:{message}",
    )
    local_logger.log("RED", "no color test")
    local_logger.remove(sink_id)

    has_no_colors = not any("\x1b[" in m for m in no_color_messages)
    assert has_no_colors, "Expected no ANSI escape codes when colorize=False"


def test_file_formats() -> None:
    """Test all file formats."""
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        txt_path = os.path.join(tmpdir, "test.txt")
        local_logger = Logger()
        sink_id = local_logger.add(txt_path, format="{level} | {message}")
        local_logger.info("text test")
        local_logger.complete()
        local_logger.remove(sink_id)
        assert os.path.exists(txt_path)

        json_path = os.path.join(tmpdir, "test.json")
        local_logger = Logger()
        sink_id = local_logger.add(json_path, serialize=True)
        local_logger.info("json test")
        local_logger.complete()
        local_logger.remove(sink_id)
        assert os.path.exists(json_path)

        pretty_path = os.path.join(tmpdir, "pretty.json")
        local_logger = Logger()
        sink_id = local_logger.add(pretty_path, serialize=True, pretty_json=True)
        local_logger.info("pretty test")
        local_logger.complete()
        local_logger.remove(sink_id)
        assert os.path.exists(pretty_path)


def test_compression() -> None:
    """Test all compression types."""
    import os
    import tempfile

    for codec in ["gzip", "zip", "bz2", "xz", "zstd"]:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.log")
            local_logger = Logger()
            sink_id = local_logger.add(log_path, rotation="1 KB", compression=codec)
            for _ in range(100):
                local_logger.info(f"Test message for {codec} compression")
            local_logger.complete()
            local_logger.remove(sink_id)


def test_rotation() -> None:
    """Test rotation options."""
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "size.log")
        local_logger = Logger()
        sink_id = local_logger.add(log_path, rotation="1 KB")
        for _ in range(100):
            local_logger.info("Size rotation test")
        local_logger.complete()
        local_logger.remove(sink_id)


def test_enqueue() -> None:
    """Test enqueue mode."""
    messages: list[str] = []
    local_logger = Logger()

    sink_id = local_logger.add(messages.append, level="TRACE", enqueue=True, format="{message}")
    local_logger.info("Enqueued message")
    local_logger.complete()
    local_logger.remove(sink_id)

    assert len(messages) >= 1


def test_patch() -> None:
    """Test patch functionality."""
    messages: list[str] = []
    local_logger = Logger()

    def add_extra(record: dict[str, Any]) -> None:
        record["extra"]["service"] = "test"

    sink_id = local_logger.add(
        messages.append,
        level="TRACE",
        format="{extra[service]}:{message}",
        patch=add_extra,
    )
    local_logger.info("Patched message")
    local_logger.complete()
    local_logger.remove(sink_id)

    assert len(messages) >= 1
    assert "test:" in messages[0]


def test_filter() -> None:
    """Test filter functionality."""
    messages: list[str] = []
    local_logger = Logger()

    def important_only(record: dict[str, object]) -> bool:
        return "important" in str(record["message"]).lower()

    sink_id = local_logger.add(
        messages.append, level="TRACE", format="{message}", filter=important_only
    )
    local_logger.info("skipped")
    local_logger.info("This is IMPORTANT")
    local_logger.complete()
    local_logger.remove(sink_id)

    assert len(messages) == 1
    assert "IMPORTANT" in messages[0]


def test_network_sinks() -> None:
    """Test network sink creation."""
    HttpJsonSink("http://localhost:3100/push")
    TcpSink("127.0.0.1", 514)
    UdpSink("127.0.0.1", 514)
    SyslogSink("127.0.0.1", 514)


def test_pretty_json_config() -> None:
    """Test PrettyJsonConfig."""
    config = PrettyJsonConfig(indent=2, sort_keys=True)
    assert config.indent == 2
    assert config.sort_keys is True
