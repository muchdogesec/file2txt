from file2txt.openai_processor import BaseCleaner
from .parsers.core import BaseParser
from .fanger import Fanger
from pathlib import Path
from typing import Type


def get_parser_class(input_type: str, filename: str) -> Type[BaseParser]:
    if input_type not in BaseParser.PARSERS:
        raise ValueError(f"Unsupported input type: {input_type}")

    parser_class, mimetypes, supported_extensions = BaseParser.PARSERS[input_type]
    if not any(filename.endswith(ext) for ext in supported_extensions):
        raise ValueError(f"Unsupported file extension for `{filename}` in mode `{input_type}`. {supported_extensions=}")



    return parser_class

def convert_file(filetype: str, file, image_processor_key, process_raw_image_urls=True, defang=True, md_cleaner: Type[BaseCleaner] = None):
    file = Path(file)
    parser_class = get_parser_class(filetype, file.name)
    parser = parser_class(file, filetype, process_raw_image_urls, image_processor_key)
    texts = parser.extract_text()
    texts, images = parser.separate_images_from_texts(texts)
    if md_cleaner:
        texts = parser.cleanup_with_ai(md_cleaner, texts)
    if defang:
        texts = Fanger(texts).defang()
    if process_raw_image_urls:
        for i, image_str in enumerate(images):
            images[i] = parser.proccess_images_to_text(image_str)
    return parser.combine_text_and_images(texts, images)