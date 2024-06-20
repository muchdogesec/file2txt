from abc import ABC
from PIL import Image
from io import BytesIO
import logging

from .core import BaseParser, CustomParser

@CustomParser("image", ['jpg', 'jpeg', 'png', 'webp', 'gif'])
class ImageFileParser(BaseParser):
    """
    An abstract class for parsing files. It loads the content of a file and provides functionality for extracting text
    and finding image links within it.
    """

    def load_file(self):
        """
        Opens and reads the file specified in the file_path attribute, storing the content in the file_content attribute
        """
        with open(self.file_path, "rb") as image_file:
            self.file_content = image_file.read()

    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        try:
            img = Image.open(BytesIO(self.file_content))
        except Exception as e:
            logging.error(f"Failed to process image: {e}")
            return ""

        try:
            text = self.image_processor._image_to_text(img)
        except Exception as e:
            logging.error(f"Failed to convert image to text: {e}")
            return ""

        return [text]

   
