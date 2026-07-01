"""Tests for Logger.root_dir() method."""

from pathlib import Path

from logly import Logger


class TestRootDir:
    def test_set_root_dir(self, tmp_path: Path) -> None:
        test_dir = tmp_path / "logs"
        lg = Logger()
        lg.root_dir(test_dir)
        assert Logger._root_dir == test_dir.resolve()

    def test_root_dir_creates_directory(self, tmp_path: Path) -> None:
        test_dir = tmp_path / "nested" / "deep" / "logs"
        lg = Logger()
        lg.root_dir(test_dir)
        assert test_dir.resolve().exists()

    def test_root_dir_class_level_shared(self, tmp_path: Path) -> None:
        test_dir = tmp_path / "shared"
        lg1 = Logger()
        lg2 = Logger()
        lg1.root_dir(test_dir)
        assert lg2.root_dir is not None or Logger._root_dir == test_dir.resolve()
        assert Logger._root_dir == test_dir.resolve()

    def test_root_dir_overwrites_previous(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "first"
        dir2 = tmp_path / "second"
        lg = Logger()
        lg.root_dir(dir1)
        assert Logger._root_dir == dir1.resolve()
        lg.root_dir(dir2)
        assert Logger._root_dir == dir2.resolve()

    def test_root_dir_accepts_string(self, tmp_path: Path) -> None:
        test_dir = str(tmp_path / "str_path")
        lg = Logger()
        lg.root_dir(test_dir)
        assert Logger._root_dir == Path(test_dir).resolve()

    def test_root_dir_accepts_path(self, tmp_path: Path) -> None:
        test_dir = tmp_path / "path_obj"
        lg = Logger()
        lg.root_dir(test_dir)
        assert Logger._root_dir == test_dir.resolve()
