import base64
from PIL import Image
import os
import pytest
from PIL import ImageDraw

from file2txt.image_processor import ImageProcessor
import pytest
from PIL import Image

# Assume ImageProcessor exists in file2txt.image_processor
from file2txt.image_processor import ImageProcessor

@pytest.fixture
def image():
    img = Image.new("RGB", (100, 30), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 5), "hello", fill=(0, 0, 0))
    return img


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_VISION_API_KEY"),
    reason="GOOGLE_VISION_API_KEY not set in environment",
)
def test_image_to_text_real_api(image):
    processor = ImageProcessor(True, os.environ["GOOGLE_VISION_API_KEY"])
    out = processor.image_to_text(image)
    assert isinstance(out, str)
    assert "hello" in out.lower()


def test_init_sets_attributes():
    processor = ImageProcessor(True, "apikey")
    assert processor.process_raw_image_urls is True
    assert processor.client != None


def test_image_to_text_failure(monkeypatch):
    processor = ImageProcessor(True, "apikey")
    monkeypatch.setattr(
        processor.client,
        "text_detection",
        lambda img: (_ for _ in ()).throw(Exception("fail")),
    )
    img = Image.new("RGB", (10, 10))
    with pytest.raises(Exception):
        processor.image_to_text(img)


def test_image_from_uri_base64(monkeypatch, tmp_path, image):
    # Create a fake PNG, encode as base64
    img_path = tmp_path / "test.png"
    image.save(img_path)
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    uri = "data:image/png;base64," + b64
    out = ImageProcessor._image_from_uri(uri, tmp_path)
    assert isinstance(out, Image.Image)


def test_image_from_uri_file(monkeypatch, tmp_path, image):
    img_path = tmp_path / "file.png"
    image.save(img_path)
    uri = str(img_path)
    out = ImageProcessor._image_from_uri(uri, tmp_path)
    assert isinstance(out, Image.Image)


@pytest.mark.parametrize("url,passes", [
    ("https://pub-99019d5e65d44129a12bd0448a6b6e64.r2.dev/image/example-1.png", True),
    ("https://pub-99019d5e65d44129a12bd0448a6b6e64.r2.dev/image/example-3.jpeg", True),
    ("http://badlocalwebsite.net.crap.bad/not_an_image.txt", False),  # connection refused
    ("https://pub-99019d5e65d44129a12bd0448a6b6e64.r2.dev/image/example-4.jpg", True),
])
def test_image_from_uri_http(monkeypatch, url, passes):
    if passes:
        assert ImageProcessor._image_from_uri(url, '')
        return
    
    with pytest.raises(Exception):
        ImageProcessor._image_from_uri(url, '')
