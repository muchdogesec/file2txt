import os
import subprocess
import sys
import textwrap


def test_parser_registry_is_lightweight_and_csv_loads_pandas_on_demand():
    subprocess.run([sys.executable, '-c', textwrap.dedent('''
        import sys
        import tempfile
        from pathlib import Path
        from file2txt.parsers.core import BaseParser
        from file2txt.parsers.csv_file_parser import CsvFileParser
        from file2txt.parsers.excel_file_parser import ExcelFileParser

        assert 'csv' in BaseParser.PARSERS
        assert 'excel' in BaseParser.PARSERS
        assert 'pandas' not in sys.modules
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'sample.csv'
            source.write_text('name,value\\nexample,42\\n')
            parser = CsvFileParser(source, 'csv', False, None)
            assert 'example' in parser.extract_text()[0]
            assert 'pandas' in sys.modules
    ''')], check=True, timeout=120, env=os.environ.copy())
