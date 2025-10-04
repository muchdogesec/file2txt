import pytest
from file2txt.fanger import Fanger

def test_defang_replaces_patterns():
    text = "hxxp://test[dot]com {at}user"
    fanger = Fanger(text)
    out = fanger.defang()
    assert "http://test.com" in out
    assert "@user" in out

def test_apply_replacements_brackets():
    text = "[.]{.}(.){at}(at)[at]{:}(:)[/]{/}"
    out = Fanger._apply_replacements_to_text(text)
    assert "." in out
    assert "@" in out
    assert ":" in out
    assert "/" in out

def test_apply_replacements_spaces():
    text = " . @ / \\ : // "
    out = Fanger._apply_replacements_to_text(text)
    assert "." in out
    assert "@" in out
    assert "/" in out
    assert ":" in out

def test_defang_empty():
    fanger = Fanger("")
    assert fanger.defang() == ""