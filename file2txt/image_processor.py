import logging
from io import BytesIO
from pathlib import Path
import requests
from PIL import Image
from google.auth import api_key
from google.cloud import vision
import base64


class LoadImageException(Exception):
    pass


class EmptyApiKeyException(Exception):
    pass


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


class ImageProcessor:
    def __init__(self, process_raw_image_urls: bool, key: str):
        if not key:
            raise EmptyApiKeyException("must provide a google vision key")
        self.process_raw_image_urls = process_raw_image_urls
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self.client = vision.ImageAnnotatorClient(credentials=api_key.Credentials(key))

    def image_to_text(self, img: Image) -> str:
        """
        Convert the given PIL Image object to text using OCR.
        """
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image = vision.Image(content=buffer.getvalue())
        logging.debug(f"google OCR image: {img}")
        response = self.client.text_detection(image=image)
        if response.error.message:
            raise Exception(
                "{}\nFor more info on errors, check:\n"
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message
                )
            )
        text = response.full_text_annotation.text
        return text.strip()

    @staticmethod
    def _download_image_from_http(url: str) -> bytes:
        """
        Download the image from the HTTP URL and return its data.
        """
        response = requests.get(url, headers=REQUEST_HEADERS.copy())
        if response.status_code != 200:
            raise ValueError(
                f"HTTP request failed with status code {response.status_code}"
            )
        if not response.headers["Content-Type"].startswith("image/"):
            raise ValueError(
                f"Expected an image, but got {response.headers['Content-Type']}"
            )
        return response.content

    @classmethod
    def _image_from_uri(cls, url: str, base_dir: Path) -> str:
        """
        Download an image from the given URL and convert it to text using OCR.
        """
        try:
            if cls._is_base64_string(url):
                imgdata = cls._base64_image_to_bytes(url)
                return Image.open(BytesIO(imgdata))
            elif url.split("://")[0] not in ["http", "https"]:
                return Image.open(BytesIO((base_dir / url).read_bytes()))
            else:
                img_data = cls._download_image_from_http(url)
                return Image.open(BytesIO(img_data))
        except Exception as e:
            raise LoadImageException(f"Failed to download image: {e}") from e

    @staticmethod
    def _base64_image_to_bytes(base64_string: str) -> str:
        """
        Convert a base64 string into a data URL by encoding the base64 string.
        """
        base64_data = base64_string.split(",")[-1]
        return base64.b64decode(base64_data)

    @staticmethod
    def _is_base64_string(url: str) -> bool:
        """
        Check if the URL is a base64 string.
        """
        return url.startswith("data:image")
