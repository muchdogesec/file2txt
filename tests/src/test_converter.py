import pytest
from unittest.mock import patch, MagicMock
from file2txt.converter import get_parser_class, convert_file
from file2txt.fanger import Fanger


class DummyParser:
    images = {}

    def __init__(self, *a, **kw):
        pass

    def convert(self):
        return "markdown"


def test_get_parser_class_supported(monkeypatch):
    monkeypatch.setitem(
        get_parser_class.__globals__["BaseParser"].PARSERS,
        "csv",
        (DummyParser, ["text/csv"], [".csv"]),
    )
    out = get_parser_class("csv", "test.csv")
    assert out == DummyParser


def test_get_parser_class_unsupported_type():
    with pytest.raises(ValueError):
        get_parser_class("badtype", "file.csv")


def test_get_parser_class_unsupported_ext(monkeypatch):
    monkeypatch.setitem(
        get_parser_class.__globals__["BaseParser"].PARSERS,
        "csv",
        (DummyParser, ["text/csv"], [".csv"]),
    )
    with pytest.raises(ValueError):
        get_parser_class("csv", "file.txt")


def test_convert_file(monkeypatch, tmp_path):
    monkeypatch.setitem(
        get_parser_class.__globals__["BaseParser"].PARSERS,
        "csv",
        (DummyParser, ["text/csv"], [".csv"]),
    )
    monkeypatch.setattr(
        "file2txt.converter.get_parser_class", lambda typ, fname: DummyParser
    )
    output_dir = tmp_path / "out"
    with patch("file2txt.converter.Fanger.defang", autospec=True) as mock_defang:
        mock_defang.side_effect = lambda self: self.input_text + ";;defanged"
        result = convert_file("csv", "test.csv", None, save_to=output_dir)

    assert (output_dir / "markdown.md").exists()
    assert result == "markdown;;defanged"
