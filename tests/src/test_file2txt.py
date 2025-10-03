import pytest
from unittest.mock import patch, MagicMock
import sys
import types
import importlib
import importlib.util

spec = importlib.util.spec_from_file_location("aaa", "./file2txt.py")
file2txt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(file2txt)

def test_str_to_bool_true():
    for val in ['yes','true','t','y','1','YES','True','T','Y','1']:
        assert file2txt.str_to_bool(val) is True

def test_str_to_bool_false():
    for val in ['no','false','f','n','0','NO','False','F','N','0']:
        assert file2txt.str_to_bool(val) is False

def test_str_to_bool_error():
    with pytest.raises(Exception):
        file2txt.str_to_bool('maybe')

def test_parse_arguments(monkeypatch):
    argv = ['file2txt.py','--mode','csv','--file','input.csv']
    monkeypatch.setattr(sys, 'argv', argv)
    args = file2txt.parse_arguments()
    assert args.mode == 'csv'
    assert args.file == 'input.csv'

# @patch('aaa.parse_arguments')
# def test_main(mock_parse_args, monkeypatch):
#     monkeypatch.setattr('dotenv.load_dotenv', lambda: None)
#     mock_parse_args.return_value = types.SimpleNamespace(
#         mode='csv', file='input.csv', output=None, extract_text_from_image=True, defang=True
#     )
    
#     patch_logger = patch('logging.info')
#     patch_convert_file = patch('file2txt.convert_file', return_value="output")
#     with patch_logger as log, patch_convert_file as conv:
#         with patch('pathlib.Path.exists', return_value=False), patch('os.getenv', return_value=None):
#             with patch('pathlib.Path.mkdir'):
#                 try:
#                     exec(open('file2txt.py').read())
#                 except Exception:
#                     pass
#         conv.assert_called_once()