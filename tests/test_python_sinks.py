from __future__ import annotations

import gzip

from logly import Logger


def test_callable_sink_and_filter() -> None:
    seen: list[str] = []
    logger = Logger()

    logger.add(
        seen.append, level="INFO", filter={"request_id": "abc"}, format="{level: <8} | {message}\n"
    )
    logger.bind(request_id="abc").info("hello")
    logger.bind(request_id="other").info("hidden")
    logger.complete()

    assert len(seen) == 1
    assert seen[0].endswith(" | hello\n")
    assert "INFO" in seen[0]


def test_callable_formatter_and_patch() -> None:
    seen: list[str] = []
    logger = Logger()

    patched = logger.patch(lambda record: record.__setitem__("message", "patched"))
    patched.add(seen.append, format=lambda record: f"{record['level']}:{record['message']}")
    patched.info("original")

    assert seen == ["INFO:patched\n"]


def test_contextualize_and_lazy_opt() -> None:
    seen: list[str] = []
    logger = Logger()

    logger.add(seen.append, format="{message}:{extra[request_id]}")
    with logger.contextualize(request_id="req-1"):
        logger.opt(lazy=True).info("value={value}", value=lambda: 42)

    assert seen == ["value=42:req-1\n"]


def test_rotation_retention_and_gzip(tmp_path) -> None:
    path = tmp_path / "app.log"
    logger = Logger()

    logger.add(path, rotation=20, retention=1, compression="gzip", format="{message}")
    logger.info("a" * 25)
    logger.info("b" * 25)
    logger.complete()

    archives = list(tmp_path.glob("app.log.*.gz"))
    assert len(archives) == 1
    with gzip.open(archives[0], "rt", encoding="utf-8") as handle:
        assert "a" * 25 in handle.read()
