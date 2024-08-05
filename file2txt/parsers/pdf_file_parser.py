import json
import logging
import os
from pathlib import Path
import subprocess
import time

import pypdfium2 as pdfium # Needs to be at the top to avoid warnings

from marker.convert import convert_single_pdf
from marker.models import load_all_models
from marker.settings import settings as marker_settings
from .marker_file_parser import split_marker_pages
from .core import BaseParser, custom_parser


@custom_parser("pdf", ["pdf"])
class PdfFileParser(BaseParser):
    """
    Subclass of FileParser specifically for parsing PDF files.
    Overrides load_file to load the PDF data and extract_text to extract text and images from the PDF's pages.
    """
    
    def extract_text(self) -> list[str]:
        marker_settings.PAGINATE_OUTPUT = True
        models = load_all_models()
        text, page_images, stats = convert_single_pdf(str(self.file_path), model_lst=models, max_pages=1)
        self.images.update(page_images)
        return split_marker_pages(text)
