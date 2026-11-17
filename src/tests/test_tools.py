import pytest

from miniharness.tools.calculator import Calculator
from miniharness.tools.read_file import ReadFile


def test_calculator_basic():
    assert Calculator().run("12 * 7 + 3") == "87"


def test_calculator_rejects_code():
    with pytest.raises(ValueError):
        Calculator().run("__import__('os').system('ls')")


def test_calculator_rejects_huge_exponent():
    with pytest.raises(ValueError):
        Calculator().run("9 ** 9999")


def test_read_file_reads_inside_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr("miniharness.tools.read_file.WORKSPACE", tmp_path)
    (tmp_path / "note.txt").write_text("hello")
    assert ReadFile().run("note.txt") == "hello"


def test_read_file_blocks_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr("miniharness.tools.read_file.WORKSPACE", tmp_path)
    with pytest.raises(PermissionError):
        ReadFile().run("../../etc/passwd")