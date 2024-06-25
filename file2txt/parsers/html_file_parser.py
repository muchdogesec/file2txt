from abc import ABC
from bs4 import BeautifulSoup
from .core import BaseParser, CustomParser
from PIL import Image
from io import BytesIO
import logging
import os
from markdownify import markdownify


@CustomParser("html", ["html"])
class HtmlFileParser(BaseParser, ABC):
    """
    Subclass of FileParser specifically for parsing HTML documents.
    Overrides load_file to load the HTML and parse it with BeautifulSoup.
    Overrides extract_text to extract and return text from the HTML.
    """

    soup = None

    def load_file(self):
        """
        Opens and reads the HTML file specified in the file_path attribute,
        storing the HTML content in the file_content attribute,
        and parsing it into a BeautifulSoup object stored in the soup attribute.
        """
        super().load_file()
        self.soup = BeautifulSoup(self.file_content, 'html.parser')

    def extract_text(self) -> list[str]:
        """
        Extracts and returns text from the HTML document,
        including replacing link tags and inserting image text into HTML.
        """
        text = self.extract_text_from_html(self.soup)
        return [text]

    def extract_text_from_html(self, soup) -> str:
        self._replace_img_tags(soup)
        return markdownify(soup.prettify())


    def _replace_img_tags(self, soup) -> list[str]:
        img_tags = soup.find_all('img')        
        for img in img_tags:
            img['src'] = img.get("src") or img.get('data-src')
