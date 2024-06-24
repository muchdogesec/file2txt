# python3 -m unittest tests/test_2_negative_tests.py

import os
import shutil
import subprocess
import unittest
from tests.base_test import TEST_FILES_DIRECTORY, MODES, TEST_FILES, get_mimetype

def delete_directories():
    """Delete 'logs' and 'output/negative_tests' directories if they exist."""
    directories = ['logs', 'output/negative_tests']
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)

class TestFile2TxtNegative(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Delete directories once before running any tests."""
        delete_directories()

    def run_test(self, test_number, mode, file):
        input_filepath = os.path.join(TEST_FILES_DIRECTORY, file)
        # Get the MIME type of the input file
        mime_type = get_mimetype(file)

        # Create the output directory
        filename_without_ext = os.path.splitext(os.path.basename(file))[0]
        output_directory = os.path.join('output', 'negative_tests', filename_without_ext)
        os.makedirs(output_directory, exist_ok=True)

        # Create a more descriptive output filename
        output_filename = f"{mode}_{filename_without_ext}_defang-false_extract-false_output"
        output_filepath = os.path.join(output_directory, output_filename)

        # Construct the command
        command = [
            "python3", "file2txt.py",
            "--mode", mode,
            "--file", input_filepath,
            "--output", output_filepath,
            "--defang", "false",
            "--extract_text_from_image", "false"
        ]

        print(f"===TEST {test_number}=== Running command: {' '.join(command)}")
        print(f"MIME type of input file '{file}': {mime_type}")

        # Execute the command and expect it to fail
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
        print(f"Errors (if any):\n{result.stderr}")

        self.assertNotEqual(result.returncode, 0, f"Command succeeded unexpectedly with error: {result.stderr}")

    def test_invalid_mode_file_combinations(self):
        test_number = 1
        # Create invalid combinations by using files with unexpected MIME types for each mode
        invalid_combinations = {
            "csv": TEST_FILES["word"],  # Word files in csv mode
            "word": TEST_FILES["html"],  # HTML files in word mode
            "html": TEST_FILES["pdf"],  # PDF files in html mode
            "pdf": TEST_FILES["image"],  # Image files in pdf mode
            "image": TEST_FILES["excel"],  # Excel files in image mode
            "excel": TEST_FILES["csv"],  # CSV files in excel mode
            "powerpoint": TEST_FILES["word"],  # Word files in powerpoint mode
        }

        for mode, files in invalid_combinations.items():
            for file in files:
                print(f"===TEST {test_number}===")  # Print test number
                with self.subTest(mode=mode, file=file):
                    self.run_test(test_number, mode, file)
                test_number += 1  # Increment test number here, outside of subTest context

    def test_csv_mode_with_extract_text_from_image_true(self):
        test_number = "special"
        mode = "csv"
        file = TEST_FILES["csv"][0]  # Use the first CSV file

        input_filepath = os.path.join(TEST_FILES_DIRECTORY, file)
        # Get the MIME type of the input file
        mime_type = get_mimetype(file)

        # Create the output directory
        filename_without_ext = os.path.splitext(os.path.basename(file))[0]
        output_directory = os.path.join('output', 'negative_tests', filename_without_ext)
        os.makedirs(output_directory, exist_ok=True)

        # Create a more descriptive output filename
        output_filename = f"{mode}_{filename_without_ext}_defang-false_extract-true_output"
        output_filepath = os.path.join(output_directory, output_filename)

        # Construct the command
        command = [
            "python3", "file2txt.py",
            "--mode", mode,
            "--file", input_filepath,
            "--output", output_filepath,
            "--defang", "false",
            "--extract_text_from_image", "true"
        ]

        print(f"===TEST {test_number}=== Running command: {' '.join(command)}")
        print(f"MIME type of input file '{file}': {mime_type}")

        # Execute the command and expect it to fail
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
        print(f"Errors (if any):\n{result.stderr}")

        self.assertNotEqual(result.returncode, 0, f"Command succeeded unexpectedly with error: {result.stderr}")

    def test_bad_mode(self):
        test_number = "bad_mode"
        mode = "bad_mode"
        file = TEST_FILES["csv"][0]  # Use the first CSV file

        input_filepath = os.path.join(TEST_FILES_DIRECTORY, file)
        # Get the MIME type of the input file
        mime_type = get_mimetype(file)

        # Create the output directory
        filename_without_ext = os.path.splitext(os.path.basename(file))[0]
        output_directory = os.path.join('output', 'negative_tests', filename_without_ext)
        os.makedirs(output_directory, exist_ok=True)

        # Create a more descriptive output filename
        output_filename = f"{mode}_{filename_without_ext}_defang-false_extract-false_output"
        output_filepath = os.path.join(output_directory, output_filename)

        # Construct the command
        command = [
            "python3", "file2txt.py",
            "--mode", mode,
            "--file", input_filepath,
            "--output", output_filepath,
            "--defang", "false",
            "--extract_text_from_image", "false"
        ]

        print(f"===TEST {test_number}=== Running command: {' '.join(command)}")
        print(f"MIME type of input file '{file}': {mime_type}")

        # Execute the command and expect it to fail
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
        print(f"Errors (if any):\n{result.stderr}")

        self.assertNotEqual(result.returncode, 0, f"Command succeeded unexpectedly with error: {result.stderr}")

if __name__ == "__main__":
    unittest.main()
