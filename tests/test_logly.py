"""Basic logger tests."""

from pathlib import Path

from logly import logger


def test_logger_basic(tmp_path: Path):
    """Test basic logger functionality."""
    # add file sink before configure
    log_file = tmp_path / "test.log"
    logger.add(str(log_file))
    logger.configure(level="INFO", color=False)

    logger.info("hello", user="alice")
    logger.error("oops", code=500)
    logger.complete()

    assert log_file.exists()
    content = log_file.read_text()
    assert "hello" in content
    assert "oops" in content
