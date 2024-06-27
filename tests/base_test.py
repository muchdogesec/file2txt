import os
# Directory containing the test files
TEST_FILES_DIRECTORY = "tests/files/"

# Mapping file extensions to their expected MIME types
EXTENSION_TO_MIMETYPE = {
    ".csv": "text/csv",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".html": "text/html",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

# Modes and their corresponding file groups
MODES = {
    "csv": "csv",
    "image": "image",
    "html": "html",
    "html_article": "html",
    "pdf": "pdf",
    "word": "word",
    "excel": "excel"
}

# Grouping files by their types
TEST_FILES = {
    "csv": [
        "csv/csv-test.csv"
    ],
    "word": [
        "doc/fanged_data.doc",
        "doc/fanged_data.docx"
    ],
    "html": [
        "html/group-ib_roasting_0ktapus-html-only.html",
        "html/unit-42_mallox_ransomware-html-only.html",
        "html/virustotal_malware-trends.html"
    ],
    "image": [
        "image/example-1.png",
        "image/example-2.webp",
        "image/example-3.jpeg",
        "image/example-4.jpg",
        "image/test-image-1.png",
        "image/test-image-2.webp",
        "image/test-image-3.png"
    ],
    "pdf": [
        "pdf/Bitdefender-Labs-Report-X-creat6958-en-EN.pdf",
        "pdf/fanged_data_good.pdf",
        "pdf/pdf-example.pdf"
    ],
    "excel": [
        "xls/xls-test.xls",
        "xls/xls-test.xlsx"
    ]
}

def get_mimetype(filename):
    _, ext = os.path.splitext(filename)
    return EXTENSION_TO_MIMETYPE.get(ext)
