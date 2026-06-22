from __future__ import annotations

from logly import Logger, __version__


def test_version_tracks_rewrite() -> None:
    assert __version__ == "0.2.0"


def test_file_sink_writes_messages(tmp_path) -> None:
    log_file = tmp_path / "app.log"
    logger = Logger()

    sink_id = logger.add(log_file, level="DEBUG", format="{level}:{message}")
    logger.debug("hello {name}", name="logly")
    logger.complete()

    assert sink_id == 1
    assert log_file.read_text(encoding="utf-8").strip() == "DEBUG:hello logly"


def test_custom_level_registration(tmp_path) -> None:
    log_file = tmp_path / "audit.log"
    logger = Logger()

    logger.level("AUDIT", no=35, color="cyan")
    logger.add(log_file, level="AUDIT", format="{level}:{message}")
    logger.log("AUDIT", "created")
    logger.complete()

    assert "AUDIT" in logger.levels
    assert log_file.read_text(encoding="utf-8").strip() == "AUDIT:created"


def test_serialize_json_compact(tmp_path) -> None:
    log_file = tmp_path / "compact.json"
    logger = Logger()
    logger.add(log_file, level="DEBUG", serialize=True)
    logger.info("compact test")
    logger.complete()

    content = log_file.read_text(encoding="utf-8").strip()
    assert '"level"' in content
    assert '"message"' in content
    assert '"compact test"' in content
    # Compact: no newlines in the JSON object itself
    assert "\n" not in content


def test_pretty_json(tmp_path) -> None:
    log_file = tmp_path / "pretty.json"
    logger = Logger()
    logger.add(log_file, level="DEBUG", serialize=True, pretty_json=True)
    logger.info("pretty test")
    logger.complete()

    content = log_file.read_text(encoding="utf-8").strip()
    assert '"level"' in content
    assert '"message"' in content
    assert '"pretty test"' in content
    # Pretty: should have newlines and indentation
    assert "\n" in content
