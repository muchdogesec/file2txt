from typing import Iterable
from .core import BaseParser, CustomParser
import csv, io
from itertools import chain

@CustomParser("csv", ["csv"])
class CsvFileParser(BaseParser):
    """
    Subclass of FileParser specifically for parsing CSV files.
    Inherits all methods from the parent class without modifications.
    """
    
    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        # return [self.file_content]
        c = csv.reader(io.StringIO(self.file_content))        
        return [self.process_sheet(list(c), f"csv-sheet")]
    
    def process_sheet(self, sheet: list[list[str]], sheet_name: str):
        output = []
        for row in sheet:
            if not any(row):
                continue
            processed_row = "| {} |".format(" | ".join(row))
            output.append(processed_row)

        if output:
            row = ["-"*(len(column_name) or 1) for column_name in sheet[0]]
            tabble_separator = "| {} |".format(" | ".join(row))
            first_row = output[0]
            other_rows = output[1:]
            sheet_header = f"#### ======= {sheet_name} ======="
            output = chain([sheet_header, "\n", first_row, tabble_separator], other_rows)
        return "\n".join(output)