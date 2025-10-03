import pytest
from unittest.mock import patch
from file2txt.parsers.csv_file_parser import CsvFileParser

def test_extract_text(tmp_path, monkeypatch):
    path = tmp_path/"test.csv"
    path.write_text("col1,col2\n1,2\n3,4\n")
    parser = CsvFileParser(path, "csv", False, None)
    out = parser.extract_text()
    assert out == ['|    |   col1 |   col2 |\n|---:|-------:|-------:|\n|  0 |      1 |      2 |\n|  1 |      3 |      4 |']