from pathlib import Path
import shutil
import tempfile

from .core import CustomParser

from .pdf_file_parser import PdfFileParser
from .html_file_parser import HtmlFileParser

import pypandoc


@CustomParser("word", ["docx"])
class WordFileParser(HtmlFileParser):
    """
    Subclass of FileParser specifically for parsing Word documents.
    Overrides load_file to load the document and extract_text to extract text from the document and its images.
    """
    def load_file(self) -> None:
        self.mkdtemp(prefix="file2txt_qword")
        outfile = self.temp_dir/"output.html"
        pypandoc.convert_file(self.file_path, "html", extra_args=["--standalone", "--extract-media", self.temp_dir], outputfile=outfile)          
        self.file_path = outfile
        super().load_file()
    
        
     