
from pathlib import Path
import pytest
from unittest.mock import patch
from file2txt.parsers.excel_file_parser import ExcelFileParser

data = '''
|    |   0 | First Name   | Last Name   | Gender   | Country       |   Age | Date       |   Id |
|---:|----:|:-------------|:------------|:---------|:--------------|------:|:-----------|-----:|
|  0 |   1 | Dulce        | Abril       | Female   | United States |    32 | 15/10/2017 | 1562 |
|  1 |   2 | Mara         | Hashimoto   | Female   | Great Britain |    25 | 16/08/2016 | 1582 |
|  2 |   3 | Philip       | Gent        | Male     | France        |    36 | 21/05/2015 | 2587 |
|  3 |   4 | Kathleen     | Hanner      | Female   | United States |    25 | 15/10/2017 | 3549 |
|  4 |   5 | Nereida      | Magwood     | Female   | United States |    58 | 16/08/2016 | 2468 |
|  5 |   6 | Gaston       | Brumm       | Male     | United States |    24 | 21/05/2015 | 2554 |
|  6 |   7 | Etta         | Hurn        | Female   | Great Britain |    56 | 15/10/2017 | 3598 |
|  7 |   8 | Earlean      | Melgar      | Female   | United States |    27 | 16/08/2016 | 2456 |
|  8 |   9 | Vincenza     | Weiland     | Female   | United States |    40 | 21/05/2015 | 6548 |
'''

def test_extract_text():
    path = Path('tests/files/excel-sample.xls')
    parser = ExcelFileParser(path, "xls", False, None)
    out = parser.extract_text()
    assert out == [data.strip()]

