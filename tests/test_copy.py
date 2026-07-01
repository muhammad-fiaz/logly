"""Tests for Logger.__copy__() and Logger.__deepcopy__()."""

import copy

from logly import Logger


class TestCopy:
    def test_shallow_copy_shares_native_engine(self) -> None:
        lg = Logger(name="original")
        shallow = copy.copy(lg)
        assert shallow._native is lg._native

    def test_shallow_copy_shares_name(self) -> None:
        lg = Logger(name="test_logger")
        shallow = copy.copy(lg)
        assert shallow._name == "test_logger"

    def test_shallow_copy_has_same_bound_values(self) -> None:
        lg = Logger(bound={"key": "value"})
        shallow = copy.copy(lg)
        assert shallow._bound == {"key": "value"}

    def test_shallow_copy_is_new_instance(self) -> None:
        lg = Logger()
        shallow = copy.copy(lg)
        assert shallow is not lg


class TestDeepCopy:
    def test_deep_copy_creates_independent_bound(self) -> None:
        lg = Logger(bound={"key": "value"})
        deep = copy.deepcopy(lg)
        assert deep._bound == {"key": "value"}
        deep._bound["key2"] = "value2"
        assert "key2" not in lg._bound

    def test_deep_copy_creates_independent_options(self) -> None:
        lg = Logger()
        deep = copy.deepcopy(lg)
        deep._options.raw = True
        assert lg._options.raw is False

    def test_deep_copy_shares_native_engine(self) -> None:
        lg = Logger()
        deep = copy.deepcopy(lg)
        assert deep._native is lg._native

    def test_deep_copy_preserves_name(self) -> None:
        lg = Logger(name="my_logger")
        deep = copy.deepcopy(lg)
        assert deep._name == "my_logger"

    def test_deep_copy_creates_independent_instance(self) -> None:
        lg = Logger()
        deep = copy.deepcopy(lg)
        assert deep is not lg
