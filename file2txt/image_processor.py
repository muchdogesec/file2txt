import codecs
import io
import logging
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, List
import requests
from PIL import Image
from google.oauth2 import service_account
from google.cloud import vision
import os 
import base64


class ImageProcessor:
    def __init__(self, process_raw_image_urls: bool, key: str|dict):
        self.process_raw_image_urls = process_raw_image_urls
        self.img_counter = 0
        self.characters_counter = 0
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        if isinstance(key, str):
            credentials = service_account.Credentials.from_service_account_file(
                filename=key,
                scopes=scopes)
        else:
            credentials = service_account.Credentials.from_service_account_info(
                key,
                scopes=scopes)
        
        self.client = vision.ImageAnnotatorClient(credentials=credentials)

    def urls_to_text(self, urls: list[str], base_dir=None) -> str:
        """
        Get text from all given URLs.
        """
        if not self.process_raw_image_urls:
            return ''
        base_dir = Path(base_dir or "")
        return self._process_to_text(urls, 'URL IMAGE', base_dir)

    def _base64_to_text(self, base64_string):
        try:
            imgdata = base64.b64decode(str(base64_string))
            img = Image.open(BytesIO(imgdata))
        except Exception as e:
            logging.error(f"Failed to process image: {e}")
            return ""
        try:
            text = self._image_to_text(img)
        except Exception as e:
            logging.error(f"Failed to convert image to text: {e}")
            return ""
        return text        

    def _image_to_text(self, img: Image) -> str:
        """
        Convert the given PIL Image object to text using OCR.
        """
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image = vision.Image(content=buffer.getvalue())
        logging.debug(f'google OCR image: {img}')
        response = self.client.text_detection(image=image)
        if response.error.message:
            raise Exception(
                "{}\nFor more info on errors, check:\n"
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message))
        text = response.text_annotations[0].description
        self._update_counters(text)
        return text
    
    

    def _update_counters(self, text: str):
        """
        Update the counters for the number of processed images and characters.
        """
        self.img_counter += 1
        self.characters_counter += len(text)

    @staticmethod
    def _download_image_from_http(url: str) -> bytes:
        """
        Download the image from the HTTP URL and return its data.
        """
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"HTTP request failed with status code {response.status_code}")
        if not response.headers['Content-Type'].startswith('image/'):
            raise ValueError(f"Expected an image, but got {response.headers['Content-Type']}")
        return response.content

    def _process_to_text(self, items: List, item_type: str, base_dir) -> str:
        """
        Process a list of items (either images or URLs) to text.
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            texts = list(executor.map(lambda url: self.process_to_text_worker(url, base_dir), items))
            
        formatted_texts = [f"\n[comment]: <> (===START {item_type} EXTRACTION===)\n ![image]({url})\n{text}\n\n[comment]: <> (===END {item_type} EXTRACTION===)\n" for url, text in texts]
        return formatted_texts
    
    def process_to_text_worker(self, url: str, base_dir: Path) -> str:
        """
        Download an image from the given URL and convert it to text using OCR.
        """
        if self._is_base64_string(url):            
            base64_string = self._base64_to_data_url(url)
            return url, self._base64_to_text(base64_string)

        
        try:
            if url.split("://")[0] not in ["http", "https"]:
                img = Image.open(BytesIO((base_dir/url).read_bytes()))
                return self.process_to_text_worker(image_to_data_url(img), None)
            else:
                img_data = self._download_image_from_http(url)
        except Exception as e:
            logging.error(f"Failed to download image: {e}")
            return url, ""
        

        try:
            img = Image.open(BytesIO(img_data))
        except Exception as e:
            logging.error(f"Failed to process image: {e}")
            return url, ""

        try:
            text = self._image_to_text(img)
        except Exception as e:
            logging.error(f"Failed to convert image to text: {e}")
            return url, ""

        return url, text
    
    @staticmethod
    def _base64_to_data_url(base64_string: str) -> str:
        """
        Convert a base64 string into a data URL by encoding the base64 string.
        """
        base64_data = base64_string.split(',')[1]
        return base64_data

    @staticmethod
    def _is_base64_string(url: str) -> bool:
        """
        Check if the URL is a base64 string.
        """
        return url.startswith('data:image')


def image_to_data_url(img):
    buffered = io.BytesIO()
    img.save(buffered, format="png")
    return 'data:image/jpeg;base64,' + codecs.encode(buffered.getvalue(), encoding="base64").replace(b"\n", b"").decode("utf-8")