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
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
}

# Modes and their corresponding file groups
MODES = {
    "csv": "csv",
    "image": "image",
    "html": "html",
    "html_article": "html",
    "pdf": "pdf",
    "word": "word",
    "excel": "excel",
    "powerpoint": "powerpoint"
}

# Grouping files by their types
TEST_FILES = {
    "csv": [
        "csv/csv-test.csv"
    ],
    "word": [
        # "doc/fanged_data.doc", # not supported
        "doc/fanged_data.docx"
    ],
    "html": [
        "html/fanged_data.html"
    ],
    "html-real": [
        "html/bitdefender-fragments-of-cross-platform-backdoor-hint-at-larger-mac-os-attack.html",
        "html/group-ib-0ktapus.html",
        "html/unit42-mallox-ransomware.html",
        "html/virustotal-malware-trends.html"
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
        "pdf/fanged_data_good.pdf",
        "pdf/pdf-example.pdf"
    ],
    "pdf-real": [
        "pdf/bitdefender-rdstealer.pdf",
        "pdf/canadian-cert-qakbot.pdf",
        "pdf/crowdstrike-fancy-bear.pdf",
        "pdf/france-cert-apt31-1.pdf",
        "pdf/france-cert-apt31-2.pdf",
        "pdf/group-ib-ransomware-report.pdf",
        "pdf/kaspersky-sofacy.pdf",
        "pdf/mandiant-apt1-report.pdf",
        "pdf/norma-cyber-oil-gas.pdf",
        "pdf/rpt-apt30.pdf",
        "pdf/sophoslabs-mykings.pdf",
        "pdf/thai-cert-threat-actors.pdf"
    ],
    "excel": [
        "xls/xls-test.xls",
        "xls/xls-test.xlsx"
    ],
    "powerpoint": [
        "ppt/fanged_data.ppt",
        "ppt/fanged_data.pptx"
    ]
}

def get_mimetype(filename):
    _, ext = os.path.splitext(filename)
    return EXTENSION_TO_MIMETYPE.get(ext)
