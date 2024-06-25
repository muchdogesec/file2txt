import base64
import codecs
import logging
from pathlib import Path
import re
from abc import ABC
import shutil
import tempfile
from types import NoneType
from typing import Any
from urllib.parse import quote
from PIL import Image
import io

from file2txt.openai_processor import BaseCleaner

from ..image_processor import ImageProcessor, image_to_data_url


class BaseParser(ABC):
    """
    An abstract class for parsing files. It loads the content of a file and provides functionality for extracting text
    and finding image links within it.
    do not remove the comments.
    """
    IMAGE_SEP_FINDER  = "[image-break]"
    PAGE_SEP_FINDER   = "[page-break]"
    IMAGE_SEPARATOR   = "\n---\n[image-break]:# (This is a break between text and images)\n\n"
    temp_dir: Path|NoneType = None
    PAGE_SEPARATOR    = "\n---\n[page-break]:# (This is a page break)\n---\n"
    MARKDOWN_IMAGE_RE = re.compile(r"(!\[([^\]]*)\]\(([^\^)]+)\))")

    PARSERS = {}

    def __init__(self, file_path: str, input_type: str, process_raw_image_urls: bool, keyfile: str):
        """
        Initialize FileParser with the path to the file and the type of the input.
        """
        self.file_path = Path(file_path)
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

    def cleanup_with_ai(self, processor: BaseCleaner, text_contents: list[str]):
        cleaned_content = []
        for index, page_str in enumerate(text_contents):
            logging.info(f"cleaning page {index+1} of {len(text_contents)}")
            cleaned_content.append(processor.do_cleanup(page_str))
        return cleaned_content

    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        text = self.file_content + self.get_text_from_image_urls(self.file_content)
        return text

    
    def __del__(self):
        try:
            if self.temp_dir:
                logging.info("removing temp dir at %s", self.temp_dir)
                shutil.rmtree(self.temp_dir)
        except:
            pass

    def mkdtemp(self, *args, **kwargs):
        self.temp_dir = Path(tempfile.mkdtemp(*args, **kwargs))
        return self.temp_dir
    
    @classmethod
    def register_parser(cls, klass, mode, mimetypes, extensions):
        cls.PARSERS[mode] = [klass, mimetypes, extensions]

    @classmethod
    def format_markdown_image(cls, image_or_url, title=""):
        url = image_or_url
        if isinstance(image_or_url, Image.Image):
            url = image_to_data_url(image_or_url)
        return f"![{title}]({url})"
    
    @classmethod
    def find_images(cls, text):
        matches = cls.MARKDOWN_IMAGE_RE.findall(text)
        return matches
    
    def proccess_images_to_text(self, texts):
        links = []
        found_images = self.find_images(texts)
        for whole, title, link in found_images:
            links.append(link)
        image_texts = self.image_processor.urls_to_text(links, self.temp_dir)
        for i, (whole, title, _) in enumerate(found_images):
            texts = texts.replace(whole, image_texts[i])
        return texts
    
    def separate_images_from_texts(self, texts):
        texts_out = [None] * len(texts)
        images_out = []
        for page, page_str in enumerate(texts):
            page_images = []
            for i, (whole, title, link) in enumerate(self.find_images(page_str)):
                ltitle = f"image-{page+1}-{i+1}".lower()
                replacement = f"[{ltitle}](#{ltitle})"
                page_str = page_str.replace(whole, replacement)
                page_images.append(f"###### {ltitle}\n{whole}")
            texts_out[page] = page_str
            images_out.append("\n\n".join(page_images))
        return texts_out, images_out
    
    def combine_text_and_images(self, texts, images):
        return [self.IMAGE_SEPARATOR.join(v) for v in zip(texts, images)]


def CustomParser(mode, extensions, mimetypes=[]):
    def wrapper(klass):
        BaseParser.register_parser(klass, mode, mimetypes, extensions)
        return klass
    return wrapper


def chunked(iterable: list[Any], chunk_size=2):
    for start in range(0, len(iterable), chunk_size):
        end = start+chunk_size
        yield start+1, end, iterable[start: end]