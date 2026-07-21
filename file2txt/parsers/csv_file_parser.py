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

        with open(self.temp_dir / "output.md", "w") as f:
            self.read_file().to_markdown(f)
        return [(self.temp_dir / "output.md").read_text()]

    def read_file(self) -> pd.DataFrame:
        """
        Reads the CSV file and returns its content as a pandas DataFrame.
        """
        encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
        errors: list[UnicodeDecodeError] = []

        for encoding in encodings:
            try:
                return pd.read_csv(self.file_path, encoding=encoding)
            except UnicodeError as exc:
                errors.append(exc)
        raise ExceptionGroup(
            f"Unable to decode {self.file_path!s} using any supported encoding",
            errors,
        )