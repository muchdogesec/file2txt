
import pytest
from unittest.mock import patch
from file2txt.parsers.markdown_file_parser import MarkdownParser

text = '''
|    |   col1 |   col2 |
|---:|-------:|-------:|
|  0 |      1 |      2 |
|  1 |      3 |      4 |
'''

def test_extract_text(tmp_path, monkeypatch):
    path = tmp_path/"test.md"
    path.write_text(text)
    parser = MarkdownParser(path, "md", False, None)
    out = parser.extract_text()
    assert parser.raw_html and parser.soup

