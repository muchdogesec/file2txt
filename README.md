# file2txt

## Overview

Another tool of ours, txt2stix, takes a .txt file input and then extracts IoCs (indicators of compromise) and TTPs (tactics, techniques and procedures).

However, in many cases the file a user wants to process is not usually in structured plain text file format (e.g. is usually in pdf, docx, etc. formats).

These files also commonly contain images with text that are useful to extract too.

file2txt is a Python library takes common file formats and turns them into plain text (a `txt` file) with Markdown styling.

In addition to the printed text, file2txt can also extract text from images.

Essentially file2txt is used by us to produce a text output that can be scanned for IoCs and TTPs (by [txt2stix](https://github.com/muchdogesec/txt2stix/)), but could be used for a variety of other use-cases as you see fit.

The general flow of the file2txt is as follows

<iframe width="768" height="432" src="https://miro.com/app/live-embed/uXjVKZXyIxA=/?moveToViewport=-609,-447,3339,1546&embedId=271586839462" frameborder="0" scrolling="no" allow="fullscreen; clipboard-read; clipboard-write" allowfullscreen></iframe>

## Install

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

## Configure

file2txt uses a few external services for its features. If you want to use these features, you must correctly setup a connection to these services as follows;

### Google's Cloud Vision (to extract text from images)

We use Cloud Vision to extract text from any images found in a document. To setup a connection between file2txt and Cloud Vision...

#### 1. Create project and enable API

Login to the [GCP Console](https://console.developers.google.com/).

The project name can be anything you want. It will only be visible to you in the GCP Console.

This app requires the following Google API's to work:

* [Cloud Vision API](https://console.cloud.google.com/marketplace/product/google/vision.googleapis.com)

#### 2. Authenticating to the Cloud Vision API

Using a service account to authenticate is the preferred method. To use a service account to authenticate to the Vision API:

[Follow the instructions to create a service account](https://cloud.google.com/iam/docs/service-accounts-create#creating_a_service_account). Select JSON as your key type.

Once complete, your service account key will be automatically downloaded.

#### 3. Add your key

You now need to create a directory for your Google key;

```shell
mkdir keys
```

Now copy your `<KEY>.json` file generated earlier, into the `keys` directory you just created.

Finally, rename your `<KEY>.json` to `key.json`.

### OpenAI (for cleaning up markdown)

We use a lot of local Python libraries to convert a file format to markdown (e.g. [Poppler's pdftohtml function](https://manpages.debian.org/testing/poppler-utils/pdftohtml.1.en.html)).

The output of this text can be visually very messy. If you only need a machine readable output from the script, this is fine.

However, if you want a human readable version you will often need to clean up the output of these local libraries. To do this in an automated way, file2txt offers the option to get an AI to do this for you. Currently we use OpenAI.

To setup;

#### 1. Create an API key

In your OpenAI account create an API key

#### 2. Add you API key to the `.env` file

Now copy the `.env` file example:

```shell
cp .env.example .env
```

And put your OpenAI key as the value to the variable `OPENAI_API_KEY`.

## Run

```shell
python3 file2txt.py \
	--mode mode \
	--file path/to/file.extension \
	--output my_document \
	--defang boolean \
	--extract_text_from_image boolean \
  --ai_prettify boolean
```

To upload a new file to be processed to text the following flags are used;

* `--mode` (required, dictionary): must be supported mode. Mode must support the filetype being used, else an error will be returned.
	* `image`
	* `csv`
	* `html`
	* `html_article`
	* `pdf`
	* `word`
	* `excel`
  * `powerpoint`
* `--file` (required, string): path to file to be converted to text. Note, if the filetype and mimetype of the document submitted does not match one of those supported by file2txt (and set for `mode`, an error will be returned.
* `--output` (optional, string): name of output directory name. Default is `{input_filename}/`.
* `--ai_prettify` (optional, boolean): default is `false`. file2txt will convert your file to markdown locally. Often the output of such conversions are messy (leave lots of whitespace, new lines, etc.). If you want to make the output more readable to a human, setting this argument to true will ask an AI model to clean it up for you. Recommended to use when output will be read by a human.
* `--defang` (optional, boolean): if output should be defanged. Default is `true`.
* `--extract_text_from_image` (optional, boolean): if images should be converted to text using OCR. Default is `true`. You need a valid `key/key.json` key for this to work. This flag MUST be `false` with `csv` mode and MUST be `true` with `image` mode.

The script will output all files to the `output/` directory in the following structure;

```txt
output
├── {input_filename}
│   ├── {input_filename}.md
│   ├── IMAGE_1
│   └── IMAGE_2
```

To ensure images are not lost (in modes that support images), the script also extracts and stores a copy of all identified images in the directory created for the input file.

### Examples

You can see the output from the commands below in the `output/` directory of this repository.

Convert document to human friendly markdown, extract text from images, and defang the text (the most common use-case for cyber-security);

```shell
python3 file2txt.py \
  --mode pdf \
  --file tests/files/pdf-real/bitdefender-rdstealer.pdf \
  --output examples/aipretty-defang-extracttext/Bitdefender-Labs-Report-X-creat6958-en-EN.md \
  --defang true \
  --extract_text_from_image true \
  --ai_prettify true
```

To compare, lets remove the AI prettify command;

```shell
python3 file2txt.py \
  --mode pdf \
  --file tests/files/pdf-real/bitdefender-rdstealer.pdf \
  --output examples/defang-extracttext/Bitdefender-Labs-Report-X-creat6958-en-EN.md \
  --defang true \
  --extract_text_from_image true \
  --ai_prettify false
```

And this time with AI pretty, but not extracting text from the detected images;

```shell
python3 file2txt.py \
  --mode pdf \
  --file tests/files/pdf-real/bitdefender-rdstealer.pdf \
  --output examples/aipretty-defang/Bitdefender-Labs-Report-X-creat6958-en-EN.md \
  --defang true \
  --extract_text_from_image false \
  --ai_prettify true
```

### Tests

For more examples, you can also run our automated scripts to generate files.

```shell
python3 -m unittest tests/test_1_output_file_generation.py
```

You will need Open AI and Google Vision in your `.env` file when running this test.

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

### Image (mode: `image`)

* Filetypes supported (mime-type): `jpg` (`image/jpg`), `.jpeg` (`image/jpeg`), `.png` (`image/png`), `.webp` (`image/webp`)
* Embedded images processed using `image` mode: TRUE
  * Output position matched input: n/a
* Supports paging: FALSE

### CSV (mode: `csv`)

* Filetypes supported (mime-type): `csv` (`text/csv`)
* Embedded images processed using `image` mode: FALSE
* Supports paging: FALSE

### HTML (mode: `html`)

* Filetypes supported (mime-type): `html` (`text/html`)
* Embedded images processed using `image` mode: TRUE
* Supports paging: FALSE
* HTML encoded content supported: TRUE

This will consider the entire HTML of the page (e.g. nav bars, footers, etc.). Generally you do not want this extra data (mainly problematic when exporting webpages as HTML from a browser).

Such HTML outputs can get very messy (stylesheets, javascript, etc). As such for exported pages we generally recommend users using `html_article` mode, or a html to pdf tool (e.g. [printfriendly](https://www.printfriendly.com/) or similar) and uploading the page in `pdf_mode` for best results.

### HTML Articles (mode: `html_article`)

* Filetypes supported (mime-type): `html` (`text/html`)
* Embedded images processed using `image` mode: TRUE
* Supports paging: FALSE
* HTML encoded content supported: TRUE

Many of our use-cases call for the actual article in the HTML of a website to be considered (versus the entirety of a page, e.g. the nav bar, the footer, advertisements, etc.). This mode will attempt to remove anything not considered the core content of the page.

### PDF (mode: `pdf`)

* Filetypes supported (mime-type): `pdf` (`application/pdf`)
* Embedded images processed using `image` mode: TRUE
* Supports paging: TRUE
* HTML encoded content supported: FALSE

### Microsoft Word (mode: `word`)

* Filetypes supported (mime-type): `docx` (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`), `doc` (`application/msword`)
* Embedded images processed using `image` mode: TRUE
* Supports paging: TRUE
* HTML encoded content supported: FALSE

### Microsoft Excel (mode: `excel`)

* Filetypes supported (mime-type): `xlsx` (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`), `xls` (`vnd.ms-excel`)
* Embedded images processed using `image` mode: FALSE
* Supports paging: TRUE (one page = one tab)
* HTML encoded content supported: FALSE

Any formulas and scripts are ignored.

### Powerpoint (mode: `powerpoint`)

* Filetypes supported (mime-type): `ppt` (`application/vnd.ms-powerpoint`), `.jpeg` (`application/vnd.openxmlformats-officedocument.presentationml.presentation`),
* Embedded images processed using `image` mode: TRUE
* Supports paging: TRUE (one page = one slide)

## A note on HTML encoding (for `html` and `html_article` modes)

HTML can come in a variety of flavours, file2stix can handle the following:

* Encoded: e.g. contains `&gt` vs `>`
* Decoded Raw: standard HTML tags
* Decoded CDATA: the actual Decoded Raw HTML is inside `<![CDATA[Decoded Raw HTML]]>` tags

In any mode that considers HTML, all these formats are automatically detected by the script and processed accordingly.

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

## A note on handling embedded images

In some filetype inputs, file2txt will convert text found in embedded images to text, if enabled by the user.

Embedded images are defined images that exist inline with the text. That is; when you read the document, you can see the actual image. 

To make it clear where the text shown is from an embedded image (i.e. where the original image was found in doc), when file2txt detects an image in a document it will insert the following tags; `[comment]: <> (===START EMBEDDED IMAGE EXTRACTION===)` and `[comment]: <> (===END EMBEDDED IMAGE EXTRACTION===)`. Between the tags will be any text identified in an embedded image, e.g.

```txt
Once upon a time
[comment]: <> (===START IMAGE DETECTED===)

![](image_url.png)

[comment]: <> (===START EMBEDDED IMAGE EXTRACTION===)
<TEXT IN IMAGE>
[comment]: <> (===END EMBEDDED IMAGE EXTRACTION===)

[comment]: <> (===END IMAGE DETECTED===)
The end
```

Due to the way text extraction from images is performed, it means the text identified in an image is outputted into the final markdown with no structure (e.g. if a table can be seen in an image found in a doc, it will not be a markdown table in text output).

If extract text from images is set to false, a user will only see the pure markdown image ref in the output, e.g. for the above

```txt
![](image_url.png)
```

The image URL points to the locally stored copy of the image.

## A note on handling paging

Some input types support paging.

file2txt will output a single text file, however, where pages are detected the output document will contain breaks to show where a page starts. For example;

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

## Support

[Minimal support provided via the DOGESEC community](https://community.dogesec.com/).

## License

[AGPLv3](/LICENSE).