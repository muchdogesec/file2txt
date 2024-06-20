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

    def __init__(self, *args, **kwargs) -> None:
        self.soup = None
        super().__init__(*args, **kwargs)

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
        text = self._extract_text_from_html()
        return [text]

    def _extract_text_from_html(self) -> str:
        self._insert_image_text_into_html()
        self._replace_link_tags()
        return markdownify(self.soup.prettify())

    def _insert_image_text_into_html(self) -> None:
        self._replace_img_tags()

    def _insert_text_into_html(self, text):
        div_tag = self.soup.new_tag("div")
        div_tag.string = text
        self.soup.append(div_tag)

    def _replace_link_tags(self) -> None:
        for a_tag in self.soup.find_all('a'):
            a_tag.replace_with(a_tag.get_text())

    def _wrap(self, to_wrap, wrap_in) -> None:
        contents = to_wrap.replace_with(wrap_in)
        wrap_in.append(contents)

    def _replace_img_tags(self) -> list[str]:
        img_tags = self.soup.find_all('img')        
        for img in img_tags:
            if src := img.get("src") or img.get('data-src'):
                logging.info("found image at %s", src[:200])
                logging.debug("found image at %s", src)
                text = self.image_processor.tags_to_text([src]) 
                div_tag = self.soup.new_tag("div")
                div_tag.string = text
                img.replace_with(div_tag)

    def _find_links_in_html_text(self) -> list[str]:
        html_text = self.soup.get_text()
        links_in_text = self.find_image_links(html_text)
        return links_in_text
