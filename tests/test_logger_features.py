from pathlib import Path

import pytest

from logly import logger


def read_log(path: Path) -> str:
    assert path.exists()
    return path.read_text()


def test_add_configure_and_basic_logging(tmp_path: Path):
    p = tmp_path / "basic.log"
    # add file before configure per MVP
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    logger.info("hello world", user="bob")
    logger.complete()

    content = read_log(p)
    assert "hello world" in content
    assert "user=bob" in content


def test_bind_and_contextualize(tmp_path: Path):
    p = tmp_path / "bind.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    bound = logger.bind(request_id="r1")
    bound.info("started")

    with bound.contextualize(step=1):
        bound.debug("step")

    logger.complete()
    content = read_log(p)
    assert "started" in content
    assert "request_id=r1" in content
    assert "step=1" in content


def test_enable_disable(tmp_path: Path):
    p = tmp_path / "enable.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    logger.disable()
    logger.info("should_not_appear")
    logger.enable()
    logger.info("should_appear")
    logger.complete()

    content = read_log(p)
    assert "should_appear" in content
    assert "should_not_appear" not in content


def test_level_mapping(tmp_path: Path):
    p = tmp_path / "level.log"
    logger.add(str(p))
    logger.level("NOTICE", "info")
    logger.configure(level="INFO", color=False)

    logger.log("NOTICE", "notice message")
    logger.complete()

    content = read_log(p)
    assert "notice message" in content


def test_opt_returns_proxy_and_logs(tmp_path: Path):
    p = tmp_path / "opt.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    opt_logger = logger.opt(colors=False)
    opt_logger.info("opt message")
    logger.complete()

    content = read_log(p)
    assert "opt message" in content


def test_catch_decorator_and_context_manager(tmp_path: Path):
    p = tmp_path / "catch.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    @logger.catch(reraise=False)
    def will_raise():
        raise RuntimeError("fail")

    # decorator should suppress (reraise=False)
    will_raise()

    # context manager: reraise=False suppresses
    with logger.catch(reraise=False):
        raise ValueError("bad")

    # context manager: reraise=True should re-raise
    with pytest.raises(ZeroDivisionError):
        with logger.catch(reraise=True):
            _ = 1 / 0

    logger.complete()
    content = read_log(p)
    # both exceptions should be logged
    assert "RuntimeError" in content or "fail" in content
    assert "ValueError" in content or "bad" in content


def test_exception_logs_traceback(tmp_path: Path):
    p = tmp_path / "exc.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    try:
        _ = 1 / 0
    except Exception:
        logger.exception("caught")

    logger.complete()
    content = read_log(p)
    assert "ZeroDivisionError" in content or "division" in content


def test_remove_and_complete_noop(tmp_path: Path):
    p = tmp_path / "rm.log"
    logger.add(str(p))
    logger.configure(level="INFO", color=False)

    ok = logger.remove(0)
    assert ok is True
    logger.info("after remove")
    logger.complete()
    content = read_log(p)
    assert "after remove" in content
