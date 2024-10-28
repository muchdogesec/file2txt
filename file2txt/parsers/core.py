import io
import logging
from pathlib import Path
import re
from abc import ABC
import shutil
import tempfile
from textwrap import dedent
from types import NoneType
from PIL import Image
import filetype


from ..image_processor import ImageProcessor


class BaseParser(ABC):
    """
    An abstract class for parsing files. It loads the content of a file and provides functionality for extracting text
    and finding image links within it.
    do not remove the comments.
    """
    IMAGE_SEP_FINDER  = "[image-break]"
    PAGE_SEP_FINDER   = "[page-break]"
    _temp_dir: Path|NoneType = None
    MARKDOWN_IMAGE_RE = re.compile(r"(!\[([^\]]*)\]\(([^\^)]+\.png)( .*?){0,1}\))")
    PARSERS = {}



    image_processor: ImageProcessor = None
    mimetype = None

    def __init__(self, file_path: str, input_type: str, process_raw_image_urls: bool, vision_apikey: str, base_url=None):
        """
        Initialize FileParser with the path to the file and the type of the input.
        """
        self.file_path = Path(file_path)
        self.input_type = input_type
        self.process_raw_image_urls = process_raw_image_urls
        self.images: dict[str, Image.Image] = {}
        self.vision_apikey = vision_apikey
        self.prepare_extractor()
        self.base_url = base_url

    def prepare_extractor(self):
        """
        Extracts and returns the text content from the file.
        """
        if self.process_raw_image_urls:
            self.image_processor = ImageProcessor(self.process_raw_image_urls, self.vision_apikey)
        try:
            self.mimetype: str = filetype.guess(self.file_path).mime
        except:
            pass


    def extract_text(self) -> list[str]:
        """
        Extracts and returns the text content from the file.
        """
        raise NotImplementedError("please implement in subclass")
    
    @staticmethod
    def join_pages(pages: list[str]):
        strbuf = io.StringIO()
        for i, page in enumerate(pages, start=1):
            strbuf.write(f"[comment]: <> (===START PAGE {i}===)\n")
            strbuf.write(page)
            strbuf.write(f"\n\n[comment]: <> (===END PAGE {i}===)\n")
        return strbuf.getvalue()

    def convert(self, **kwargs) -> str:
        texts = self.join_pages(self.extract_text())
        if not self.process_raw_image_urls:
            return texts
        image_texts = {}
        for i, (link, image) in enumerate(self.images.items()):
            try:
                image_texts[link] = self.image_processor.image_to_text(image)
            except Exception as e:
                logging.debug(e)

        for whole, _, link, _ in self.find_md_images(texts):
            if img_text := image_texts.get(link):
                texts = texts.replace(whole, dedent(f"""

[comment]: <> (===START IMAGE DETECTED===)
        
{whole}

[comment]: <> (===START EMBEDDED IMAGE EXTRACTION===)
{img_text}
[comment]: <> (===END EMBEDDED IMAGE EXTRACTION===)

[comment]: <> (===END IMAGE DETECTED===)
"""))
        return texts


    def __del__(self):
        try:
            if self._temp_dir:
                logging.info("removing temp dir at %s", self._temp_dir)
                shutil.rmtree(self._temp_dir)
        except:
            pass

    @property
    def temp_dir(self):
        if self._temp_dir:
            return self._temp_dir
        self._temp_dir = Path(tempfile.mkdtemp(prefix="file2txt_"))
        return self._temp_dir
    
    @classmethod
    def register_parser(cls, klass, mode, mimetypes, extensions):
        cls.PARSERS[mode] = [klass, mimetypes, extensions]

    @classmethod
    def find_md_images(cls, text):
        matches = cls.MARKDOWN_IMAGE_RE.findall(text)
        return matches
    

def custom_parser(mode, extensions, mimetypes=[]):
    def wrapper(klass):
        BaseParser.register_parser(klass, mode, mimetypes, extensions)
        return klass
    return wrapper


@custom_parser(
    'txt',
    extensions=["txt", "md", "markdown"]
)
class PlaintextParser(BaseParser):
    def extract_text(self) -> list[str]:
        return [Path(self.file_path).read_text()]