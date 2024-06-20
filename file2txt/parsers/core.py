from pathlib import Path
import re
from abc import ABC
import shutil
import tempfile
from types import NoneType
from urllib.parse import quote
from PIL import Image
import io

from ..image_processor import ImageProcessor


class BaseParser(ABC):
    """
    An abstract class for parsing files. It loads the content of a file and provides functionality for extracting text
    and finding image links within it.
    """

    temp_dir: Path|NoneType = None

    PARSERS = {}

    def __init__(self, file_path: str, input_type: str, process_raw_image_urls: bool, keyfile: str):
        """
        Initialize FileParser with the path to the file and the type of the input.
        """
        self.file_path = file_path
        self.input_type = input_type
        self.process_raw_image_urls = process_raw_image_urls
        self.file_content = None
        self.image_processor = ImageProcessor(process_raw_image_urls, keyfile)
        self.load_file()

    def load_file(self):
        """
        Opens and reads the file specified in the file_path attribute, storing the content in the file_content attribute
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.file_content = file.read()

    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        text = self.file_content + self.get_text_from_image_urls(self.file_content)
        return [self.remove_image_links(text)]

    def find_image_links(self, text: str) -> list[str]:
        """
        Uses a regex pattern to find all image links within a text string and returns them in a list.
        Also checks for base64 encoded image strings and decodes them into data URLs.
        """
        image_regex = r'\b(?:https?://\S+?\.(?:tiff|jpeg|jpg|png|bmp|gif|pnm|webp))\b'
        image_links = list(set(re.findall(image_regex, text, re.IGNORECASE)))
        base64_image_regex = r'data:image/[a-zA-Z+.-]+;base64,[a-zA-Z0-9+/]+=*'
        base64_images = list(set(re.findall(base64_image_regex, text, re.IGNORECASE)))
        base64_urls = [self._base64_to_data_url(img) for img in base64_images]
        return image_links + base64_urls

    @staticmethod
    def _base64_to_data_url(base64_string: str) -> str:
        """
        Convert a base64 string into a data URL by encoding the base64 string.
        """
        base64_data = base64_string.split(',')[1]
        return quote(base64_data)

    @staticmethod
    def _is_base64_string(url: str) -> bool:
        """
        Check if the URL is a base64 string.
        """
        return url.startswith('data:image')

    def get_text_from_image_urls(self, text: str) -> str:
        """
        Replace all image links in the provided text with their text representations.
        """
        image_links = self.find_image_links(text)
        replaced_text = self.image_processor.urls_to_text(image_links)

        return ' ' + replaced_text

    def remove_image_links(self, text: str) -> str:
        """
        Find all image links in the provided text and replace them with an empty string.
        """
        image_links = self.find_image_links(text)
        for link in image_links:
            text = text.replace(link, '')
        return text

    @staticmethod
    def convert_bytes_to_images(images_bytes: list[bytes]) -> list[Image.Image]:
        """
        Convert a list of bytes to a list of PIL Images
        """
        pil_images = []
        for img_bytes in images_bytes:
            image = Image.open(io.BytesIO(img_bytes))
            pil_images.append(image)
        return pil_images

    @staticmethod
    def convert_bytesio_to_images(images_bytesio: list[io.BytesIO]) -> list[Image.Image]:
        """
        Convert a list of BytesIO objects to a list of PIL Images
        """
        pil_images = []
        for img_bytesio in images_bytesio:
            # Read the bytes from the BytesIO object
            image = Image.open(img_bytesio)
            pil_images.append(image)
        return pil_images
    
    def __del__(self):
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def mkdtemp(self, *args, **kwargs):
        self.temp_dir = Path(tempfile.mkdtemp(*args, **kwargs))
        return self.temp_dir
    
    @classmethod
    def register_parser(cls, klass, mode, mimetypes, extensions):
        cls.PARSERS[mode] = [klass, mimetypes, extensions]


def CustomParser(mode, extensions, mimetypes=[]):
    def wrapper(klass):
        BaseParser.register_parser(klass, mode, mimetypes, extensions)
        return klass
    return wrapper