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

def convert_file(filetype: str, file, image_processor_key, process_raw_image_urls=True, defang=True, save_to=None, **kwargs):
    file = Path(file)
    parser_class = get_parser_class(filetype, file.name)
    converter = parser_class(file, filetype, process_raw_image_urls, image_processor_key)
    output = converter.convert()
    if defang:
        output = Fanger(output).defang()
    if save_to:
        save_to = Path(save_to)
        save_to.mkdir(exist_ok=True, parents=True)
        (save_to/"markdown.md").write_text(output)
        for name, img in converter.images.items():
            img.save(save_to/name, format='png')
    return output