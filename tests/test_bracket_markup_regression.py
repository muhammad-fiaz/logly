"""Regression tests for literal square-bracket handling.

Literal square brackets and their contents must be preserved during
formatted logging while valid markup continues to work.
"""

from __future__ import annotations

import json
from pathlib import Path

from logly import Logger, parse_rich_markup, strip_rich_tags


def _capture(
    fmt: str = "{message}", colorize: bool = False, **kwargs: object
) -> tuple[Logger, list[str], int]:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(
        lambda m: messages.append(m), level="DEBUG", format=fmt, colorize=colorize, **kwargs
    )
    return logger, messages, sink_id


def _capture_file(
    tmp_path: Path,
    fmt: str = "{message}",
    name: str = "test.log",
) -> tuple[Logger, Path, int]:
    logger = Logger()
    tmp = tmp_path / name
    sink_id = logger.add(str(tmp), level="DEBUG", format=fmt, colorize=False)
    return logger, tmp, sink_id


class TestBracketFormattingCore:
    def test_plain_format(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info("do {}things", "some")
        finally:
            logger.remove(sink_id)
        assert messages == ["do somethings\n"]

    def test_bracket_format(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info("do [{}]things", "some")
        finally:
            logger.remove(sink_id)
        assert messages == ["do [some]things\n"]

    def test_escaped_open_bracket(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info(r"do \[{}]things", "some")
        finally:
            logger.remove(sink_id)
        assert messages == ["do \\[some]things\n"]

    def test_escaped_close_bracket(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info(r"do [{}\]things", "some")
        finally:
            logger.remove(sink_id)
        assert messages == ["do [some\\]things\n"]

    def test_spaced_brackets(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info("do [ {} ]things", "some")
        finally:
            logger.remove(sink_id)
        assert messages == ["do [ some ]things\n"]

    def test_empty_brackets(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info("do [] {}things", "some")
        finally:
            logger.remove(sink_id)
        assert messages == ["do [] somethings\n"]

    def test_file_sink_matches_issue_cases(self, tmp_path: Path) -> None:
        cases = [
            ("do {}things", ("some",), "do somethings"),
            ("do [{}]things", ("some",), "do [some]things"),
            (r"do \[{}]things", ("some",), r"do \[some]things"),
            (r"do [{}\]things", ("some",), r"do [some\]things"),
            ("do [ {} ]things", ("some",), "do [ some ]things"),
            ("do [] {}things", ("some",), "do [] somethings"),
        ]
        logger, tmp, sink_id = _capture_file(tmp_path)
        try:
            for fmt, args, _ in cases:
                logger.info(fmt, *args)
            logger.complete()
            lines = tmp.read_text(encoding="utf-8").splitlines()
        finally:
            logger.remove(sink_id)
        assert lines == [expected for _, _, expected in cases]


class TestLiteralBrackets:
    def test_common_literals_preserved(self) -> None:
        literals = [
            "[hello]",
            "[]",
            "[ hello ]",
            "[123]",
            "[INFO]",
            "[unknown]",
            "[foo bar]",
            "[user@example.com]",
            "[/path/to/file]",
            r"[C:\Users\test]",
        ]
        for text in literals:
            logger, messages, sink_id = _capture()
            try:
                logger.info(text)
            finally:
                logger.remove(sink_id)
            assert messages == [text + "\n"], text

    def test_brackets_with_format_args(self) -> None:
        cases = [
            ("value=[{}]", ("test",), "value=[test]"),
            ("response=[] status={}", (200,), "response=[] status=200"),
            ("payload=[{}]", ('{"ok": true}',), 'payload=[{"ok": true}]'),
            ("path=[{}]", (r"C:\Users\test",), r"path=[C:\Users\test]"),
            ("GET /users/[{}]", (123,), "GET /users/[123]"),
            ("[{}]", ("value",), "[value]"),
            ("[{}] [{}]", ("one", "two"), "[one] [two]"),
            ("items=[{}]", ("one, two",), "items=[one, two]"),
            ("data=[{}]", ('{"key": "[value]"}',), 'data=[{"key": "[value]"}]'),
            ("text=[[{}]]", ("value",), "text=[[value]]"),
        ]
        for fmt, args, expected in cases:
            logger, messages, sink_id = _capture()
            try:
                logger.info(fmt, *args)
            finally:
                logger.remove(sink_id)
            assert messages == [expected + "\n"], (fmt, args)

    def test_file_sink_preserves_literals(self, tmp_path: Path) -> None:
        literals = ["[hello]", "[]", "[ hello ]", "[123]", "[INFO]", "[unknown]"]
        logger, tmp, sink_id = _capture_file(tmp_path)
        try:
            for text in literals:
                logger.info(text)
            logger.complete()
            lines = tmp.read_text(encoding="utf-8").splitlines()
        finally:
            logger.remove(sink_id)
        assert lines == literals


class TestFormattingSemantics:
    def test_positional_and_kwargs(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info("{0} {1}", "a", "b")
            logger.info("{v:>5}", v="x")
            logger.info("{{literal}} {}", "val")
            logger.info("{0.attr}", type("O", (), {"attr": "X"})())
            logger.info("{0[key]}", {"key": "Y"})
        finally:
            logger.remove(sink_id)
        assert messages[0] == "a b\n"
        assert messages[1] == "    x\n"
        assert messages[2] == "{literal} val\n"
        assert messages[3] == "X\n"
        assert messages[4] == "Y\n"

    def test_brackets_do_not_interfere_with_format(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info("[{}] [{}]", "one", "two")
            logger.info("[[{}]]", "x")
            logger.info("[{}][{}]", "a", "b")
        finally:
            logger.remove(sink_id)
        assert messages == ["[one] [two]\n", "[[x]]\n", "[a][b]\n"]

    def test_unicode_urls_json_paths(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info("unicode [{}]", "test-unicode")
            logger.info("url [{}]", "https://example.com/a?b=1")
            logger.info("data=[{}]", '{"a": [1, 2]}')
            logger.info("path [{}]", "/tmp/a/b")
        finally:
            logger.remove(sink_id)
        assert messages[0] == "unicode [test-unicode]\n"
        assert "[https://example.com/a?b=1]" in messages[1]
        assert messages[2] == 'data=[{"a": [1, 2]}]\n'


class TestValidMarkupStillWorks:
    def test_bracket_markup_colorized(self) -> None:
        logger, messages, sink_id = _capture(colorize=True)
        try:
            logger.info("[red]Error[/red]")
            logger.info("[bold]Important[/bold]")
        finally:
            logger.remove(sink_id)
        assert "\x1b[31mError\x1b[0m" in messages[0]
        assert "\x1b[1mImportant\x1b[0m" in messages[1]

    def test_bracket_markup_stripped_for_plain_sink(self, tmp_path: Path) -> None:
        logger, tmp, sink_id = _capture_file(tmp_path)
        try:
            logger.info("[red]Error[/red]")
            logger.info("[bold]Important[/bold]")
            logger.complete()
            content = tmp.read_text(encoding="utf-8")
        finally:
            logger.remove(sink_id)
        assert "Error" in content
        assert "Important" in content
        assert "[red]" not in content

    def test_invalid_markup_preserved_with_color(self) -> None:
        logger, messages, sink_id = _capture(colorize=True)
        try:
            logger.info("[hello]")
            logger.info("[]")
            logger.info("[ unknown ]")
        finally:
            logger.remove(sink_id)
        assert "[hello]" in messages[0]
        assert "[]" in messages[1]
        assert "[ unknown ]" in messages[2]

    def test_parse_helpers(self) -> None:
        assert parse_rich_markup("[red]Error[/red]", True) == "\x1b[31mError\x1b[0m"
        assert parse_rich_markup("[hello]", True) == "[hello]"
        assert parse_rich_markup("[]", True) == "[]"
        assert parse_rich_markup("[red]Error[/red]", False) == "Error"
        assert parse_rich_markup("[hello]", False) == "[hello]"
        assert strip_rich_tags("[hello]") == "[hello]"
        assert strip_rich_tags("[]") == "[]"
        assert strip_rich_tags("[red]Error[/red]") == "Error"
        assert strip_rich_tags("do [some]things") == "do [some]things"

    def test_escaped_valid_markup_literal(self) -> None:
        assert parse_rich_markup(r"\[red] literal", True) == "[red] literal"
        assert strip_rich_tags(r"\[red] literal") == "[red] literal"
        # Escaping a non-markup bracket keeps the backslash.
        assert parse_rich_markup(r"\[some] literal", True) == r"\[some] literal"

    def test_unterminated_bracket_preserved(self) -> None:
        assert parse_rich_markup("array[0", True) == "array[0"
        assert strip_rich_tags("array[0") == "array[0"


class TestSinksStructuredExceptions:
    def test_json_sink_preserves_brackets(self) -> None:
        logger = Logger()
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m), level="DEBUG", format="{message}", serialize=True
        )
        try:
            logger.info("do [{}]things", "some")
        finally:
            logger.remove(sink_id)
        assert len(messages) == 1
        assert json.loads(messages[0])["message"] == "do [some]things"

    def test_enqueue_sink_preserves_brackets(self) -> None:
        logger, messages, sink_id = _capture(enqueue=True)
        try:
            logger.info("do [{}]things", "some")
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert messages == ["do [some]things\n"]

    def test_custom_formatter_preserves_brackets(self) -> None:
        logger = Logger()
        messages: list[str] = []
        sink_id = logger.add(
            lambda m: messages.append(m),
            level="DEBUG",
            format=lambda r: f"CUSTOM:{r['message']}",
        )
        try:
            logger.info("do [{}]things", "some")
        finally:
            logger.remove(sink_id)
        assert messages == ["CUSTOM:do [some]things\n"]

    def test_structured_values_preserve_brackets(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.bind(data={"items": ["one", "two"]}).info("items=[{}]", "test")
            logger.info("payload=[{}]", '{"items": [1, 2, 3]}')
        finally:
            logger.remove(sink_id)
        assert messages[0] == "items=[test]\n"
        assert messages[1] == 'payload=[{"items": [1, 2, 3]}]\n'

    def test_exception_preserves_brackets(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            try:
                raise ValueError("[something]")
            except ValueError as exc:
                logger.opt(exception=exc).error("failed [operation]")
        finally:
            logger.remove(sink_id)
        assert "[operation]" in messages[0]
        assert "[something]" in messages[0]

    def test_bind_contextualize_patch(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.bind(user="alice").info("hi [{}]", "there")
            with logger.contextualize(req="123"):
                logger.info("req [{}]", "x")
            logger.patch(lambda r: r).info("patched [{}]", "y")
        finally:
            logger.remove(sink_id)
        assert messages == ["hi [there]\n", "req [x]\n", "patched [y]\n"]

    def test_lazy_and_raw(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.opt(lazy=True).info("value=[{}]", lambda: "test")
            logger.opt(raw=True).info("do [{}]things", "some")
        finally:
            logger.remove(sink_id)
        assert messages[0] == "value=[test]\n"
        assert messages[1] == "do [{}]things\n"

    def test_file_and_custom_consistent_for_literals(self, tmp_path: Path) -> None:
        literals = ["[hello]", "[]", "[ hello ]", "do [some]things"]
        for index, text in enumerate(literals):
            c_logger, c_messages, c_id = _capture()
            f_logger, tmp, f_id = _capture_file(tmp_path, name=f"case-{index}.log")
            try:
                c_logger.info(text)
                f_logger.info(text)
                f_logger.complete()
                file_content = tmp.read_text(encoding="utf-8")
            finally:
                c_logger.remove(c_id)
                f_logger.remove(f_id)
            assert c_messages == [text + "\n"]
            assert file_content == text + "\n"

    def test_windows_paths(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.info(r"path=[C:\Users\test]")
            logger.info(r"path=[C:\Users\{}\logs]", "user")
        finally:
            logger.remove(sink_id)
        assert messages[0] == r"path=[C:\Users\test]" + "\n"
        assert messages[1] == r"path=[C:\Users\user\logs]" + "\n"

    def test_catch_preserves_brackets(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            with logger.catch():
                raise RuntimeError("failed [operation]")
        finally:
            logger.remove(sink_id)
        assert "[operation]" in messages[0]

    def test_opt_colors_preserves_literals(self) -> None:
        logger, messages, sink_id = _capture()
        try:
            logger.opt(colors=True).info("do [{}]things", "some")
            logger.opt(colors=True).info("[hello]")
        finally:
            logger.remove(sink_id)
        assert "do [some]things" in messages[0]
        assert "[hello]" in messages[1]
