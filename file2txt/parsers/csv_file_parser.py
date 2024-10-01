from .core import BaseParser, custom_parser
import pandas as pd


@custom_parser("csv", ["csv"])
class CsvFileParser(BaseParser):
    """
    Subclass of FileParser specifically for parsing CSV files.
    Inherits all methods from the parent class without modifications.
    """
    
    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        
        with open(self.temp_dir/"output.md", 'w') as f:
            pd.read_csv(self.file_path).to_markdown(f)
        return [(self.temp_dir/"output.md").read_text()]