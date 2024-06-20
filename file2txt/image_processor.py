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

    def images_to_text(self, images: list[Image.Image]) -> str:
        """
        Get text from all given images.
        """
        return self._process_to_text(images, self._image_to_text, 'EMBEDDED IMAGE')

    def urls_to_text(self, urls: list[str]) -> str:
        """
        Get text from all given URLs.
        """
        if not self.process_raw_image_urls:
            return ''
        return self._process_to_text(urls, self._url_to_text, 'URL IMAGE')

    def tags_to_text(self, urls: list[str]) -> str:
        """
        Get text from all given URLs.
        """   
        return self._process_to_text(urls, self._url_to_text, 'EMBEDDED IMAGE')
    
    def webpages_to_text(self, images: list[Image.Image]) -> str:
        """
        Get text from all given webpage images.
        """
        return self._process_to_text_without_tag(images, self._webpage_to_text)
    
    def _webpage_to_text(self, img: Image) -> str:
        """
        Convert the given PIL Image object to text using OCR.
        """
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image = vision.Image(content=buffer.getvalue())
        response = self.client.text_detection(image=image)
        if response.error.message:
            raise Exception(
                "{}\nFor more info on errors, check:\n"
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message))
        text = response.text_annotations[0].description
        self._update_counters(text)
        return text

    def _url_to_text(self, url: str) -> str:
        """
        Download an image from the given URL and convert it to text using OCR.
        """
        if self._is_base64_string(url):            
            base64_string = self._base64_to_data_url(url)
            return self._base64_to_text(base64_string)

        try:
            img_data = self._download_image_from_http(url)
        except Exception as e:
            logging.error(f"Failed to download image: {e}")
            return ""

        try:
            img = Image.open(BytesIO(img_data))
        except Exception as e:
            logging.error(f"Failed to process image: {e}")
            return ""

        try:
            text = self._image_to_text(img)
        except Exception as e:
            logging.error(f"Failed to convert image to text: {e}")
            return ""

        return text

    def _base64_to_text(self, base64_string):
        try:
            imgdata = base64.b64decode(str(base64_string))
            #filename = 'temp.png' 
            #with open(filename, 'wb') as f:
            #    f.write(imgdata)
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
        if url.split("://")[0] not in ["http", "https"]:
            return Path(url).read_bytes()
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"HTTP request failed with status code {response.status_code}")
        if not response.headers['Content-Type'].startswith('image/'):
            raise ValueError(f"Expected an image, but got {response.headers['Content-Type']}")
        return response.content

    @staticmethod
    def _process_to_text(items: List, process_item: Callable, item_type: str) -> str:
        """
        Process a list of items (either images or URLs) to text.
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            texts = list(executor.map(process_item, items))

        
        formatted_texts = [f"\n[comment]: <> (===START {item_type} EXTRACTION===)\n{text}\n\n[comment]: <> (===END {item_type} EXTRACTION===)\n" for text in texts]

        return "".join(formatted_texts)
    
    @staticmethod
    def _process_to_text_without_tag(items: List, process_item: Callable) -> str:
        """
        Process a list of items (either images or URLs) to text.
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            texts = list(executor.map(process_item, items))
        return "".join(texts)
    
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
