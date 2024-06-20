import os
import openpyxl
import xlrd
from openpyxl.workbook.workbook import Workbook as OpenpyxlWorkbook
from xlrd.book import Book as XlrdBook

from .core import BaseParser, CustomParser
from .csv_file_parser import CsvFileParser

from xlrd.sheet import Sheet


@CustomParser("excel", ["xls", "xlsx"])
class ExcelFileParser(CsvFileParser):
    """
    Subclass of FileParser specifically for parsing Excel files.
    Overrides load_file to load the workbook and extract_text to extract workbook's sheets.
    """

    def load_file(self):
        """
        Opens and reads the Excel file
        """
        _, file_extension = os.path.splitext(self.file_path)
        if file_extension == ".xlsx":
            self.file_content = openpyxl.load_workbook(filename=self.file_path, read_only=False, keep_vba=True)
        elif file_extension == ".xls":
            self.file_content = xlrd.open_workbook(self.file_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}. Only .xls and .xlsx are supported.")

    def extract_text(self) -> list[str]:
        """
        Extracts and returns text from an Excel file.
        """
        text = ""
        
        result_texts = []
        if isinstance(self.file_content, OpenpyxlWorkbook):
            for sheet_name in self.file_content.sheetnames:
                current_sheet = self.file_content[sheet_name]
                # handle text cells
                processed_rows = []
                for row in current_sheet.iter_rows(values_only=True):
                    processed_rows.append([str(cell or '') for cell in row])

                text = self.process_sheet(processed_rows, sheet_name)
                
                # handle images
                if getattr(current_sheet, "_images", None):
                    # convert openpyxl Image to BytesIO
                    image_bytesio = [img.ref for img in current_sheet._images]
                    # convert BytesIO to PIL Images
                    images = self.convert_bytesio_to_images(image_bytesio)
                    img_texts = self.image_processor.images_to_text(images)
                    text += img_texts
                    
                # Call replace_image_links_with_text and add the resulting text to the original text
                text += self.get_text_from_image_urls(text) 
                text = self.remove_image_links(text)
                result_texts.append(text)

        elif isinstance(self.file_content, XlrdBook):
            for sheet_name in self.file_content.sheet_names():
                text = ""
                current_sheet = self.file_content[sheet_name]
                # handle text cells
                rows = current_sheet.get_rows()
                processed_rows = []
                for row in rows:                                                                  
                    # text += '| ' + ' | '.join(str(cell.value) for cell in row if cell is not None)
                    # text += ' |\n'
                    processed_rows.append([str(cell.value or '') for cell in row])

                text = self.process_sheet(processed_rows, sheet_name)
                
                # Call replace_image_links_with_text and add the resulting text to the original text
                text += self.get_text_from_image_urls(text) 
                text = self.remove_image_links(text)
                result_texts.append(text)
        else:
            raise ValueError("Unsupported workbook type.")

        return result_texts
    