from abc import ABC
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from file2txt.image_processor import ImageProcessor
from .core import BaseParser, custom_parser
import logging
from markdownify import markdownify
from bs4 import BeautifulSoup
from readability.readability import Document

from .core import custom_parser

@custom_parser("html", ["html"])
class HtmlFileParser(BaseParser, ABC):
    """
    Subclass of FileParser specifically for parsing HTML documents.
    Overrides load_file to load the HTML and parse it with BeautifulSoup.
    Overrides extract_text to extract and return text from the HTML.
    """

    soup = None

    def prepare_extractor(self):
        """
        Opens and reads the HTML file specified in the file_path attribute,
        storing the HTML content in the file_content attribute,
        and parsing it into a BeautifulSoup object stored in the soup attribute.
        """
        self.soup = BeautifulSoup(self.file_path.read_text(), 'html.parser')
        return super().prepare_extractor()

    def extract_text(self) -> list[str]:
        """
        Extracts and returns text from the HTML document,
        including replacing link tags and inserting image text into HTML.
        """
        self.prepare_extractor()
        text = self.extract_text_from_html(self.soup)
        return [text]
    
    def make_links_absolute(self):
        for anchor in self.soup.find_all('a'):
            anchor['href'] = urljoin(self.base_url, anchor.get('href', "#no-link"))

        for img in self.soup.find_all('img'):
            orig_src = img.get("src") or img.get('data-src') or '#no-image'
            img['src'] = urljoin(self.base_url, orig_src)

    def extract_text_from_html(self, soup: BeautifulSoup) -> str:
        self.make_links_absolute()
        self.find_images(soup)
        return markdownify(soup.prettify())

    def find_images(self, soup: BeautifulSoup):
        img_tags = soup.find_all('img')
        for img in img_tags:
            img['src'] = self.add_image(img['src'])
        
    def add_image(self, src):
        try:
            new_src = f"0_image_{len(self.images)}.png"
            if self.processed_image_base_url:
                new_src = urljoin(self.processed_image_base_url, new_src)
            self.images[new_src] = ImageProcessor._image_from_uri(src, self.file_path.parent)
            return new_src
        except BaseException as e:
            logging.debug(e)
            return src
        
    def convert(self, processed_image_base_url=None, **kwargs) -> str:
        self.processed_image_base_url = processed_image_base_url
        return super().convert(**kwargs)



@custom_parser("html_article", ["html"])
class HtmlArticleFileParser(HtmlFileParser):
    """
    A subclass of HtmlFileParser, specifically for parsing HTML files representing articles.
    Utilizes the readability library to extract the main content of the article from the HTML file.
    """

    def prepare_extractor(self):
        super().prepare_extractor()
        doc = Document(self.soup.prettify())
        self.soup = BeautifulSoup(doc.summary(), 'html.parser')
    