from PIL import Image

from .core import BaseParser, custom_parser

@custom_parser("image", ['jpg', 'jpeg', 'png', 'webp', 'gif'])
class ImageFileParser(BaseParser):
    """
    An abstract class for parsing files. It loads the content of a file and provides functionality for extracting text
    and finding image links within it.
    """

    def prepare_extractor(self):
        self.process_raw_image_urls = True
        return super().prepare_extractor()

    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        with open(self.file_path, "rb") as image_file:
            self.images['0_image_0.png'] = Image.open(image_file).copy()
        return [f"![{self.file_path.name}](0_image_0.png)"]

   
