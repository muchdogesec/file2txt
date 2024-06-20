## Background

There are many existing Python libraries that convert rich files into plain text, for example [pdfPlumber](https://github.com/jsvine/pdfplumber) for turning PDFs into text files.

We use off-the-shelf python libraries to convert raw text.

There are also cloud services that extract images into text (using OCR), e.g. [Google Cloud OCR](https://cloud.google.com/vision/docs/ocr).

This is what is used to extract text from images.

At present, a number of AI solutions can also be used to convert structured files into text (and read the text in images). However, the cost of doing this at scale is high and it doesn't really offer any added value for very structure tasks like the ones needed here.

The general flow of the file2txt is as follows

[![image](https://github.com/muchdogesec/file2txt/assets/29603874/5a5bdc87-f65a-41f7-8882-1163140d4827)](https://miro.com/app/live-embed/uXjVKZXyIxA=/?moveToViewport=-702,-793,3505,1688&embedId=254157208472)


## File types and Input types

You can upload a range of filetypes to file2txt.

File extensions and mimetypes are validated on input for security, if they are not supported an error is returned.

The input file type determines how the files should be handled.

### Image (mode: `image`)

* Filetypes supported (mime-type): `jpg` (`image/jpg`), `.jpeg` (`image/jpeg`), `.png` (`image/png`), `.webp` (`image/webp`)
* Embedded images processed using `image` mode: TRUE
  * Output position matched input: n/a
* Supports paging: FALSE

The text in the image is printed as raw text in the output. It does not maintain the struture (e.g. if table in image, it will not be a table in text output)

### CSV (mode: `csv`)

* Filetypes supported (mime-type): `csv` (`text/csv`)
* Embedded images processed using `image` mode: n/a
  * Output position matched input: n/a
* Supports paging: FALSE

The tabular structure of the CSV is converted into a single markdown table.

### HTML (mode: `html`)

* Filetypes supported (mime-type): `html` (`text/html`)
* Embedded images processed using `image` mode: TRUE
  * Output position matched input: TRUE
* Supports paging: FALSE
* HTML encoded content supported: TRUE

This will consider the entire HTML of the page (e.g. nav bars, footers, etc.). Generally you do not want this extra data (mainly problematic when exporting webpages as HTML from a browser).

Such HTML outputs can get very messy (stylesheets, javascript, etc). As such for exported pages we generally recommend users using `html_article` mode, or a html to pdf tool (e.g. [printfriendly](https://www.printfriendly.com/) or similar) and uploading the page in `pdf_mode` for best results.

### HTML Articles (mode: `html_article`)

* Filetypes supported (mime-type): `html` (`text/html`)
* Embedded images processed using `image` mode: TRUE
  * Output position matched input: TRUE
* Supports paging: FALSE
* HTML encoded content supported: TRUE

Our use-case only calls for the actual article in the HTML to be considered (versus the entirety of a page, e.g. the nav bar)

[To only convert the article in the text the readability-lxml python library is used by file2txt](https://pypi.org/project/readability-lxml/).

### PDF (mode: `pdf`)

* Filetypes supported (mime-type): `pdf` (`application/pdf`)
* Embedded images processed using `image` mode: TRUE
  * Output position matched input: FALSE
* Supports paging: TRUE
* HTML encoded content supported: FALSE

Note, to support pagination, the pdf is first broken up into seperate pdf files (one for each page) for processing.

### Microsoft Word (mode: `word`)

* Filetypes supported (mime-type): `docx` (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`), `doc` (`application/msword`)
* Embedded images processed using `image` mode: TRUE
  * Output position matched input: FALSE
* Supports paging: TRUE
* HTML encoded content supported: FALSE

To simplify processing pipeline, all Word documents are first converted to PDF, and then processed as per the PDF pipeline.

Note, script is designed to run on Linux machines (thus no Microsoft only compatible tooling is used).

### Microsoft Excel (mode: `excel`)

* Filetypes supported (mime-type): `xlsx` (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`), `xls` (`vnd.ms-excel`)
* Embedded images processed using `image` mode: FALSE
  * Output position matched input: n/a
* Supports paging: TRUE (one page = one tab)
* HTML encoded content supported: FALSE

Any formulas and scripts are ignored.

Note, script is designed to run on Linux machines (thus no Microsoft only compatible tooling is used).

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

## A note on embedded images

In some filetype inputs, file2txt will convert text found in embedded images to text, if enabled by the user.

Embedded images are defined images that exist inline with the text. That is; when you read the document, you can see the actual image. 

To make it clear where the text shown is from an embedded image (i.e. where the original image was found in doc), when file2txt detects an image in a document it will insert the following tags; `[comment]: <> (===START EMBEDDED IMAGE EXTRACTION===)` and `[comment]: <> (===END EMBEDDED IMAGE EXTRACTION===)`. Between the tags will be any text identified in an embedded image, e.g.

```txt
Once upon a time
[comment]: <> (===START EMBEDDED IMAGE EXTRACTION===)
<MARKDOWN IMAGE TAG KEPT FOR REFERENCE>
Some text in an image
[comment]: <> (===END EMBEDDED IMAGE EXTRACTION===)
The end
```

## A note on paging

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

Note, if the input type does not support paging, page breaks are included, but will only ever show page 1.

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
