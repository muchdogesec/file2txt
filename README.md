# file2txt

## Overview

Another tool of ours, txt2stix, takes a .txt file input and then extracts IoCs (indicators of compromise) and TTPs (tactics, techniques and procedures).

However, in many cases the file a user wants to process is not usually in structured plain text file format (e.g. is usually in pdf, docx, etc. formats).

These files also commonly contain images with text that are useful to extract too.

file2txt is a Python library takes common file formats and turns them into plain text (a `.md` file) with Markdown styling to make it as nice as possible to read.

In addition to the printed text, file2txt can also extract text from images found in the input file.

Essentially file2txt is used by us to produce a text output that can be scanned for IoCs and TTPs (by [txt2stix](https://github.com/muchdogesec/txt2stix/)), but could be used for a variety of other use-cases as you see fit.

The general flow of the file2txt is as follows:

https://miro.com/app/board/uXjVKZXyIxA=/

## tl;dr

[![file2txt](https://img.youtube.com/vi/u9Pnhs3_Qv4/0.jpg)](https://www.youtube.com/watch?v=u9Pnhs3_Qv4)

[Watch the demo](https://www.youtube.com/watch?v=u9Pnhs3_Qv4).

## Download and Install

```shell
# clone the latest code
git clone https://github.com/signalscorps/file2txt
# create a venv
cd file2txt
python3 -m venv file2txt-venv
source file2txt-venv/bin/activate
# install requirements
pip3 install -r requirements.txt
```

### Configuration options

file2txt has various settings that are defined in an `.env` file.

To create a template for the file:

```shell
cp .env.example .env
```

To see more information about how to set the variables, and what they do, read the `.env.markdown` file.


### Optional: Add Marker API Key (`MARKER_API_KEY`)

file2txt uses the [Marker API](https://www.datalab.to/marker) to process the following filetypes;

* PDF `.pdf` (`application/pdf`)
* Word `.doc` (`application/msword`), `.docx` `(application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
* Powerpoint `.ppt` (`application/vnd.ms-powerpoint`), `.pptx` (`application/vnd.openxmlformats-officedocument.presentationml.presentation`)

You only need a Marker API key if you intend to use one of the above modes.

[Get your Marker API key here](https://www.datalab.to/app/keys).

Once it's generated add your API key using the `MARKER_API_KEY` variable in the `.env` file.

You do not need a Marker API key if you only intend to convert the following file types;

* HTML `html` (`text/html`)
* HTML Article `html_article` (`text/html`)
* CSV `csv` (`text/csv`)
* Image `jpg` (`image/jpg`), `.jpeg` (`image/jpeg`), `.png` (`image/png`), `.webp` (`image/webp`)

### Optional: Add Google's Cloud Vision API Key (`GOOGLE_VISION_API_KEY`)

file2txt uses Cloud Vision to text from images found in the input documents. This feature is optional. If you do not set a Cloud Vision key, you will not be able to use the `extract_text_from_image` feature.

If you want to use this feature you must set your Cloud Vision credentials as follows...

Login to the [GCP Console](https://console.developers.google.com/).

The project name can be anything you want. It will only be visible to you in the GCP Console.

This app requires the following Google API's to work:

* [Cloud Vision API](https://console.cloud.google.com/marketplace/product/google/vision.googleapis.com)

Go to APIs and Services and create a new API Key. It's a good idea to limit the keys scope to the Cloud Vision API.

Once it's generated add your API key using the `GOOGLE_VISION_API_KEY` variable in the `.env` file.

You do not need a Google API key if you don't want to convert images to text.

## Run

```shell
python3 file2txt.py \
	--mode mode \
	--file path/to/file.extension \
	--output my_document \
	--defang boolean \
	--extract_text_from_image boolean
```

To upload a new file to be processed to text the following flags are used;

* `--mode` (required, dictionary): must be supported mode. Mode must support the filetype being used, else an error will be returned.
  * `txt`
  * `md`
	* `image`
	* `csv`
	* `html`
	* `html_article`
	* `pdf` (requires marker api key)
  * `word` (requires marker api key)
  * `powerpoint` (requires marker api key)
* `--file` (required, string): path to file to be converted to text. Note, if the filetype and mimetype of the document submitted does not match one of those supported by file2txt (and set for `mode`, an error will be returned.
* `--output` (optional, string): name of output directory name. Default is `{input_filename}/`.
* `--defang` (optional, boolean): if output should be defanged. Default is `true`.
* `--extract_text_from_image` (optional, boolean, required Google Vision api key): if images should be converted to text using OCR. Default is `true`. This flag MUST be `false` with `csv` mode and MUST be `true` with `image` mode.

The script will output all files to the `output/` directory in the following structure;

```txt
output
├── {input_filename}
│   ├── {input_filename}.md
│   ├── EXTRACTED_IMAGE_1.FORMAT
│   └── EXTRACTED_IMAGE_2.FORMAT
```

To ensure images are not lost (in modes that support images), the script also extracts and stores a copy of all identified images in the directory created for the input file.

### Examples

You can see the output from the commands below in the `examples/` directory of this repository.

If you want to try with the same files I used, read how to download them in `tests/README.md`

Turn a CSV into markdown table;

```shell
python3 file2txt.py \
  --mode csv \
  --file tests/files/csv/csv-test.csv \
  --output examples/csv_input \
  --defang true \
  --extract_text_from_image false
```

And a spreadsheet;

```shell
python3 file2txt.py \
  --mode excel \
  --file tests/files/xls/fanged_data.xlsx \
  --output examples/xls_input \
  --defang true \
  --extract_text_from_image false
```

Convert a PDF document to human friendly markdown, extract text from images, and defang the text (the most common use-case for cyber-security);

```shell
python3 file2txt.py \
  --mode pdf \
  --file tests/files/pdf-real/bitdefender-rdstealer.pdf \
  --output examples/pdf_input \
  --defang true \
  --extract_text_from_image true
```

Only convert the text in the main article on the webpage into markdown, also extract text from images, and defang the text;

```shell
python3 file2txt.py \
  --mode html_article \
  --file tests/files/html-real/unit42-Fighting-Ursa-Luring-Targets-With-Car-for-Sale.html \
  --output examples/html_article_input \
  --defang true \
  --extract_text_from_image true
```

Now convert the entire HTML content, not just the article

```shell
python3 file2txt.py \
  --mode html \
  --file tests/files/html-real/unit42-Fighting-Ursa-Luring-Targets-With-Car-for-Sale.html \
  --output examples/html_input \
  --defang true \
  --extract_text_from_image true
```

Do not defang this Word file;

```shell
python3 file2txt.py \
  --mode word \
  --file tests/files/doc/fanged_data.docx \
  --output examples/word_input_defang_f \
  --defang false \
  --extract_text_from_image true
```

Defang this word file;

```shell
python3 file2txt.py \
  --mode word \
  --file tests/files/doc/fanged_data.docx \
  --output examples/word_input_defang_t \
  --defang true \
  --extract_text_from_image true
```

Now try a Powerpoint

```shell
python3 file2txt.py \
  --mode powerpoint \
  --file tests/files/ppt/fanged_data.pptx \
  --output examples/ppt_input \
  --defang true \
  --extract_text_from_image true
```

Extract data from an png image;

```shell
python3 file2txt.py \
  --mode image \
  --file tests/files/image/example-1.png \
  --output examples/image_input \
  --defang true \
  --extract_text_from_image true
```

See how file2txt deals with markdown inputs;

```shell
python3 file2txt.py \
  --mode md \
  --file tests/files/markdown/threat-report.md \
  --output examples/markdown_input \
  --defang true \
  --extract_text_from_image true
```

### Tests

For more examples, you can also run our automated scripts to generate files.

```shell
python3 -m unittest tests/test_1_output_file_generation.py
```

You will need a Google Vision in your `.env` file when running this test.

This script generates output files using a combination of file2txt settings.

You need to check the output manually to ensure it matches expectations.

```shell
python3 -m unittest tests/test_2_negative_tests.py
```

This will test invalid file input settings. All tests are expected to fail.

## Debugging

If the script is failing, you can examine the log file printed in `logs/` to try and resolve any issues. Each run has its own log, named using execution time (e.g. `file2txt_20231127-205228_846248.log`).

## File types and Input types

You can upload a range of filetypes to file2txt.

File extensions and mimetypes are validated on input for security, if they are not supported an error is returned.

The input file type determines how the files should be handled.

### Text (mode: `txt`)

* Filetypes supported (mime-type): `txt` (`text/plain`)
* Embedded images processed using `image` mode and stored locally: FALSE
* Supports paging: FALSE
* Python library used for conversion to markdown: n/a

### Text (mode: `md`)

* Filetypes supported (mime-type): `.md` (`text/markdown`), `.markdown` (`text/markdown`)
* Embedded images processed using `image` mode and stored locally: TRUE
* Supports paging: FALSE
* Python library used for conversion to markdown: n/a

### Image (mode: `image`)

* Filetypes supported (mime-type): `jpg` (`image/jpg`), `.jpeg` (`image/jpeg`), `.png` (`image/png`), `.webp` (`image/webp`)
* Embedded images processed using `image` mode and stored locally: TRUE
* Supports paging: FALSE
* Python library used for conversion to markdown: n/a

### CSV (mode: `csv`)

* Filetypes supported (mime-type): `csv` (`text/csv`)
* Embedded images processed using `image` mode and stored locally: FALSE
* Supports paging: FALSE
* Python library used for conversion to markdown: `pandas`

### Microsoft Excel (mode: `excel`)

* Filetypes supported (mime-type): `xls` (`application/vnd.ms-excel`), `xlsx` (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
* Embedded images processed using `image` mode and stored locally: FALSE
* Supports paging: FALSE (only considers first tab)
* Python library used for conversion to markdown: `pandas`

### HTML (mode: `html`)

* Filetypes supported (mime-type): `html` (`text/html`)
* Embedded images processed using `image` mode and stored locally: TRUE
* Supports paging: FALSE
* Python library used for conversion to markdown: `python-markdownify`

This will consider the entire HTML of the page (e.g. nav bars, footers, etc.). Generally you do not want this extra data (mainly problematic when exporting webpages as HTML from a browser).

Such HTML outputs can get very messy (stylesheets, javascript, etc). As such for exported pages we generally recommend users using `html_article` mode, or a html to pdf tool (e.g. [printfriendly](https://www.printfriendly.com/) or similar) and uploading the page in `pdf_mode` for best results.

### HTML Articles (mode: `html_article`)

* Filetypes supported (mime-type): `html` (`text/html`)
* Embedded images processed using `image` mode and stored locally: TRUE
* Supports paging: FALSE
* Python library used for conversion to markdown: see `html` mode

Many of our use-cases call for the actual article in the HTML of a website to be considered (versus the entirety of a page, e.g. the nav bar, the footer, advertisements, etc.). This mode will attempt to remove anything not considered the core content of the page.

### PDF (mode: `pdf`)

* Filetypes supported (mime-type): `pdf` (`application/pdf`)
* Embedded images processed using `image` mode and stored locally: TRUE
* Supports paging: TRUE
* Marker API

### Microsoft Word (mode: `word`)

* Filetypes supported (mime-type): `docx` (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`), `doc` (`application/msword`)
* Embedded images processed using `image` mode and stored locally: TRUE
* Supports paging: TRUE
* Marker API

### Powerpoint (mode: `powerpoint`)

* Filetypes supported (mime-type): `ppt` (`application/vnd.ms-powerpoint`), `.jpeg` (`application/vnd.openxmlformats-officedocument.presentationml.presentation`),
* Embedded images processed using `image` mode and stored locally: TRUE
* Supports paging: TRUE (one page = one slide)
* Marker API

### Unsupported Microsoft propriety filetypes and workarounds

Generally, where a filetype is not supportedt

Similarly, for other word processing formats, there is usually the option to save to pdf, which can then be uploaded to file2txt.

## A note on HTML encoding (for `html` and `html_article` modes)

HTML can be printed in a variety of ways

* Encoded: e.g. contains `&gt` vs `>`
* Decoded Raw: standard HTML tags
* Decoded CDATA: the actual Decoded Raw HTML is inside `<![CDATA[Decoded Raw HTML]]>` tags (most common in XML/JSON docs containing HTML, most commonly RSS/ATOM feeds)

As an example, endcoded

```html
&gt;img src=&quot;https://cms.therecord.media/uploads/2023_0706_Ransomware_Tracker_Most_Prolific_Groups_6a567c11da.jpg&quot;&lt;
```

Which as decoded raw html looks as follows

```html
<img src="https://cms.therecord.media/uploads/2023_0706_Ransomware_Tracker_Most_Prolific_Groups_6a567c11da.jpg">
```

Which as decoded CDATA looks like

```html
<![CDATA[<img src="https://cms.therecord.media/uploads/2023_0706_Ransomware_Tracker_Most_Prolific_Groups_6a567c11da.jpg">]]>
```

**IMPORTANT:** file2txt only supports decoded HTML.

If your HTML data is encoded, or wrapped in CDATA tags, you must first convert it to decoded HTML before processing with file2txt otherwise you the output will not be converted correctly.

## A note on handling embedded images

In some filetype inputs, file2txt will convert text found in embedded images to text, if enabled by the user.

Embedded images are defined images that exist inline with the text. That is; when you read the document, you can see the actual image.

Images are identified using image tags in the supported modes (HTML and PDF). file2txt will always store a copy of identified images locally, even if you do not enable image text extraction.

To make it clear where the text shown is from an embedded image (i.e. where the original image was found in doc) in the output, when file2txt detects an image in a document it will insert the following tags; `[comment]: <> (===START EMBEDDED IMAGE EXTRACTION===)` and `[comment]: <> (===END EMBEDDED IMAGE EXTRACTION===)`. Between the tags will be any text identified in an embedded image, e.g.

```txt
Once upon a time
[comment]: <> (===START IMAGE DETECTED===)

![](local/path/to/image_url.png)

[comment]: <> (===START EMBEDDED IMAGE EXTRACTION===)
<TEXT IN IMAGE>
[comment]: <> (===END EMBEDDED IMAGE EXTRACTION===)

[comment]: <> (===END IMAGE DETECTED===)
The end
```

Due to the way text extraction from images is performed, it means the text identified in an image is outputted into the final markdown with no structure (e.g. if a table can be seen in an image found in a doc, it will not be a markdown table in text output).

If extract text from images is set to false, a user will only see the pure markdown image ref in the output, e.g. for the above

```txt
![](local/path/to/image_url.png)
```

The image URL always points to the locally stored copy of the image.

## A note on handling paging

PDF input types support paging. This is done by splitting a pdf of many pages, into individual pdf files per page.

file2txt will output a single text file with all the pdf page text extractions merged. Pages (i.e. each txt file for each pdf page produced) is shown in the output document with breaks to show where a page starts and ends. 

For example;

```txt
[comment]: <> (===START PAGE 1===)

Some content

OK
[comment]: <> (===END PAGE 1===)
[comment]: <> (===START PAGE 2===)

Another page
[comment]: <> (===END PAGE 2===)
```

Note, if the input type does not support paging, page breaks are included, but will only ever show page 1 start and end.

## Defanging

### An introduction to fanging

Fanging obfuscates indicators into a safer representations so that a user reading a report does not accidentally click on a malicious URL or inadvertently run malicious code. Many cyber threat intelligence reports shared electronically employ fanging.

Typical types of fanged Observables include IPv4 addresses (e.g. `1.1.1[.]1`), IPv6 addresses (e.g. `2001:0db8:85a3:0000:0000:8a2e:0370[:]7334`), domain names (e.g. `example[.]com`), URLs (e.g. `https[:]//example.com/research/index.html`), email addresses (e.g. `example[@]example.com`), file extensions (e.g. `malicious[.]exe`), and directory paths (e.g. `[C:]\\Windows\\System32`).

As file2txt was built for security reports, it is very likely the input will be fanged. Therefore, file2txt offers users the ability to defang all text in the input.

Unfortunately, there is no universal standard for fanging, although there are some common methods. Some samples of fanging I have observed include the following:

* Wrapping one or more special characters in `[` `]`
  * e.g. `www[.]example[.]com`
  * e.g. `http[:]//example.com`
  * e.g. `http[://]example.com`
  * e.g. `1.1.1.1[/]24`
* Wrapping one or more special characters in `{` `}`
* Wrapping one or more special characters in `(` `)`
* Replacing `http` and `hxxp`
  * e.g. `hxxps://google.com`
* Replacing `.` with ` dot `
  * e.g. `example@example dot com`
  * e.g. `http://example dot com`
* Replacing `.` with `[dot]` (or  `(dot)`, or `{dot}`)
  * e.g. `example@example[dot]com`
* Replacing `@` with ` at `
  * e.g. `example at example.com`
* Replacing `@` with `[at]` (or  `(at)`, or `{at}`)
  * e.g. `example[at]example.com` 

A combination of the above techniques are also commonly implemented for defanging. For example replacing `.` with ` dot ` and replacing `@` with ` at ` for an email like so; fanged = `example at example dot com`, defanged = `example@example.com`

Another example using even more fanging technique combinations for a URL; fanged = `hxxps[:]//test\.example[.)com[/]path`, defanged = `https://test.example.com/path`

### Defanging observables logic

At the final step of processing, file2txt will defang all txt outputs using a find and replace stratergy in the following order to defang:

* replaces the text `hxxp` with `http`
* replaces the text `{dot}` with `.`
* replaces the text ` {dot} ` with `.`
* replaces the text `[dot]` with `.`
* replaces the text ` [dot] ` with `.`
* replaces the text `(dot)` with `.`
* replaces the text ` (dot) ` with `.`
* replaces the text `{at}` with `@`
* replaces the text ` {at} ` with `@`
* replaces the text `[at]` with `@`
* replaces the text ` [at] ` with `@`
* replaces the text `(at)` with `@`
* replaces the text ` (at) ` with `@`
* removes the square bracket characters (`[` and `]`) around the following special characters;
    * `.`
  * ` . `
    * `@`
  * ` @ `
    * `/`
  * ` / `
    * `\`
  * ` \ `
  * `://`
  * ` :// `
* removes the curly bracket characters (`{` and `}`) around the following special characters;
  * `.`
  * ` . `
  * `@`
  * ` @ `
  * `/`
  * ` / `
  * `\`
  * ` \ `
  * `://`
  * ` :// `
* removes the parentheses characters (`(` and `)`) around the following special characters;
  * `.`
  * ` . `
  * `@`
  * ` @ `
  * `/`
  * ` / `
  * `\`
  * ` \ `
  * `://`
  * ` :// `

As an example, `/tests/txt/fanged_data_good.txt` processed in `defang` mode goes from

```txt
...
C: (\) Windows (\) System32
[2002(:)(:)abcd(:)ffff(:)c0a8(:)101](:)80
[2002 (:)  (:) abcd (:) ffff (:) c0a8 (:) 101] (:) 80
someone(@)example.com
someone (@) example.com
http(://)example.com
http (://) example.com
http (://) example[.]something{dot}other(dot)com(/)this[/]file{.}html
...
```

to

```txt
C:\Windows\System32
[2002::abcd:ffff:c0a8:101]:80
[2002::abcd:ffff:c0a8:101]:80
someone@example.com
someone@example.com
http://example.com
http://example.com
http://example.something.other.com/this/file.html 
```

## A note on output structure

The output of the script is always markdown.

It will generally markdown title tags (e.g. `#`, `##`, `###`), table, image tags, link tags, etc as the output is designed to closely match the styling of the input document.

However, it is not always perfect. As a general rule, the cleaner the styling for input (i.e, report type structure is best -> interactive webpages worst) the better file2txt will handle the output.

This does not apply to images (see embedded images).

## Support

[Minimal support provided via the DOGESEC community](https://community.dogesec.com/).

## License

[Apache 2.0](/LICENSE).