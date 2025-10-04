import tempfile
import pytest
from unittest.mock import patch, MagicMock
import file2txt.parsers.marker_file_parser as marker_mod

@pytest.fixture
def fake_env(monkeypatch):
    monkeypatch.setenv('MARKER_API_KEY', 'fakekey')


def test_prepare_extractor(fake_env):
    parser = marker_mod.MarkerFileParser("file.docx", "word", True, MagicMock())
    assert parser.api_key == 'fakekey'
    assert parser.prepare_extractor() is None

def test_prepare_extractor__missing_api_key(monkeypatch):
    monkeypatch.setenv('MARKER_API_KEY', '')
    with pytest.raises(marker_mod.MarkerAPIError):
        parser = marker_mod.MarkerFileParser("file.docx", "word", True, MagicMock())

def test_extract_text(monkeypatch, fake_env):
    with tempfile.NamedTemporaryFile(mode='r') as f:
        parser = marker_mod.MarkerFileParser(f.name, "word", True, MagicMock())
        monkeypatch.setattr(parser, 'make_api_request', lambda m,u,files=None: {'request_check_url':'url','status':'complete','markdown':'test','images':{}})
        monkeypatch.setattr(marker_mod, 'split_marker_pages', lambda x: ["pg1"])
        monkeypatch.setattr(parser, 'parse_images', lambda imgs: None)
        out = parser.extract_text()
        assert out == ["pg1"]

def test_make_api_request_success(monkeypatch, fake_env):
    parser = marker_mod.MarkerFileParser("file.docx", "word", True, MagicMock())
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'ok': True}
    monkeypatch.setattr(marker_mod.requests, 'request', lambda *a, **kw: mock_resp)
    out = parser.make_api_request("GET", "url")
    assert out['ok'] is True

def test_make_api_request_failure(monkeypatch, fake_env):
    parser = marker_mod.MarkerFileParser("file.docx", "word", True, MagicMock())
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.json.return_value = {'error': 'fail'}
    monkeypatch.setattr(marker_mod.requests, 'request', lambda *a, **kw: mock_resp)
    with pytest.raises(marker_mod.MarkerAPIError):
        parser.make_api_request("GET", "url")

def test_parse_images(monkeypatch, fake_env):
    parser = marker_mod.MarkerFileParser("file.docx", "word", True, MagicMock())
    parser.images = {}
    monkeypatch.setattr(marker_mod.ImageProcessor, '_image_from_uri', lambda uri, p: "imgobj")
    parser.parse_images({'link': 'imgdata'})
    assert parser.images['link'] == "imgobj"

def test_split_marker_pages():
    text = "one\n\n----------------\n\ntwo"
    out = marker_mod.split_marker_pages(text)
    assert out == ['one', 'two']