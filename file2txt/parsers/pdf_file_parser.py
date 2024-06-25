import logging
import os
from pathlib import Path
import subprocess

from file2txt.parsers.html_file_parser import HtmlFileParser

from .core import CustomParser
from bs4 import BeautifulSoup
import fitz, pymupdf4llm, shutil

class PopplerException(Exception):
    pass

@CustomParser("pdf-poppler", ["pdf"])
class PdfFileParser(HtmlFileParser):
    """
    Subclass of FileParser specifically for parsing PDF files.
    Overrides load_file to load the PDF data and extract_text to extract text and images from the PDF's pages.
    """

    def load_file(self):
        """
        Opens and reads the PDF file specified in the file_path attribute,
        storing the PDF data in the file_content attribute.
        """
        try:
            self.executable_path = os.getenv("POPPLER_PDFTOHTML_PATH", "pdftohtml")
            outdir = self.mkdtemp(prefix=__name__.split(".")[0]+"_")
            logging.info(f"writing temporary files to {outdir}")
            subprocess.check_call([
                self.executable_path,
                "-c", # output complex document
                self.file_path,
                "-s",        # generate single document that includes all pages
                outdir/"output",
            ])
            self.file_content = (outdir/"output-html.html").read_bytes()
            self.prepare_soup(outdir)
        except BaseException as e:
            raise PopplerException(f"failed to run pdftohtml on {self.file_path}") from e
    
    def extract_text(self) -> list[str]:
        output = []
        for soup in self.soup.find_all("html"):
            text = self.extract_text_from_html(soup)
            output.append(text)
        return output
        
    def prepare_soup(self, parent_dir: Path):
        self.soup = BeautifulSoup(self.file_content, "html.parser")
        for title in self.soup.find_all("title"):
            title.extract()

@CustomParser("pdf", ["pdf"])
class PymupdfFileParser(HtmlFileParser):
    def load_file(self):
        outdir = self.mkdtemp(prefix=__name__.split(".")[0]+"_")
        shutil.copy(self.file_path, outdir/"images")
        self.file_path = outdir/"images"
        
    def extract_text(self) -> list[str]:
        doc = fitz.open(self.file_path)
        md_text = [self.remove_html_elements(pymupdf4llm.to_markdown(doc, write_images=True, pages=[page])) for page in range(doc.page_count)]
        return md_text
    
    @staticmethod
    def remove_html_elements(string: str):
        return string #.replace("<", "&lt;").replace(">", "&gt;")