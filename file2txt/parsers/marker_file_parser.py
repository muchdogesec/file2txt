import os
import time

import requests

from file2txt.image_processor import ImageProcessor

from .core import BaseParser, custom_parser

MARKER_URL = "https://www.datalab.to/api/v1/marker"
class MarkerAPIError(Exception):
    pass

class MarkerFileParser(BaseParser):
    def prepare_extractor(self):
        self.api_key = os.environ.get('MARKER_API_KEY')
        if not self.api_key:
            raise MarkerAPIError('MARKER_API_KEY not set in env')
        return super().prepare_extractor()
    def extract_text(self) -> list[str]:
        payload = {
            'file': (self.file_path.name, self.file_path.open('rb'), self.mimetype),
            'langs': (None, "en"),
            'paginate': (None, True),
            'force_ocr': (None, False),
        }
        data = self.make_api_request("POST", MARKER_URL, files=payload)
        check_url = data['request_check_url']
        while data.get('status') != 'complete':
            time.sleep(2)
            data = self.make_api_request("GET", check_url)
        self.parse_images(data.get('images', {}))
        return split_marker_pages(data.get('markdown', ''))
    
    def make_api_request(self, method, url, files=None):
        headers = {"X-Api-Key": self.api_key}
        resp = requests.request(method, url, files=files, headers=headers)
        data = resp.json()
        if resp.status_code != 200:
            error = data.get("error") or data.get("detail") or "Unknown"
            raise MarkerAPIError(f'HTTP {resp.status_code}: {error}')
        return data
    
    def parse_images(self, marker_images: dict[str, str]):
        for link, img in marker_images.items():
            self.images[link] = ImageProcessor._image_from_uri('data:image/png;base64,' + img, self.file_path.parent)

def split_marker_pages(text: str):
    return text.split('\n\n' + 16*'-' + '\n\n')
     

@custom_parser("word", ["doc", "docx"])
class MarkerWordFileParser(MarkerFileParser):
    pass

@custom_parser("pdf", ["pdf"])
class MarkerPdfFileParser(MarkerFileParser):
    pass

@custom_parser("powerpoint", ["ppt", "pptx"])
class MarkerPowerpointFileParser(MarkerFileParser):
    pass
