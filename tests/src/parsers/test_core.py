import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from file2txt.parsers.core import BaseParser, PlaintextParser

class DummyImage:
    def save(self, *args, **kw): pass

class DummyImageProcessor:
    def __init__(self, *a, **kw): pass
    def image_to_text(self, img): return "imgtext"

class DummyParser(BaseParser):
    def extract_text(self): return ["page1", "page2", "this page contains an ![image](img.png) huzzah"]

def test_join_pages():
    out = BaseParser.join_pages(["a","b"])
    assert "[comment]: <> (===START_PAGE" in out

def test_convert(monkeypatch):
    parser = DummyParser("file.txt","txt",True,"key")
    parser.images = {"img.png": DummyImage()}
    parser.image_processor = DummyImageProcessor()
    text = parser.convert()
    print(text)
    assert "imgtext" in text

def test_convert_no_images(monkeypatch):
    parser = DummyParser("file.txt","txt",False,"key")
    parser.images = {}
    parser.image_processor = DummyImageProcessor()
    text = parser.convert()
    assert "START_PAGE" in text

def test_del_temp(monkeypatch):
    parser = DummyParser("file.txt","txt",True,"key")
    parser._temp_dir = Path("tmp_should_not_exist")
    with patch("shutil.rmtree") as rm:
        parser.__del__()
        rm.assert_called_once()


text = '''
|    |   col1 |   col2 |
|---:|-------:|-------:|
|  0 |      1 |      2 |
|  1 |      3 |      4 |
'''

def test_plaintext_parser(tmp_path, monkeypatch):
    path = tmp_path/"test.md"
    path.write_text(text)
    parser = PlaintextParser(path, "md", False, None)
    out = parser.extract_text()
    assert out == [text]