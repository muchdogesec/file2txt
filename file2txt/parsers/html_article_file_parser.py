from bs4 import BeautifulSoup
from readability.readability import Document

from .html_file_parser import HtmlFileParser
from .core import CustomParser
import datetime

@CustomParser("html_article", ["html"])
class HtmlArticleFileParser(HtmlFileParser):
    """
    A subclass of HtmlFileParser, specifically for parsing HTML files representing articles.
    Utilizes the readability library to extract the main content of the article from the HTML file.
    """

    def load_file(self):
        super().load_file()
        doc = Document(self.file_content)
        self.file_content = doc.summary()
        
        self.soup = BeautifulSoup(self.file_content, 'html.parser')
    