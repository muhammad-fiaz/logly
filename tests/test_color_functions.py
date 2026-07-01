"""Tests for strip_rich_tags(), paint_themed(), and colorize() functions."""

from logly import colorize, paint_themed, strip_rich_tags


class TestStripRichTags:
    def test_single_bold_tag(self):
        assert strip_rich_tags("<bold>Hello</bold>") == "Hello"

    def test_single_color_tag(self):
        assert strip_rich_tags("<red>Warning</red>") == "Warning"

    def test_opening_tag_only(self):
        assert strip_rich_tags("<green>text") == "text"

    def test_closing_tag_only(self):
        assert strip_rich_tags("text</blue>") == "text"

    def test_multiple_different_tags(self):
        assert strip_rich_tags("<bold>Hello</bold> <red>World</red>") == "Hello World"

    def test_nested_tags(self):
        assert strip_rich_tags("<bold><red>Nested</red></bold>") == "Nested"

    def test_no_tags(self):
        assert strip_rich_tags("plain text") == "plain text"

    def test_empty_string(self):
        assert strip_rich_tags("") == ""

    def test_tags_with_empty_content(self):
        assert strip_rich_tags("<bold></bold>") == ""

    def test_mixed_content_and_tags(self):
        assert strip_rich_tags("<bold>A</bold>B<red>C</red>") == "ABC"


class TestPaintThemed:
    def test_success_level(self):
        result = paint_themed("Done!", "success", colorize=True)
        assert result != "Done!"
        assert "\033[" in result
        assert "\033[0m" in result

    def test_error_level(self):
        result = paint_themed("Failed!", "error", colorize=True)
        assert result != "Failed!"
        assert "\033[" in result
        assert "\033[0m" in result

    def test_warning_level(self):
        result = paint_themed("Careful", "warning", colorize=True)
        assert result != "Careful"
        assert "\033[" in result

    def test_info_level(self):
        result = paint_themed("Info msg", "info", colorize=True)
        assert isinstance(result, str)

    def test_debug_level(self):
        result = paint_themed("Debug msg", "debug", colorize=True)
        assert result != "Debug msg"
        assert "\033[" in result

    def test_colorize_false_returns_plain(self):
        result = paint_themed("Done!", "success", colorize=False)
        assert result == "Done!"

    def test_colorize_false_all_levels(self):
        for level in ("success", "error", "warning", "info", "debug"):
            result = paint_themed("msg", level, colorize=False)
            assert result == "msg"


class TestColorize:
    def test_red(self):
        result = colorize("Error", "red", colorize=True)
        assert "\033[" in result
        assert "\033[0m" in result
        assert "Error" in result

    def test_green(self):
        result = colorize("OK", "green", colorize=True)
        assert "\033[" in result
        assert "OK" in result

    def test_blue(self):
        result = colorize("Info", "blue", colorize=True)
        assert "\033[" in result
        assert "Info" in result

    def test_bold_red(self):
        result = colorize("Critical", "bold_red", colorize=True)
        assert "\033[" in result
        assert "Critical" in result

    def test_colorize_false_returns_plain(self):
        assert colorize("Error", "red", colorize=False) == "Error"

    def test_colorize_false_various_colors(self):
        for c in ("red", "green", "blue", "bold_red"):
            assert colorize("text", c, colorize=False) == "text"

    def test_empty_string(self):
        result = colorize("", "red", colorize=True)
        assert "\033[" in result
        assert "\033[0m" in result
        assert result.endswith("\033[0m")
