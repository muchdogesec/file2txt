import pytest
from file2txt.parsers.image_file_parser import ImageFileParser
from PIL import Image
from pathlib import Path

def test_extract_text(tmp_path):
    img_path = tmp_path/"img.png"
    img = Image.new('RGB', (10,10))
    img.save(img_path)
    parser = ImageFileParser(img_path, "image", True, "None")
    out = parser.extract_text()
    assert "![img.png]" in out[0]
    assert parser.images['0_image_0.png']

def test_prepare_extractor(monkeypatch):
    parser = ImageFileParser("img.png", "image", True, "None")
    assert parser.process_raw_image_urls is True