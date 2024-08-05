import os
import time

import requests

from .core import BaseParser, custom_parser

MARKER_URL = "https://www.datalab.to/api/v1/marker"
class MarkerAPIError(Exception):
    pass
@custom_parser("marker", ["pdf", "doc", "docx", "ppt", "pptx"])
class MarkerFileParser(BaseParser):
    def load_file(self):
        try:
            self.api_key = os.environ['MARKER_API_KEY']
        except KeyError as e:
            raise MarkerAPIError('MARKER_API_KEY not in env')
        return super().load_file()
    def extract_text(self) -> list[str]:
        payload = {
            'file': (self.file_path.name, self.file_path.open('rb'), self.mimetype),
            'langs': (None, "en"),
            'paginate': (None, True),
            'force_ocr': (None, False),
        }
        headers = {"X-Api-Key": self.api_key}
        resp = requests.post(MARKER_URL, files=payload, headers=headers)
        data = resp.json()
        check_url = data['request_check_url']
        while data.get('status') != 'complete':
            time.sleep(2)
            resp = requests.get(check_url, headers=headers)
            data = resp.json()
        if data.get('error'):
            raise MarkerAPIError(data['error'])
        self.parse_images(data.get('images', {}))
        return split_marker_pages(data.get('markdown', ''))
    
    def parse_images(self, marker_images: dict[str, str]):
        for link, img in marker_images.items():
            self.images[link] = self.image_processor.image_from_uri('data:image/png;base64,' + img, self.file_path.parent)

def split_marker_pages(text: str):
    return text.split('\n\n' + 16*'-' + '\n\n')
     