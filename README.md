# file2txt

## Overview

Another tool of ours, txt2stix, takes a .txt file input and then extracts IoCs (indicators of compromise) and TTPs (tactics, techniques and procedures).

However, in many cases the file a user wants to process is not usually in structured plain text file format (e.g. is usually in pdf, docx, etc. formats).

These files also commonly contain images with text that are useful to extract too.

file2txt is a Python library takes common file formats and turns them into plain text (a `txt` file) with Markdown styling. file2txt not only consider raw text inside a file input, it also converts any embedded images that contain text in the output.

Essentially file2txt is used by us to produce a text output that can be scanned for IoCs (for txt2stix), but could be used for a variety of other use-cases as you see fit.

## Configure

file2txt uses Google's Cloud Vision API.

To use the Cloud Vision API you will need to setup a new project in Google Cloud to access the Google API's.

### 1. Create project and enable API

To do this, login to the [GCP Console](https://console.developers.google.com/).

The project name can be anything you want. It will only be visible to you in the GCP Console.

This app requires the following Google API's to work:

* [Cloud Vision API](https://console.cloud.google.com/marketplace/product/google/vision.googleapis.com)

### 2. Authenticating to the Cloud Vision API

Using a service account to authenticate is the preferred method. To use a service account to authenticate to the Vision API:

[Follow the instructions to create a service account](https://cloud.google.com/iam/docs/service-accounts-create#creating_a_service_account). Select JSON as your key type.

Once complete, your service account key will be automatically downloaded.

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

### Post install required steps

You now need to create a directory for your Google key;

```shell
mkdir keys
```

Now copy your `<KEY>.json` file generated earlier, into the `keys` directory you just created.

Finally, rename your `<KEY>.json` to `key.json`.

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
	* `image`
	* `csv`
	* `html`
	* `html_article`
	* `pdf`
	* `word`
	* `excel`
* `--file` (required, string): path to file to be converted to text. Note, if the filetype and mimetype of the document submitted does not match one of those supported by file2txt (and set for `mode`, an error will be returned.
* `--output` (optional, string): name of output path/file. Default is `output/{input_filename}.file2txt-{mode}.md`.
* `--defang` (optional, boolean): if output should be defanged. Default is `true`.
* `--extract_text_from_image` (optional, boolean): if images should be converted to text using OCR. Default is `true`. You need a valid `key/key.json` key for this to work. This flag cannot be used with `csv` mode.

## Debugging

If the script is failing, you can examine the log file printed in `logs/` to try and resolve any issues. Each run has its own log, named using execution time (e.g. `file2txt_20231127-205228_846248.log`).

## Support

[Minimal support provided via the DOGESEC community](https://community.dogesec.com/).

## License

[Apache 2.0](/LICENSE).