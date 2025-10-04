html_text = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample Image Display</title>
</head>
<body>

    <h1>Image 1</h1>
    <p>Public Domain icon from Wikimedia Commons (should display correctly):</p>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/PD-icon.svg/120px-PD-icon.svg.png" alt="PD icon">

    <h1>Image 2</h1>
    <p>Pixel red stop sign (should display correctly):</p>
    <img src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Pixel_Red_Stop_Sign_16x16.png" alt="Pixel Stop Sign">

    <h1>Image 3</h1>
    <p>Broken image (connection will likely be refused):</p>
    <img src="http://badlocalwebsite.net.crap.bad/not_an_image.txt" alt="Broken image (connection refused)">

    <h1>Image 4</h1>
    <p>Link to a Wikimedia Commons page that likely returns 404 (not an image URL):</p>
    <img src="https://commons.wikimedia.org/wiki/File:thisdoesnotexistso-404-possibly.png" alt="Broken image (404)">

</body>
</html>

"""
md_output_basic = '''
Sample Image Display


Image 1
=======

Public Domain icon from Wikimedia Commons (should display correctly):

![PD icon](0_image_0.png)

Image 2
=======

Pixel red stop sign (should display correctly):

![Pixel Stop Sign](0_image_1.png)

Image 3
=======

Broken image (connection will likely be refused):

![Broken image (connection refused)](http://badlocalwebsite.net.crap.bad/not_an_image.txt)

Image 4
=======

Link to a Wikimedia Commons page that likely returns 404 (not an image URL):

![Broken image (404)](https://commons.wikimedia.org/wiki/File:thisdoesnotexistso-404-possibly.png)
'''
md_output_article = '''
Image 1
=======

Public Domain icon from Wikimedia Commons (should display correctly):

![PD icon](0_image_0.png)

Image 2
=======

Pixel red stop sign (should display correctly):

![Pixel Stop Sign](0_image_1.png)

Image 3
=======

Broken image (connection will likely be refused):

![Broken image (connection refused)](http://badlocalwebsite.net.crap.bad/not_an_image.txt)

Image 4
=======

Link to a Wikimedia Commons page that likely returns 404 (not an image URL):

![Broken image (404)](https://commons.wikimedia.org/wiki/File:thisdoesnotexistso-404-possibly.png)
'''


from pathlib import Path
from typing import Type
import pytest
from unittest.mock import patch
from file2txt.parsers.html_file_parser import HtmlArticleFileParser, HtmlFileParser


@pytest.mark.parametrize(
    "parser_cls,expected_output",
    [
        (HtmlFileParser, md_output_basic),
        (HtmlArticleFileParser, md_output_article),
    ],
)
def test_extract_text(tmp_path, parser_cls: Type[HtmlArticleFileParser], expected_output):
    path = tmp_path/"html-sample.html"
    path.write_text(html_text)
    parser = parser_cls(path, "html", False, True)
    parser.processed_image_base_url = "https://upload.wikimedia.org/wikipedia/commons/"
    out = parser.extract_text()
    assert out == [expected_output.strip()]
