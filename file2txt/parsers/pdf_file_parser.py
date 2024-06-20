from io import BytesIO
import logging
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from file2txt.parsers.html_file_parser import HtmlFileParser

from .core import BaseParser, CustomParser
import time
from bs4 import BeautifulSoup

class PopplerException(Exception):
    pass

@CustomParser("pdf", ["pdf"])
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
                # "-c", # output complex document
                self.file_path,
                "-s",        # generate single document that includes all pages
                "-dataurls", # use data URLs instead of external images in HTML
                outdir/"output",
            ])
            self.file_content = (outdir/"output-html.html").read_bytes()
            self.prepare_soup()
        except BaseException as e:
            raise PopplerException(f"failed to run pdftohtml on {self.file_path}") from e
        
    def prepare_soup(self):
        self.soup = BeautifulSoup(self.file_content, "lxml")
