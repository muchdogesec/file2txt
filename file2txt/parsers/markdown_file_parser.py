from bs4 import BeautifulSoup

from .core import custom_parser, BaseParser
from .html_file_parser import HtmlFileParser
import mistune


@custom_parser("md", ["md", "markdown"])
class MarkdownParser(HtmlFileParser):
    def prepare_extractor(self):
        self.raw_html = mistune.html(self.file_path.read_text())
        self.soup = BeautifulSoup(self.raw_html, 'html.parser')
