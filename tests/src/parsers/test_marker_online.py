import os
from urllib.parse import urljoin
import pytest
import requests

from file2txt.parsers.marker_file_parser import MarkerPdfFileParser


url = "https://pub-99019d5e65d44129a12bd0448a6b6e64.r2.dev/pdf/fanged_data_good.pdf"


@pytest.mark.skipif(
    not os.environ.get("MARKER_API_KEY"),
    reason="MARKER_API_KEY not set in environment",
)
@pytest.mark.parametrize(
    "urlpath,expecteds",
    [
        ("pdf/fanged_data_good.pdf", ["example.com", "1.1.1.1"]),
        (
            "ppt/fanged_data.ppt",
            ["example.com", "1.1.1.1", "![](_page_0_Figure_0.jpeg)"],
        ),
        ("doc/txt2stix-local-extractions.docx", ["fortinet.com"]),
    ],
)
def test_extract_text(tmp_path, urlpath, expecteds):
    path = tmp_path / "file.pdf"
    path.write_bytes(
        requests.get(
            urljoin("https://pub-99019d5e65d44129a12bd0448a6b6e64.r2.dev/", urlpath)
        ).content
    )
    parser = MarkerPdfFileParser(path, path.suffix, False, None)
    out = parser.extract_text()
    for expected in expecteds:
        assert expected.strip() in "\n".join(out)
