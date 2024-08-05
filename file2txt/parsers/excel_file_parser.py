import pandas as pd
from .core import BaseParser, custom_parser


@custom_parser("excel", ["xls", "xlsx"])
class ExcelFileParser(BaseParser):
    """
    Subclass of FileParser specifically for parsing Excel files.
    Overrides load_file to load the workbook and extract_text to extract workbook's sheets.
    """

    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        
        with open(self.temp_dir/"output.md", 'w') as f:
            pd.read_excel(self.file_path).to_markdown(f)
        return [(self.temp_dir/"output.md").read_text()]